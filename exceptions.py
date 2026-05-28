"""Typed exception hierarchy for Tanjun Bot.

Provides structured error classes that enable granular error handling,
logging, and user-facing error messages throughout the codebase.
"""

from __future__ import annotations


class TanjunError(Exception):
    """Base exception for all bot errors."""


class DatabaseError(TanjunError):
    """Database connection or query error."""


class ConfigurationError(TanjunError):
    """Missing or invalid configuration."""


class EntityNotFoundError(TanjunError):
    """Requested entity (guild, user, channel) not found in the database."""


class BotPermissionError(TanjunError):
    """Insufficient permissions for an operation."""


class ExternalAPIError(TanjunError):
    """Error from an external API (Twitch, Brawl Stars, ImgBB, etc.)."""


class ValidationError(TanjunError):
    """Validation failure (Pydantic or otherwise)."""


class RateLimitError(TanjunError):
    """Rate limit exceeded on an external API."""


class OperationTimeoutError(TanjunError):
    """Operation timed out."""


# Backward compatibility alias — deprecated, use OperationTimeoutError instead.
TimeoutError = OperationTimeoutError
