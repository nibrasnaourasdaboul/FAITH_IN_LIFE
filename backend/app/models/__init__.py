"""Importing this package registers every ERD table on Base.metadata."""

from app.models.entities import *  # noqa: F403
from app.models.entities import __all__ as _entity_all

__all__ = list(_entity_all)
