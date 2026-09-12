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

    // Tournament client state
    this.selectedTourneyFormat = "points";
    this.selectedTourneyStyle = "spectated";
    this.selectedTourneyGame = "connect4";
    this.selectedTourneyRounds = 3;
    this.renderedCheerCount = 0;
    this.currentTourneyC4Rows = 0;
    this.currentTourneyC4Cols = 0;

    // Previous board trackers for drop, pop, and shake animations
    this.prevTTTBoard = null;
    this.prevC4Board = null;
    this.prevTourneyTTTBoard = null;
    this.prevTourneyC4Board = null;
    this.prevRpsRound = null;
    this.prevRpsFinished = null;
    this.prevTourneyRpsRound = null;

    this.inTournamentView = false;
    this.selectedNextRoundGame = "connect4";
    this.soundEnabled = localStorage.getItem("tanjun_sound_enabled") !== "false";
    this.audioCtx = null;
    this.prevGameFinished = false;
    this.prevCountdownSec = null;

    // Available games list (fallback if not yet received from WS)
    this.availableGames = [
      {
        type: "connect4",
        name: "Vier Gewinnt",
        description: "Taktisches 7x6 Raster. Wirf deine Chips ein und bilde eine 4er-Reihe!",
        icon: "🔴🟡",
        badge: "Taktik"
      },
      {
        type: "tictactoe",
        name: "Tic-Tac-Toe",
        description: "Klassisches 3x3 Duell. Wer zuerst drei Symbole in einer Reihe hat, gewinnt!",
        icon: "❌⭕",
        badge: "Klassiker"
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

  initAudio() {
    if (!this.audioCtx && (window.AudioContext || window.webkitAudioContext)) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.audioCtx = new AudioCtx();
    }
    if (this.audioCtx && this.audioCtx.state === "suspended") {
      this.audioCtx.resume().catch(() => {});
    }
  }

  toggleSound() {
    this.soundEnabled = !this.soundEnabled;
    localStorage.setItem("tanjun_sound_enabled", this.soundEnabled ? "true" : "false");
    if (this.el.soundToggleBtn) {
      this.el.soundToggleBtn.textContent = this.soundEnabled ? "🔊" : "🔇";
    }
    if (this.soundEnabled) {
      this.playPop();
    }
  }

  playPop() {
    if (!this.soundEnabled) return;
    try {
      this.initAudio();
      if (!this.audioCtx) return;
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(520, this.audioCtx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(320, this.audioCtx.currentTime + 0.08);
      gain.gain.setValueAtTime(0.18, this.audioCtx.currentTime);
      gain.gain.linearRampToValueAtTime(0.01, this.audioCtx.currentTime + 0.08);
      osc.connect(gain);
      gain.connect(this.audioCtx.destination);
      osc.start();
      osc.stop(this.audioCtx.currentTime + 0.09);
    } catch (e) {}
  }

  playDrop() {
    if (!this.soundEnabled) return;
    try {
      this.initAudio();
      if (!this.audioCtx) return;
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      osc.type = "triangle";
      osc.frequency.setValueAtTime(240, this.audioCtx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(80, this.audioCtx.currentTime + 0.12);
      gain.gain.setValueAtTime(0.25, this.audioCtx.currentTime);
      gain.gain.linearRampToValueAtTime(0.01, this.audioCtx.currentTime + 0.12);
      osc.connect(gain);
      gain.connect(this.audioCtx.destination);
      osc.start();
      osc.stop(this.audioCtx.currentTime + 0.13);
    } catch (e) {}
  }

  playClash() {
    if (!this.soundEnabled) return;
    try {
      this.initAudio();
      if (!this.audioCtx) return;
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      osc.type = "sawtooth";
      osc.frequency.setValueAtTime(440, this.audioCtx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(220, this.audioCtx.currentTime + 0.15);
      gain.gain.setValueAtTime(0.14, this.audioCtx.currentTime);
      gain.gain.linearRampToValueAtTime(0.01, this.audioCtx.currentTime + 0.15);
      osc.connect(gain);
      gain.connect(this.audioCtx.destination);
      osc.start();
      osc.stop(this.audioCtx.currentTime + 0.16);
    } catch (e) {}
  }

  playWin() {
    if (!this.soundEnabled) return;
    try {
      this.initAudio();
      if (!this.audioCtx) return;
      const notes = [261.63, 329.63, 392.00, 523.25];
      notes.forEach((freq, idx) => {
        const osc = this.audioCtx.createOscillator();
        const gain = this.audioCtx.createGain();
        const startTime = this.audioCtx.currentTime + idx * 0.1;
        osc.type = "triangle";
        osc.frequency.setValueAtTime(freq, startTime);
        gain.gain.setValueAtTime(0.16, startTime);
        gain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.35);
        osc.connect(gain);
        gain.connect(this.audioCtx.destination);
        osc.start(startTime);
        osc.stop(startTime + 0.36);
      });
    } catch (e) {}
  }

  playCheer() {
    if (!this.soundEnabled) return;
    try {
      this.initAudio();
      if (!this.audioCtx) return;
      const freqs = [587.33, 880.0];
      freqs.forEach((freq, idx) => {
        const osc = this.audioCtx.createOscillator();
        const gain = this.audioCtx.createGain();
        const startTime = this.audioCtx.currentTime + idx * 0.08;
        osc.type = "sine";
        osc.frequency.setValueAtTime(freq, startTime);
        gain.gain.setValueAtTime(0.12, startTime);
        gain.gain.linearRampToValueAtTime(0.01, startTime + 0.18);
        osc.connect(gain);
        gain.connect(this.audioCtx.destination);
        osc.start(startTime);
        osc.stop(startTime + 0.19);
      });
    } catch (e) {}
  }

  playCountdown() {
    if (!this.soundEnabled) return;
    try {
      this.initAudio();
      if (!this.audioCtx) return;
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(780, this.audioCtx.currentTime);
      gain.gain.setValueAtTime(0.15, this.audioCtx.currentTime);
      gain.gain.linearRampToValueAtTime(0.01, this.audioCtx.currentTime + 0.07);
      osc.connect(gain);
      gain.connect(this.audioCtx.destination);
      osc.start();
      osc.stop(this.audioCtx.currentTime + 0.08);
    } catch (e) {}
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
      display_name: storedUserName,
      avatarUrl: "https://cdn.discordapp.com/embed/avatars/0.png",
      avatar_url: "https://cdn.discordapp.com/embed/avatars/0.png"
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
      hubTourneyBanner: document.getElementById("hubTourneyBanner"),
      hubTourneyTitle: document.getElementById("hubTourneyTitle"),
      hubTourneyDesc: document.getElementById("hubTourneyDesc"),
      hubTourneyStatusBadge: document.getElementById("hubTourneyStatusBadge"),
      hubTourneyBtn: document.getElementById("hubTourneyBtn"),

      // Lobby Elements
      backToHubBtn: document.getElementById("backToHubBtn"),
      selectedGameBadge: document.getElementById("selectedGameBadge"),
      lobbyGameTitle: document.getElementById("lobbyGameTitle"),
      lobbyGameSubtitle: document.getElementById("lobbyGameSubtitle"),
      modeBotBtn: document.getElementById("modeBotBtn"),
      modePvpBtn: document.getElementById("modePvpBtn"),
      connectionBanner: document.getElementById("connectionBanner"),

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
      hubBtn: document.getElementById("hubBtn"),

      // Tournament Views & Overlays
      tournamentLobbyView: document.getElementById("tournamentLobbyView"),
      tournamentPodiumView: document.getElementById("tournamentPodiumView"),
      tournamentHud: document.getElementById("tournamentHud"),
      tournamentLeaderboardModal: document.getElementById("tournamentLeaderboardModal"),

      // Tournament HUD Elements
      tourneyHudCupName: document.getElementById("tourneyHudCupName"),
      tourneyHudRoundBadge: document.getElementById("tourneyHudRoundBadge"),
      tourneyHudGameBadge: document.getElementById("tourneyHudGameBadge"),
      tourneyHudMatchRow: document.getElementById("tourneyHudMatchRow"),
      tourneyHudMatchText: document.getElementById("tourneyHudMatchText"),
      tourneyHudUserStats: document.getElementById("tourneyHudUserStats"),
      tourneyHudUserScore: document.getElementById("tourneyHudUserScore"),
      tourneyHudLeaderboardBtn: document.getElementById("tourneyHudLeaderboardBtn"),
      tourneyHudHostBtn: document.getElementById("tourneyHudHostBtn"),

      // Tournament Modal Elements
      tourneyModalRoundInfo: document.getElementById("tourneyModalRoundInfo"),
      tourneyModalCloseBtn: document.getElementById("tourneyModalCloseBtn"),
      tourneyModalCloseBtn2: document.getElementById("tourneyModalCloseBtn2"),
      tourneyModalLeaderboardList: document.getElementById("tourneyModalLeaderboardList"),
      tourneyHostControlsBox: document.getElementById("tourneyHostControlsBox"),
      tourneyRoundEndMsg: document.getElementById("tourneyRoundEndMsg"),
      tourneyNextGamePills: document.querySelectorAll("#tourneyNextGamePills .diff-pill"),
      tourneyNextRoundBtn: document.getElementById("tourneyNextRoundBtn"),
      tourneyNextMatchBtn: document.getElementById("tourneyNextMatchBtn"),
      tourneyModalHistoryList: document.getElementById("tourneyModalHistoryList"),
      tourneyEndEarlyBtn: document.getElementById("tourneyEndEarlyBtn"),
      tourneyCheerBtns: document.querySelectorAll(".tourney-cheer-btn"),
      tourneyCheerOverlay: document.getElementById("tourneyCheerOverlay"),

      // Tournament Lobby Elements
      tourneyBackToHubBtn: document.getElementById("tourneyBackToHubBtn"),
      tourneySettingsContainer: document.getElementById("tourneySettingsContainer"),
      tourneyFormatLabel: document.getElementById("tourneyFormatLabel"),
      tourneyFormatPills: document.querySelectorAll("#tourneyFormatPills .diff-pill"),
      tourneyStyleLabel: document.getElementById("tourneyStyleLabel"),
      tourneyStylePills: document.querySelectorAll("#tourneyStylePills .diff-pill"),
      tourneyGameLabel: document.getElementById("tourneyGameLabel"),
      tourneyGamePills: document.querySelectorAll("#tourneyGamePills .diff-pill"),
      tourneyRoundsGroup: document.getElementById("tourneyRoundsGroup"),
      tourneyRoundsLabel: document.getElementById("tourneyRoundsLabel"),
      tourneyRoundsPills: document.querySelectorAll("#tourneyRoundsPills .diff-pill"),
      tourneyPlayerCountBadge: document.getElementById("tourneyPlayerCountBadge"),
      tourneyPlayersList: document.getElementById("tourneyPlayersList"),
      tourneyLobbyStatusMsg: document.getElementById("tourneyLobbyStatusMsg"),
      tourneyStartBtn: document.getElementById("tourneyStartBtn"),

      // Match Transition Banner Elements
      tourneyMatchTransitionBanner: document.getElementById("tourneyMatchTransitionBanner"),
      tourneyTransitionTitle: document.getElementById("tourneyTransitionTitle"),
      tourneyTransitionSubtitle: document.getElementById("tourneyTransitionSubtitle"),
      tourneyTransitionCountdown: document.getElementById("tourneyTransitionCountdown"),
      tourneyTransitionSkipBtn: document.getElementById("tourneyTransitionSkipBtn"),

      // Rewards Box Elements
      tourneyRewardsBox: document.getElementById("tourneyRewardsBox"),
      tourneyRewardsBadge: document.getElementById("tourneyRewardsBadge"),
      tourneyRewardsContent: document.getElementById("tourneyRewardsContent"),

      // Tournament Podium Elements
      podiumTop3: document.getElementById("podiumTop3"),
      podiumRewardsBanner: document.getElementById("podiumRewardsBanner"),
      podiumRewardsText: document.getElementById("podiumRewardsText"),
      tourneyFinalTable: document.getElementById("tourneyFinalTable"),
      tourneyNewCupBtn: document.getElementById("tourneyNewCupBtn"),
      tourneyPodiumHubBtn: document.getElementById("tourneyPodiumHubBtn"),

      // Audio & Global Overlays
      soundToggleBtn: document.getElementById("soundToggleBtn"),
      globalCheerOverlay: document.getElementById("globalCheerOverlay"),
      tourneyLeaveBtn: document.getElementById("tourneyLeaveBtn")
    };
  }

  setupEventListeners() {
    // Sound toggle
    if (this.el.soundToggleBtn) {
      this.el.soundToggleBtn.textContent = this.soundEnabled ? "🔊" : "🔇";
      this.el.soundToggleBtn.addEventListener("click", () => this.toggleSound());
    }

    // Tournament Leave (lobby)
    if (this.el.tourneyLeaveBtn) {
      this.el.tourneyLeaveBtn.addEventListener("click", () => {
        this.inTournamentView = false;
        this.sendAction("tournament_leave");
        this.returnToHub();
      });
    }

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

    // Hub Tournament Banner Action
    if (this.el.hubTourneyBtn) {
      this.el.hubTourneyBtn.addEventListener("click", () => {
        const tourney = this.gameState?.tournament;
        if (!tourney || tourney.status === "finished") {
          this.inTournamentView = true;
          this.sendAction("create_tournament", {
            username: this.user.username,
            display_name: this.user.displayName,
            avatar_url: this.user.avatarUrl
          });
        } else {
          const isParticipant = tourney.is_participant || (tourney.leaderboard && tourney.leaderboard.some(p => p.user_id === this.user.id));
          if (!isParticipant) {
            this.sendAction("tournament_join", {
              username: this.user.username,
              display_name: this.user.displayName,
              avatar_url: this.user.avatarUrl
            });
          }
          this.inTournamentView = true;
          this.handleStateUpdate(this.gameState);
        }
      });
    }

    // ── Tournament Event Listeners ─────────────────────────────
    if (this.el.tourneyBackToHubBtn) {
      this.el.tourneyBackToHubBtn.addEventListener("click", () => this.returnToHub());
    }

    // Format Pills
    this.el.tourneyFormatPills.forEach(pill => {
      pill.addEventListener("click", () => {
        if (!this.isTournamentHost()) return;
        this.el.tourneyFormatPills.forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
        this.selectedTourneyFormat = pill.dataset.tourneyFormat || "points";
        if (this.el.tourneyFormatLabel) this.el.tourneyFormatLabel.textContent = pill.textContent;
        if (this.el.tourneyRoundsGroup) {
          this.el.tourneyRoundsGroup.style.display = this.selectedTourneyFormat === "points" ? "block" : "none";
        }
        this.broadcastTourneySettings();
      });
    });

    // Style Pills
    this.el.tourneyStylePills.forEach(pill => {
      pill.addEventListener("click", () => {
        if (!this.isTournamentHost()) return;
        this.el.tourneyStylePills.forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
        this.selectedTourneyStyle = pill.dataset.tourneyStyle || "spectated";
        if (this.el.tourneyStyleLabel) this.el.tourneyStyleLabel.textContent = pill.textContent;
        this.broadcastTourneySettings();
      });
    });

    // Game Pills
    this.el.tourneyGamePills.forEach(pill => {
      pill.addEventListener("click", () => {
        if (!this.isTournamentHost()) return;
        this.el.tourneyGamePills.forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
        const val = pill.dataset.tourneyGame || "playlist";
        if (val === "playlist") {
          this.selectedTourneyGameSelection = "playlist";
        } else if (val === "random") {
          this.selectedTourneyGameSelection = "random";
        } else {
          this.selectedTourneyGameSelection = "host_choice";
          this.selectedTourneyGame = val;
        }
        if (this.el.tourneyGameLabel) this.el.tourneyGameLabel.textContent = pill.textContent;
        this.broadcastTourneySettings();
      });
    });

    // Rounds Pills
    this.el.tourneyRoundsPills.forEach(pill => {
      pill.addEventListener("click", () => {
        if (!this.isTournamentHost()) return;
        this.el.tourneyRoundsPills.forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
        this.selectedTourneyRounds = parseInt(pill.dataset.tourneyRounds, 10) || 3;
        if (this.el.tourneyRoundsLabel) this.el.tourneyRoundsLabel.textContent = pill.textContent;
        this.broadcastTourneySettings();
      });
    });

    // Tournament Start
    if (this.el.tourneyStartBtn) {
      this.el.tourneyStartBtn.addEventListener("click", () => {
        if (!this.isTournamentHost()) return;
        this.sendAction("tournament_start", { selected_game: this.selectedTourneyGame });
      });
    }

    // Match Transition Skip Button
    if (this.el.tourneyTransitionSkipBtn) {
      this.el.tourneyTransitionSkipBtn.addEventListener("click", () => {
        if (!this.isTournamentHost()) return;
        this.sendAction("tournament_advance_match");
      });
    }

    // HUD Leaderboard & Host Menu Buttons
    if (this.el.tourneyHudLeaderboardBtn) {
      this.el.tourneyHudLeaderboardBtn.addEventListener("click", () => {
        this.openTournamentLeaderboardModal();
      });
    }
    if (this.el.tourneyHudHostBtn) {
      this.el.tourneyHudHostBtn.addEventListener("click", () => {
        this.openTournamentLeaderboardModal();
      });
    }

    // Modal Close Buttons
    if (this.el.tourneyModalCloseBtn) {
      this.el.tourneyModalCloseBtn.addEventListener("click", () => {
        this.closeTournamentLeaderboardModal();
      });
    }
    if (this.el.tourneyModalCloseBtn2) {
      this.el.tourneyModalCloseBtn2.addEventListener("click", () => {
        this.closeTournamentLeaderboardModal();
      });
    }
    if (this.el.tournamentLeaderboardModal) {
      this.el.tournamentLeaderboardModal.addEventListener("click", (e) => {
        if (e.target === this.el.tournamentLeaderboardModal) {
          this.closeTournamentLeaderboardModal();
        }
      });
    }

    // Cheer Buttons
    this.el.tourneyCheerBtns.forEach(btn => {
      btn.addEventListener("click", () => {
        const emote = btn.dataset.tourneyEmote || "🎉";
        this.sendAction("tournament_cheer", { emote: emote });
      });
    });

    // Next Round Game Selector (Master Choice)
    if (this.el.tourneyNextGamePills) {
      this.el.tourneyNextGamePills.forEach(pill => {
        pill.addEventListener("click", () => {
          if (!this.isTournamentHost()) return;
          this.el.tourneyNextGamePills.forEach(p => p.classList.remove("active"));
          pill.classList.add("active");
          this.selectedNextRoundGame = pill.dataset.tourneyNextGame || "connect4";
        });
      });
    }

    // Next Round Button
    if (this.el.tourneyNextRoundBtn) {
      this.el.tourneyNextRoundBtn.addEventListener("click", () => {
        if (!this.isTournamentHost()) return;
        const nextGame = this.selectedNextRoundGame || this.selectedTourneyGame || "connect4";
        this.sendAction("tournament_next_round", { selected_game: nextGame });
        this.closeTournamentLeaderboardModal();
      });
    }

    // Next Match Button
    if (this.el.tourneyNextMatchBtn) {
      this.el.tourneyNextMatchBtn.addEventListener("click", () => {
        if (!this.isTournamentHost()) return;
        this.sendAction("tournament_next_match");
        this.closeTournamentLeaderboardModal();
      });
    }

    // End Early Button
    if (this.el.tourneyEndEarlyBtn) {
      this.el.tourneyEndEarlyBtn.addEventListener("click", () => {
        if (!this.isTournamentHost()) return;
        if (confirm("Möchtest du das Turnier wirklich beenden?")) {
          this.sendAction("tournament_end");
          this.closeTournamentLeaderboardModal();
        }
      });
    }

    // Leave & Hub Buttons
    if (this.el.tourneyLeaveBtn) {
      this.el.tourneyLeaveBtn.addEventListener("click", () => this.returnToHub());
    }
    if (this.el.tourneyNewCupBtn) {
      this.el.tourneyNewCupBtn.addEventListener("click", () => {
        if (!this.isTournamentHost()) return;
        this.sendAction("tournament_reset_to_lobby");
      });
    }
    if (this.el.tourneyPodiumHubBtn) {
      this.el.tourneyPodiumHubBtn.addEventListener("click", () => this.returnToHub());
    }
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
                        this.user.display_name = this.user.displayName;
                        if (auth.user.avatar) {
                          this.user.avatarUrl = `https://cdn.discordapp.com/avatars/${auth.user.id}/${auth.user.avatar}.png?size=128`;
                          this.user.avatar_url = this.user.avatarUrl;
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

    // Connect to WebSocket if sessionId exists, or create a standalone hub session
    if (this.sessionId || paramSession) {
      this.sessionId = this.sessionId || paramSession;
      this.connectWebSocket();
    } else {
      this.renderHubPlayers();
      this.createStandaloneSession("hub");
    }
  }

  renderHubGames() {
    if (!this.el.gamesGrid) return;

    const games = this.gameState?.available_games || this.availableGames;
    const isHost = this.isHost();

    let html = "";
    games.forEach(g => {
      html += `
        <div class="game-hub-card" data-game="${g.type}">
          <div class="game-card-icon">${g.icon}</div>
          <div class="game-card-body">
            <div class="game-card-top">
              <span class="game-card-title">${this.escapeHtml(g.name)}</span>
              <span class="game-card-tag">${this.escapeHtml(g.badge || 'Spiel')}</span>
            </div>
            <div class="game-card-desc">${this.escapeHtml(g.description)}</div>
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
        const hostPlayer = (this.gameState?.players || []).find(p => p.is_host) || (this.gameState?.players || [])[0];
        const hostName = hostPlayer?.display_name || "Der Host";
        this.el.hubStatusMsg.textContent = `Warte darauf, dass ${hostName} ein Spiel auswählt...`;
        this.el.hubStatusMsg.style.color = "#94a3b8";
      }
    }
  }

  selectGameFromHub(gameType) {
    const isHost = this.isHost();
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
      const res = await fetch("/api/sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          game_type: gameType,
          user_id: this.user.id,
          username: this.user.username,
          display_name: this.user.display_name,
          avatar_url: this.user.avatar_url
        })
      });
      const data = await res.json();
      this.sessionId = data.session_id;
      const newUrl = new URL(window.location.href);
      newUrl.searchParams.set("session", this.sessionId);
      window.history.replaceState({}, "", newUrl.toString());
      this.connectWebSocket();
    } catch (e) {
      console.error("[Discord Activity] Failed to create session:", e);
    }
  }

  escapeHtml(str) {
    if (str === null || str === undefined) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  isHost() {
    if (!this.gameState) return true;
    if (this.gameState.tournament && this.gameState.tournament.host_id) {
      return this.gameState.tournament.host_id === this.user.id;
    }
    const players = this.gameState.players || [];
    const thisPlayer = players.find(p => p.user_id === this.user.id);
    if (thisPlayer) {
      return Boolean(thisPlayer.is_host);
    }
    const spectators = this.gameState.spectators || [];
    const thisSpectator = spectators.find(p => p.user_id === this.user.id);
    if (thisSpectator) {
      return Boolean(thisSpectator.is_host);
    }
    return players.length === 0 || players[0]?.user_id === this.user.id;
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

    if (this.ws) {
      try {
        this.ws.onopen = null;
        this.ws.onmessage = null;
        this.ws.onclose = null;
        this.ws.onerror = null;
        if (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING) {
          this.ws.close();
        }
      } catch (e) {}
    }

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws/${this.sessionId}`;

    try {
      this.ws = new WebSocket(wsUrl);
    } catch (err) {
      console.error("[Discord Activity] WebSocket connection failed:", err);
      if (this.el.connectionBanner) this.el.connectionBanner.style.display = "flex";
      this.reconnectTimer = setTimeout(() => this.connectWebSocket(onOpenCallback), 2000);
      return;
    }

    this.ws.onopen = () => {
      if (this.el.connectionBanner) this.el.connectionBanner.style.display = "none";
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
      if (this.el.connectionBanner) this.el.connectionBanner.style.display = "flex";
      if (this.sessionId) {
        this.reconnectTimer = setTimeout(() => {
          this.connectWebSocket();
        }, 2000);
      }
    };

    this.ws.onerror = () => {
      if (this.el.connectionBanner) this.el.connectionBanner.style.display = "flex";
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

  clearAnimationCaches() {
    this.prevTTTBoard = null;
    this.prevC4Board = null;
    this.prevTourneyTTTBoard = null;
    this.prevTourneyC4Board = null;
    this.prevRpsRound = null;
    this.prevRpsFinished = null;
    this.prevTourneyRpsRound = null;
  }

  restartGame() {
    this.clearAnimationCaches();
    this.sendAction("restart");
  }

  returnToLobby() {
    this.clearAnimationCaches();
    if (this.gameState && this.gameState.is_started && !this.gameState.is_finished && this.gameState.game_mode === "pvp") {
      this.sendAction("forfeit");
    }
    this.sendAction("lobby");
  }

  returnToHub() {
    this.clearAnimationCaches();
    this.inTournamentView = false;
    if (this.el.tournamentLeaderboardModal) this.el.tournamentLeaderboardModal.style.display = "none";
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
            <img class="lobby-player-avatar-small" src="${this.escapeHtml(p.avatar_url || 'https://cdn.discordapp.com/embed/avatars/0.png')}" alt="Avatar">
            <span>${this.escapeHtml(p.display_name || p.username)}</span>
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
      const isHost = p.is_host;
      const isOffline = p.connected === false;
      html += `
        <div class="lobby-player-row">
          <div class="lobby-player-meta">
            <img class="lobby-player-avatar-small" src="${this.escapeHtml(p.avatar_url || 'https://cdn.discordapp.com/embed/avatars/0.png')}" alt="Avatar">
            <span>${this.escapeHtml(p.display_name || p.username)}</span>
            ${isYou ? '<span class="lobby-tag-you">Du</span>' : ''}
          </div>
          ${isOffline ? '<span class="lobby-tag-offline">Getrennt ⚠️</span>' : (isHost ? '<span class="lobby-tag-host">Host 👑</span>' : '<span style="font-size:0.75rem; color:#94a3b8;">Bereit</span>')}
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

    const tourney = state.tournament;
    const isParticipant = tourney && (tourney.is_participant || (tourney.leaderboard && tourney.leaderboard.some(p => p.user_id === this.user.id)));
    const isTourneyActive = tourney && tourney.status !== "finished";

    // ── Update Hub Tournament Banner (Option) ──────────────────
    if (this.el.hubTourneyBanner) {
      if (!isTourneyActive) {
        this.el.hubTourneyBanner.classList.remove("active-tourney");
        if (this.el.hubTourneyStatusBadge) {
          this.el.hubTourneyStatusBadge.textContent = "Bereit";
          this.el.hubTourneyStatusBadge.className = "tourney-status-pill";
        }
        if (this.el.hubTourneyTitle) this.el.hubTourneyTitle.textContent = "Tanjun Voice Cup";
        if (this.el.hubTourneyDesc) this.el.hubTourneyDesc.textContent = "Veranstalte ein Turnier über mehrere, unterschiedliche Spiele mit automatischer Spielzuteilung & Gesamtrangliste!";
        if (this.el.hubTourneyBtn) this.el.hubTourneyBtn.textContent = "🏆 Turnier starten";
      } else {
        this.el.hubTourneyBanner.classList.add("active-tourney");
        if (this.el.hubTourneyStatusBadge) {
          this.el.hubTourneyStatusBadge.textContent = tourney.status === "lobby" ? "Offene Lobby" : `Runde ${tourney.current_round}/${tourney.total_rounds}`;
          this.el.hubTourneyStatusBadge.className = "tourney-status-pill live";
        }
        if (this.el.hubTourneyTitle) this.el.hubTourneyTitle.textContent = tourney.title || "Tanjun Voice Cup";
        const hostName = tourney.host_name || "Host";
        const pCount = tourney.participants_count || 1;
        if (this.el.hubTourneyDesc) this.el.hubTourneyDesc.textContent = `Turnierleiter: ${hostName} • ${pCount} Teilnehmer • Format: ${tourney.format === "knockout" ? "K.O." : "Mehrkampf"}`;
        if (this.el.hubTourneyBtn) {
          this.el.hubTourneyBtn.textContent = isParticipant ? "▶ Zurück zum Turnier" : "🎟️ Turnier beitreten";
        }
      }
    }

    // Automatically transition joined participants into active tournament rounds
    if (tourney && isParticipant && (tourney.status === "active" || tourney.status === "round_end")) {
      this.inTournamentView = true;
    }

    // ── Route to Tournament Screens if User is Active in Tournament ──
    if (this.inTournamentView && tourney && (isParticipant || tourney.host_id === this.user.id)) {
      if (this.el.hubView) this.el.hubView.style.display = "none";
      if (this.el.lobbyView) this.el.lobbyView.style.display = "none";

      if (tourney.status === "lobby") {
        if (this.el.gameView) this.el.gameView.style.display = "none";
        if (this.el.tournamentHud) this.el.tournamentHud.style.display = "none";
        if (this.el.tournamentLobbyView) this.el.tournamentLobbyView.style.display = "block";
        if (this.el.tournamentPodiumView) this.el.tournamentPodiumView.style.display = "none";
        if (this.el.tournamentLeaderboardModal) this.el.tournamentLeaderboardModal.style.display = "none";
        this.renderTournamentLobby(tourney);
        return;
      } else if (tourney.status === "active" || tourney.status === "round_end") {
        if (this.el.tournamentLobbyView) this.el.tournamentLobbyView.style.display = "none";
        if (this.el.tournamentPodiumView) this.el.tournamentPodiumView.style.display = "none";
        if (this.el.tournamentHud) this.el.tournamentHud.style.display = "flex";
        this.renderTournamentHud(tourney);

        // Render Match Transition Countdown Banner
        if (tourney.transition_info && tourney.transition_info.active) {
          if (this.el.tourneyMatchTransitionBanner) {
            this.el.tourneyMatchTransitionBanner.style.display = "flex";
            const info = tourney.transition_info;
            const gameNames = { connect4: "Vier Gewinnt", tictactoe: "Tic-Tac-Toe", rps: "Schere-Stein-Papier" };
            const nextGameStr = gameNames[info.next_game] || info.next_game || "";
            if (this.el.tourneyTransitionTitle) {
              const prevW = info.prev_winner === "draw" ? "Unentschieden" : (info.prev_winner ? `Sieger: ${info.prev_winner}` : "Duell beendet");
              this.el.tourneyTransitionTitle.textContent = `🎉 ${prevW}!`;
            }
            if (this.el.tourneyTransitionSubtitle) {
              this.el.tourneyTransitionSubtitle.textContent = `Nächstes Duell: ${info.next_p1} vs ${info.next_p2} (${nextGameStr})`;
            }
            if (this.el.tourneyTransitionCountdown) {
              const sec = info.seconds_remaining || 5;
              this.el.tourneyTransitionCountdown.textContent = `${sec}s`;
              if (this.prevCountdownSec !== sec) {
                this.prevCountdownSec = sec;
                if (sec > 0) this.playCountdown();
              }
            }
            if (this.el.tourneyTransitionSkipBtn) {
              this.el.tourneyTransitionSkipBtn.style.display = this.isTournamentHost() ? "inline-block" : "none";
            }
          }
        } else {
          if (this.el.tourneyMatchTransitionBanner) {
            this.el.tourneyMatchTransitionBanner.style.display = "none";
          }
        }

        if (this.el.gameView) this.el.gameView.style.display = "block";
        this.renderGame(state);

        if (this.el.tournamentLeaderboardModal && this.el.tournamentLeaderboardModal.style.display === "flex") {
          this.renderTournamentLeaderboardModalContent(tourney);
        }

        if (tourney.status === "round_end" && !this.roundEndModalOpened) {
          this.openTournamentLeaderboardModal();
          this.roundEndModalOpened = true;
        } else if (tourney.status === "active") {
          this.roundEndModalOpened = false;
        }

        return;
      } else if (tourney.status === "finished") {
        if (this.el.tourneyMatchTransitionBanner) this.el.tourneyMatchTransitionBanner.style.display = "none";
        if (this.el.tournamentHud) this.el.tournamentHud.style.display = "none";
        if (this.el.tournamentLobbyView) this.el.tournamentLobbyView.style.display = "none";
        if (this.el.gameView) this.el.gameView.style.display = "none";
        if (this.el.tournamentLeaderboardModal) this.el.tournamentLeaderboardModal.style.display = "none";
        if (this.el.tournamentPodiumView) this.el.tournamentPodiumView.style.display = "flex";
        this.renderTournamentPodium(tourney);
        return;
      }
    }

    if (this.el.tourneyMatchTransitionBanner) this.el.tourneyMatchTransitionBanner.style.display = "none";
    if (this.el.tournamentHud) this.el.tournamentHud.style.display = "none";
    if (this.el.tournamentLobbyView) this.el.tournamentLobbyView.style.display = "none";
    if (this.el.tournamentPodiumView) this.el.tournamentPodiumView.style.display = "none";
    if (this.el.tournamentLeaderboardModal) this.el.tournamentLeaderboardModal.style.display = "none";

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
    if (p1.connected === false) {
      this.el.p1Score.innerHTML = `<span class="player-tag-offline">Getrennt (30s)</span>`;
    }

    this.el.p2Name.textContent = p2.display_name || p2.username;
    this.el.p2Avatar.src = p2.avatar_url || (p2.is_bot ? "/static/images/tanjun_avatar.png" : "https://cdn.discordapp.com/embed/avatars/1.png");
    this.el.p2Score.textContent = `${state.scores?.[p2.user_id] || 0} Siege`;
    if (p2.connected === false && !p2.is_bot) {
      this.el.p2Score.innerHTML = `<span class="player-tag-offline">Getrennt (30s)</span>`;
    }

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
      const isNewMove = (idx) => {
        return state.last_move === idx && (!this.prevTTTBoard || this.prevTTTBoard[idx] !== state.board[idx]);
      };

      state.board.forEach((val, idx) => {
        const cell = this.el.tttCells[idx];
        cell.textContent = val;
        cell.className = "cell";
        if (val === "X") cell.classList.add("cell-x", "taken");
        if (val === "O") cell.classList.add("cell-o", "taken");
        if (winningLine.includes(idx)) cell.classList.add("winner-cell");
        if (val && isNewMove(idx)) {
          cell.classList.add("anim-pop");
          this.playPop();
        }
      });
      this.prevTTTBoard = [...state.board];
    }

    // ── Render Connect 4 (Dynamic Grid) ──
    if (gameType === "connect4") {
      const rows = state.rows || 6;
      const cols = state.cols || 7;
      const totalCells = rows * cols;

      if (this.currentC4Cols !== cols || this.currentC4Rows !== rows || this.el.c4Grid.children.length !== totalCells) {
        this.currentC4Cols = cols;
        this.currentC4Rows = rows;
        this.prevC4Board = null;

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
      const cellSize = parseInt(getComputedStyle(this.el.c4Grid).getPropertyValue("--c4-cell-size")) || 40;
      const isNewMove = (idx) => {
        return state.last_move === idx && (!this.prevC4Board || this.prevC4Board[idx] !== state.board[idx]);
      };

      state.board.forEach((val, idx) => {
        const cell = cells[idx];
        if (cell) {
          cell.className = "c4-cell";
          if (val === "R") cell.classList.add("chip-r");
          if (val === "Y") cell.classList.add("chip-y");
          if (winningLine.includes(idx)) cell.classList.add("winner-cell");

          if (val && isNewMove(idx)) {
            const row = Math.floor(idx / cols);
            const dropDist = (row + 1) * (cellSize + 6) + 16;
            cell.style.setProperty("--drop-dist", `-${dropDist}px`);
            cell.style.setProperty("--drop-duration", `${0.26 + row * 0.04}s`);
            cell.classList.add("anim-drop");
            this.playDrop();
          }
        }
      });
      this.prevC4Board = [...state.board];
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
      const choiceNames = { rock: "Stein", paper: "Papier", scissors: "Schere", lizard: "Echse", spock: "Spock" };
      this.el.rpsRoundBadge.textContent = `Runde ${state.current_round} (Ziel: ${state.target_wins} Siege)`;

      const picks = state.current_picks || {};
      const otherId = p1.user_id === this.user.id ? p2.user_id : p1.user_id;

      let myPick = picks[this.user.id] || "";
      let otherPick = picks[otherId] || "";

      if (!myPick && this.el.rpsBtns) {
        this.el.rpsBtns.forEach(btn => btn.classList.remove("selected"));
      }

      // If a round finished and new picks haven't begun, show the revealed gestures from last_round_result!
      const lr = state.last_round_result;
      const isRoundRevealed = !!(lr && (!myPick && !otherPick));
      if (isRoundRevealed && lr.picks) {
        myPick = lr.picks[this.user.id] || "";
        otherPick = lr.picks[otherId] || "";
      }

      this.el.rpsP1Pick.textContent = emojis[myPick] || "❓";
      this.el.rpsP2Pick.textContent = emojis[otherPick] || (picks[otherId] === "locked" ? "🔒" : "❓");

      this.el.rpsP1Pick.className = "rps-fighter-pick";
      this.el.rpsP2Pick.className = "rps-fighter-pick";

      this.el.rpsP1Label.textContent = this.user.displayName;
      this.el.rpsP2Label.textContent = p1.user_id === this.user.id ? (p2.display_name || p2.username) : (p1.display_name || p1.username);

      if (isRoundRevealed && lr) {
        if (this.prevRpsRound !== state.current_round || this.prevRpsFinished !== state.is_finished) {
          this.el.rpsP1Pick.classList.add("anim-reveal");
          this.el.rpsP2Pick.classList.add("anim-reveal");
          this.playClash();
        }
        const myChoiceName = choiceNames[myPick] || myPick;
        const otherChoiceName = choiceNames[otherPick] || otherPick;
        if (lr.winner === "draw") {
          this.el.rpsRoundResult.textContent = `Gleichstand in Runde ${lr.round}! (${myChoiceName} gegen ${otherChoiceName})`;
          this.el.rpsRoundResult.style.color = "#f0b232";
        } else {
          const won = lr.winner === this.user.id;
          const wName = won ? "Du hast" : "Gegner hat";
          const winnerPick = won ? myChoiceName : otherChoiceName;
          const loserPick = won ? otherChoiceName : myChoiceName;
          this.el.rpsRoundResult.textContent = `🎉 ${wName} Runde ${lr.round} gewonnen! (${winnerPick} schlägt ${loserPick})`;
          this.el.rpsRoundResult.style.color = won ? "#23a55a" : "#da373c";
        }
      } else if (myPick && (!otherPick || otherPick === "locked")) {
        this.el.rpsRoundResult.textContent = "Wahl eingeloggt! Warte auf Gegner...";
        this.el.rpsRoundResult.style.color = "#f0b232";
        this.el.rpsP2Pick.classList.add("anim-shake");
      } else if (!myPick && otherPick === "locked") {
        this.el.rpsRoundResult.textContent = "Gegner hat gewählt! Wähle deine Geste.";
        this.el.rpsRoundResult.style.color = "#5865f2";
      } else {
        this.el.rpsRoundResult.textContent = isLizardSpock ? "Wähle deine Geste (5 zur Auswahl)!" : "Wähle deine Geste!";
        this.el.rpsRoundResult.style.color = "#949ba4";
      }

      this.prevRpsRound = state.current_round;
      this.prevRpsFinished = state.is_finished;
    }

    // ── In-game Status Bar Text ──
    if (state.is_finished) {
      if (!this.prevGameFinished) {
        if (state.winner && state.winner !== "draw") {
          this.playWin();
        }
      }
      if (state.winner === "draw") {
        this.el.statusBar.textContent = "🤝 Unentschieden! Großartiges Match.";
        this.el.statusBar.style.color = "#f0b232";
      } else {
        const winnerObj = players.find(p => p.user_id === state.winner);
        const name = winnerObj ? (winnerObj.display_name || winnerObj.username) : state.winner;
        this.el.statusBar.textContent = `🎉 ${name} gewinnt das Match!`;
        this.el.statusBar.style.color = "#23a55a";
      }
    } else if (state.is_started) {
      this.prevGameFinished = false;
      const offlineOpponent = players.find(p => p.connected === false && !p.is_bot);
      if (offlineOpponent) {
        const offName = offlineOpponent.display_name || offlineOpponent.username;
        this.el.statusBar.textContent = `⏳ ${offName} hat die Verbindung verloren. Warte auf Reconnect (30s)...`;
        this.el.statusBar.style.color = "#ef4444";
      } else if (gameType === "rps") {
        this.el.statusBar.textContent = "⚡ Wähle Stein, Papier oder Schere!";
        this.el.statusBar.style.color = "#5865f2";
      } else if (state.current_turn === this.user.id) {
        this.el.statusBar.textContent = "⚡ Du bist am Zug! Setze deinen Zug.";
        this.el.statusBar.style.color = "#5865f2";
      } else if (state.current_turn === "bot_tanjun") {
        this.el.statusBar.innerHTML = `
          <span class="bot-thinking-status">
            <span>🤖 Tanjun AI überlegt</span>
            <span class="typing-dots">
              <span class="typing-dot"></span>
              <span class="typing-dot"></span>
              <span class="typing-dot"></span>
            </span>
          </span>
        `;
        this.el.statusBar.style.color = "#5865f2";
      } else {
        const currObj = players.find(p => p.user_id === state.current_turn);
        const name = currObj ? (currObj.display_name || currObj.username) : "Gegner";
        this.el.statusBar.textContent = `⏳ ${name} überlegt...`;
        this.el.statusBar.style.color = "#949ba4";
      }
    }

    if (this.el.restartBtn) {
      const tourney = state.tournament;
      const inTourney = tourney && (tourney.status === "active" || tourney.status === "round_end");
      this.el.restartBtn.style.display = inTourney ? "none" : "inline-block";
    }
  }

  // ==========================================================================
  // Tournament Methods
  // ==========================================================================

  isTournamentHost() {
    if (this.gameState?.tournament) {
      return this.gameState.tournament.host_id === this.user.id;
    }
    return this.isHost();
  }

  broadcastTourneySettings() {
    if (!this.isTournamentHost()) return;
    this.sendAction("tournament_update_settings", {
      format: this.selectedTourneyFormat,
      match_style: this.selectedTourneyStyle,
      game_selection: this.selectedTourneyGameSelection || "host_choice",
      selected_game: this.selectedTourneyGame || "connect4",
      total_rounds: this.selectedTourneyRounds
    });
  }

  renderTournamentLobby(tourney) {
    if (!tourney) return;
    const isHost = this.isTournamentHost();

    // Sync settings if not currently modifying
    this.selectedTourneyFormat = tourney.format || "points";
    this.selectedTourneyStyle = tourney.match_style || "spectated";
    this.selectedTourneyGame = tourney.selected_game || "connect4";
    this.selectedTourneyGameSelection = tourney.game_selection || "playlist";
    this.selectedTourneyRounds = tourney.total_rounds || 3;

    // Update Pills
    this.el.tourneyFormatPills.forEach(p => {
      const active = p.dataset.tourneyFormat === this.selectedTourneyFormat;
      p.classList.toggle("active", active);
      p.classList.toggle("disabled", !isHost);
      if (active && this.el.tourneyFormatLabel) this.el.tourneyFormatLabel.textContent = p.textContent;
    });

    this.el.tourneyStylePills.forEach(p => {
      const active = p.dataset.tourneyStyle === this.selectedTourneyStyle;
      p.classList.toggle("active", active);
      p.classList.toggle("disabled", !isHost);
      if (active && this.el.tourneyStyleLabel) this.el.tourneyStyleLabel.textContent = p.textContent;
    });

    this.el.tourneyGamePills.forEach(p => {
      const key = this.selectedTourneyGameSelection === "playlist" ? "playlist" : (this.selectedTourneyGameSelection === "random" ? "random" : this.selectedTourneyGame);
      const active = p.dataset.tourneyGame === key;
      p.classList.toggle("active", active);
      p.classList.toggle("disabled", !isHost);
      if (active && this.el.tourneyGameLabel) this.el.tourneyGameLabel.textContent = p.textContent;
    });

    if (this.el.tourneyRoundsGroup) {
      this.el.tourneyRoundsGroup.style.display = this.selectedTourneyFormat === "points" ? "block" : "none";
    }
    this.el.tourneyRoundsPills.forEach(p => {
      const active = parseInt(p.dataset.tourneyRounds, 10) === this.selectedTourneyRounds;
      p.classList.toggle("active", active);
      p.classList.toggle("disabled", !isHost);
      if (active && this.el.tourneyRoundsLabel) this.el.tourneyRoundsLabel.textContent = p.textContent;
    });

    // Render Rewards Box
    if (this.el.tourneyRewardsBox && this.el.tourneyRewardsContent) {
      const rew = tourney.rewards;
      if (rew && (rew.can_grant_xp || rew.can_grant_role)) {
        this.el.tourneyRewardsBox.style.display = "block";
        if (this.el.tourneyRewardsBadge) {
          this.el.tourneyRewardsBadge.textContent = "Server-Event Aktiv";
          this.el.tourneyRewardsBadge.className = "tourney-rewards-badge active";
        }
        let rewHtml = `<div class="tourney-rewards-list">`;
        if (rew.can_grant_xp) {
          if (rew.xp_1st > 0) rewHtml += `<div class="tourney-reward-pill">🥇 +${rew.xp_1st.toLocaleString()} XP</div>`;
          if (rew.xp_2nd > 0) rewHtml += `<div class="tourney-reward-pill">🥈 +${rew.xp_2nd.toLocaleString()} XP</div>`;
          if (rew.xp_3rd > 0) rewHtml += `<div class="tourney-reward-pill">🥉 +${rew.xp_3rd.toLocaleString()} XP</div>`;
        }
        if (rew.can_grant_role && (rew.role_name || rew.role_id)) {
          rewHtml += `<div class="tourney-reward-pill role-pill">👑 Rolle: @${rew.role_name || "Champion"}</div>`;
        }
        rewHtml += `</div>`;
        this.el.tourneyRewardsContent.innerHTML = rewHtml;
      } else if (rew && rew.guild_id) {
        this.el.tourneyRewardsBox.style.display = "block";
        if (this.el.tourneyRewardsBadge) {
          this.el.tourneyRewardsBadge.textContent = "Fun-Modus";
          this.el.tourneyRewardsBadge.className = "tourney-rewards-badge";
        }
        this.el.tourneyRewardsContent.innerHTML = `<span style="font-size: 0.8rem; color: #94a3b8; font-style: italic;">Turnier um Ruhm & Ehre (Keine Server-Belohnungen konfiguriert).</span>`;
      } else {
        this.el.tourneyRewardsBox.style.display = "none";
      }
    }

    // Render Participant List
    if (this.el.tourneyPlayersList) {
      const players = tourney.leaderboard || [];
      const count = tourney.participants_count || players.length;
      if (this.el.tourneyPlayerCountBadge) {
        this.el.tourneyPlayerCountBadge.textContent = `${count}/16`;
      }

      let html = "";
      players.forEach(p => {
        const isYou = p.user_id === this.user.id;
        const isH = p.is_host;
        html += `
          <div class="lobby-player-row">
            <div class="lobby-player-meta">
              <img class="lobby-player-avatar-small" src="${this.escapeHtml(p.avatar_url || 'https://cdn.discordapp.com/embed/avatars/0.png')}" alt="Avatar">
              <span>${this.escapeHtml(p.display_name)}</span>
              ${isYou ? '<span class="lobby-tag-you">Du</span>' : ''}
            </div>
            ${isH ? '<span class="lobby-tag-host">Turnierleiter 👑</span>' : '<span style="font-size:0.75rem; color:#23a55a;">Bereit</span>'}
          </div>
        `;
      });

      if (count < 2) {
        html += `
          <div class="lobby-player-row" style="opacity: 0.6; border: 1px dashed rgba(255,255,255,0.2);">
            <div class="lobby-player-meta">
              <span>⏳</span>
              <span style="color: #94a3b8; font-style: italic;">Warte auf mindestens 2 Teilnehmer...</span>
            </div>
          </div>
        `;
      }

      this.el.tourneyPlayersList.innerHTML = html;
    }

    // Update Start Button & Status
    if (this.el.tourneyStartBtn) {
      if (!isHost) {
        this.el.tourneyStartBtn.disabled = true;
        this.el.tourneyStartBtn.textContent = "Warte auf Turnierleiter...";
        if (this.el.tourneyLobbyStatusMsg) {
          this.el.tourneyLobbyStatusMsg.textContent = "Warte darauf, dass der Turnierleiter das Turnier startet.";
          this.el.tourneyLobbyStatusMsg.style.color = "#94a3b8";
        }
      } else {
        const ready = (tourney.participants_count || 0) >= 2;
        this.el.tourneyStartBtn.disabled = !ready;
        this.el.tourneyStartBtn.textContent = "🏆 Turnier Starten";
        if (this.el.tourneyLobbyStatusMsg) {
          if (ready) {
            this.el.tourneyLobbyStatusMsg.textContent = "Bereit! Klicke auf 'Turnier Starten', um Runde 1 einzuläuten.";
            this.el.tourneyLobbyStatusMsg.style.color = "#23a55a";
          } else {
            this.el.tourneyLobbyStatusMsg.textContent = "Mindestens 2 Teilnehmer werden für ein Turnier benötigt!";
            this.el.tourneyLobbyStatusMsg.style.color = "#fb8500";
          }
        }
      }
      if (this.el.tourneyLeaveBtn) {
        this.el.tourneyLeaveBtn.style.display = isHost ? "none" : "inline-block";
      }
    }
  }

  renderTournamentHud(tourney) {
    if (!tourney) return;

    if (this.el.tourneyHudCupName) {
      this.el.tourneyHudCupName.textContent = tourney.title || "Tanjun Voice Cup";
    }

    if (this.el.tourneyHudRoundBadge) {
      if (tourney.status === "round_end") {
        this.el.tourneyHudRoundBadge.textContent = `Runde ${tourney.current_round} Ende`;
        this.el.tourneyHudRoundBadge.classList.add("pulse");
      } else {
        this.el.tourneyHudRoundBadge.textContent = `Runde ${tourney.current_round}/${tourney.total_rounds}`;
        this.el.tourneyHudRoundBadge.classList.remove("pulse");
      }
    }

    if (this.el.tourneyHudGameBadge) {
      const gameIcons = {
        connect4: "🔴 Vier Gewinnt",
        tictactoe: "❌ Tic-Tac-Toe",
        rps: "✊ Schere-Stein-Papier"
      };
      const gameLabel = gameIcons[tourney.selected_game] || tourney.selected_game;
      if (tourney.game_selection === "playlist") {
        this.el.tourneyHudGameBadge.textContent = `🎖️ ${gameLabel}`;
      } else {
        this.el.tourneyHudGameBadge.textContent = gameLabel;
      }
    }

    if (this.el.tourneyHudMatchText) {
      const m = tourney.current_match;
      if (m) {
        this.el.tourneyHudMatchText.textContent = `⚔️ ${m.p1_name} vs ${m.p2_name}`;
      } else {
        this.el.tourneyHudMatchText.textContent = "⏳ Pause / Nächste Runde";
      }
    }

    if (this.el.tourneyHudUserScore) {
      const myEntry = (tourney.leaderboard || []).find(p => p.user_id === this.user.id);
      if (myEntry) {
        const medal = myEntry.rank === 1 ? "🥇" : myEntry.rank === 2 ? "🥈" : myEntry.rank === 3 ? "🥉" : `#${myEntry.rank}`;
        this.el.tourneyHudUserScore.textContent = `${myEntry.score} Pkt (${medal})`;
      } else {
        this.el.tourneyHudUserScore.textContent = "Zuschauer";
      }
    }

    if (this.el.tourneyHudHostBtn) {
      const isHost = this.isTournamentHost();
      this.el.tourneyHudHostBtn.style.display = isHost ? "inline-block" : "none";
      if (tourney.status === "round_end" && isHost) {
        this.el.tourneyHudHostBtn.textContent = "⚡ Nächste Runde wählen";
        this.el.tourneyHudHostBtn.classList.add("anim-pulse-btn");
      } else {
        this.el.tourneyHudHostBtn.textContent = "⚙️ Cup-Menü";
        this.el.tourneyHudHostBtn.classList.remove("anim-pulse-btn");
      }
    }
  }

  openTournamentLeaderboardModal() {
    if (!this.el.tournamentLeaderboardModal) return;
    this.el.tournamentLeaderboardModal.style.display = "flex";
    const tourney = this.gameState?.tournament;
    if (tourney) {
      this.renderTournamentLeaderboardModalContent(tourney);
    }
  }

  closeTournamentLeaderboardModal() {
    if (!this.el.tournamentLeaderboardModal) return;
    this.el.tournamentLeaderboardModal.style.display = "none";
  }

  renderTournamentLeaderboardModalContent(tourney) {
    if (!tourney) return;
    const isHost = this.isTournamentHost();

    // Round info text
    if (this.el.tourneyModalRoundInfo) {
      this.el.tourneyModalRoundInfo.textContent = `Runde ${tourney.current_round} von ${tourney.total_rounds} • ${tourney.format === 'knockout' ? 'K.O.-System' : 'Punkte-Mehrkampf'}`;
    }

    // Leaderboard table
    if (this.el.tourneyModalLeaderboardList) {
      const medals = ["🥇", "🥈", "🥉"];
      let lbHtml = "";
      (tourney.leaderboard || []).forEach((p, idx) => {
        const rankDisplay = idx < 3 ? medals[idx] : `#${idx + 1}`;
        const isYou = p.user_id === this.user.id;
        lbHtml += `
          <div class="tourney-leaderboard-row ${idx === 0 ? 'rank-1' : ''} ${isYou ? 'current-user-row' : ''}">
            <div class="tourney-leaderboard-meta">
              <span class="tourney-rank-num">${rankDisplay}</span>
              <img class="lobby-player-avatar-small" src="${this.escapeHtml(p.avatar_url || 'https://cdn.discordapp.com/embed/avatars/0.png')}" alt="Avatar">
              <span style="font-weight: 700;">${this.escapeHtml(p.display_name)}</span>
              ${isYou ? '<span class="lobby-tag-you">Du</span>' : ''}
              ${p.is_host ? '<span title="Turnierleiter">👑</span>' : ''}
              ${p.is_eliminated ? '<span style="font-size:0.7rem; color:#da373c;">(Ausgeschieden)</span>' : ''}
            </div>
            <div class="tourney-leaderboard-scores">
              <span class="tourney-score-points">${p.score} Pkt</span>
              <span class="tourney-score-record">${p.wins}S - ${p.draws || 0}U - ${p.losses}N</span>
            </div>
          </div>
        `;
      });
      this.el.tourneyModalLeaderboardList.innerHTML = lbHtml;
    }

    // Host Controls Box
    if (this.el.tourneyHostControlsBox) {
      if (isHost) {
        this.el.tourneyHostControlsBox.style.display = "block";
        if (this.el.tourneyEndEarlyBtn) this.el.tourneyEndEarlyBtn.style.display = "inline-block";

        if (tourney.status === "round_end") {
          if (this.el.tourneyRoundEndMsg) {
            this.el.tourneyRoundEndMsg.textContent = `Runde ${tourney.current_round} beendet! Wähle das Spiel und starte Runde ${tourney.current_round + 1}:`;
            this.el.tourneyRoundEndMsg.style.color = "#23a55a";
          }
          if (this.el.tourneyNextRoundBtn) {
            this.el.tourneyNextRoundBtn.style.display = "inline-block";
            this.el.tourneyNextRoundBtn.textContent = `▶ Runde ${tourney.current_round + 1} starten`;
          }
          if (this.el.tourneyNextMatchBtn) {
            this.el.tourneyNextMatchBtn.style.display = "none";
          }
          const picker = document.querySelector(".tourney-next-game-picker");
          if (picker) picker.style.display = "block";
        } else {
          // In active round
          const hasMoreMatches = tourney.active_matches && tourney.active_matches.some(m => m.status === "pending" || (!m.is_active && m.status !== "finished"));
          if (this.el.tourneyRoundEndMsg) {
            this.el.tourneyRoundEndMsg.textContent = "Runde läuft aktiv...";
            this.el.tourneyRoundEndMsg.style.color = "#94a3b8";
          }
          if (this.el.tourneyNextRoundBtn) {
            this.el.tourneyNextRoundBtn.style.display = "none";
          }
          const picker = document.querySelector(".tourney-next-game-picker");
          if (picker) picker.style.display = "none";

          if (this.el.tourneyNextMatchBtn) {
            if (tourney.current_match && tourney.current_match.status === "finished" && hasMoreMatches) {
              this.el.tourneyNextMatchBtn.style.display = "inline-block";
              this.el.tourneyNextMatchBtn.textContent = "⚔️ Nächstes Duell aufrufen";
            } else {
              this.el.tourneyNextMatchBtn.style.display = "none";
            }
          }
        }
      } else {
        this.el.tourneyHostControlsBox.style.display = "none";
        if (this.el.tourneyEndEarlyBtn) this.el.tourneyEndEarlyBtn.style.display = "none";
      }
    }

    // Match history list
    if (this.el.tourneyModalHistoryList) {
      const history = tourney.match_history || [];
      if (history.length === 0) {
        this.el.tourneyModalHistoryList.innerHTML = `<div style="font-size: 0.8rem; color: #94a3b8; font-style: italic;">Noch keine Duelle gespielt.</div>`;
      } else {
        const gameNames = { connect4: "Vier Gewinnt", tictactoe: "Tic-Tac-Toe", rps: "Schere Stein Papier" };
        let histHtml = "";
        history.slice(-8).reverse().forEach(h => {
          let winnerLabel = "🤝 Unentschieden";
          if (h.winner && h.winner !== "draw") {
            winnerLabel = `🏆 ${this.escapeHtml(h.winner)}`;
          }
          histHtml += `
            <div class="tourney-history-item">
              <span class="tourney-history-details">Runde ${h.round} (${gameNames[h.game_type] || h.game_type}): <strong>${this.escapeHtml(h.p1)}</strong> vs <strong>${this.escapeHtml(h.p2)}</strong></span>
              <span class="tourney-history-winner">${winnerLabel}</span>
            </div>
          `;
        });
        this.el.tourneyModalHistoryList.innerHTML = histHtml;
      }
    }

    // Cheers animation
    if (tourney.current_match?.cheers && tourney.current_match.cheers.length > 0) {
      if (tourney.current_match.cheers.length > this.renderedCheerCount) {
        const newCheers = tourney.current_match.cheers.slice(this.renderedCheerCount);
        newCheers.forEach(c => this.spawnFloatingCheer(c.name, c.emote));
        this.renderedCheerCount = tourney.current_match.cheers.length;
      }
    } else {
      this.renderedCheerCount = 0;
    }
  }

  renderTournamentPodium(tourney) {
    if (!tourney) return;
    const isHost = this.isTournamentHost();
    const leaderboard = tourney.leaderboard || [];

    // Render Podium Rewards Banner
    if (this.el.podiumRewardsBanner) {
      const rew = tourney.rewards;
      if (rew && (rew.can_grant_xp || rew.can_grant_role)) {
        this.el.podiumRewardsBanner.style.display = "flex";
        let rewParts = [];
        if (rew.can_grant_xp && (rew.xp_1st > 0)) {
          rewParts.push(`Level-XP vergeben (🥇 +${rew.xp_1st.toLocaleString()} XP)`);
        }
        if (rew.can_grant_role && (rew.role_name || rew.role_id)) {
          rewParts.push(`Sieger-Rolle verliehen (@${this.escapeHtml(rew.role_name || "Champion")})`);
        }
        if (this.el.podiumRewardsText) {
          this.el.podiumRewardsText.innerHTML = `<strong>Server-Belohnungen:</strong> ${rewParts.join(" & ")} im Discord-Server gutgeschrieben!`;
        }
      } else {
        this.el.podiumRewardsBanner.style.display = "none";
      }
    }

    // Top 3 Podium
    if (this.el.podiumTop3) {
      const p1 = leaderboard[0];
      const p2 = leaderboard[1];
      const p3 = leaderboard[2];

      let podiumHtml = "";

      // 2nd Place (Left)
      if (p2) {
        podiumHtml += `
          <div class="podium-step podium-step-2">
            <div class="podium-avatar-wrap">
              <img class="podium-avatar" src="${this.escapeHtml(p2.avatar_url || 'https://cdn.discordapp.com/embed/avatars/1.png')}" alt="2nd">
              <span class="podium-medal">🥈</span>
            </div>
            <div class="podium-name">${this.escapeHtml(p2.display_name)}</div>
            <div class="podium-score">${p2.score} Pkt</div>
          </div>
        `;
      }

      // 1st Place (Center, Gold)
      if (p1) {
        podiumHtml += `
          <div class="podium-step podium-step-1">
            <div class="podium-avatar-wrap">
              <img class="podium-avatar" src="${this.escapeHtml(p1.avatar_url || 'https://cdn.discordapp.com/embed/avatars/0.png')}" alt="1st">
              <span class="podium-medal">🥇</span>
            </div>
            <div class="podium-name">${this.escapeHtml(p1.display_name)}</div>
            <div class="podium-score">${p1.score} Pkt</div>
          </div>
        `;
      }

      // 3rd Place (Right)
      if (p3) {
        podiumHtml += `
          <div class="podium-step podium-step-3">
            <div class="podium-avatar-wrap">
              <img class="podium-avatar" src="${this.escapeHtml(p3.avatar_url || 'https://cdn.discordapp.com/embed/avatars/2.png')}" alt="3rd">
              <span class="podium-medal">🥉</span>
            </div>
            <div class="podium-name">${this.escapeHtml(p3.display_name)}</div>
            <div class="podium-score">${p3.score} Pkt</div>
          </div>
        `;
      }

      this.el.podiumTop3.innerHTML = podiumHtml;
    }

    // Final Leaderboard Table
    if (this.el.tourneyFinalTable) {
      let tableHtml = "";
      leaderboard.forEach((p, idx) => {
        tableHtml += `
          <div class="tourney-leaderboard-row ${idx === 0 ? 'rank-1' : ''}">
            <div class="tourney-leaderboard-meta">
              <span class="tourney-rank-num">#${idx + 1}</span>
              <img class="lobby-player-avatar-small" src="${this.escapeHtml(p.avatar_url || 'https://cdn.discordapp.com/embed/avatars/0.png')}" alt="Avatar">
              <span>${this.escapeHtml(p.display_name)}</span>
              ${p.user_id === this.user.id ? '<span class="lobby-tag-you">Du</span>' : ''}
            </div>
            <div class="tourney-leaderboard-scores">
              <span class="tourney-score-points">${p.score} Pkt</span>
              <span class="tourney-score-record">${p.wins}S / ${p.losses}N</span>
            </div>
          </div>
        `;
      });
      this.el.tourneyFinalTable.innerHTML = tableHtml;
    }

    if (this.el.tourneyNewCupBtn) {
      this.el.tourneyNewCupBtn.style.display = isHost ? "inline-block" : "none";
    }
  }

  spawnFloatingCheer(name, emote) {
    this.playCheer();
    const targets = [this.el.tourneyCheerOverlay, this.el.globalCheerOverlay].filter(Boolean);
    targets.forEach(overlay => {
      const cheerEl = document.createElement("div");
      cheerEl.className = "floating-cheer";
      const leftPercent = Math.floor(15 + Math.random() * 70);
      cheerEl.style.left = `${leftPercent}%`;
      cheerEl.innerHTML = `
        <span>${this.escapeHtml(emote)}</span>
        <span class="floating-cheer-name">${this.escapeHtml(name)}</span>
      `;
      overlay.appendChild(cheerEl);
      setTimeout(() => {
        if (cheerEl.parentNode) cheerEl.remove();
      }, 2400);
    });
  }
}

document.addEventListener("DOMContentLoaded", () => {
  window.app = new TanjunActivityClient();
  window.app.init();
});
