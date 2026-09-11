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
    this.selectedFirstTurn = "host"; // "host", "random", "guest"
    this.selectedC4Rows = 6;
    this.selectedC4Cols = 7;
    this.selectedC4Connect = 4;
    this.selectedRpsVariation = "classic";
    this.currentC4Cols = 0;
    this.currentC4Rows = 0;
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

      // Game Settings Elements
      gameSettingsContainer: document.getElementById("gameSettingsContainer"),
      c4Settings: document.getElementById("c4Settings"),
      c4SizeLabel: document.getElementById("c4SizeLabel"),
      c4SizePills: document.querySelectorAll("#c4SizePills .diff-pill"),
      c4ConnectLabel: document.getElementById("c4ConnectLabel"),
      c4ConnectPills: document.querySelectorAll("#c4ConnectPills .diff-pill"),
      rpsSettings: document.getElementById("rpsSettings"),
      rpsRoundsLabel: document.getElementById("rpsRoundsLabel"),
      rpsRoundsPills: document.querySelectorAll("#rpsRoundsPills .diff-pill"),
      rpsVarLabel: document.getElementById("rpsVarLabel"),
      rpsVarPills: document.querySelectorAll("#rpsVarPills .diff-pill"),
      turnOrderContainer: document.getElementById("turnOrderContainer"),
      firstTurnLabel: document.getElementById("firstTurnLabel"),
      firstTurnPills: document.querySelectorAll("#firstTurnPills .diff-pill"),
      diffContainer: document.getElementById("diffContainer"),
      diffLabel: document.getElementById("diffLabel"),
      botDiffPills: document.querySelectorAll("#botDiffPills .diff-pill"),
      rpsExtendedBtns: document.querySelectorAll(".rps-extended"),

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
  }

  setupEventListeners() {
    // Mode toggles
    this.el.modeBotBtn.addEventListener("click", () => this.setMode("bot"));
    this.el.modePvpBtn.addEventListener("click", () => this.setMode("pvp"));

    // Connect 4 Grid Size
    this.el.c4SizePills.forEach(pill => {
      pill.addEventListener("click", () => {
        if (!this.isHost()) return;
        this.el.c4SizePills.forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
        this.selectedC4Rows = parseInt(pill.dataset.c4Rows, 10) || 6;
        this.selectedC4Cols = parseInt(pill.dataset.c4Cols, 10) || 7;
        if (this.el.c4SizeLabel) this.el.c4SizeLabel.textContent = pill.textContent;
        this.broadcastSettings();
      });
    });

    // Connect 4 Target in a Row
    this.el.c4ConnectPills.forEach(pill => {
      pill.addEventListener("click", () => {
        if (!this.isHost()) return;
        this.el.c4ConnectPills.forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
        this.selectedC4Connect = parseInt(pill.dataset.c4Connect, 10) || 4;
        if (this.el.c4ConnectLabel) this.el.c4ConnectLabel.textContent = pill.textContent;
        this.broadcastSettings();
      });
    });

    // RPS Rounds
    this.el.rpsRoundsPills.forEach(pill => {
      pill.addEventListener("click", () => {
        if (!this.isHost()) return;
        this.el.rpsRoundsPills.forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
        this.selectedRpsRounds = parseInt(pill.dataset.rpsRounds, 10) || 3;
        if (this.el.rpsRoundsLabel) this.el.rpsRoundsLabel.textContent = pill.textContent;
        this.broadcastSettings();
      });
    });

    // RPS Variation (Classic vs Lizard & Spock)
    this.el.rpsVarPills.forEach(pill => {
      pill.addEventListener("click", () => {
        if (!this.isHost()) return;
        this.el.rpsVarPills.forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
        this.selectedRpsVariation = pill.dataset.rpsVar || "classic";
        if (this.el.rpsVarLabel) this.el.rpsVarLabel.textContent = pill.textContent;
        this.broadcastSettings();
      });
    });

    // Turn Order
    this.el.firstTurnPills.forEach(pill => {
      pill.addEventListener("click", () => {
        if (!this.isHost()) return;
        this.el.firstTurnPills.forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
        this.selectedFirstTurn = pill.dataset.firstTurn || "host";
        if (this.el.firstTurnLabel) this.el.firstTurnLabel.textContent = pill.textContent;
        this.broadcastSettings();
      });
    });

    // Bot Difficulty
    this.el.botDiffPills.forEach(pill => {
      pill.addEventListener("click", () => {
        if (!this.isHost()) return;
        this.el.botDiffPills.forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
        this.selectedDifficulty = parseInt(pill.dataset.diff, 10) || 3;
        const diffNames = { 1: "1 (Leicht)", 2: "2", 3: "3 (Normal)", 4: "4", 5: "5 (Meister)" };
        if (this.el.diffLabel) this.el.diffLabel.textContent = diffNames[this.selectedDifficulty] || `Stufe ${this.selectedDifficulty}`;
        this.broadcastSettings();
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

  isHost() {
    const players = this.gameState?.players || [this.user];
    return !this.gameState || players[0]?.user_id === this.user.id;
  }

  broadcastSettings() {
    if (!this.isHost()) return;
    this.sendAction("update_settings", {
      mode: this.selectedMode,
      difficulty: this.selectedDifficulty,
      first_turn: this.selectedFirstTurn,
      rows: this.selectedC4Rows,
      cols: this.selectedC4Cols,
      connect: this.selectedC4Connect,
      target_wins: this.selectedRpsRounds,
      variation: this.selectedRpsVariation
    });
  }

  applyLobbySettings(s) {
    if (!s) return;
    if (s.mode) {
      this.selectedMode = s.mode;
      this.el.modeBotBtn.classList.toggle("active", s.mode === "bot");
      this.el.modePvpBtn.classList.toggle("active", s.mode === "pvp");
      if (this.el.diffContainer) {
        this.el.diffContainer.style.display = s.mode === "bot" ? "block" : "none";
      }
    }
    if (s.difficulty) {
      this.selectedDifficulty = s.difficulty;
      this.el.botDiffPills.forEach(p => p.classList.toggle("active", parseInt(p.dataset.diff, 10) === s.difficulty));
      const diffNames = { 1: "1 (Leicht)", 2: "2", 3: "3 (Normal)", 4: "4", 5: "5 (Meister)" };
      if (this.el.diffLabel) this.el.diffLabel.textContent = diffNames[s.difficulty] || `Stufe ${s.difficulty}`;
    }
    if (s.first_turn) {
      this.selectedFirstTurn = s.first_turn;
      this.el.firstTurnPills.forEach(p => {
        const isActive = p.dataset.firstTurn === s.first_turn;
        p.classList.toggle("active", isActive);
        if (isActive && this.el.firstTurnLabel) this.el.firstTurnLabel.textContent = p.textContent;
      });
    }
    if (s.rows && s.cols) {
      this.selectedC4Rows = s.rows;
      this.selectedC4Cols = s.cols;
      this.el.c4SizePills.forEach(p => {
        const isActive = parseInt(p.dataset.c4Rows, 10) === s.rows && parseInt(p.dataset.c4Cols, 10) === s.cols;
        p.classList.toggle("active", isActive);
        if (isActive && this.el.c4SizeLabel) this.el.c4SizeLabel.textContent = p.textContent;
      });
    }
    if (s.connect) {
      this.selectedC4Connect = s.connect;
      this.el.c4ConnectPills.forEach(p => {
        const isActive = parseInt(p.dataset.c4Connect, 10) === s.connect;
        p.classList.toggle("active", isActive);
        if (isActive && this.el.c4ConnectLabel) this.el.c4ConnectLabel.textContent = p.textContent;
      });
    }
    if (s.target_wins) {
      this.selectedRpsRounds = s.target_wins;
      this.el.rpsRoundsPills.forEach(p => {
        const isActive = parseInt(p.dataset.rpsRounds, 10) === s.target_wins;
        p.classList.toggle("active", isActive);
        if (isActive && this.el.rpsRoundsLabel) this.el.rpsRoundsLabel.textContent = p.textContent;
      });
    }
    if (s.variation) {
      this.selectedRpsVariation = s.variation;
      this.el.rpsVarPills.forEach(p => {
        const isActive = p.dataset.rpsVar === s.variation;
        p.classList.toggle("active", isActive);
        if (isActive && this.el.rpsVarLabel) this.el.rpsVarLabel.textContent = p.textContent;
      });
    }
  }

  setMode(mode) {
    if (!this.isHost()) return;
    this.selectedMode = mode;
    this.el.modeBotBtn.classList.toggle("active", mode === "bot");
    this.el.modePvpBtn.classList.toggle("active", mode === "pvp");
    if (this.el.diffContainer) {
      this.el.diffContainer.style.display = mode === "bot" ? "block" : "none";
    }
    this.broadcastSettings();
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
        first_turn: this.selectedFirstTurn,
        rows: this.selectedC4Rows,
        cols: this.selectedC4Cols,
        connect: this.selectedC4Connect,
        target_wins: this.selectedRpsRounds,
        variation: this.selectedRpsVariation
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
    const isHost = this.isHost();
    const humanPlayers = players.filter(p => !p.is_bot);

    // Disable settings interactions for guests
    const allPills = document.querySelectorAll(".game-settings-container .diff-pill");
    allPills.forEach(p => p.classList.toggle("disabled", !isHost));
    if (this.el.modeBotBtn) this.el.modeBotBtn.classList.toggle("disabled", !isHost);
    if (this.el.modePvpBtn) this.el.modePvpBtn.classList.toggle("disabled", !isHost);

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

  renderHubGames() {
    if (!this.el.gamesGrid) return;
    const games = this.gameState?.available_games || this.availableGames || [];
    let html = "";
    games.forEach(g => {
      html += `
        <div class="game-hub-card" data-game="${g.type}">
          <div class="game-card-icon">${g.icon || '🎮'}</div>
          <div class="game-card-body">
            <div class="game-card-top">
              <span class="game-card-title">${g.name}</span>
              <span class="game-card-tag">${g.badge || 'Spiel'}</span>
            </div>
            <div class="game-card-desc">${g.description}</div>
          </div>
          <div class="game-card-arrow">▶</div>
        </div>
      `;
    });
    this.el.gamesGrid.innerHTML = html;

    this.el.gamesGrid.querySelectorAll(".game-hub-card").forEach(card => {
      card.addEventListener("click", () => {
        const gameType = card.dataset.game;
        this.selectGame(gameType);
      });
    });
  }

  selectGame(gameType) {
    this.sendAction("select_game", { game_type: gameType });
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

      // Sync settings from server if available (e.g. for guest)
      if (state.lobby_settings) {
        this.applyLobbySettings(state.lobby_settings);
      }

      // Settings visibility per game
      if (this.el.c4Settings) {
        this.el.c4Settings.style.display = gameType === "connect4" ? "block" : "none";
      }
      if (this.el.rpsSettings) {
        this.el.rpsSettings.style.display = gameType === "rps" ? "block" : "none";
      }
      if (this.el.turnOrderContainer) {
        this.el.turnOrderContainer.style.display = (gameType === "connect4" || gameType === "tictactoe") ? "block" : "none";
      }
      if (this.el.diffContainer) {
        this.el.diffContainer.style.display = this.selectedMode === "bot" ? "block" : "none";
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

    // ── Render Connect 4 (Dynamic Grid) ──
    if (gameType === "connect4") {
      const rows = state.rows || 6;
      const cols = state.cols || 7;
      const totalCells = rows * cols;

      if (this.currentC4Cols !== cols || this.currentC4Rows !== rows || this.el.c4Grid.children.length !== totalCells) {
        this.currentC4Cols = cols;
        this.currentC4Rows = rows;

        // Dynamic responsive cell size
        const availableWidth = Math.min(window.innerWidth - 40, 460);
        const cellSize = Math.floor(Math.min(42, Math.max(26, (availableWidth - (cols * 6) - 20) / cols)));
        this.el.c4Grid.style.setProperty("--c4-cols", cols);
        this.el.c4Grid.style.setProperty("--c4-rows", rows);
        this.el.c4Grid.style.setProperty("--c4-cell-size", `${cellSize}px`);

        this.el.c4DropRow.style.setProperty("--c4-cols", cols);
        this.el.c4DropRow.style.setProperty("--c4-cell-size", `${cellSize}px`);

        // Rebuild drop row buttons
        this.el.c4DropRow.innerHTML = "";
        for (let c = 0; c < cols; c++) {
          const btn = document.createElement("button");
          btn.className = "c4-drop-btn";
          btn.dataset.col = c;
          btn.textContent = "▼";
          btn.addEventListener("click", () => this.makeMoveConnect4(c));
          this.el.c4DropRow.appendChild(btn);
        }

        // Rebuild cells
        this.el.c4Grid.innerHTML = "";
        for (let i = 0; i < totalCells; i++) {
          const cell = document.createElement("div");
          cell.className = "c4-cell";
          cell.dataset.index = i;
          const col = i % cols;
          cell.addEventListener("click", () => this.makeMoveConnect4(col));
          this.el.c4Grid.appendChild(cell);
        }
      }

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
      const isLizardSpock = state.variation === "lizard_spock";
      if (this.el.rpsExtendedBtns) {
        this.el.rpsExtendedBtns.forEach(btn => {
          btn.style.display = isLizardSpock ? "flex" : "none";
        });
      }

      const emojis = { rock: "✊", paper: "✋", scissors: "✌️", lizard: "🦎", spock: "🖖", locked: "🔒", "": "❓" };
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
        this.el.rpsRoundResult.textContent = isLizardSpock ? "Wähle deine Geste (5 zur Auswahl)!" : "Wähle deine Geste!";
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
