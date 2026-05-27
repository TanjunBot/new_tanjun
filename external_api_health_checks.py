"""External API health checks for Tanjun bot.

Provides health checks for:
- GIPHY API
- Brawl Stars API
- ImgBB API
- bytebin Storage
- GitHub API
"""

from __future__ import annotations

from aiohttp import ClientError, ClientSession

from health.checks import HealthCheck, HealthCheckResult, HealthStatus


class GIPHYHealthCheck(HealthCheck):
    """Health check for the GIPHY API."""

    @property
    def name(self) -> str:
        return "GIPHY API"

    @property
    def critical(self) -> bool:
        return False  # Non-critical, degrades gracefully

    async def run(self) -> HealthCheckResult:
        from config import giphyAPIKey

        if not giphyAPIKey:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.DEGRADED,
                message="GIPHY API key not configured.",
            )

        try:
            async with ClientSession() as session:
                async with session.get(
                    f"https://api.giphy.com/v1/gifs/trending?api_key={giphyAPIKey}&limit=1",
                    timeout=10,
                ) as response:
                    if response.status != 200:
                        return HealthCheckResult(
                            check_name=self.name,
                            status=HealthStatus.DEGRADED,
                            message=f"GIPHY API returned HTTP {response.status}",
                        )
        except TimeoutError:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.DEGRADED,
                message="GIPHY API request timed out after 10s",
            )
        except ClientError as e:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.DEGRADED,
                message=f"GIPHY API connection error: {e}",
            )

        return HealthCheckResult(
            check_name=self.name,
            status=HealthStatus.HEALTHY,
            message="GIPHY API is reachable.",
        )


class BrawlStarsHealthCheck(HealthCheck):
    """Health check for the Brawl Stars API."""

    @property
    def name(self) -> str:
        return "Brawl Stars API"

    @property
    def critical(self) -> bool:
        return False

    async def run(self) -> HealthCheckResult:
        from config import brawlstarsToken

        if not brawlstarsToken:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.DEGRADED,
                message="Brawl Stars token not configured.",
            )

        headers = {"Authorization": f"Bearer {brawlstarsToken}"}

        try:
            async with ClientSession() as session:
                async with session.get(
                    "https://api.brawlstars.com/v1/brawlers",
                    headers=headers,
                    timeout=10,
                ) as response:
                    if response.status == 403:
                        return HealthCheckResult(
                            check_name=self.name,
                            status=HealthStatus.DEGRADED,
                            message="Brawl Stars token is invalid (HTTP 403).",
                        )
                    elif response.status != 200:
                        return HealthCheckResult(
                            check_name=self.name,
                            status=HealthStatus.DEGRADED,
                            message=f"Brawl Stars API returned HTTP {response.status}",
                        )
        except TimeoutError:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.DEGRADED,
                message="Brawl Stars API request timed out after 10s",
            )
        except ClientError as e:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.DEGRADED,
                message=f"Brawl Stars API connection error: {e}",
            )

        return HealthCheckResult(
            check_name=self.name,
            status=HealthStatus.HEALTHY,
            message="Brawl Stars API is reachable.",
        )


class ImgBBHealthCheck(HealthCheck):
    """Health check for the ImgBB API."""

    @property
    def name(self) -> str:
        return "ImgBB API"

    @property
    def critical(self) -> bool:
        return False

    async def run(self) -> HealthCheckResult:
        from config import ImgBBApiKey

        if not ImgBBApiKey:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.DEGRADED,
                message="ImgBB API key not configured.",
            )

        try:
            async with ClientSession() as session:
                # Verify key with a simple ping — 400 is expected without image,
                # which means the key works.
                async with session.get(
                    f"https://api.imgbb.com/1/upload?key={ImgBBApiKey}",
                    timeout=10,
                ) as response:
                    if response.status not in (200, 400):
                        return HealthCheckResult(
                            check_name=self.name,
                            status=HealthStatus.DEGRADED,
                            message=f"ImgBB API returned HTTP {response.status}",
                        )
        except TimeoutError:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.DEGRADED,
                message="ImgBB API request timed out after 10s",
            )
        except ClientError as e:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.DEGRADED,
                message=f"ImgBB API connection error: {e}",
            )

        return HealthCheckResult(
            check_name=self.name,
            status=HealthStatus.HEALTHY,
            message="ImgBB API key is valid.",
        )


class BytebinHealthCheck(HealthCheck):
    """Health check for bytebin storage."""

    @property
    def name(self) -> str:
        return "bytebin Storage"

    @property
    def critical(self) -> bool:
        return False

    async def run(self) -> HealthCheckResult:
        from config import bytebin_url, bytebin_username, bytebin_password

        if not bytebin_url:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.DEGRADED,
                message="bytebin URL not configured.",
            )

        headers: dict[str, str] = {}
        if bytebin_username and bytebin_password:
            import base64

            auth = base64.b64encode(
                f"{bytebin_username}:{bytebin_password}".encode()
            ).decode()
            headers["Authorization"] = f"Basic {auth}"

        try:
            async with ClientSession() as session:
                async with session.get(
                    bytebin_url, headers=headers, timeout=10
                ) as response:
                    if response.status >= 500:
                        return HealthCheckResult(
                            check_name=self.name,
                            status=HealthStatus.DEGRADED,
                            message=f"bytebin returned HTTP {response.status}",
                        )
        except TimeoutError:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.DEGRADED,
                message="bytebin request timed out after 10s",
            )
        except ClientError as e:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.DEGRADED,
                message=f"bytebin connection error: {e}",
            )

        return HealthCheckResult(
            check_name=self.name,
            status=HealthStatus.HEALTHY,
            message="bytebin is reachable.",
        )


class GitHubAPIHealthCheck(HealthCheck):
    """Health check for the GitHub API."""

    @property
    def name(self) -> str:
        return "GitHub API"

    @property
    def critical(self) -> bool:
        return False

    async def run(self) -> HealthCheckResult:
        from config import GithubAuthToken

        if not GithubAuthToken:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.DEGRADED,
                message="GitHub token not configured.",
            )

        headers = {"Authorization": f"Bearer {GithubAuthToken}"}

        try:
            async with ClientSession() as session:
                async with session.get(
                    "https://api.github.com/user",
                    headers=headers,
                    timeout=10,
                ) as response:
                    if response.status == 401:
                        return HealthCheckResult(
                            check_name=self.name,
                            status=HealthStatus.DEGRADED,
                            message="GitHub token is invalid (HTTP 401).",
                        )
                    elif response.status != 200:
                        return HealthCheckResult(
                            check_name=self.name,
                            status=HealthStatus.DEGRADED,
                            message=f"GitHub API returned HTTP {response.status}",
                        )
        except TimeoutError:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.DEGRADED,
                message="GitHub API request timed out after 10s",
            )
        except ClientError as e:
            return HealthCheckResult(
                check_name=self.name,
                status=HealthStatus.DEGRADED,
                message=f"GitHub API connection error: {e}",
            )

        return HealthCheckResult(
            check_name=self.name,
            status=HealthStatus.HEALTHY,
            message="GitHub API is authenticated and reachable.",
        )
