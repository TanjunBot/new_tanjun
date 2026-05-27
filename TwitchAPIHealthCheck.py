"""Twitch API health check for Tanjun bot.

Validates:
1. twitchId and twitchSecret are configured
2. App access token can be obtained
3. API is reachable
"""

from __future__ import annotations

from aiohttp import ClientError, ClientSession

from health.checks import HealthCheck, HealthCheckResult, HealthStatus


class TwitchAPIHealthCheck(HealthCheck):
    """Health check for the Twitch API."""

    @property
    def name(self) -> str:
        return "Twitch API"

    @property
    def critical(self) -> bool:
        return True  # Should refuse to start if misconfigured

    async def run(self) -> HealthCheckResult:
        from config import twitchId, twitchSecret

        if not twitchId or not twitchSecret:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.CRITICAL,
                message="Twitch client ID or secret not configured. Set twitchId and twitchSecret in .env",
            )

        try:
            async with ClientSession() as session:
                # Test token acquisition
                auth_params: dict[str, str] = {
                    "client_id": twitchId,
                    "client_secret": twitchSecret,
                    "grant_type": "client_credentials",
                }
                async with session.post(
                    "https://id.twitch.tv/oauth2/token",
                    params=auth_params,
                    timeout=10,
                ) as response:
                    if response.status != 200:
                        data = await response.json()
                        return HealthCheckResult(
                            check_name=self.name,
                            status=HealthStatus.CRITICAL,
                            message=f"Twitch auth failed (HTTP {response.status}): {data.get('message', 'Unknown error')}",
                        )
                    data = await response.json()
                    token = data.get("access_token")

                    if not token:
                        return HealthCheckResult(
                            check_name=self.name,
                            status=HealthStatus.CRITICAL,
                            message="Twitch auth failed: No access token returned in response",
                        )

                # Test API call with token
                headers = {"Client-ID": twitchId, "Authorization": f"Bearer {token}"}
                async with session.get(
                    "https://api.twitch.tv/helix/streams",
                    headers=headers,
                    timeout=10,
                ) as response:
                    if response.status != 200:
                        return HealthCheckResult(
                            check_name=self.name,
                            status=HealthStatus.DEGRADED,
                            message=f"Twitch API call failed (HTTP {response.status})",
                        )

        except TimeoutError:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.DEGRADED,
                message="Twitch API request timed out after 10s",
            )
        except ClientError as e:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.DEGRADED,
                message=f"Twitch API connection error: {e}",
            )

        return HealthCheckResult(
            check_name=self.name,
            status=HealthStatus.HEALTHY,
            message="Twitch API is authenticated and reachable.",
        )
