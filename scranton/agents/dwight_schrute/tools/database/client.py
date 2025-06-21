"""
Module for interacting with database using ORMDBClient.
"""

from typing import Any, List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class ORMDBClient:
    def __init__(self, url: str):
        self.engine = create_engine(url, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)

    def __enter__(self):
        self.session = self.Session()
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()

    def get(self, model, pk) -> Any:
        return self.session.query(model).get(pk)

    def list(self, model, **filters) -> List[Any]:
        return self.session.query(model).filter_by(**filters).all()

    def add(self, instance: Any) -> Any:
        self.session.add(instance)
        return instance

    def execute(self, stmt) -> Any:
        return self.session.execute(stmt)
