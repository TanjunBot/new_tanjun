
from aiohttp import ClientSession

from health_check import HealthCheck, HealthCheckResult, HealthStatus


class OpenAIHealthCheck(HealthCheck):
    @property
    def name(self) -> str:
        return "OpenAI API"

    @property
    def critical(self) -> bool:
        return True  # AI features are a selling point

    async def run(self) -> HealthCheckResult:
        from config import openAiKey

        if not openAiKey:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.CRITICAL,
                message="OpenAI API key not configured. Set openAIKey in .env",
            )

        try:
            async with ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {openAiKey}",
                    "Content-Type": "application/json",
                }
                # Use a lightweight model list call to verify the key
                async with session.get(
                    "https://api.openai.com/v1/models",
                    headers=headers,
                    timeout=10,
                ) as response:
                    if response.status == 401:
                        return HealthCheckResult(
                            check_name=self.name,
                            status=HealthStatus.CRITICAL,
                            message="OpenAI API key is invalid or revoked (HTTP 401).",
                        )
                    elif response.status == 429:
                        return HealthCheckResult(
                            check_name=self.name,
                            status=HealthStatus.DEGRADED,
                            message="OpenAI rate limit exceeded. Consider upgrading tier.",
                        )
                    elif response.status != 200:
                        return HealthCheckResult(
                            check_name=self.name,
                            status=HealthStatus.DEGRADED,
                            message=f"OpenAI API returned HTTP {response.status}",
                        )

        except TimeoutError:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.DEGRADED,
                message="OpenAI API request timed out after 10s",
            )
        except ClientError as e:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.DEGRADED,
                message=f"OpenAI API connection error: {e}",
            )

        return HealthCheckResult(
            check_name=self.name,
            status=HealthStatus.HEALTHY,
            message="OpenAI API key is valid and reachable.",
        )
