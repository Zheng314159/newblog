from sqlalchemy import Column, Integer, String, DateTime, Boolean, func, ForeignKey
from app.core.database import Base

class SystemNotification(Base):
    __tablename__ = "system_notification"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(128), nullable=False)
    message = Column(String(1024), nullable=False)
    notification_type = Column(String(32), default="info")
    created_at = Column(DateTime, server_default=func.now())
    is_sent = Column(Boolean, default=False)
    admin_id = Column(Integer, ForeignKey("user.id"), nullable=True) 