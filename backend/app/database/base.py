"""
Database Base
=============
Declarative base for SQLAlchemy ORM models.
All models inherit from Base defined here.
"""

from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class Base(DeclarativeBase):
    """
    SQLAlchemy declarative base.

    All ORM models should inherit from this class.
    Common columns (id, created_at, updated_at) are defined
    on each model individually for explicit control.
    """
    pass
