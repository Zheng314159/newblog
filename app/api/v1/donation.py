from datetime import datetime, timedelta
from typing import List, Optional
from decimal import Decimal
import json
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlmodel import select, func
from sqlalchemy import and_

from app.core.database import async_session
from app.core.security import get_current_user, require_admin
from app.models.user import User, UserRole
from app.models.donation import (
    DonationConfig, DonationRecord, DonationGoal,
    DonationStatus, PaymentMethod, DonationType,
    DonationConfigUpdate, DonationCreate, DonationResponse,
    DonationGoalCreate, DonationGoalUpdate, DonationGoalResponse,
    DonationStats
)
from app.core.email import email_service
from app.core.config import settings
from app.core.exceptions import BlogException

router = APIRouter(prefix="/donation", tags=["捐赠"])


# ==================== 捐赠配置管理 ====================

@router.get("/config", response_model=DonationConfig)
async def get_donation_config():
    """获取捐赠配置"""
    async with async_session() as session:
        result = await session.execute(select(DonationConfig).limit(1))
        config = result.scalar_one_or_none()
        
        if not config:
            # 创建默认配置
            config = DonationConfig()
            session.add(config)
            await session.commit()
            await session.refresh(config)
        
        return config


@router.put("/config", response_model=DonationConfig)
async def update_donation_config(
    config_update: DonationConfigUpdate,
    current_user: User = Depends(require_admin)
):
    """更新捐赠配置（仅管理员）"""
    async with async_session() as session:
        result = await session.execute(select(DonationConfig).limit(1))
        config = result.scalar_one_or_none()
        
        if not config:
            config = DonationConfig()
            session.add(config)
        
        # 更新配置
        update_data = config_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(config, field, value)
        
        config.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(config)
        
        return config


# ==================== 捐赠记录管理 ====================

@router.post("/create", response_model=DonationResponse)
async def create_donation(
    donation_data: DonationCreate,
    current_user: Optional[User] = Depends(get_current_user),
    background_tasks: BackgroundTasks = None
):
    """创建捐赠记录"""
    async with async_session() as session:
        # 检查捐赠功能是否启用
        result = await session.execute(select(DonationConfig).limit(1))
        config = result.scalar_one_or_none()
        
        if not config or not config.is_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="捐赠功能未启用"
            )
        
        # 检查支付方式是否启用
        payment_enabled = getattr(config, f"{donation_data.payment_method.lower()}_enabled", False)
        if not payment_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{donation_data.payment_method} 支付方式未启用"
            )
        
        # 创建捐赠记录
        donation = DonationRecord(
            donor_name=donation_data.donor_name,
            donor_email=donation_data.donor_email,
            donor_message=donation_data.donor_message,
            is_anonymous=donation_data.is_anonymous,
            amount=donation_data.amount,
            currency=donation_data.currency,
            donation_type=donation_data.donation_type,
            payment_method=donation_data.payment_method,
            user_id=current_user.id if current_user else None
        )
        
        session.add(donation)
        await session.commit()
        await session.refresh(donation)
        
        # 发送确认邮件（如果提供了邮箱）
        if donation.donor_email and background_tasks:
            background_tasks.add_task(
                send_donation_confirmation_email,
                donation.donor_email,
                donation.donor_name,
                donation.amount,
                donation.currency
            )
        
        return donation


@router.get("/records", response_model=List[DonationResponse])
async def get_donation_records(
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[DonationStatus] = None,
    current_user: User = Depends(require_admin)
):
    """获取捐赠记录列表（仅管理员）"""
    async with async_session() as session:
        query = select(DonationRecord)
        
        if status_filter:
            query = query.where(DonationRecord.payment_status == status_filter)
        
        query = query.order_by(DonationRecord.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await session.execute(query)
        donations = result.scalars().all()
        
        return donations


@router.get("/records/my", response_model=List[DonationResponse])
async def get_my_donation_records(
    current_user: User = Depends(get_current_user)
):
    """获取我的捐赠记录"""
    async with async_session() as session:
        query = select(DonationRecord).where(
            DonationRecord.user_id == current_user.id
        ).order_by(DonationRecord.created_at.desc())
        
        result = await session.execute(query)
        donations = result.scalars().all()
        
        return donations


@router.put("/records/{donation_id}/status")
async def update_donation_status(
    donation_id: int,
    status: DonationStatus,
    transaction_id: Optional[str] = None,
    current_user: User = Depends(require_admin)
):
    """更新捐赠状态（仅管理员）"""
    async with async_session() as session:
        result = await session.execute(
            select(DonationRecord).where(DonationRecord.id == donation_id)
        )
        donation = result.scalar_one_or_none()
        
        if not donation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="捐赠记录不存在"
            )
        
        donation.payment_status = status
        if transaction_id:
            donation.transaction_id = transaction_id
        
        if status == DonationStatus.SUCCESS:
            donation.paid_at = datetime.utcnow()
            
            # 更新统计信息
            config_result = await session.execute(select(DonationConfig).limit(1))
            config = config_result.scalar_one_or_none()
            if config:
                config.total_donations += 1
                config.total_amount += donation.amount
                config.updated_at = datetime.utcnow()
        
        donation.updated_at = datetime.utcnow()
        await session.commit()
        
        return {"message": "状态更新成功"}


# ==================== 捐赠目标管理 ====================

@router.post("/goals", response_model=DonationGoalResponse)
async def create_donation_goal(
    goal_data: DonationGoalCreate,
    current_user: User = Depends(require_admin)
):
    """创建捐赠目标（仅管理员）"""
    async with async_session() as session:
        goal = DonationGoal(**goal_data.dict())
        session.add(goal)
        await session.commit()
        await session.refresh(goal)
        
        # 计算进度百分比
        goal.progress_percentage = float(goal.current_amount / goal.target_amount * 100)
        
        return goal


@router.get("/goals", response_model=List[DonationGoalResponse])
async def get_donation_goals(
    active_only: bool = True
):
    """获取捐赠目标列表"""
    async with async_session() as session:
        query = select(DonationGoal)
        
        if active_only:
            query = query.where(
                and_(
                    DonationGoal.is_active == True,
                    DonationGoal.is_completed == False
                )
            )
        
        query = query.order_by(DonationGoal.created_at.desc())
        result = await session.execute(query)
        goals = result.scalars().all()
        
        # 计算进度百分比
        for goal in goals:
            goal.progress_percentage = float(goal.current_amount / goal.target_amount * 100)
        
        return goals


@router.put("/goals/{goal_id}", response_model=DonationGoalResponse)
async def update_donation_goal(
    goal_id: int,
    goal_update: DonationGoalUpdate,
    current_user: User = Depends(require_admin)
):
    """更新捐赠目标（仅管理员）"""
    async with async_session() as session:
        result = await session.execute(
            select(DonationGoal).where(DonationGoal.id == goal_id)
        )
        goal = result.scalar_one_or_none()
        
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="捐赠目标不存在"
            )
        
        # 更新目标
        update_data = goal_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(goal, field, value)
        
        goal.updated_at = datetime.utcnow()
        
        # 检查是否完成
        if goal.current_amount >= goal.target_amount:
            goal.is_completed = True
        
        await session.commit()
        await session.refresh(goal)
        
        # 计算进度百分比
        goal.progress_percentage = float(goal.current_amount / goal.target_amount * 100)
        
        return goal


@router.delete("/goals/{goal_id}")
async def delete_donation_goal(
    goal_id: int,
    current_user: User = Depends(require_admin)
):
    """删除捐赠目标（仅管理员）"""
    async with async_session() as session:
        result = await session.execute(
            select(DonationGoal).where(DonationGoal.id == goal_id)
        )
        goal = result.scalar_one_or_none()
        
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="捐赠目标不存在"
            )
        
        await session.delete(goal)
        await session.commit()
        
        return {"message": "捐赠目标删除成功"}


# ==================== 捐赠统计 ====================

@router.get("/stats", response_model=DonationStats)
async def get_donation_stats(
    current_user: User = Depends(require_admin)
):
    """获取捐赠统计信息（仅管理员）"""
    async with async_session() as session:
        # 总捐赠统计
        total_result = await session.execute(
            select(
                func.count(DonationRecord.id).label("total_donations"),
                func.sum(DonationRecord.amount).label("total_amount")
            ).where(DonationRecord.payment_status == DonationStatus.SUCCESS)
        )
        total_stats = total_result.first()
        
        # 本月捐赠统计
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_result = await session.execute(
            select(
                func.count(DonationRecord.id).label("monthly_donations"),
                func.sum(DonationRecord.amount).label("monthly_amount")
            ).where(
                and_(
                    DonationRecord.payment_status == DonationStatus.SUCCESS,
                    DonationRecord.paid_at >= month_start
                )
            )
        )
        monthly_stats = monthly_result.first()
        
        # 目标统计
        goals_result = await session.execute(
            select(
                func.count(DonationGoal.id).label("total_goals"),
                func.sum(func.case((DonationGoal.is_completed == True, 1), else_=0)).label("completed_goals")
            ).where(DonationGoal.is_active == True)
        )
        goals_stats = goals_result.first()
        
        return DonationStats(
            total_donations=total_stats.total_donations or 0,
            total_amount=total_stats.total_amount or Decimal('0.00'),
            currency="CNY",
            monthly_donations=monthly_stats.monthly_donations or 0,
            monthly_amount=monthly_stats.monthly_amount or Decimal('0.00'),
            active_goals=goals_stats.total_goals or 0,
            completed_goals=goals_stats.completed_goals or 0
        )


@router.get("/public-stats")
async def get_public_donation_stats():
    """获取公开的捐赠统计信息"""
    async with async_session() as session:
        # 总捐赠统计
        total_result = await session.execute(
            select(
                func.count(DonationRecord.id).label("total_donations"),
                func.sum(DonationRecord.amount).label("total_amount")
            ).where(DonationRecord.payment_status == DonationStatus.SUCCESS)
        )
        total_stats = total_result.first()
        
        # 活跃目标
        active_goals_result = await session.execute(
            select(func.count(DonationGoal.id)).where(
                and_(
                    DonationGoal.is_active == True,
                    DonationGoal.is_completed == False
                )
            )
        )
        active_goals = active_goals_result.scalar() or 0
        
        return {
            "total_donations": total_stats.total_donations or 0,
            "total_amount": float(total_stats.total_amount or 0),
            "currency": "CNY",
            "active_goals": active_goals
        }


# ==================== 支付回调处理 ====================

@router.post("/callback/alipay")
async def alipay_callback():
    """支付宝支付回调"""
    # TODO: 实现支付宝回调处理
    pass


@router.post("/callback/wechat")
async def wechat_callback():
    """微信支付回调"""
    # TODO: 实现微信支付回调处理
    pass


@router.post("/callback/paypal")
async def paypal_callback():
    """PayPal支付回调"""
    # TODO: 实现PayPal回调处理
    pass


# ==================== 辅助函数 ====================

async def send_donation_confirmation_email(
    email: str,
    donor_name: str,
    amount: Decimal,
    currency: str
):
    """发送捐赠确认邮件"""
    subject = "感谢您的捐赠！"
    html_content = f"""
    <h2>亲爱的 {donor_name}，</h2>
    <p>感谢您对我们博客系统的支持！</p>
    <p>您的捐赠金额：{amount} {currency}</p>
    <p>我们会继续努力，为您提供更好的服务。</p>
    <p>祝您生活愉快！</p>
    """
    
    try:
        email_service.send_email(email, subject, "", html_content)
    except Exception as e:
        print(f"发送捐赠确认邮件失败: {e}")


async def send_donation_notification_email(
    amount: Decimal,
    currency: str,
    donor_name: str,
    donor_message: Optional[str] = None
):
    """发送捐赠通知邮件给管理员"""
    # 获取管理员邮箱
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.role == UserRole.ADMIN)
        )
        admins = result.scalars().all()
        
        if not admins:
            return
        
        subject = f"收到新的捐赠：{amount} {currency}"
        html_content = f"""
        <h2>收到新的捐赠</h2>
        <p><strong>捐赠者：</strong>{donor_name}</p>
        <p><strong>金额：</strong>{amount} {currency}</p>
        """
        
        if donor_message:
            html_content += f"<p><strong>留言：</strong>{donor_message}</p>"
        
        for admin in admins:
            if admin.email:
                try:
                    email_service.send_email(admin.email, subject, "", html_content)
                except Exception as e:
                    print(f"发送捐赠通知邮件失败: {e}") 