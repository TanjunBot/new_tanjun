import json
from aiohttp import web
from activities.base import Player
from activities.manager import session_manager
from config import activity_server_host, activity_server_port, applicationId
from pathlib import Path

STATIC_DIR = Path(__file__).parent / "static"
TEMPLATES_DIR = Path(__file__).parent / "templates"


class ActivityServer:
    """Embedded HTTP and WebSocket server for Discord Activities."""

    def __init__(self, host: str = activity_server_host, port: int = activity_server_port) -> None:
        self.host = host
        self.port = port
        self.app = web.Application()
        self.runner = None
        self.site = None
        self._setup_routes()

    @web.middleware
    async def cors_middleware(self, request, handler):
        if request.method == "OPTIONS":
            response = web.Response(status=200)
        else:
            response = await handler(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        # Discord Activity iframe support
        response.headers["Content-Security-Policy"] = "frame-ancestors https://*.discord.com https://discord.com;"
        if "X-Frame-Options" in response.headers:
            del response.headers["X-Frame-Options"]
        return response

    def _setup_routes(self) -> None:
        self.app.middlewares.append(self.cors_middleware)
        self.app.router.add_static("/static", path=str(STATIC_DIR), name="static")
        self.app.router.add_get("/", self.handle_index)
        self.app.router.add_get("/activity", self.handle_activity)
        self.app.router.add_get("/api/config", self.handle_api_config)
        self.app.router.add_get("/api/games", self.handle_api_games)
        self.app.router.add_post("/api/sessions", self.handle_create_session)
        self.app.router.add_get("/api/sessions/{session_id}", self.handle_get_session)
        self.app.router.add_get("/ws/{session_id}", self.handle_ws)

    async def handle_index(self, request: web.Request) -> web.Response:
        index_file = TEMPLATES_DIR / "index.html"
        if not index_file.exists():
            return web.Response(text="Activity server active. Templates missing.", content_type="text/plain")
        return web.FileResponse(path=str(index_file))

    async def handle_activity(self, request: web.Request) -> web.Response:
        return await self.handle_index(request)

    async def handle_api_config(self, request: web.Request) -> web.Response:
        return web.json_response({
            "client_id": applicationId,
            "supported_games": session_manager.get_supported_games()
        })

    async def handle_api_games(self, request: web.Request) -> web.Response:
        return web.json_response({
            "games": session_manager.get_supported_games()
        })

    async def handle_create_session(self, request: web.Request) -> web.Response:
        try:
            body = await request.json()
        except Exception:
            return web.json_response({"error": "Invalid JSON"}, status=400)

        game_type = body.get("game_type", "tictactoe")
        user_id = body.get("user_id", "guest_1")
        username = body.get("username", "Player")
        display_name = body.get("display_name", username)
        avatar_url = body.get("avatar_url")

        host = Player(
            user_id=str(user_id),
            username=str(username),
            display_name=str(display_name),
            avatar_url=avatar_url,
            is_host=True
        )

        try:
            session = session_manager.create_session(game_type=game_type, host=host)
        except ValueError as e:
            return web.json_response({"error": str(e)}, status=400)

        return web.json_response({
            "session_id": session.session_id,
            "game_type": game_type,
            "state": session.game.get_state()
        })

    async def handle_get_session(self, request: web.Request) -> web.Response:
        session_id = request.match_info.get("session_id", "")
        session = session_manager.get_session(session_id)
        if not session:
            return web.json_response({"error": "Session not found"}, status=404)
        return web.json_response({
            "session_id": session.session_id,
            "state": session.game.get_state()
        })

    async def handle_ws(self, request: web.Request) -> web.WebSocketResponse:
        session_id = request.match_info.get("session_id", "")
        session = session_manager.get_session(session_id)
        if not session:
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            await ws.send_json({"type": "error", "message": "Session not found"})
            await ws.close()
            return ws

        ws = web.WebSocketResponse(heartbeat=30.0)
        await ws.prepare(request)

        user_id = None

        try:
            from aiohttp import WSMsgType
            import asyncio
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    session.last_activity = asyncio.get_event_loop().time()
                    try:
                        data = json.loads(msg.data)
                    except json.JSONDecodeError:
                        continue

                    msg_type = data.get("type")

                    if msg_type == "join":
                        user_id = str(data.get("user_id", "unknown"))
                        username = str(data.get("username", "Player"))
                        display_name = str(data.get("display_name", username))
                        avatar_url = data.get("avatar_url")

                        session.sockets[user_id] = ws

                        player = Player(
                            user_id=user_id,
                            username=username,
                            display_name=display_name,
                            avatar_url=avatar_url,
                            is_host=(user_id == session.game.host.user_id)
                        )
                        session.game.add_player(player)

                        await ws.send_json({
                            "type": "joined",
                            "user_id": user_id,
                            "state": session.game.get_state(user_id)
                        })
                        await session.broadcast_state()

                    elif msg_type == "action":
                        p_id = str(data.get("user_id", user_id or ""))
                        action_name = data.get("action", "")
                        action_payload = data.get("data", {})

                        result = await session.game.handle_action(p_id, action_name, action_payload)
                        await session.broadcast_state()

                    elif msg_type == "chat":
                        await session.broadcast({
                            "type": "chat_message",
                            "user_id": user_id,
                            "sender": data.get("sender", "User"),
                            "text": data.get("text", "")
                        })

                elif msg.type == WSMsgType.ERROR:
                    pass

        finally:
            if user_id and user_id in session.sockets:
                del session.sockets[user_id]
                session.game.remove_player(user_id)
                await session.broadcast_state()

        return ws

    async def start(self) -> None:
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        try:
            await self.site.start()
        except OSError:
            pass

    async def stop(self) -> None:
        if self.runner:
            await self.runner.cleanup()
            self.runner = None
            self.site = None
