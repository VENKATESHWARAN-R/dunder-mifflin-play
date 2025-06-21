"""
This module contains the SQLAlchemy ORM models for the Dunder Mifflin MCP application.
"""

from datetime import datetime, timezone
import enum


from sqlalchemy import Column, DateTime, Integer, Float, ForeignKey, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# <-- Application DB Models -->


class SubscriptionStatus(enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))


class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String)


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    start_date = Column(DateTime, default=datetime.now(timezone.utc))
    end_date = Column(DateTime, nullable=True)
    status = Column(
        SQLEnum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False
    )


class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    user_subscription_id = Column(
        Integer, ForeignKey("user_subscriptions.id"), nullable=False
    )
    invoice_date = Column(DateTime, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, nullable=False, default="paid")
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
