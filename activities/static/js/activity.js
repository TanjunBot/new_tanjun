/**
 * Tanjun Discord Activity Client Application
 * Supports Discord Embedded App SDK (ES Module) & Browser Direct / Standalone mode.
 */

import { DiscordSDK, patchUrlMappings } from './discord-sdk.mjs';

class TanjunActivityClient {
  constructor() {
    this.discordSdk = null;
    this.auth = null;
    this.sessionId = null;
    this.ws = null;
    this.gameState = null;
    this.selectedMode = "bot"; // "bot" or "pvp"
    this.selectedDifficulty = 3;
    this.reconnectTimer = null;

    // Load or generate stable user identity
    this.initUser();
    this.initElements();
    this.setupEventListeners();
  }

  initUser() {
    let storedUserId = sessionStorage.getItem("tanjun_activity_user_id");
    let storedUserName = sessionStorage.getItem("tanjun_activity_user_name");
    if (!storedUserId) {
      storedUserId = "guest_" + Math.floor(1000 + Math.random() * 9000);
      storedUserName = "Gast " + storedUserId.replace("guest_", "");
      sessionStorage.setItem("tanjun_activity_user_id", storedUserId);
      sessionStorage.setItem("tanjun_activity_user_name", storedUserName);
    }
    this.user = {
      id: storedUserId,
      username: storedUserName,
      displayName: storedUserName,
      avatarUrl: "https://cdn.discordapp.com/embed/avatars/0.png"
    };
  }

  initElements() {
    this.el = {
      usernameDisplay: document.getElementById("usernameDisplay"),
      userAvatar: document.getElementById("userAvatar"),
      lobbyView: document.getElementById("lobbyView"),
      gameView: document.getElementById("gameView"),
      modeBotBtn: document.getElementById("modeBotBtn"),
      modePvpBtn: document.getElementById("modePvpBtn"),
      diffContainer: document.getElementById("diffContainer"),
      diffPills: document.querySelectorAll(".diff-pill"),
      lobbyPlayersBox: document.getElementById("lobbyPlayersBox"),
      lobbyPlayersList: document.getElementById("lobbyPlayersList"),
      playerCountBadge: document.getElementById("playerCountBadge"),
      lobbyStatusMsg: document.getElementById("lobbyStatusMsg"),
      startBtn: document.getElementById("startBtn"),
      statusBar: document.getElementById("statusBar"),
      board: document.getElementById("tttBoard"),
      cells: document.querySelectorAll(".cell"),
      p1Avatar: document.getElementById("p1Avatar"),
      p1Name: document.getElementById("p1Name"),
      p1Score: document.getElementById("p1Score"),
      p1Card: document.getElementById("p1Card"),
      p2Avatar: document.getElementById("p2Avatar"),
      p2Name: document.getElementById("p2Name"),
      p2Score: document.getElementById("p2Score"),
      p2Card: document.getElementById("p2Card"),
      restartBtn: document.getElementById("restartBtn"),
      leaveBtn: document.getElementById("leaveBtn")
    };
  }

  setupEventListeners() {
    this.el.modeBotBtn.addEventListener("click", () => this.setMode("bot"));
    this.el.modePvpBtn.addEventListener("click", () => this.setMode("pvp"));

    this.el.diffPills.forEach(pill => {
      pill.addEventListener("click", () => {
        this.el.diffPills.forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
        this.selectedDifficulty = parseInt(pill.dataset.diff, 10);
      });
    });

    this.el.startBtn.addEventListener("click", () => this.startGameSession());

    this.el.cells.forEach(cell => {
      cell.addEventListener("click", () => {
        const index = parseInt(cell.dataset.index, 10);
        this.makeMove(index);
      });
    });

    this.el.restartBtn.addEventListener("click", () => this.restartGame());
    this.el.leaveBtn.addEventListener("click", () => this.returnToLobby());
  }

  isInsideDiscord() {
    try {
      return (
        window.self !== window.top ||
        new URLSearchParams(window.location.search).has("frame_id") ||
        new URLSearchParams(window.location.search).has("instance_id")
      );
    } catch {
      return true;
    }
  }

  async init() {
    const urlParams = new URLSearchParams(window.location.search);
    const paramSession = urlParams.get("session") || urlParams.get("instance_id");

    if (this.isInsideDiscord()) {
      try {
        const configResp = await fetch("/api/config");
        if (configResp.ok) {
          const config = await configResp.json();
          if (config.client_id) {
            this.discordSdk = new DiscordSDK(config.client_id);

            // Complete RPC handshake with Discord client with 4s timeout
            await Promise.race([
              this.discordSdk.ready(),
              new Promise((_, reject) =>
                setTimeout(() => reject(new Error("Discord SDK ready timeout")), 4000)
              )
            ]);

            if (this.discordSdk.instanceId) {
              this.sessionId = this.discordSdk.instanceId;
            }

            // If client secret is configured on the backend, exchange OAuth code for user identity
            if (config.has_client_secret) {
              try {
                const authCode = await this.discordSdk.commands.authorize({
                  client_id: config.client_id,
                  response_type: "code",
                  state: "",
                  prompt: "none",
                  scope: ["identify"]
                });

                if (authCode && authCode.code) {
                  const tokenResp = await fetch("/api/token", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ code: authCode.code })
                  });
                  if (tokenResp.ok) {
                    const tokenData = await tokenResp.json();
                    if (tokenData.access_token) {
                      const auth = await this.discordSdk.commands.authenticate({
                        access_token: tokenData.access_token
                      });
                      if (auth && auth.user) {
                        this.user.id = auth.user.id;
                        this.user.username = auth.user.username;
                        this.user.displayName = auth.user.global_name || auth.user.username;
                        if (auth.user.avatar) {
                          this.user.avatarUrl = `https://cdn.discordapp.com/avatars/${auth.user.id}/${auth.user.avatar}.png?size=128`;
                        }
                        sessionStorage.setItem("tanjun_activity_user_id", this.user.id);
                        sessionStorage.setItem("tanjun_activity_user_name", this.user.displayName);
                      }
                    }
                  }
                }
              } catch (authErr) {
                console.info("[Discord Activity] OAuth optional step skipped:", authErr);
              }
            }
          }
        }
      } catch (err) {
        console.warn("[Discord Activity] Discord SDK initialization failed or timed out:", err);
      }
    }

    // Refresh UI with user profile
    this.el.usernameDisplay.textContent = this.user.displayName;
    this.el.userAvatar.src = this.user.avatarUrl;

    // Connect to WebSocket if sessionId exists from Discord instanceId or URL query
    if (this.sessionId || paramSession) {
      this.sessionId = this.sessionId || paramSession;
      this.connectWebSocket();
    } else {
      this.renderLobbyPlayers();
    }
  }

  setMode(mode) {
    this.selectedMode = mode;
    if (mode === "bot") {
      this.el.modeBotBtn.classList.add("active");
      this.el.modePvpBtn.classList.remove("active");
      this.el.diffContainer.style.display = "block";
    } else {
      this.el.modePvpBtn.classList.add("active");
      this.el.modeBotBtn.classList.remove("active");
      this.el.diffContainer.style.display = "none";
    }
    this.updateLobbyControls();
  }

  setLobbyStatus(message, isWarning = false) {
    if (!this.el.lobbyStatusMsg) return;
    this.el.lobbyStatusMsg.textContent = message;
    this.el.lobbyStatusMsg.style.color = isWarning ? "#fb8500" : "#00f2fe";
  }

  async startGameSession() {
    // If already in a connected WebSocket session, send start action directly
    if (this.sessionId && this.ws && this.ws.readyState === WebSocket.OPEN) {
      if (this.selectedMode === "pvp") {
        const humanPlayers = (this.gameState?.players || []).filter(p => !p.is_bot);
        if (humanPlayers.length < 2) {
          this.setLobbyStatus("⚠️ Für den Mitspieler-Modus wird noch ein 2. Spieler benötigt! (Tritt dem Voice-Channel bei oder teile den Link)", true);
          return;
        }
      }
      this.setLobbyStatus("Spiel wird gestartet...");
      this.sendAction("start", {
        mode: this.selectedMode,
        difficulty: this.selectedDifficulty
      });
      return;
    }

    // Otherwise (standalone direct browser access), create session via HTTP API
    try {
      this.el.startBtn.disabled = true;
      this.el.startBtn.textContent = "Starten...";

      const resp = await fetch("/api/sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          game_type: "tictactoe",
          user_id: this.user.id,
          username: this.user.username,
          display_name: this.user.displayName,
          avatar_url: this.user.avatarUrl
        })
      });
      const data = await resp.json();
      this.sessionId = data.session_id;

      this.connectWebSocket(() => {
        this.sendAction("start", {
          mode: this.selectedMode,
          difficulty: this.selectedDifficulty
        });
      });
    } catch (e) {
      console.error("[Discord Activity] Failed to create session:", e);
      alert("Fehler beim Erstellen der Sitzung.");
      this.el.startBtn.disabled = false;
      this.el.startBtn.textContent = "Spiel Starten";
    }
  }

  connectWebSocket(onOpenCallback) {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws/${this.sessionId}`;

    try {
      this.ws = new WebSocket(wsUrl);
    } catch (err) {
      console.error("[Discord Activity] WebSocket connection failed:", err);
      return;
    }

    this.ws.onopen = () => {
      this.ws.send(JSON.stringify({
        type: "join",
        user_id: this.user.id,
        username: this.user.username,
        display_name: this.user.displayName,
        avatar_url: this.user.avatarUrl
      }));
      if (onOpenCallback) onOpenCallback();
    };

    this.ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === "joined" || msg.type === "state_update") {
          this.handleStateUpdate(msg.state);
        }
      } catch (err) {
        console.error("[Discord Activity] Error parsing WS message:", err);
      }
    };

    this.ws.onclose = () => {
      // Auto-reconnect if session still active and not intentionally closed
      if (this.sessionId && (!this.gameState || !this.gameState.is_finished)) {
        this.reconnectTimer = setTimeout(() => {
          this.connectWebSocket();
        }, 2000);
      }
    };
  }

  sendAction(action, data = {}) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;
    this.ws.send(JSON.stringify({
      type: "action",
      user_id: this.user.id,
      action: action,
      data: data
    }));
  }

  makeMove(cellIndex) {
    if (!this.gameState || !this.gameState.is_started || this.gameState.is_finished) return;
    if (this.gameState.current_turn !== this.user.id) return;
    if (this.gameState.board[cellIndex] !== "") return;

    this.sendAction("move", { cell: cellIndex });
  }

  restartGame() {
    this.sendAction("restart");
  }

  returnToLobby() {
    this.sendAction("lobby");
    this.el.lobbyView.style.display = "block";
    this.el.gameView.style.display = "none";
    this.updateLobbyControls();
  }

  updateLobbyControls() {
    const players = this.gameState?.players || [this.user];
    const isHost = !this.gameState || players[0]?.user_id === this.user.id;
    const humanPlayers = players.filter(p => !p.is_bot);

    if (this.el.startBtn) {
      if (!isHost) {
        this.el.startBtn.disabled = true;
        this.el.startBtn.textContent = "Warte auf Host...";
        this.setLobbyStatus("Warte darauf, dass der Host das Spiel startet.");
      } else {
        this.el.startBtn.disabled = false;
        this.el.startBtn.textContent = "Spiel Starten";
        if (this.selectedMode === "pvp") {
          if (humanPlayers.length < 2) {
            this.setLobbyStatus("Warte auf Mitspieler (Teile den Link oder tritt im Discord-Voice bei)...");
          } else {
            this.setLobbyStatus("Mitspieler bereit! Klicke auf 'Spiel Starten'.");
          }
        } else {
          this.setLobbyStatus("Bereit gegen Tanjun AI anzutreten!");
        }
      }
    }
  }

  renderLobbyPlayers() {
    if (!this.el.lobbyPlayersList) return;

    const players = (this.gameState?.players || []).filter(p => !p.is_bot);
    const count = Math.max(1, players.length);
    if (this.el.playerCountBadge) {
      this.el.playerCountBadge.textContent = `${count}/2`;
    }

    if (players.length === 0) {
      this.el.lobbyPlayersList.innerHTML = `
        <div class="lobby-player-row">
          <div class="lobby-player-meta">
            <img class="lobby-player-avatar-small" src="${this.user.avatarUrl}" alt="Avatar">
            <span>${this.user.displayName}</span>
          </div>
          <span class="lobby-tag-host">Host 👑</span>
        </div>
      `;
      return;
    }

    let html = "";
    players.forEach((p, idx) => {
      const isYou = p.user_id === this.user.id;
      const isHost = idx === 0 || p.is_host;
      html += `
        <div class="lobby-player-row">
          <div class="lobby-player-meta">
            <img class="lobby-player-avatar-small" src="${p.avatar_url || 'https://cdn.discordapp.com/embed/avatars/0.png'}" alt="Avatar">
            <span>${p.display_name || p.username}</span>
            ${isYou ? '<span class="lobby-tag-you">Du</span>' : ''}
          </div>
          ${isHost ? '<span class="lobby-tag-host">Host 👑</span>' : '<span style="font-size:0.75rem; color:#94a3b8;">Bereit</span>'}
        </div>
      `;
    });

    if (players.length < 2 && this.selectedMode === "pvp") {
      html += `
        <div class="lobby-player-row" style="opacity: 0.6; border: 1px dashed rgba(255,255,255,0.2);">
          <div class="lobby-player-meta">
            <span>⏳</span>
            <span style="color: #94a3b8; font-style: italic;">Warten auf Mitspieler...</span>
          </div>
        </div>
      `;
    }

    this.el.lobbyPlayersList.innerHTML = html;
  }

  handleStateUpdate(state) {
    if (!state) return;
    this.gameState = state;

    // Transition between lobby and game view based on is_started
    if (state.is_started) {
      this.el.lobbyView.style.display = "none";
      this.el.gameView.style.display = "flex";
    } else {
      this.el.lobbyView.style.display = "block";
      this.el.gameView.style.display = "none";
      this.renderLobbyPlayers();
      this.updateLobbyControls();
      return;
    }

    // Scoreboard setup
    const players = state.players || [];
    const p1 = players[0] || { display_name: "Warten...", user_id: "" };
    const p2 = players[1] || { display_name: "Warten auf Gegner...", user_id: "" };

    this.el.p1Name.textContent = p1.display_name || p1.username;
    this.el.p1Avatar.src = p1.avatar_url || "https://cdn.discordapp.com/embed/avatars/0.png";
    this.el.p1Score.textContent = `${state.scores?.[p1.user_id] || 0} Siege`;

    this.el.p2Name.textContent = p2.display_name || p2.username;
    this.el.p2Avatar.src = p2.avatar_url || (p2.is_bot ? "/static/images/tanjun_avatar.png" : "https://cdn.discordapp.com/embed/avatars/1.png");
    this.el.p2Score.textContent = `${state.scores?.[p2.user_id] || 0} Siege`;

    // Active turn highlight
    if (state.current_turn === p1.user_id) {
      this.el.p1Card.classList.add("turn-active");
      this.el.p2Card.classList.remove("turn-active");
    } else if (state.current_turn === p2.user_id) {
      this.el.p2Card.classList.add("turn-active");
      this.el.p1Card.classList.remove("turn-active");
    } else {
      this.el.p1Card.classList.remove("turn-active");
      this.el.p2Card.classList.remove("turn-active");
    }

    // Board rendering
    const winningLine = state.winning_line || [];
    state.board.forEach((val, idx) => {
      const cell = this.el.cells[idx];
      cell.textContent = val;
      cell.className = "cell";
      if (val === "X") cell.classList.add("cell-x", "taken");
      if (val === "O") cell.classList.add("cell-o", "taken");
      if (winningLine.includes(idx)) {
        cell.classList.add("winner-cell");
      }
    });

    // In-game status bar
    if (state.is_finished) {
      if (state.winner === "draw") {
        this.el.statusBar.textContent = "🤝 Unentschieden! Niemand gewinnt.";
        this.el.statusBar.style.color = "#ffb703";
      } else {
        const winnerObj = players.find(p => p.user_id === state.winner);
        const name = winnerObj ? (winnerObj.display_name || winnerObj.username) : state.winner;
        this.el.statusBar.textContent = `🎉 ${name} gewinnt das Spiel!`;
        this.el.statusBar.style.color = "#00f2fe";
      }
    } else if (state.is_started) {
      if (state.current_turn === this.user.id) {
        this.el.statusBar.textContent = "⚡ Du bist am Zug! Setze dein Zeichen.";
        this.el.statusBar.style.color = "#00f2fe";
      } else {
        const currObj = players.find(p => p.user_id === state.current_turn);
        const name = currObj ? (currObj.display_name || currObj.username) : "Gegner";
        this.el.statusBar.textContent = `⏳ ${name} überlegt...`;
        this.el.statusBar.style.color = "#94a3b8";
      }
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  window.app = new TanjunActivityClient();
  window.app.init();
});
