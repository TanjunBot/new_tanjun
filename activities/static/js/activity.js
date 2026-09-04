/**
 * Tanjun Discord Activity Client Application
 * Supports Discord Embedded App SDK & Fallback Standalone / Browser mode.
 */

class TanjunActivityClient {
  constructor() {
    this.discordSdk = null;
    this.auth = null;
    this.user = {
      id: "guest_" + Math.floor(Math.random() * 10000),
      username: "Guest",
      displayName: "Guest Player",
      avatarUrl: "https://cdn.discordapp.com/embed/avatars/0.png"
    };
    this.sessionId = null;
    this.ws = null;
    this.gameState = null;
    this.selectedMode = "bot"; // "bot" or "pvp"
    this.selectedDifficulty = 3;

    this.initElements();
    this.setupEventListeners();
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
      pill.addEventListener("click", (e) => {
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
    this.el.leaveBtn.addEventListener("click", () => this.leaveSession());
  }

  async init() {
    const urlParams = new URLSearchParams(window.location.search);
    const paramSession = urlParams.get("session") || urlParams.get("instance_id");

    // Initialize Discord Embedded App SDK if available in window
    if (window.DiscordSDK) {
      try {
        const configResp = await fetch("/api/config");
        const config = await configResp.json();
        this.discordSdk = new window.DiscordSDK(config.client_id);
        await this.discordSdk.ready();

        // Authorize with Discord Client
        const { code } = await this.discordSdk.commands.authorize({
          client_id: config.client_id,
          response_type: "code",
          state: "",
          prompt: "none",
          scope: ["identify", "guilds"]
        });

        // Set user info if Discord SDK instance provides it
        if (this.discordSdk.instanceId) {
          this.sessionId = this.discordSdk.instanceId;
        }
      } catch (err) {
        console.warn("Discord SDK initialization skipped/running in web mode:", err);
      }
    }

    // Populate user UI
    this.el.usernameDisplay.textContent = this.user.displayName;
    this.el.userAvatar.src = this.user.avatarUrl;

    if (paramSession) {
      this.sessionId = paramSession;
      this.connectWebSocket();
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
  }

  async startGameSession() {
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
        // Send initial start action
        this.sendAction("start", {
          mode: this.selectedMode,
          difficulty: this.selectedDifficulty
        });
      });
    } catch (e) {
      console.error("Failed to create session:", e);
      alert("Fehler beim Erstellen der Sitzung.");
      this.el.startBtn.disabled = false;
      this.el.startBtn.textContent = "Spiel Starten";
    }
  }

  connectWebSocket(onOpenCallback) {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws/${this.sessionId}`;

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      // Send join
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
        if (msg.type === "state_update" || msg.type === "joined") {
          this.handleStateUpdate(msg.state);
        }
      } catch (err) {
        console.error("Error parsing WS message:", err);
      }
    };

    this.ws.onclose = () => {
      console.log("WebSocket disconnected");
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

  leaveSession() {
    if (this.ws) {
      this.ws.close();
    }
    this.el.lobbyView.style.display = "block";
    this.el.gameView.style.display = "none";
    this.el.startBtn.disabled = false;
    this.el.startBtn.textContent = "Spiel Starten";
  }

  handleStateUpdate(state) {
    this.gameState = state;

    this.el.lobbyView.style.display = "none";
    this.el.gameView.style.display = "flex";

    // Update scoreboard
    const players = state.players || [];
    const p1 = players[0] || { display_name: "Warten...", user_id: "" };
    const p2 = players[1] || { display_name: "Warten auf Gegner...", user_id: "" };

    this.el.p1Name.textContent = p1.display_name;
    this.el.p1Avatar.src = p1.avatar_url || "https://cdn.discordapp.com/embed/avatars/0.png";
    this.el.p1Score.textContent = `${state.scores?.[p1.user_id] || 0} Siege`;

    this.el.p2Name.textContent = p2.display_name;
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

    // Status text
    if (state.is_finished) {
      if (state.winner === "draw") {
        this.el.statusBar.textContent = "Unentschieden! Niemand gewinnt.";
        this.el.statusBar.style.color = "#ffb703";
      } else {
        const winnerObj = players.find(p => p.user_id === state.winner);
        const name = winnerObj ? winnerObj.display_name : state.winner;
        this.el.statusBar.textContent = `🎉 ${name} gewinnt das Spiel!`;
        this.el.statusBar.style.color = "#00f2fe";
      }
    } else if (state.is_started) {
      if (state.current_turn === this.user.id) {
        this.el.statusBar.textContent = "⚡ Du bist am Zug! Setze dein Zeichen.";
        this.el.statusBar.style.color = "#00f2fe";
      } else {
        const currObj = players.find(p => p.user_id === state.current_turn);
        const name = currObj ? currObj.display_name : "Gegner";
        this.el.statusBar.textContent = `⏳ ${name} überlegt...`;
        this.el.statusBar.style.color = "#94a3b8";
      }
    } else {
      this.el.statusBar.textContent = "Warte auf Mitspieler...";
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  window.app = new TanjunActivityClient();
  window.app.init();
});
