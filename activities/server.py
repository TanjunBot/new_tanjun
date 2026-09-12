import asyncio
import contextlib
import json
import logging
import re
try:
    from aiohttp import web
    _middleware_decorator = web.middleware
except ImportError:
    web = None
    def _middleware_decorator(f):
        return f

from activities.base import Player
from activities.manager import session_manager
from config import activity_server_host, activity_server_port, applicationId
from pathlib import Path

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"
TEMPLATES_DIR = Path(__file__).parent / "templates"
MAX_ACTIVITY_TEXT_LENGTH = 2000
MAX_ACTIVITY_ID_LENGTH = 128
SESSION_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


class ActivityServer:
    """Embedded HTTP and WebSocket server for Discord Activities."""

    def __init__(self, host: str = activity_server_host, port: int = activity_server_port) -> None:
        self.host = host
        self.port = port
        if web is not None:
            self.app = web.Application()
            self._setup_routes()
        else:
            self.app = None
        self.runner = None
        self.site = None
        self._cleanup_task: asyncio.Task | None = None

    @_middleware_decorator
    async def cors_middleware(self, request, handler):
        if request.method == "OPTIONS":
            response = web.Response(status=200)
        else:
            response = await handler(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        # Discord Activity iframe support
        response.headers["Content-Security-Policy"] = (
            "frame-ancestors 'self' https://*.discord.com https://discord.com https://*.discordsays.com https://discordsays.com;"
        )
        if "X-Frame-Options" in response.headers:
            del response.headers["X-Frame-Options"]
        if request.path.startswith("/static/"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

    def _setup_routes(self) -> None:
        self.app.middlewares.append(self.cors_middleware)
        self.app.router.add_static("/static", path=str(STATIC_DIR), name="static")
        self.app.router.add_get("/", self.handle_index)
        self.app.router.add_get("/activity", self.handle_activity)
        self.app.router.add_get("/api/config", self.handle_api_config)
        self.app.router.add_post("/api/token", self.handle_api_token)
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

    def get_config_dict(self) -> dict:
        import config
        secret_obj = getattr(config, "discord_client_secret", None)
        client_secret = secret_obj.get_secret_value() if hasattr(secret_obj, "get_secret_value") else str(secret_obj or "")
        has_client_secret = bool(client_secret and client_secret.strip())
        return {
            "client_id": applicationId,
            "has_client_secret": has_client_secret,
            "supported_games": session_manager.get_supported_games()
        }

    async def handle_api_config(self, request: web.Request) -> web.Response:
        return web.json_response(self.get_config_dict())

    async def handle_api_token(self, request: web.Request) -> web.Response:
        try:
            body = await request.json()
            code = body.get("code")
        except Exception:
            return web.json_response({"error": "Invalid JSON"}, status=400)

        import config
        client_id = applicationId
        secret_obj = getattr(config, "discord_client_secret", None)
        client_secret = secret_obj.get_secret_value() if hasattr(secret_obj, "get_secret_value") else str(secret_obj or "")

        if not client_secret or not client_secret.strip():
            return web.json_response({"error": "client_secret not configured"}, status=501)

        data = {
            "client_id": client_id,
            "client_secret": client_secret.strip(),
            "grant_type": "authorization_code",
            "code": code,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post("https://discord.com/api/v10/oauth2/token", data=data, headers=headers) as resp:
                    resp_json = await resp.json()
                    return web.json_response(resp_json, status=resp.status)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def handle_api_games(self, request: web.Request) -> web.Response:
        return web.json_response({
            "games": session_manager.get_supported_games()
        })

    async def handle_create_session(self, request: web.Request) -> web.Response:
        try:
            body = await request.json()
        except Exception:
            return web.json_response({"error": "Invalid JSON"}, status=400)

        game_type = str(body.get("game_type", "hub"))
        user_id = str(body.get("user_id", "guest_1")).strip()[:MAX_ACTIVITY_ID_LENGTH]
        username = str(body.get("username", "Player")).strip()[:32] or "Player"
        display_name = body.get("display_name", username)
        avatar_url = body.get("avatar_url")
        if not user_id:
            return web.json_response({"error": "user_id must not be empty"}, status=400)

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
            "state": session.get_full_state()
        })

    async def handle_get_session(self, request: web.Request) -> web.Response:
        session_id = request.match_info.get("session_id", "")
        session = session_manager.get_session(session_id)
        if not session:
            return web.json_response({"error": "Session not found"}, status=404)
        return web.json_response({
            "session_id": session.session_id,
            "state": session.get_full_state()
        })

    async def handle_ws(self, request: web.Request) -> web.WebSocketResponse:
        session_id = request.match_info.get("session_id", "")
        if not SESSION_ID_PATTERN.fullmatch(session_id):
            return web.json_response({"error": "Invalid session ID"}, status=400)
        session = session_manager.get_session(session_id)
        if not session:
            channel_id = request.query.get("channel_id")
            if channel_id:
                session = session_manager.get_session_by_channel(channel_id)
                if session and session_id:
                    session_manager.register_channel_alias(session_id, session.session_id)
        if not session:
            # If launched directly through Discord instance_id or direct link, auto-create Hub session
            default_host = Player(
                user_id="discord_player",
                username="Player",
                display_name="Player",
                is_host=True
            )
            try:
                session = session_manager.create_session("hub", host=default_host, session_id=session_id)
            except ValueError:
                # A concurrent websocket may have created this session between
                # the lookup above and the create call.
                session = session_manager.get_session(session_id)
                if not session:
                    raise

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
                    except (TypeError, json.JSONDecodeError):
                        continue
                    if not isinstance(data, dict):
                        await ws.send_json({"type": "error", "error": "Message must be a JSON object"})
                        continue

                    msg_type = data.get("type")

                    if msg_type == "join":
                        if user_id is not None:
                            await ws.send_json({"type": "error", "error": "This websocket is already joined"})
                            continue
                        user_id = str(data.get("user_id", "")).strip()[:MAX_ACTIVITY_ID_LENGTH]
                        if not user_id:
                            await ws.send_json({"type": "error", "error": "A user_id is required to join"})
                            continue
                        username = str(data.get("username", "Player")).strip()[:32] or "Player"
                        display_name = str(data.get("display_name", username)).strip()[:32] or username
                        avatar_url = data.get("avatar_url")

                        # Replacing a stale connection is supported, but its
                        # finally block must not remove this live connection.
                        session.sockets[user_id] = ws

                        # If the session was auto-created with a placeholder host,
                        # promote the first real user to host instead of adding them as player 2.
                        PLACEHOLDER_HOST_IDS = {"discord_player", "guest_host", "guest_1"}
                        is_placeholder = (
                            session.game.host.user_id in PLACEHOLDER_HOST_IDS
                            or session.game.host.user_id.startswith("host_")
                            or (
                                len(session.game.players) <= 1
                                and any(pid in PLACEHOLDER_HOST_IDS or pid.startswith("host_") for pid in session.game.players)
                            )
                        )
                        if is_placeholder:
                            old_placeholder_id = session.game.host.user_id
                            real_host = Player(
                                user_id=user_id,
                                username=username,
                                display_name=display_name,
                                avatar_url=avatar_url,
                                is_host=True
                            )
                            # Remove placeholder from players dict and set real host
                            session.game.players.pop(old_placeholder_id, None)
                            session.game.host = real_host
                            session.game.players[user_id] = real_host
                            session.cancel_disconnect_forfeit(user_id)
                            if session.tournament:
                                session.tournament.participants.pop(old_placeholder_id, None)
                                session.tournament.host_id = user_id
                                session.tournament.add_participant(real_host)
                        else:
                            player = Player(
                                user_id=user_id,
                                username=username,
                                display_name=display_name,
                                avatar_url=avatar_url,
                                is_host=(user_id == session.game.host.user_id)
                            )
                            session.game.add_player(player)
                            session.cancel_disconnect_forfeit(user_id)
                            if session.tournament:
                                session.tournament.add_participant(player)
                                user_m = session.tournament.get_match_for_user(user_id)
                                if user_m and user_m.game_instance and user_id in user_m.game_instance.players:
                                    user_m.game_instance.players[user_id].connected = True

                        await ws.send_json({
                            "type": "joined",
                            "user_id": user_id,
                            "state": session.get_full_state(for_user_id=user_id)
                        })
                        await session.broadcast_state()

                    elif msg_type == "action":
                        if user_id is None:
                            continue
                        # The websocket identity is authoritative. Never trust an
                        # action payload to select another player's identity.
                        p_id = user_id
                        action_name = data.get("action", "")
                        if not isinstance(action_name, str):
                            continue
                        action_payload = data.get("data", {})
                        if not isinstance(action_payload, dict):
                            continue

                        is_host = (p_id == session.game.host.user_id) or bool(session.tournament and p_id == session.tournament.host_id)

                        if action_name == "select_game":
                            if not is_host:
                                continue
                            game_type = action_payload.get("game_type", "tictactoe")
                            try:
                                session.switch_game(game_type)
                            except Exception as e:
                                pass
                            await session.broadcast_state()
                        elif action_name == "return_to_hub":
                            if not is_host:
                                continue
                            session.is_hub = True
                            if hasattr(session.game, "reset"):
                                await session.game.reset()
                            await session.broadcast_state()
                        elif action_name == "update_settings":
                            if not is_host:
                                continue
                            session.lobby_settings.update(action_payload)
                            await session.broadcast_state()
                        elif action_name in ("forfeit", "surrender"):
                            if session.tournament and session.tournament.status == "active":
                                user_m = session.tournament.get_match_for_user(p_id) or session.tournament.get_current_match()
                                forfeited_winner = session.leave_tournament(p_id)
                                if forfeited_winner and user_m:
                                    await session.tournament._resolve_match(user_m, forfeited_winner)
                                    if session.tournament.transition_info and session.tournament.match_style == "spectated":
                                        session.schedule_match_transition(delay=5.0)
                                    elif session.tournament.status in ("round_end", "finished"):
                                        session.sync_tournament_match()
                            elif session.game and session.game.is_started and not session.game.is_finished:
                                if p_id in session.game.players:
                                    opponents = [pid for pid in session.game.players if pid != p_id and not session.game.players[pid].is_bot]
                                    if opponents:
                                        winner = opponents[0]
                                        session.game.is_finished = True
                                        session.game.winner = winner
                                        session.game.scores[winner] = session.game.scores.get(winner, 0) + 1
                            await session.broadcast_state()
                        elif action_name in ("create_tournament", "tournament_create"):
                            if not is_host:
                                continue
                            current_p = session.game.players.get(p_id) or session.game.spectators.get(p_id)
                            if current_p is None:
                                continue
                            session.create_tournament(host=current_p)
                            session.tournament.add_participant(current_p)
                            await session.broadcast_state()
                        elif action_name == "tournament_join":
                            current_p = session.game.players.get(p_id) or session.game.spectators.get(p_id)
                            if session.tournament and current_p is not None:
                                session.tournament.add_participant(current_p)
                            await session.broadcast_state()
                        elif action_name == "tournament_leave":
                            if session.tournament:
                                user_m = session.tournament.get_match_for_user(p_id) or session.tournament.get_current_match()
                                forfeited_winner = session.leave_tournament(p_id)
                                if forfeited_winner and user_m:
                                    await session.tournament._resolve_match(user_m, forfeited_winner)
                                    if session.tournament.transition_info and session.tournament.match_style == "spectated":
                                        session.schedule_match_transition(delay=5.0)
                                    elif session.tournament.status in ("round_end", "finished"):
                                        session.sync_tournament_match()
                                session.migrate_host_if_needed(p_id)
                            await session.broadcast_state()
                        elif action_name == "tournament_destroy":
                            if session.tournament and session.tournament.host_id == p_id:
                                session.tournament = None
                            await session.broadcast_state()
                        elif action_name == "update_profile":
                            new_name = str(action_payload.get("display_name", "")).strip()
                            new_avatar = action_payload.get("avatar_url")
                            if new_name:
                                new_name = new_name[:32]
                                if p_id in session.game.players:
                                    session.game.players[p_id].display_name = new_name
                                    session.game.players[p_id].username = new_name
                                    if new_avatar:
                                        session.game.players[p_id].avatar_url = new_avatar
                                if p_id in session.game.spectators:
                                    session.game.spectators[p_id].display_name = new_name
                                    session.game.spectators[p_id].username = new_name
                                    if new_avatar:
                                        session.game.spectators[p_id].avatar_url = new_avatar
                                if session.tournament and p_id in session.tournament.participants:
                                    session.tournament.participants[p_id].display_name = new_name
                                    session.tournament.participants[p_id].username = new_name
                                    if new_avatar:
                                        session.tournament.participants[p_id].avatar_url = new_avatar
                                await session.broadcast_state()
                        elif action_name.startswith("tournament_"):
                            if session.tournament:
                                if action_name in ("tournament_next_match", "tournament_advance_match"):
                                    session.cancel_match_transition()
                                await session.tournament.handle_action(p_id, action_name, action_payload)
                                if action_name in ("tournament_start", "tournament_next_round", "tournament_next_match", "tournament_advance_match"):
                                    session.sync_tournament_match()
                                await session.broadcast_state()
                        else:
                            if session.tournament and session.tournament.status == "active":
                                user_m = session.tournament.get_match_for_user(p_id)
                                if user_m and user_m.game_instance and user_m.status == "active":
                                    result = await user_m.game_instance.handle_action(
                                        p_id, action_name, action_payload, broadcast_cb=session.broadcast_state
                                    )
                                    if user_m.game_instance.is_finished:
                                        winner = user_m.game_instance.winner or "draw"
                                        await session.tournament._resolve_match(user_m, winner)
                                        if session.tournament.transition_info and session.tournament.match_style == "spectated":
                                            session.schedule_match_transition(delay=5.0)
                                        elif session.tournament.status in ("round_end", "finished"):
                                            session.sync_tournament_match()
                                    await session.broadcast_state()
                                    continue

                            if action_name == "start":
                                if not is_host:
                                    continue
                                full_payload = dict(session.lobby_settings)
                                full_payload.update(action_payload)
                                action_payload = full_payload
                            result = await session.game.handle_action(
                                p_id, action_name, action_payload, broadcast_cb=session.broadcast_state
                            )
                            # If active in tournament and match just completed, resolve tournament score
                            if session.tournament and session.tournament.status == "active" and session.game.is_finished:
                                winner = session.game.winner or "draw"
                                await session.tournament.resolve_current_match(winner)
                                if session.tournament.transition_info:
                                    session.schedule_match_transition(delay=5.0)
                                elif session.tournament.status == "round_end":
                                    session.sync_tournament_match()
                            await session.broadcast_state()

                    elif msg_type == "chat":
                        if user_id is None:
                            continue
                        text = str(data.get("text", "")).strip()
                        if not text:
                            continue
                        await session.broadcast({
                            "type": "chat_message",
                            "user_id": user_id,
                            "sender": session.game.players.get(user_id, session.game.spectators.get(user_id)).display_name
                            if session.game.players.get(user_id, session.game.spectators.get(user_id))
                            else "User",
                            "text": text[:MAX_ACTIVITY_TEXT_LENGTH]
                        })

                elif msg.type == WSMsgType.ERROR:
                    pass

        finally:
            # A reconnect may have replaced this websocket.  Only the current
            # socket for the identity is allowed to remove the player.
            if user_id and session.sockets.get(user_id) is ws:
                del session.sockets[user_id]
                session.game.remove_player(user_id)
                if session.tournament:
                    session.tournament.remove_participant(user_id, voluntary=False)
                    user_m = session.tournament.get_match_for_user(user_id)
                    if user_m and user_m.game_instance and user_id in user_m.game_instance.players:
                        user_m.game_instance.players[user_id].connected = False
                session.schedule_disconnect_forfeit(user_id, delay=30.0)
                await session.broadcast_state()

        return ws

    async def start(self) -> None:
        if self.runner is not None:
            return
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        try:
            await self.site.start()
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            print(f"[Activities] Discord Activity HTTP & WebSocket server started on http://{self.host}:{self.port}")
        except OSError as exc:
            print(f"[Activities] Warning: Could not bind Activity server to {self.host}:{self.port}: {exc}")

    async def stop(self) -> None:
        cleanup_task = self._cleanup_task
        self._cleanup_task = None
        if cleanup_task and not cleanup_task.done():
            cleanup_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await cleanup_task
        if self.runner:
            await self.runner.cleanup()
            self.runner = None
            self.site = None
            print("[Activities] Discord Activity server stopped.")

    async def _cleanup_loop(self) -> None:
        try:
            while True:
                await asyncio.sleep(300)
                await session_manager.cleanup_idle_sessions(max_idle_seconds=3600)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error("Error in session cleanup loop: %s", e)
