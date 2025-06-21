"""
This module contains tools for interacting with a database.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import inspect

from dwight_schrute.tools.database.client import ORMDBClient  # pylint: disable=E0401
from dwight_schrute.tools.database.models import (  # pylint: disable=E0401
    User,
    Subscription,
    UserSubscription,
    Invoice,
    SubscriptionStatus,
    Base,
)  # pylint: disable=E0401
from dwight_schrute.config import settings  # pylint: disable=E0401


logger = logging.getLogger(__name__)


class DatabaseTools:
    """
    A class that provides tools for interacting with the database.
    """

    # Constants for error messages
    _INVALID_DATE_RANGE_ERROR = "Invalid date range provided."

    def __init__(self, database_url: str = settings.app_database_url) -> None:
        """
        Initialize the DatabaseTools class.
        :param database_url: The URL of the database to connect to.
        :type database_url: str
        """
        self.database_url = database_url
        
    def _validate_and_convert_datetime(self, datetime_string: str) -> Optional[datetime]:
        """
        Validates if a string is in ISO format, if not, tries to convert it.
        
        Args:
            datetime_string (str): The datetime string to validate or convert
            
        Returns:
            Optional[datetime]: The parsed datetime object or None if datetime_string is None
            
        Raises:
            ValueError: If the string cannot be parsed or converted
        """
        if not datetime_string:
            return None

        # Try to parse as ISO format first
        try:
            return datetime.fromisoformat(datetime_string)
        except ValueError:
            # Not ISO format, try to convert
            result = self.convert_to_iso_format(datetime_string)
            if result["status"] == "success":
                return datetime.fromisoformat(result["results"]["iso_datetime"])
            else:
                raise ValueError(
                    f"Could not parse or convert datetime string: {datetime_string}. {result['message']}"
                )

    @staticmethod
    def _get_schema_description(base) -> str:
        """
        Generates a textual description of the database schema from SQLAlchemy ORM models.
        """
        description = "Database Schema:\n"
        mapper_registry = base.registry.mappers
        for mapper in mapper_registry:
            cls = mapper.class_
            table = cls.__table__
            description += f"\nTable: {table.name}\n"
            description += f"  Mapped Class: {cls.__name__}\n"
            description += "  Columns:\n"
            for column in table.columns:
                col_type = str(column.type)
                constraints = []
                if column.primary_key:
                    constraints.append("PRIMARY KEY")
                for fk in column.foreign_keys:
                    constraints.append(
                        f"REFERENCES {fk.column.table.name}({fk.column.name})"
                    )
                if not column.nullable and not column.primary_key:
                    constraints.append("NOT NULL")
                if column.unique:
                    constraints.append("UNIQUE")
                description += f"    - {column.name} ({col_type})"
                if constraints:
                    description += f" [{', '.join(constraints)}]"
                description += "\n"
            inspector = inspect(cls)
            if inspector.relationships:
                description += "  Relationships:\n"
                for name, rel in inspector.relationships.items():
                    target = rel.mapper.class_
                    description += (
                        f"    - {name}: {rel.direction.name} -> {target.__tablename__} "
                        f"(Class: {target.__name__})\n"
                    )
        return description

    def get_schema_description(self) -> Dict[str, Any]:
        """
        Retrieve a textual description of the database tables schema.

        Returns:
            Dict[str, Any]:A dictionary containing the schema description.
            or an error message if retrieval fails.
        """
        try:
            description = self._get_schema_description(Base)
            return {
                "status": "success",
                "message": "Schema description retrieved successfully",
                "results": {
                    "description": description,
                },
            }
        except Exception as e:
            logger.error("Error retrieving schema description: %s", e)
            return {
                "status": "error",
                "message": str(e),
                "results": {},
            }

    def convert_to_iso_format(
        self, datetime_string: str, input_format: str = None
    ) -> Dict[str, Any]:
        """
        Convert a datetime string to ISO format (YYYY-MM-DDTHH:MM:SS).

        Args:
            datetime_string (str): The datetime string to convert
            input_format (str, optional): The format of the input string.
                If None, the function will try to parse the string automatically.
                Example: '%Y-%m-%d %H:%M:%S' for '2025-01-15 14:30:00'

        Returns:
            Dict[str, Any]: A dictionary containing the ISO formatted datetime string or an error message.

        Examples:
            >>> convert_to_iso_format('2025-01-15 14:30:00')
            '2025-01-15T14:30:00'
            >>> convert_to_iso_format('01/15/2025 2:30 PM', '%m/%d/%Y %I:%M %p')
            '2025-01-15T14:30:00'
        """

        # If format is specified, use it to parse the string
        if input_format:
            dt_obj = datetime.strptime(datetime_string, input_format)
        else:
            # Try common formats
            formats_to_try = [
                "%Y-%m-%d %H:%M:%S",  # 2025-01-15 14:30:00
                "%Y-%m-%d %H:%M",  # 2025-01-15 14:30
                "%Y-%m-%d",  # 2025-01-15
                "%m/%d/%Y %H:%M:%S",  # 01/15/2025 14:30:00
                "%m/%d/%Y %I:%M %p",  # 01/15/2025 2:30 PM
                "%d-%b-%Y %H:%M:%S",  # 15-Jan-2025 14:30:00
                "%d/%m/%Y %H:%M:%S",  # 15/01/2025 14:30:00
            ]

            for fmt in formats_to_try:
                try:
                    dt_obj = datetime.strptime(datetime_string, fmt)
                    break
                except ValueError:
                    continue
            else:
                return {
                    "status": "error",
                    "message": f"Invalid datetime string format: '{datetime_string}'. "
                    "Please provide a valid datetime string or specify the input format.",
                    "results": {},
                }

        # Convert to ISO format
        return {
            "status": "success",
            "message": "Datetime string converted to ISO format successfully",
            "results": {
                "iso_datetime": dt_obj.isoformat(
                    timespec="seconds"
                )  # YYYY-MM-DDTHH:MM:SS
            },
        }

    # <-- Methods for interacting with Users -->
    def get_user_by_username(self, username: str) -> Dict[str, Any]:
        """
        Retrieve a user by their username.

        Args:
            username (str): The username of the user to retrieve.

        Returns:
            Dict[str, Any]: A dictionary containing the user details or an error message.
        """
        try:
            with ORMDBClient(self.database_url) as db:
                user = (
                    db.session.query(User)
                    .filter_by(username=username.lower())
                    .one_or_none()
                )
                if not user:
                    return {
                        "status": "error",
                        "message": f"User with username '{username}' not found.",
                        "results": {},
                    }
                return {
                    "status": "success",
                    "message": "User retrieved successfully",
                    "results": {
                        "user_id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "created_at": str(user.created_at.isoformat()),
                    },
                }
        except Exception as e:
            logger.error("Error retrieving user by username: %s", e)
            return {
                "status": "error",
                "message": str(e),
                "results": {},
            }

    def get_user_by_email(self, email: str) -> Dict[str, Any]:
        """
        Retrieve a user by their email.

        Args:
            email (str): The email of the user to retrieve.

        Returns:
            Dict[str, Any]: A dictionary containing the user details or an error message.
        """
        try:
            with ORMDBClient(self.database_url) as db:
                user = (
                    db.session.query(User).filter_by(email=email.lower()).one_or_none()
                )
                if not user:
                    return {
                        "status": "error",
                        "message": f"User with email '{email}' not found.",
                        "results": {},
                    }
                return {
                    "status": "success",
                    "message": "User retrieved successfully",
                    "results": {
                        "user_id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "created_at": str(user.created_at.isoformat()),
                    },
                }
        except Exception as e:
            logger.error("Error retrieving user by email: %s", e)
            return {
                "status": "error",
                "message": str(e),
                "results": {},
            }

    def count_users(
        self, created_after: Optional[str] = None, created_before: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Count the number of users in the database.

        Args:
            created_after (Optional[str]): Optional. Date string to filter users created after this date.
                Can be ISO format or any common date format.
            created_before (Optional[str]): Optional. Date string to filter users created before this date.
                Can be ISO format or any common date format.

        Returns:
            Dict[str, Any]: A dictionary containing the user count or an error message.
        """
        try:
            try:
                created_after = self._validate_and_convert_datetime(created_after) if created_after else None
                created_before = self._validate_and_convert_datetime(created_before) if created_before else None
            except ValueError as ve:
                return {
                    "status": "error",
                    "message": str(ve),
                    "results": {},
                }
            with ORMDBClient(self.database_url) as db:
                query = db.session.query(User)
                if created_after:
                    query = query.filter(User.created_at >= created_after)
                if created_before:
                    query = query.filter(User.created_at <= created_before)
                user_count = query.count()
                return {
                    "status": "success",
                    "message": "User count retrieved successfully",
                    "results": {
                        "user_count": user_count,
                    },
                }
        except Exception as e:
            logger.error("Error counting users: %s", e)
            return {
                "status": "error",
                "message": str(e),
                "results": {},
            }

    # <-- Methods for interacting with Subscriptions -->
    def get_subscription_pricing(self, name: str) -> Dict[str, Any]:
        """
        Retrieve the pricing details of a subscription by its name.

        Args:
            name (str): The name of the subscription to retrieve. available options are
            "Basic SD", "Standard HD", "Premium 4K", "Family Plan" and "Annual Plan"

        Returns:
            Dict[str, Any]: A dictionary containing the subscription pricing details or an error message.
        """
        try:
            if name not in [
                "Basic SD",
                "Standard HD",
                "Premium 4K",
                "Family Plan",
                "Annual Plan",
            ]:
                return {
                    "status": "error",
                    "message": f"Invalid subscription name '{name}'. Available options are: "
                    "'Basic SD', 'Standard HD', 'Premium 4K', 'Family Plan', 'Annual Plan'.",
                    "results": {},
                }
            with ORMDBClient(self.database_url) as db:
                subscription = (
                    db.session.query(Subscription).filter_by(name=name).one_or_none()
                )
                if not subscription:
                    return {
                        "status": "error",
                        "message": f"Subscription with name '{name}' not found.",
                        "results": {},
                    }
                return {
                    "status": "success",
                    "message": "Subscription pricing retrieved successfully",
                    "results": {
                        "subscription_id": subscription.id,
                        "name": subscription.name,
                        "price": subscription.price,
                        "description": subscription.description,
                    },
                }
        except Exception as e:
            logger.error("Error retrieving subscription pricing: %s", e)
            return {
                "status": "error",
                "message": str(e),
                "results": {},
            }

    # <-- Methods for interacting with UserSubscriptions -->
    def count_subscriptions_by_status(
        self,
        status: str,
        period_start: Optional[str] = None,
        period_end: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Count the number of user subscriptions by status.

        Args:
            status (str): The status of the subscriptions to count. Options are "active", "cancelled", "expired".
            period_start (Optional[str]): Optional. Date string to filter subscriptions created after this date.
                Can be ISO format or any common date format.
            period_end (Optional[str]): Optional. Date string to filter subscriptions created before this date.
                Can be ISO format or any common date format.

        Returns:
            Dict[str, Any]: A dictionary containing the subscription count or an error message.
        """
        try:
            try:
                period_start = self._validate_and_convert_datetime(period_start) if period_start else None
                period_end = self._validate_and_convert_datetime(period_end) if period_end else None
            except ValueError as ve:
                return {
                    "status": "error",
                    "message": str(ve),
                    "results": {},
                }
            if not status or status.lower() not in ["active", "cancelled", "expired"]:
                return {
                    "status": "error",
                    "message": "Invalid status provided. Options are 'active', 'cancelled', or 'expired'.",
                    "results": {},
                }
            
            # Map the status string to the SubscriptionStatus enum value
            status_enum = getattr(SubscriptionStatus, status.upper())
            
            with ORMDBClient(self.database_url) as db:
                query = db.session.query(UserSubscription).filter(
                    UserSubscription.status == status_enum
                )
                if period_start:
                    query = query.filter(UserSubscription.start_date >= period_start)
                if period_end:
                    query = query.filter(UserSubscription.end_date <= period_end)
                subscription_count = query.count()
                return {
                    "status": "success",
                    "message": "Subscription count retrieved successfully",
                    "results": {
                        "subscription_count": subscription_count,
                    },
                }
        except Exception as e:
            logger.error("Error counting subscriptions by status: %s", e)
            return {
                "status": "error",
                "message": str(e),
                "results": {},
            }

    def sum_revenue(
        self, date_from: str, date_to: str, status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate the total revenue from invoices within a specified date range and status.

        Args:
            date_from (str): The start date. Can be ISO format or any common date format.
            date_to (str): The end date. Can be ISO format or any common date format.
            status (Optional[str]): Optional. The status of the invoices to include in the revenue calculation.
            Options are "paid", "unpaid" and the default is paid.

        Returns:
            Dict[str, Any]: A dictionary containing the total revenue or an error message.
        """
        try:
            try:
                date_from = self._validate_and_convert_datetime(date_from)
                date_to = self._validate_and_convert_datetime(date_to)
            except ValueError as ve:
                return {
                    "status": "error",
                    "message": str(ve),
                    "results": {},
                }
            if date_from >= date_to:
                return {
                    "status": "error",
                    "message": self._INVALID_DATE_RANGE_ERROR,
                    "results": {},
                }
            if status and status.lower() not in ["paid", "unpaid"]:
                return {
                    "status": "error",
                    "message": "Invalid status provided. Options are 'paid' or 'unpaid'.",
                    "results": {},
                }
            status = status.lower() if status else "paid"
            with ORMDBClient(self.database_url) as db:
                query = (
                    db.session.query(Invoice.amount)
                    .join(
                        UserSubscription,
                        Invoice.user_subscription_id == UserSubscription.id,
                    )
                    .filter(
                        UserSubscription.start_date >= date_from,
                        UserSubscription.end_date <= date_to,
                    )
                )
                if status:
                    query = query.filter(Invoice.status == status.lower())
                total_revenue = sum(invoice.amount for invoice in query.all())
                return {
                    "status": "success",
                    "message": "Total revenue calculated successfully",
                    "results": {
                        "total_revenue": total_revenue,
                    },
                }
        except Exception as e:
            logger.error("Error calculating total revenue: %s", e)
            return {
                "status": "error",
                "message": str(e),
                "results": {},
            }

    def compare_revenue(
        self, p1_start: str, p1_end: str, p2_start: str, p2_end: str
    ) -> Dict[str, Any]:
        """
        Compare the total revenue between two periods.

        Args:
            p1_start (str): The start date of the first period. Can be ISO format or any common date format.
            p1_end (str): The end date of the first period. Can be ISO format or any common date format.
            p2_start (str): The start date of the second period. Can be ISO format or any common date format.
            p2_end (str): The end date of the second period. Can be ISO format or any common date format.

        Returns:
            Dict[str, Any]: A dictionary containing the comparison results or an error message.
        """
        try:
            try:
                p1_start_dt = self._validate_and_convert_datetime(p1_start)
                p1_end_dt = self._validate_and_convert_datetime(p1_end)
                p2_start_dt = self._validate_and_convert_datetime(p2_start)
                p2_end_dt = self._validate_and_convert_datetime(p2_end)
            except ValueError as ve:
                return {
                    "status": "error",
                    "message": str(ve),
                    "results": {},
                }
            if p1_start_dt >= p1_end_dt or p2_start_dt >= p2_end_dt:
                return {
                    "status": "error",
                    "message": self._INVALID_DATE_RANGE_ERROR,
                    "results": {},
                }
            revenue_p1 = self.sum_revenue(p1_start, p1_end)
            revenue_p2 = self.sum_revenue(p2_start, p2_end)

            if revenue_p1["status"] == "error" or revenue_p2["status"] == "error":
                return {
                    "status": "error",
                    "message": "Error calculating revenue for one or both periods.",
                    "results": {},
                }

            delta = (
                revenue_p2["results"]["total_revenue"]
                - revenue_p1["results"]["total_revenue"]
            )
            pct = (
                delta / revenue_p1["results"]["total_revenue"] * 100
                if revenue_p1["results"]["total_revenue"] > 0
                else 0
            )

            return {
                "status": "success",
                "message": "Revenue comparison calculated successfully",
                "results": {
                    "period_1_revenue": revenue_p1["results"]["total_revenue"],
                    "period_2_revenue": revenue_p2["results"]["total_revenue"],
                    "delta": delta,
                    "percentage_change": pct,
                    "period_1": {
                        "start": p1_start_dt.isoformat(),
                        "end": p1_end_dt.isoformat(),
                    },
                    "period_2": {
                        "start": p2_start_dt.isoformat(),
                        "end": p2_end_dt.isoformat(),
                    },
                },
            }
        except Exception as e:
            logger.error("Error comparing revenues: %s", e)
            return {
                "status": "error",
                "message": str(e),
                "results": {},
            }

    def calculate_mrr(self, as_of_date: str) -> Dict[str, Any]:
        """
        Calculate the Monthly Recurring Revenue (MRR) as of a specific date.

        Args:
            as_of_date (str): The date to calculate MRR for. Can be ISO format or any common date format.

        Returns:
            Dict[str, Any]: A dictionary containing the MRR or an error message.
        """
        try:
            try:
                as_of_date = self._validate_and_convert_datetime(as_of_date)
            except ValueError as ve:
                return {
                    "status": "error",
                    "message": str(ve),
                    "results": {},
                }
            with ORMDBClient(self.database_url) as db:
                # Query active subscriptions as of the given date, and sum the associated invoice amounts
                query = (
                    db.session.query(Invoice.amount)
                    .join(
                        UserSubscription,
                        Invoice.user_subscription_id == UserSubscription.id,
                    )
                    .filter(
                        UserSubscription.start_date <= as_of_date,
                        UserSubscription.end_date >= as_of_date,
                        UserSubscription.status == SubscriptionStatus.ACTIVE
                    )
                )
                mrr = sum(invoice.amount for invoice in query.all())
                return {
                    "status": "success",
                    "message": "MRR calculated successfully",
                    "results": {
                        "mrr": mrr,
                        "as_of_date": as_of_date.isoformat(),
                    },
                }
        except Exception as e:
            logger.error("Error calculating MRR: %s", e)
            return {
                "status": "error",
                "message": str(e),
                "results": {},
            }

    def calculate_churn_rate(
        self, period_start: str, period_end: str
    ) -> Dict[str, Any]:
        """
        Calculate the churn rate for a specific period.

        Args:
            period_start (str): The start date of the period. Can be ISO format or any common date format.
            period_end (str): The end date of the period. Can be ISO format or any common date format.

        Returns:
            Dict[str, Any]: A dictionary containing the churn rate or an error message.
        """
        try:
            try:
                period_start = self._validate_and_convert_datetime(period_start)
                period_end = self._validate_and_convert_datetime(period_end)
            except ValueError as ve:
                return {
                    "status": "error",
                    "message": str(ve),
                    "results": {},
                }
            if period_start >= period_end:
                return {
                    "status": "error",
                    "message": self._INVALID_DATE_RANGE_ERROR,
                    "results": {},
                }
            with ORMDBClient(self.database_url) as db:
                # Count subscriptions that ended during the period
                churned_subscriptions = (
                    db.session.query(UserSubscription)
                    .filter(
                        UserSubscription.end_date >= period_start,
                        UserSubscription.end_date <= period_end,
                        UserSubscription.status == SubscriptionStatus.CANCELLED,
                    )
                    .count()
                )
                # Count active subscriptions at the start of the period
                active_subscriptions_start = (
                    db.session.query(UserSubscription)
                    .filter(
                        UserSubscription.start_date <= period_start,
                        UserSubscription.end_date >= period_start,
                        UserSubscription.status == SubscriptionStatus.ACTIVE,
                    )
                    .count()
                )
                if active_subscriptions_start == 0:
                    return {
                        "status": "error",
                        "message": "No active subscriptions at the start of the period.",
                        "results": {},
                    }
                churn_rate = churned_subscriptions / active_subscriptions_start * 100
                return {
                    "status": "success",
                    "message": "Churn rate calculated successfully",
                    "results": {
                        "churn_rate": churn_rate,
                        "period_start": period_start.isoformat(),
                        "period_end": period_end.isoformat(),
                        "churned_subscriptions": churned_subscriptions,
                        "active_subscriptions_start": active_subscriptions_start,
                    },
                }
        except Exception as e:
            logger.error("Error calculating churn rate: %s", e)
            return {
                "status": "error",
                "message": str(e),
                "results": {},
            }
