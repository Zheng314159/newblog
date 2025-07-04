from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from decimal import Decimal

if TYPE_CHECKING:
    from .user import User


class DonationStatus(str, Enum):
    PENDING = "PENDING"      # 待处理
    SUCCESS = "SUCCESS"      # 成功
    FAILED = "FAILED"        # 失败
    CANCELLED = "CANCELLED"  # 已取消


class PaymentMethod(str, Enum):
    ALIPAY = "ALIPAY"        # 支付宝
    WECHAT = "WECHAT"        # 微信支付
    PAYPAL = "PAYPAL"        # PayPal
    BANK_TRANSFER = "BANK_TRANSFER"  # 银行转账
    CRYPTO = "CRYPTO"        # 加密货币


class DonationType(str, Enum):
    ONE_TIME = "ONE_TIME"    # 一次性捐赠
    MONTHLY = "MONTHLY"      # 月度捐赠
    YEARLY = "YEARLY"        # 年度捐赠


class DonationConfig(SQLModel, table=True):
    """捐赠配置表"""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 基本配置
    is_enabled: bool = Field(default=True, description="是否启用捐赠功能")
    title: str = Field(default="支持我们", description="捐赠页面标题")
    description: str = Field(default="感谢您的支持！", description="捐赠页面描述")
    
    # 支付方式配置
    alipay_enabled: bool = Field(default=True, description="是否启用支付宝")
    wechat_enabled: bool = Field(default=True, description="是否启用微信支付")
    paypal_enabled: bool = Field(default=True, description="是否启用PayPal")
    bank_transfer_enabled: bool = Field(default=False, description="是否启用银行转账")
    crypto_enabled: bool = Field(default=False, description="是否启用加密货币")
    
    # 支付配置
    alipay_app_id: Optional[str] = Field(default=None, description="支付宝App ID")
    alipay_private_key: Optional[str] = Field(default=None, description="支付宝私钥")
    alipay_public_key: Optional[str] = Field(default=None, description="支付宝公钥")
    
    wechat_app_id: Optional[str] = Field(default=None, description="微信App ID")
    wechat_mch_id: Optional[str] = Field(default=None, description="微信商户号")
    wechat_key: Optional[str] = Field(default=None, description="微信API密钥")
    
    paypal_client_id: Optional[str] = Field(default=None, description="PayPal Client ID")
    paypal_client_secret: Optional[str] = Field(default=None, description="PayPal Client Secret")
    paypal_mode: str = Field(default="sandbox", description="PayPal模式: sandbox/live")
    
    # 银行转账信息
    bank_name: Optional[str] = Field(default=None, description="银行名称")
    bank_account: Optional[str] = Field(default=None, description="银行账号")
    bank_holder: Optional[str] = Field(default=None, description="账户持有人")
    
    # 加密货币地址
    bitcoin_address: Optional[str] = Field(default=None, description="比特币地址")
    ethereum_address: Optional[str] = Field(default=None, description="以太坊地址")
    
    # 预设金额
    preset_amounts: str = Field(default="[5, 10, 20, 50, 100]", description="预设捐赠金额，JSON格式")
    
    # 统计信息
    total_donations: int = Field(default=0, description="总捐赠次数")
    total_amount: Decimal = Field(default=Decimal('0.00'), description="总捐赠金额")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DonationRecord(SQLModel, table=True):
    """捐赠记录表"""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 捐赠者信息
    donor_name: str = Field(description="捐赠者姓名")
    donor_email: Optional[str] = Field(default=None, description="捐赠者邮箱")
    donor_message: Optional[str] = Field(default=None, description="捐赠留言")
    is_anonymous: bool = Field(default=False, description="是否匿名捐赠")
    
    # 捐赠信息
    amount: Decimal = Field(description="捐赠金额")
    currency: str = Field(default="CNY", description="货币类型")
    donation_type: DonationType = Field(default=DonationType.ONE_TIME, description="捐赠类型")
    
    # 支付信息
    payment_method: PaymentMethod = Field(description="支付方式")
    payment_status: DonationStatus = Field(default=DonationStatus.PENDING, description="支付状态")
    transaction_id: Optional[str] = Field(default=None, description="第三方交易ID")
    
    # 关联用户（可选）
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", description="关联用户ID")
    user: Optional["User"] = Relationship(back_populates="donations")
    
    # 时间信息
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    paid_at: Optional[datetime] = Field(default=None, description="支付完成时间")


class DonationGoal(SQLModel, table=True):
    """捐赠目标表"""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    title: str = Field(description="目标标题")
    description: str = Field(description="目标描述")
    target_amount: Decimal = Field(description="目标金额")
    current_amount: Decimal = Field(default=Decimal('0.00'), description="当前金额")
    currency: str = Field(default="CNY", description="货币类型")
    
    start_date: datetime = Field(description="开始日期")
    end_date: Optional[datetime] = Field(default=None, description="结束日期")
    
    is_active: bool = Field(default=True, description="是否激活")
    is_completed: bool = Field(default=False, description="是否完成")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Schema 定义
class DonationConfigUpdate(SQLModel):
    is_enabled: Optional[bool] = None
    title: Optional[str] = None
    description: Optional[str] = None
    alipay_enabled: Optional[bool] = None
    wechat_enabled: Optional[bool] = None
    paypal_enabled: Optional[bool] = None
    bank_transfer_enabled: Optional[bool] = None
    crypto_enabled: Optional[bool] = None
    alipay_app_id: Optional[str] = None
    alipay_private_key: Optional[str] = None
    alipay_public_key: Optional[str] = None
    wechat_app_id: Optional[str] = None
    wechat_mch_id: Optional[str] = None
    wechat_key: Optional[str] = None
    paypal_client_id: Optional[str] = None
    paypal_client_secret: Optional[str] = None
    paypal_mode: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    bank_holder: Optional[str] = None
    bitcoin_address: Optional[str] = None
    ethereum_address: Optional[str] = None
    preset_amounts: Optional[str] = None


class DonationCreate(SQLModel):
    donor_name: str
    donor_email: Optional[str] = None
    donor_message: Optional[str] = None
    is_anonymous: bool = False
    amount: Decimal
    currency: str = "CNY"
    donation_type: DonationType = DonationType.ONE_TIME
    payment_method: PaymentMethod


class DonationResponse(SQLModel):
    id: int
    donor_name: str
    donor_email: Optional[str] = None
    donor_message: Optional[str] = None
    is_anonymous: bool
    amount: Decimal
    currency: str
    donation_type: DonationType
    payment_method: PaymentMethod
    payment_status: DonationStatus
    transaction_id: Optional[str] = None
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    paid_at: Optional[datetime] = None


class DonationGoalCreate(SQLModel):
    title: str
    description: str
    target_amount: Decimal
    currency: str = "CNY"
    start_date: datetime
    end_date: Optional[datetime] = None


class DonationGoalUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_amount: Optional[Decimal] = None
    currency: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None


class DonationGoalResponse(SQLModel):
    id: int
    title: str
    description: str
    target_amount: Decimal
    current_amount: Decimal
    currency: str
    start_date: datetime
    end_date: Optional[datetime] = None
    is_active: bool
    is_completed: bool
    progress_percentage: float
    created_at: datetime
    updated_at: datetime


class DonationStats(SQLModel):
    total_donations: int
    total_amount: Decimal
    currency: str
    monthly_donations: int
    monthly_amount: Decimal
    active_goals: int
    completed_goals: int 