/**
 * Tanjun Discord Activity Client Application
 * Supports Discord Embedded App SDK (ES Module) & Browser Direct / Standalone mode.
 * Features: Tanjun Game Hub, Tic-Tac-Toe, Connect 4 (Vier Gewinnt), and Rock-Paper-Scissors.
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
    this.selectedTargetWins = 3;
    this.reconnectTimer = null;

    // Available games list (fallback if not yet received from WS)
    this.availableGames = [
      {
        type: "tictactoe",
        name: "Tic-Tac-Toe",
        description: "Klassisches 3x3 Duell. Wer zuerst drei Symbole in einer Reihe hat, gewinnt!",
        icon: "❌⭕",
        badge: "Klassiker"
      },
      {
        type: "connect4",
        name: "Vier Gewinnt",
        description: "Taktisches 7x6 Raster. Wirf deine Chips ein und bilde eine 4er-Reihe!",
        icon: "🔴🟡",
        badge: "Taktik"
      },
      {
        type: "rps",
        name: "Schere Stein Papier",
        description: "Schnelles Duell mit verdeckter Wahl im Best-of-5 Modus.",
        icon: "✊✋✌️",
        badge: "Action"
      }
    ];

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

      // Views
      hubView: document.getElementById("hubView"),
      lobbyView: document.getElementById("lobbyView"),
      gameView: document.getElementById("gameView"),

      // Hub Elements
      gamesGrid: document.getElementById("gamesGrid"),
      hubPlayersList: document.getElementById("hubPlayersList"),
      hubPlayerCount: document.getElementById("hubPlayerCount"),
      hubStatusMsg: document.getElementById("hubStatusMsg"),

      // Lobby Elements
      backToHubBtn: document.getElementById("backToHubBtn"),
      selectedGameBadge: document.getElementById("selectedGameBadge"),
      lobbyGameTitle: document.getElementById("lobbyGameTitle"),
      lobbyGameSubtitle: document.getElementById("lobbyGameSubtitle"),
      modeBotBtn: document.getElementById("modeBotBtn"),
      modePvpBtn: document.getElementById("modePvpBtn"),
      diffContainer: document.getElementById("diffContainer"),
      diffPills: document.querySelectorAll(".diff-pill"),
      rpsRoundsContainer: document.getElementById("rpsRoundsContainer"),
      roundPills: document.querySelectorAll("#rpsRoundsContainer .diff-pill"),
      lobbyPlayersBox: document.getElementById("lobbyPlayersBox"),
      lobbyPlayersList: document.getElementById("lobbyPlayersList"),
      playerCountBadge: document.getElementById("playerCountBadge"),
      lobbyStatusMsg: document.getElementById("lobbyStatusMsg"),
      startBtn: document.getElementById("startBtn"),

      // Common Game View Elements
      statusBar: document.getElementById("statusBar"),
      p1Card: document.getElementById("p1Card"),
      p1Avatar: document.getElementById("p1Avatar"),
      p1Tag: document.getElementById("p1Tag"),
      p1Name: document.getElementById("p1Name"),
      p1Score: document.getElementById("p1Score"),
      p2Card: document.getElementById("p2Card"),
      p2Avatar: document.getElementById("p2Avatar"),
      p2Tag: document.getElementById("p2Tag"),
      p2Name: document.getElementById("p2Name"),
      p2Score: document.getElementById("p2Score"),

      // Game Boards
      tttBoardContainer: document.getElementById("tttBoardContainer"),
      tttCells: document.querySelectorAll("#tttBoard .cell"),

      c4BoardContainer: document.getElementById("c4BoardContainer"),
      c4DropRow: document.getElementById("c4DropRow"),
      c4Grid: document.getElementById("c4Grid"),

      rpsBoardContainer: document.getElementById("rpsBoardContainer"),
      rpsRoundBadge: document.getElementById("rpsRoundBadge"),
      rpsP1Pick: document.getElementById("rpsP1Pick"),
      rpsP1Label: document.getElementById("rpsP1Label"),
      rpsP2Pick: document.getElementById("rpsP2Pick"),
      rpsP2Label: document.getElementById("rpsP2Label"),
      rpsRoundResult: document.getElementById("rpsRoundResult"),
      rpsBtns: document.querySelectorAll(".rps-btn"),

      // Footer Controls
      restartBtn: document.getElementById("restartBtn"),
      leaveBtn: document.getElementById("leaveBtn"),
      hubBtn: document.getElementById("hubBtn")
    };

    // Initialize 42 Connect 4 cells dynamically if empty
    if (this.el.c4Grid && this.el.c4Grid.children.length === 0) {
      for (let i = 0; i < 42; i++) {
        const cell = document.createElement("div");
        cell.className = "c4-cell";
        cell.dataset.index = i;
        const col = i % 7;
        cell.addEventListener("click", () => this.makeMoveConnect4(col));
        this.el.c4Grid.appendChild(cell);
      }
    }
  }

  setupEventListeners() {
    // Mode toggles
    this.el.modeBotBtn.addEventListener("click", () => this.setMode("bot"));
    this.el.modePvpBtn.addEventListener("click", () => this.setMode("pvp"));

    // Difficulty selection
    this.el.diffPills.forEach(pill => {
      pill.addEventListener("click", () => {
        this.el.diffPills.forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
        this.selectedDifficulty = parseInt(pill.dataset.diff, 10);
      });
    });

    // Rounds selection for RPS
    this.el.roundPills.forEach(pill => {
      pill.addEventListener("click", () => {
        this.el.roundPills.forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
        this.selectedTargetWins = parseInt(pill.dataset.rounds, 10);
      });
    });

    // Start Button
    this.el.startBtn.addEventListener("click", () => this.startGameSession());

    // Tic-Tac-Toe Move
    this.el.tttCells.forEach(cell => {
      cell.addEventListener("click", () => {
        const index = parseInt(cell.dataset.index, 10);
        this.makeMoveTTT(index);
      });
    });

    // Connect 4 Drop buttons
    if (this.el.c4DropRow) {
      this.el.c4DropRow.querySelectorAll(".c4-drop-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          const col = parseInt(btn.dataset.col, 10);
          this.makeMoveConnect4(col);
        });
      });
    }

    // RPS Choice buttons
    this.el.rpsBtns.forEach(btn => {
      btn.addEventListener("click", () => {
        const choice = btn.dataset.choice;
        this.makeMoveRPS(choice);
      });
    });

    // Navigation Buttons
    this.el.restartBtn.addEventListener("click", () => this.restartGame());
    this.el.leaveBtn.addEventListener("click", () => this.returnToLobby());
    this.el.hubBtn.addEventListener("click", () => this.returnToHub());
    this.el.backToHubBtn.addEventListener("click", () => this.returnToHub());
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

            // Optional OAuth token exchange
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

    // Render Hub cards initially
    this.renderHubGames();

    // Connect to WebSocket if sessionId exists
    if (this.sessionId || paramSession) {
      this.sessionId = this.sessionId || paramSession;
      this.connectWebSocket();
    } else {
      this.renderHubPlayers();
    }
  }

  renderHubGames() {
    if (!this.el.gamesGrid) return;

    const games = this.gameState?.available_games || this.availableGames;
    const isHost = !this.gameState || (this.gameState.players || [])[0]?.user_id === this.user.id;

    let html = "";
    games.forEach(g => {
      html += `
        <div class="game-hub-card" data-game="${g.type}">
          <div class="game-card-icon">${g.icon}</div>
          <div class="game-card-body">
            <div class="game-card-top">
              <span class="game-card-title">${g.name}</span>
              <span class="game-card-tag">${g.badge || 'Spiel'}</span>
            </div>
            <div class="game-card-desc">${g.description}</div>
          </div>
        </div>
      `;
    });

    this.el.gamesGrid.innerHTML = html;

    this.el.gamesGrid.querySelectorAll(".game-hub-card").forEach(card => {
      card.addEventListener("click", () => {
        const gameType = card.dataset.game;
        this.selectGameFromHub(gameType);
      });
    });

    if (this.el.hubStatusMsg) {
      if (isHost) {
        this.el.hubStatusMsg.textContent = "Wähle ein Spiel aus, um die Runde zu starten!";
        this.el.hubStatusMsg.style.color = "#00f2fe";
      } else {
        const hostName = (this.gameState?.players || [])[0]?.display_name || "Der Host";
        this.el.hubStatusMsg.textContent = `Warte darauf, dass ${hostName} ein Spiel auswählt...`;
        this.el.hubStatusMsg.style.color = "#94a3b8";
      }
    }
  }

  selectGameFromHub(gameType) {
    const isHost = !this.gameState || (this.gameState.players || [])[0]?.user_id === this.user.id;
    if (!isHost) {
      alert("Nur der Host kann ein neues Spiel auswählen.");
      return;
    }

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.sendAction("select_game", { game_type: gameType });
    } else {
      // Direct visit without session: create session for this game
      this.createStandaloneSession(gameType);
    }
  }

  async createStandaloneSession(gameType) {
    try {
      const resp = await fetch("/api/sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          game_type: gameType,
          user_id: this.user.id,
          username: this.user.username,
          display_name: this.user.displayName,
          avatar_url: this.user.avatarUrl
        })
      });
      const data = await resp.json();
      this.sessionId = data.session_id;
      this.connectWebSocket();
    } catch (e) {
      console.error("[Discord Activity] Failed to create session:", e);
    }
  }

  setMode(mode) {
    this.selectedMode = mode;
    if (mode === "bot") {
      this.el.modeBotBtn.classList.add("active");
      this.el.modePvpBtn.classList.remove("active");
      if (this.gameState?.game_type !== "rps") {
        this.el.diffContainer.style.display = "block";
      }
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
        difficulty: this.selectedDifficulty,
        target_wins: this.selectedTargetWins
      });
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
      if (this.sessionId) {
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

  // ── Game-specific Moves ───────────────────────────────────────
  makeMoveTTT(cellIndex) {
    if (!this.gameState || !this.gameState.is_started || this.gameState.is_finished) return;
    if (this.gameState.current_turn !== this.user.id) return;
    if (this.gameState.board[cellIndex] !== "") return;
    this.sendAction("move", { cell: cellIndex });
  }

  makeMoveConnect4(col) {
    if (!this.gameState || !this.gameState.is_started || this.gameState.is_finished) return;
    if (this.gameState.current_turn !== this.user.id) return;
    this.sendAction("move", { col: col });
  }

  makeMoveRPS(choice) {
    if (!this.gameState || !this.gameState.is_started || this.gameState.is_finished) return;
    this.el.rpsBtns.forEach(btn => {
      btn.classList.toggle("selected", btn.dataset.choice === choice);
    });
    this.sendAction("pick", { choice: choice });
  }

  restartGame() {
    this.sendAction("restart");
  }

  returnToLobby() {
    this.sendAction("lobby");
  }

  returnToHub() {
    this.sendAction("return_to_hub");
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

  renderHubPlayers() {
    if (!this.el.hubPlayersList) return;
    const players = (this.gameState?.players || []).filter(p => !p.is_bot);
    const count = Math.max(1, players.length);
    if (this.el.hubPlayerCount) {
      this.el.hubPlayerCount.textContent = `${count}/2`;
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
          ${isHost ? '<span class="lobby-tag-host">Host 👑</span>' : '<span style="font-size:0.75rem; color:#94a3b8;">Verbunden</span>'}
        </div>
      `;
    });
    this.el.hubPlayersList.innerHTML = html;
  }

  renderLobbyPlayers() {
    if (!this.el.lobbyPlayersList) return;
    const players = (this.gameState?.players || []).filter(p => !p.is_bot);
    const count = Math.max(1, players.length);
    if (this.el.playerCountBadge) {
      this.el.playerCountBadge.textContent = `${count}/2`;
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

    // View Navigation Logic
    if (state.is_hub) {
      this.el.hubView.style.display = "block";
      this.el.lobbyView.style.display = "none";
      this.el.gameView.style.display = "none";
      this.renderHubGames();
      this.renderHubPlayers();
      return;
    }

    if (!state.is_started) {
      this.el.hubView.style.display = "none";
      this.el.lobbyView.style.display = "block";
      this.el.gameView.style.display = "none";

      // Configure Lobby view for selected game
      const gameType = state.game_type || "tictactoe";
      const gameNames = { tictactoe: "Tic-Tac-Toe", connect4: "Vier Gewinnt", rps: "Schere Stein Papier" };
      const title = gameNames[gameType] || "Spiel";
      this.el.selectedGameBadge.textContent = title;
      this.el.lobbyGameTitle.textContent = title;

      if (gameType === "rps") {
        this.el.diffContainer.style.display = "none";
        this.el.rpsRoundsContainer.style.display = "block";
      } else {
        this.el.rpsRoundsContainer.style.display = "none";
        if (this.selectedMode === "bot") {
          this.el.diffContainer.style.display = "block";
        }
      }

      this.renderLobbyPlayers();
      this.updateLobbyControls();
      return;
    }

    // Active Game View
    this.el.hubView.style.display = "none";
    this.el.lobbyView.style.display = "none";
    this.el.gameView.style.display = "flex";

    const gameType = state.game_type;
    const players = state.players || [];
    const p1 = players[0] || { display_name: "Warten...", user_id: "" };
    const p2 = players[1] || { display_name: "Warten auf Gegner...", user_id: "" };

    // Scoreboard header
    this.el.p1Name.textContent = p1.display_name || p1.username;
    this.el.p1Avatar.src = p1.avatar_url || "https://cdn.discordapp.com/embed/avatars/0.png";
    this.el.p1Score.textContent = `${state.scores?.[p1.user_id] || 0} Siege`;

    this.el.p2Name.textContent = p2.display_name || p2.username;
    this.el.p2Avatar.src = p2.avatar_url || (p2.is_bot ? "/static/images/tanjun_avatar.png" : "https://cdn.discordapp.com/embed/avatars/1.png");
    this.el.p2Score.textContent = `${state.scores?.[p2.user_id] || 0} Siege`;

    // Active turn highlight
    if (gameType !== "rps") {
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
    } else {
      this.el.p1Card.classList.remove("turn-active");
      this.el.p2Card.classList.remove("turn-active");
    }

    // Symbol tags
    if (gameType === "tictactoe") {
      this.el.p1Tag.textContent = "X";
      this.el.p1Tag.className = "player-symbol-tag sym-x";
      this.el.p2Tag.textContent = "O";
      this.el.p2Tag.className = "player-symbol-tag sym-o";
    } else if (gameType === "connect4") {
      this.el.p1Tag.textContent = "🔴";
      this.el.p1Tag.className = "player-symbol-tag sym-x";
      this.el.p2Tag.textContent = "🟡";
      this.el.p2Tag.className = "player-symbol-tag sym-o";
    } else if (gameType === "rps") {
      this.el.p1Tag.textContent = "⚔️";
      this.el.p1Tag.className = "player-symbol-tag sym-x";
      this.el.p2Tag.textContent = "⚔️";
      this.el.p2Tag.className = "player-symbol-tag sym-o";
    }

    // Switch visible board container
    this.el.tttBoardContainer.style.display = gameType === "tictactoe" ? "flex" : "none";
    this.el.c4BoardContainer.style.display = gameType === "connect4" ? "flex" : "none";
    this.el.rpsBoardContainer.style.display = gameType === "rps" ? "flex" : "none";

    // ── Render Tic-Tac-Toe ──
    if (gameType === "tictactoe") {
      const winningLine = state.winning_line || [];
      state.board.forEach((val, idx) => {
        const cell = this.el.tttCells[idx];
        cell.textContent = val;
        cell.className = "cell";
        if (val === "X") cell.classList.add("cell-x", "taken");
        if (val === "O") cell.classList.add("cell-o", "taken");
        if (winningLine.includes(idx)) cell.classList.add("winner-cell");
      });
    }

    // ── Render Connect 4 ──
    if (gameType === "connect4") {
      const winningLine = state.winning_line || [];
      const cells = this.el.c4Grid.querySelectorAll(".c4-cell");
      state.board.forEach((val, idx) => {
        const cell = cells[idx];
        if (cell) {
          cell.className = "c4-cell";
          if (val === "R") cell.classList.add("chip-r");
          if (val === "Y") cell.classList.add("chip-y");
          if (winningLine.includes(idx)) cell.classList.add("winner-cell");
        }
      });
    }

    // ── Render Rock-Paper-Scissors ──
    if (gameType === "rps") {
      const emojis = { rock: "✊", paper: "✋", scissors: "✌️", locked: "🔒", "": "❓" };
      this.el.rpsRoundBadge.textContent = `Runde ${state.current_round} (Ziel: ${state.target_wins} Siege)`;

      const picks = state.current_picks || {};
      const myPick = picks[this.user.id] || "";
      const otherId = p1.user_id === this.user.id ? p2.user_id : p1.user_id;
      const otherPick = picks[otherId] || "";

      this.el.rpsP1Pick.textContent = emojis[myPick] || "❓";
      this.el.rpsP2Pick.textContent = emojis[otherPick] || "❓";

      this.el.rpsP1Label.textContent = this.user.displayName;
      this.el.rpsP2Label.textContent = p1.user_id === this.user.id ? (p2.display_name || p2.username) : (p1.display_name || p1.username);

      if (state.last_round_result) {
        const lr = state.last_round_result;
        if (lr.winner === "draw") {
          this.el.rpsRoundResult.textContent = `Gleichstand in Runde ${lr.round}!`;
          this.el.rpsRoundResult.style.color = "#ffb703";
        } else {
          const wName = lr.winner === this.user.id ? "Du hast" : "Gegner hat";
          this.el.rpsRoundResult.textContent = `🎉 ${wName} Runde ${lr.round} gewonnen!`;
          this.el.rpsRoundResult.style.color = lr.winner === this.user.id ? "#00f2fe" : "#ff4b4b";
        }
      } else if (myPick && !otherPick) {
        this.el.rpsRoundResult.textContent = "Wahl eingeloggt! Warte auf Gegner...";
        this.el.rpsRoundResult.style.color = "#ffb703";
      } else {
        this.el.rpsRoundResult.textContent = "Wähle deine Geste!";
        this.el.rpsRoundResult.style.color = "#94a3b8";
      }
    }

    // ── In-game Status Bar Text ──
    if (state.is_finished) {
      if (state.winner === "draw") {
        this.el.statusBar.textContent = "🤝 Unentschieden! Großartiges Match.";
        this.el.statusBar.style.color = "#ffb703";
      } else {
        const winnerObj = players.find(p => p.user_id === state.winner);
        const name = winnerObj ? (winnerObj.display_name || winnerObj.username) : state.winner;
        this.el.statusBar.textContent = `🎉 ${name} gewinnt das Match!`;
        this.el.statusBar.style.color = "#00f2fe";
      }
    } else if (state.is_started) {
      if (gameType === "rps") {
        this.el.statusBar.textContent = "⚡ Wähle Stein, Papier oder Schere!";
        this.el.statusBar.style.color = "#00f2fe";
      } else if (state.current_turn === this.user.id) {
        this.el.statusBar.textContent = "⚡ Du bist am Zug! Setze deinen Zug.";
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
