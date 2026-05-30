"""OpenRouter API health check for Tanjun bot.

Validates:
1. OPENROUTER_API_KEY is configured
2. API is reachable with valid credentials
"""

from __future__ import annotations

from aiohttp import ClientError, ClientSession, ClientTimeout

from health.checks import HealthCheck, HealthCheckResult, HealthStatus


class OpenRouterHealthCheck(HealthCheck):
    """Health check for the OpenRouter API."""

    @property
    def name(self) -> str:
        return "OpenRouter API"

    @property
    def critical(self) -> bool:
        return True

    async def run(self) -> HealthCheckResult:
        from services.openrouter_client import get_openrouter_api_key

        api_key = get_openrouter_api_key()
        if not api_key:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.CRITICAL,
                message="OpenRouter API key not configured. Set OPENROUTER_API_KEY in .env",
            )

        try:
            async with ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }
                async with session.get(
                    "https://openrouter.ai/api/v1/models",
                    headers=headers,
                    timeout=ClientTimeout(total=10),
                ) as response:
                    if response.status == 401:
                        return HealthCheckResult(
                            check_name=self.name,
                            status=HealthStatus.DEGRADED,
                            message="OpenRouter API key is invalid or revoked (HTTP 401).",
                        )
                    if response.status == 429:
                        return HealthCheckResult(
                            check_name=self.name,
                            status=HealthStatus.DEGRADED,
                            message="OpenRouter rate limit exceeded.",
                        )
                    if response.status != 200:
                        return HealthCheckResult(
                            check_name=self.name,
                            status=HealthStatus.DEGRADED,
                            message=f"OpenRouter API returned HTTP {response.status}",
                        )

        except TimeoutError:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.DEGRADED,
                message="OpenRouter API request timed out after 10s",
            )
        except ClientError as e:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.DEGRADED,
                message=f"OpenRouter API connection error: {e}",
            )

        return HealthCheckResult(
            check_name=self.name,
            status=HealthStatus.HEALTHY,
            message="OpenRouter API key is valid and reachable.",
        )
