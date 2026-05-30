"""Backward compatibility shim — use health.checks.openrouter instead."""

from health.checks.openrouter import OpenRouterHealthCheck

OpenAIHealthCheck = OpenRouterHealthCheck

__all__ = ["OpenAIHealthCheck", "OpenRouterHealthCheck"]
