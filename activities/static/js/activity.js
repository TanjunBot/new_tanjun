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

      // Tournament Views
      tournamentLobbyView: document.getElementById("tournamentLobbyView"),
      tournamentArenaView: document.getElementById("tournamentArenaView"),
      tournamentPodiumView: document.getElementById("tournamentPodiumView"),

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

      // Tournament Arena Elements
      tourneyRoundIndicator: document.getElementById("tourneyRoundIndicator"),
      tourneyGameIndicator: document.getElementById("tourneyGameIndicator"),
      tourneyModeIndicator: document.getElementById("tourneyModeIndicator"),
      tourneyLeaderboardToggleBtn: document.getElementById("tourneyLeaderboardToggleBtn"),
      tourneyMatchSwitcher: document.getElementById("tourneyMatchSwitcher"),
      tourneyMatchTabs: document.getElementById("tourneyMatchTabs"),
      tourneyP1Card: document.getElementById("tourneyP1Card"),
      tourneyP1Avatar: document.getElementById("tourneyP1Avatar"),
      tourneyP1Name: document.getElementById("tourneyP1Name"),
      tourneyP1Score: document.getElementById("tourneyP1Score"),
      tourneyP1Tag: document.getElementById("tourneyP1Tag"),
      tourneyP2Card: document.getElementById("tourneyP2Card"),
      tourneyP2Avatar: document.getElementById("tourneyP2Avatar"),
      tourneyP2Name: document.getElementById("tourneyP2Name"),
      tourneyP2Score: document.getElementById("tourneyP2Score"),
      tourneyP2Tag: document.getElementById("tourneyP2Tag"),
      tourneyStatusBar: document.getElementById("tourneyStatusBar"),
      tourneyTttBoard: document.getElementById("tourneyTttBoard"),
      tourneyTttCells: document.querySelectorAll("#tourneyTttBoard .cell"),
      tourneyC4Board: document.getElementById("tourneyC4Board"),
      tourneyC4DropRow: document.getElementById("tourneyC4DropRow"),
      tourneyC4Grid: document.getElementById("tourneyC4Grid"),
      tourneyRpsBoard: document.getElementById("tourneyRpsBoard"),
      tourneyRpsRoundBadge: document.getElementById("tourneyRpsRoundBadge"),
      tourneyRpsP1Pick: document.getElementById("tourneyRpsP1Pick"),
      tourneyRpsP1Label: document.getElementById("tourneyRpsP1Label"),
      tourneyRpsP2Pick: document.getElementById("tourneyRpsP2Pick"),
      tourneyRpsP2Label: document.getElementById("tourneyRpsP2Label"),
      tourneyRpsRoundResult: document.getElementById("tourneyRpsRoundResult"),
      tourneyRpsBtns: document.querySelectorAll("#tourneyRpsChoices .rps-btn"),
      tourneyCheerBtns: document.querySelectorAll(".tourney-cheer-btn"),
      tourneyCheerOverlay: document.getElementById("tourneyCheerOverlay"),
      tourneyRoundEndControls: document.getElementById("tourneyRoundEndControls"),
      tourneyRoundEndMsg: document.getElementById("tourneyRoundEndMsg"),
      tourneyNextGameSelector: document.getElementById("tourneyNextGameSelector"),
      tourneyNextGamePills: document.querySelectorAll("#tourneyNextGamePills .diff-pill"),
      tourneyNextRoundBtn: document.getElementById("tourneyNextRoundBtn"),
      tourneyLeaderboardDrawer: document.getElementById("tourneyLeaderboardDrawer"),
      tourneyLeaderboardCloseBtn: document.getElementById("tourneyLeaderboardCloseBtn"),
      tourneyLiveLeaderboardList: document.getElementById("tourneyLiveLeaderboardList"),
      tourneyEndEarlyBtn: document.getElementById("tourneyEndEarlyBtn"),
      tourneyLeaveBtn: document.getElementById("tourneyLeaveBtn"),

      // Tournament Podium Elements
      podiumTop3: document.getElementById("podiumTop3"),
      tourneyFinalTable: document.getElementById("tourneyFinalTable"),
      tourneyNewCupBtn: document.getElementById("tourneyNewCupBtn"),
      tourneyPodiumHubBtn: document.getElementById("tourneyPodiumHubBtn")
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
        const val = pill.dataset.tourneyGame || "connect4";
        if (val === "random") {
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

    // Leaderboard Toggle
    if (this.el.tourneyLeaderboardToggleBtn) {
      this.el.tourneyLeaderboardToggleBtn.addEventListener("click", () => {
        if (!this.el.tourneyLeaderboardDrawer) return;
        const isShown = this.el.tourneyLeaderboardDrawer.style.display === "flex";
        this.el.tourneyLeaderboardDrawer.style.display = isShown ? "none" : "flex";
      });
    }

    if (this.el.tourneyLeaderboardCloseBtn) {
      this.el.tourneyLeaderboardCloseBtn.addEventListener("click", () => {
        if (this.el.tourneyLeaderboardDrawer) this.el.tourneyLeaderboardDrawer.style.display = "none";
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
        this.sendAction("tournament_next_round", { selected_game: this.selectedNextRoundGame });
      });
    }

    // End Early Button
    if (this.el.tourneyEndEarlyBtn) {
      this.el.tourneyEndEarlyBtn.addEventListener("click", () => {
        if (!this.isTournamentHost()) return;
        if (confirm("Möchtest du das Turnier wirklich beenden?")) {
          this.sendAction("tournament_end");
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

    // Tournament Board Moves: TTT
    this.el.tourneyTttCells.forEach(cell => {
      cell.addEventListener("click", () => {
        const idx = parseInt(cell.dataset.tourneyTtt, 10);
        this.makeMoveTournamentTTT(idx);
      });
    });

    // Tournament Board Moves: RPS
    this.el.tourneyRpsBtns.forEach(btn => {
      btn.addEventListener("click", () => {
        const choice = btn.dataset.tourneyRps;
        this.makeMoveTournamentRPS(choice);
      });
    });
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
    this.sendAction("lobby");
  }

  returnToHub() {
    this.clearAnimationCaches();
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
      if (this.el.gameView) this.el.gameView.style.display = "none";

      if (tourney.status === "lobby") {
        if (this.el.tournamentLobbyView) this.el.tournamentLobbyView.style.display = "block";
        if (this.el.tournamentArenaView) this.el.tournamentArenaView.style.display = "none";
        if (this.el.tournamentPodiumView) this.el.tournamentPodiumView.style.display = "none";
        this.renderTournamentLobby(tourney);
      } else if (tourney.status === "active" || tourney.status === "round_end") {
        if (this.el.tournamentLobbyView) this.el.tournamentLobbyView.style.display = "none";
        if (this.el.tournamentArenaView) this.el.tournamentArenaView.style.display = "flex";
        if (this.el.tournamentPodiumView) this.el.tournamentPodiumView.style.display = "none";
        this.renderTournamentArena(tourney);
      } else if (tourney.status === "finished") {
        if (this.el.tournamentLobbyView) this.el.tournamentLobbyView.style.display = "none";
        if (this.el.tournamentArenaView) this.el.tournamentArenaView.style.display = "none";
        if (this.el.tournamentPodiumView) this.el.tournamentPodiumView.style.display = "flex";
        this.renderTournamentPodium(tourney);
      }
      return;
    }

    if (this.el.tournamentLobbyView) this.el.tournamentLobbyView.style.display = "none";
    if (this.el.tournamentArenaView) this.el.tournamentArenaView.style.display = "none";
    if (this.el.tournamentPodiumView) this.el.tournamentPodiumView.style.display = "none";

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
        if (val && isNewMove(idx)) cell.classList.add("anim-pop");
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
      this.el.rpsRoundBadge.textContent = `Runde ${state.current_round} (Ziel: ${state.target_wins} Siege)`;

      const picks = state.current_picks || {};
      const myPick = picks[this.user.id] || "";
      const otherId = p1.user_id === this.user.id ? p2.user_id : p1.user_id;
      const otherPick = picks[otherId] || "";

      this.el.rpsP1Pick.textContent = emojis[myPick] || "❓";
      this.el.rpsP2Pick.textContent = emojis[otherPick] || "❓";

      this.el.rpsP1Pick.className = "rps-fighter-pick";
      this.el.rpsP2Pick.className = "rps-fighter-pick";

      this.el.rpsP1Label.textContent = this.user.displayName;
      this.el.rpsP2Label.textContent = p1.user_id === this.user.id ? (p2.display_name || p2.username) : (p1.display_name || p1.username);

      if (state.last_round_result) {
        const lr = state.last_round_result;
        if (this.prevRpsRound !== state.current_round || this.prevRpsFinished !== state.is_finished) {
          this.el.rpsP1Pick.classList.add("anim-reveal");
          this.el.rpsP2Pick.classList.add("anim-reveal");
        }
        if (lr.winner === "draw") {
          this.el.rpsRoundResult.textContent = `Gleichstand in Runde ${lr.round}!`;
          this.el.rpsRoundResult.style.color = "#f0b232";
        } else {
          const wName = lr.winner === this.user.id ? "Du hast" : "Gegner hat";
          this.el.rpsRoundResult.textContent = `🎉 ${wName} Runde ${lr.round} gewonnen!`;
          this.el.rpsRoundResult.style.color = lr.winner === this.user.id ? "#23a55a" : "#da373c";
        }
      } else if (myPick && !otherPick) {
        this.el.rpsRoundResult.textContent = "Wahl eingeloggt! Warte auf Gegner...";
        this.el.rpsRoundResult.style.color = "#f0b232";
        this.el.rpsP2Pick.classList.add("anim-shake");
      } else {
        this.el.rpsRoundResult.textContent = isLizardSpock ? "Wähle deine Geste (5 zur Auswahl)!" : "Wähle deine Geste!";
        this.el.rpsRoundResult.style.color = "#949ba4";
      }

      this.prevRpsRound = state.current_round;
      this.prevRpsFinished = state.is_finished;
    }

    // ── In-game Status Bar Text ──
    if (state.is_finished) {
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
      if (gameType === "rps") {
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
    this.selectedTourneyGameSelection = tourney.game_selection || "host_choice";
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
      const key = this.selectedTourneyGameSelection === "random" ? "random" : this.selectedTourneyGame;
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
              <img class="lobby-player-avatar-small" src="${p.avatar_url || 'https://cdn.discordapp.com/embed/avatars/0.png'}" alt="Avatar">
              <span>${p.display_name}</span>
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
    }
  }

  getCurrentTournamentMatch() {
    const tourney = this.gameState?.tournament;
    if (!tourney) return null;
    if (tourney.match_style === "parallel") {
      if (tourney.user_match && tourney.user_match.status === "active") {
        return tourney.user_match;
      }
    }
    return tourney.spectated_match;
  }

  renderTournamentArena(tourney) {
    if (!tourney) return;

    // Header Badges
    const isKnockout = tourney.format === "knockout";
    if (this.el.tourneyRoundIndicator) {
      this.el.tourneyRoundIndicator.textContent = isKnockout 
        ? `K.O. Runde ${tourney.current_round}` 
        : `Runde ${tourney.current_round} / ${tourney.total_rounds}`;
    }

    const gameNames = {
      connect4: "🔴 Vier Gewinnt",
      tictactoe: "❌ Tic-Tac-Toe",
      rps: "✊ Schere-Stein-Papier"
    };
    if (this.el.tourneyGameIndicator) {
      this.el.tourneyGameIndicator.textContent = gameNames[tourney.selected_game] || tourney.selected_game;
    }

    if (this.el.tourneyModeIndicator) {
      this.el.tourneyModeIndicator.textContent = tourney.match_style === "spectated" ? "📺 Showmatch" : "⚡ Parallel";
    }

    // Parallel Match Switcher
    if (this.el.tourneyMatchSwitcher && this.el.tourneyMatchTabs) {
      if (tourney.match_style === "parallel" && tourney.active_matches?.length > 1) {
        this.el.tourneyMatchSwitcher.style.display = "flex";
        let tabsHtml = "";
        tourney.active_matches.forEach(m => {
          const isSelected = (m.match_id === tourney.spectated_match?.match_id);
          const icon = m.status === "finished" ? "✓" : "⚡";
          tabsHtml += `
            <button class="tourney-tab-btn ${isSelected ? 'active' : ''}" data-match-id="${m.match_id}">
              ${m.p1_name} vs ${m.p2_name} ${icon}
            </button>
          `;
        });
        this.el.tourneyMatchTabs.innerHTML = tabsHtml;
        this.el.tourneyMatchTabs.querySelectorAll(".tourney-tab-btn").forEach(btn => {
          btn.addEventListener("click", () => {
            const mid = btn.dataset.matchId;
            this.sendAction("tournament_switch_spectate", { match_id: mid });
          });
        });
      } else {
        this.el.tourneyMatchSwitcher.style.display = "none";
      }
    }

    // Active Duel Stage & Scoreboard
    const match = this.getCurrentTournamentMatch();
    if (!match) return;

    const p1 = match.player1;
    const p2 = match.player2;

    if (this.el.tourneyP1Name) this.el.tourneyP1Name.textContent = p1.display_name;
    if (this.el.tourneyP1Avatar) this.el.tourneyP1Avatar.src = p1.avatar_url || "https://cdn.discordapp.com/embed/avatars/0.png";
    if (this.el.tourneyP1Score) this.el.tourneyP1Score.textContent = `${p1.score} Pkt`;

    if (p2) {
      if (this.el.tourneyP2Name) this.el.tourneyP2Name.textContent = p2.display_name;
      if (this.el.tourneyP2Avatar) this.el.tourneyP2Avatar.src = p2.avatar_url || "https://cdn.discordapp.com/embed/avatars/1.png";
      if (this.el.tourneyP2Score) this.el.tourneyP2Score.textContent = `${p2.score} Pkt`;
    } else {
      if (this.el.tourneyP2Name) this.el.tourneyP2Name.textContent = "Freilos (Bye)";
      if (this.el.tourneyP2Avatar) this.el.tourneyP2Avatar.src = "https://cdn.discordapp.com/embed/avatars/2.png";
      if (this.el.tourneyP2Score) this.el.tourneyP2Score.textContent = "-";
    }

    // Active Turn Highlight
    const gameState = match.game_state;
    if (gameState && gameState.current_turn) {
      if (gameState.current_turn === p1.user_id) {
        this.el.tourneyP1Card.classList.add("turn-active");
        this.el.tourneyP2Card.classList.remove("turn-active");
      } else if (p2 && gameState.current_turn === p2.user_id) {
        this.el.tourneyP2Card.classList.add("turn-active");
        this.el.tourneyP1Card.classList.remove("turn-active");
      } else {
        this.el.tourneyP1Card.classList.remove("turn-active");
        this.el.tourneyP2Card.classList.remove("turn-active");
      }
    } else {
      this.el.tourneyP1Card.classList.remove("turn-active");
      this.el.tourneyP2Card.classList.remove("turn-active");
    }

    // Board Rendering
    const gameType = match.game_type;
    if (this.el.tourneyTttBoard) this.el.tourneyTttBoard.style.display = (gameType === "tictactoe") ? "grid" : "none";
    if (this.el.tourneyC4Board) this.el.tourneyC4Board.style.display = (gameType === "connect4") ? "flex" : "none";
    if (this.el.tourneyRpsBoard) this.el.tourneyRpsBoard.style.display = (gameType === "rps") ? "flex" : "none";

    if (gameType === "tictactoe" && gameState) {
      const winningLine = gameState.winning_line || [];
      const isNewMove = (idx) => {
        return gameState.last_move === idx && (!this.prevTourneyTTTBoard || this.prevTourneyTTTBoard[idx] !== gameState.board[idx]);
      };
      (gameState.board || []).forEach((val, idx) => {
        const cell = this.el.tourneyTttCells[idx];
        if (cell) {
          cell.textContent = val;
          cell.className = "cell";
          if (val === "X") cell.classList.add("cell-x", "taken");
          if (val === "O") cell.classList.add("cell-o", "taken");
          if (winningLine.includes(idx)) cell.classList.add("winner-cell");
          if (val && isNewMove(idx)) cell.classList.add("anim-pop");
        }
      });
      this.prevTourneyTTTBoard = [...(gameState.board || [])];
    } else if (gameType === "connect4" && gameState) {
      const rows = gameState.rows || 6;
      const cols = gameState.cols || 7;
      const totalCells = rows * cols;

      if (this.currentTourneyC4Cols !== cols || this.currentTourneyC4Rows !== rows || this.el.tourneyC4Grid.children.length !== totalCells) {
        this.currentTourneyC4Cols = cols;
        this.currentTourneyC4Rows = rows;
        this.prevTourneyC4Board = null;
        const availableWidth = Math.min(window.innerWidth - 40, 460);
        const cellSize = Math.floor(Math.min(42, Math.max(26, (availableWidth - (cols * 6) - 20) / cols)));

        this.el.tourneyC4Grid.style.setProperty("--c4-cols", cols);
        this.el.tourneyC4Grid.style.setProperty("--c4-rows", rows);
        this.el.tourneyC4Grid.style.setProperty("--c4-cell-size", `${cellSize}px`);

        this.el.tourneyC4DropRow.style.setProperty("--c4-cols", cols);
        this.el.tourneyC4DropRow.style.setProperty("--c4-cell-size", `${cellSize}px`);

        // Drop buttons
        this.el.tourneyC4DropRow.innerHTML = "";
        for (let c = 0; c < cols; c++) {
          const btn = document.createElement("button");
          btn.className = "c4-drop-btn";
          btn.dataset.col = c;
          btn.textContent = "▼";
          btn.addEventListener("click", () => this.makeMoveTournamentC4(c));
          this.el.tourneyC4DropRow.appendChild(btn);
        }

        // Cells
        this.el.tourneyC4Grid.innerHTML = "";
        for (let i = 0; i < totalCells; i++) {
          const cell = document.createElement("div");
          cell.className = "c4-cell";
          cell.dataset.index = i;
          const col = i % cols;
          cell.addEventListener("click", () => this.makeMoveTournamentC4(col));
          this.el.tourneyC4Grid.appendChild(cell);
        }
      }

      const winningLine = gameState.winning_line || [];
      const cells = this.el.tourneyC4Grid.querySelectorAll(".c4-cell");
      const cellSize = parseInt(getComputedStyle(this.el.tourneyC4Grid).getPropertyValue("--c4-cell-size")) || 40;
      const isNewMove = (idx) => {
        return gameState.last_move === idx && (!this.prevTourneyC4Board || this.prevTourneyC4Board[idx] !== gameState.board[idx]);
      };

      (gameState.board || []).forEach((val, idx) => {
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
          }
        }
      });
      this.prevTourneyC4Board = [...(gameState.board || [])];
    } else if (gameType === "rps" && gameState) {
      const emojis = { rock: "✊", paper: "✋", scissors: "✌️", lizard: "🦎", spock: "🖖", locked: "🔒", "": "❓" };
      this.el.tourneyRpsRoundBadge.textContent = `Runde ${gameState.current_round || 1}`;

      const picks = gameState.current_picks || {};
      const myPick = picks[p1.user_id] || "";
      const otherPick = p2 ? (picks[p2.user_id] || "") : "";

      this.el.tourneyRpsP1Pick.textContent = emojis[myPick] || "❓";
      this.el.tourneyRpsP2Pick.textContent = emojis[otherPick] || "❓";

      this.el.tourneyRpsP1Pick.className = "rps-fighter-pick";
      this.el.tourneyRpsP2Pick.className = "rps-fighter-pick";

      this.el.tourneyRpsP1Label.textContent = p1.display_name;
      this.el.tourneyRpsP2Label.textContent = p2 ? p2.display_name : "Gegner";

      if (gameState.last_round_result) {
        const lr = gameState.last_round_result;
        if (this.prevTourneyRpsRound !== gameState.current_round) {
          this.el.tourneyRpsP1Pick.classList.add("anim-reveal");
          this.el.tourneyRpsP2Pick.classList.add("anim-reveal");
        }
        if (lr.winner === "draw") {
          this.el.tourneyRpsRoundResult.textContent = `Gleichstand in Runde ${lr.round}!`;
          this.el.tourneyRpsRoundResult.style.color = "#ffb703";
        } else {
          const wName = lr.winner === p1.user_id ? p1.display_name : (p2 ? p2.display_name : "Gegner");
          this.el.tourneyRpsRoundResult.textContent = `🎉 ${wName} hat die Runde gewonnen!`;
          this.el.tourneyRpsRoundResult.style.color = "#23a55a";
        }
      } else if (myPick && !otherPick) {
        this.el.tourneyRpsRoundResult.textContent = "Wahl eingeloggt! Warte auf Gegner...";
        this.el.tourneyRpsRoundResult.style.color = "#ffb703";
        this.el.tourneyRpsP2Pick.classList.add("anim-shake");
      } else {
        this.el.tourneyRpsRoundResult.textContent = "Wähle deine Geste!";
        this.el.tourneyRpsRoundResult.style.color = "#94a3b8";
      }
      this.prevTourneyRpsRound = gameState.current_round;
    }

    // Status bar text
    if (match.status === "finished") {
      if (match.winner_id === "draw") {
        this.el.tourneyStatusBar.textContent = "🤝 Match endete unentschieden!";
        this.el.tourneyStatusBar.style.color = "#f0b232";
      } else {
        const winnerName = match.winner_id === p1.user_id ? p1.display_name : (p2 ? p2.display_name : "Gegner");
        this.el.tourneyStatusBar.textContent = `🏆 ${winnerName} gewinnt das Duell!`;
        this.el.tourneyStatusBar.style.color = "#23a55a";
      }
    } else {
      if (match.is_bye) {
        this.el.tourneyStatusBar.textContent = `⚡ ${p1.display_name} hat ein Freilos (Bye)!`;
        this.el.tourneyStatusBar.style.color = "#23a55a";
      } else if (gameState?.current_turn === this.user.id) {
        this.el.tourneyStatusBar.textContent = "⚡ Du bist am Zug!";
        this.el.tourneyStatusBar.style.color = "#5865f2";
      } else {
        const isParticipant = (this.user.id === p1.user_id || (p2 && this.user.id === p2.user_id));
        if (isParticipant) {
          this.el.tourneyStatusBar.textContent = "⏳ Gegner ist am Zug...";
          this.el.tourneyStatusBar.style.color = "#94a3b8";
        } else {
          this.el.tourneyStatusBar.textContent = `📺 Live-Zuschauer: ${p1.display_name} vs ${p2 ? p2.display_name : "Gegner"}`;
          this.el.tourneyStatusBar.style.color = "#94a3b8";
        }
      }
    }

    // Cheers animation
    if (match.cheers && match.cheers.length > 0) {
      if (match.cheers.length > this.renderedCheerCount) {
        const newCheers = match.cheers.slice(this.renderedCheerCount);
        newCheers.forEach(c => this.spawnFloatingCheer(c.name, c.emote));
        this.renderedCheerCount = match.cheers.length;
      }
    } else {
      this.renderedCheerCount = 0;
    }

    // Round End Controls
    if (this.el.tourneyRoundEndControls) {
      if (tourney.status === "round_end") {
        this.el.tourneyRoundEndControls.style.display = "block";
        const isHost = this.isTournamentHost();
        if (isHost) {
          this.el.tourneyNextRoundBtn.style.display = "inline-block";
          if (this.el.tourneyNextGameSelector) this.el.tourneyNextGameSelector.style.display = "block";
          this.el.tourneyRoundEndMsg.textContent = `Runde ${tourney.current_round} beendet! Wähle das Spiel und starte Runde ${tourney.current_round + 1}:`;
        } else {
          this.el.tourneyNextRoundBtn.style.display = "none";
          if (this.el.tourneyNextGameSelector) this.el.tourneyNextGameSelector.style.display = "none";
          this.el.tourneyRoundEndMsg.textContent = `Runde ${tourney.current_round} beendet! Warte auf den Turnierleiter...`;
        }
      } else {
        this.el.tourneyRoundEndControls.style.display = "none";
      }
    }

    // Leaderboard Drawer Content
    if (this.el.tourneyLiveLeaderboardList) {
      const medals = ["🥇", "🥈", "🥉"];
      let lbHtml = "";
      (tourney.leaderboard || []).forEach((p, idx) => {
        const rankDisplay = idx < 3 ? medals[idx] : `#${idx + 1}`;
        const isYou = p.user_id === this.user.id;
        lbHtml += `
          <div class="tourney-leaderboard-row ${idx === 0 ? 'rank-1' : ''}">
            <div class="tourney-leaderboard-meta">
              <span class="tourney-rank-num">${rankDisplay}</span>
              <img class="lobby-player-avatar-small" src="${p.avatar_url || 'https://cdn.discordapp.com/embed/avatars/0.png'}" alt="Avatar">
              <span style="font-weight: 700;">${p.display_name}</span>
              ${isYou ? '<span class="lobby-tag-you">Du</span>' : ''}
              ${p.is_host ? '<span>👑</span>' : ''}
              ${p.is_eliminated ? '<span style="font-size:0.7rem; color:#da373c;">(Ausgeschieden)</span>' : ''}
            </div>
            <div class="tourney-leaderboard-scores">
              <span class="tourney-score-points">${p.score} Pkt</span>
              <span class="tourney-score-record">${p.wins}S - ${p.losses}N</span>
            </div>
          </div>
        `;
      });
      this.el.tourneyLiveLeaderboardList.innerHTML = lbHtml;
    }
  }

  renderTournamentPodium(tourney) {
    if (!tourney) return;
    const isHost = this.isTournamentHost();
    const leaderboard = tourney.leaderboard || [];

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
              <img class="podium-avatar" src="${p2.avatar_url || 'https://cdn.discordapp.com/embed/avatars/1.png'}" alt="2nd">
              <span class="podium-medal">🥈</span>
            </div>
            <div class="podium-name">${p2.display_name}</div>
            <div class="podium-score">${p2.score} Pkt</div>
          </div>
        `;
      }

      // 1st Place (Center, Gold)
      if (p1) {
        podiumHtml += `
          <div class="podium-step podium-step-1">
            <div class="podium-avatar-wrap">
              <img class="podium-avatar" src="${p1.avatar_url || 'https://cdn.discordapp.com/embed/avatars/0.png'}" alt="1st">
              <span class="podium-medal">🥇</span>
            </div>
            <div class="podium-name">${p1.display_name}</div>
            <div class="podium-score">${p1.score} Pkt</div>
          </div>
        `;
      }

      // 3rd Place (Right)
      if (p3) {
        podiumHtml += `
          <div class="podium-step podium-step-3">
            <div class="podium-avatar-wrap">
              <img class="podium-avatar" src="${p3.avatar_url || 'https://cdn.discordapp.com/embed/avatars/2.png'}" alt="3rd">
              <span class="podium-medal">🥉</span>
            </div>
            <div class="podium-name">${p3.display_name}</div>
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
              <img class="lobby-player-avatar-small" src="${p.avatar_url || 'https://cdn.discordapp.com/embed/avatars/0.png'}" alt="Avatar">
              <span>${p.display_name}</span>
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

  makeMoveTournamentTTT(cellIndex) {
    const match = this.getCurrentTournamentMatch();
    if (!match || match.status !== "active" || match.game_type !== "tictactoe") return;
    if (match.game_state?.current_turn !== this.user.id) return;
    if (match.game_state?.board?.[cellIndex] !== "") return;
    this.sendAction("tournament_match_action", {
      match_id: match.match_id,
      sub_action: "move",
      sub_data: { cell: cellIndex }
    });
  }

  makeMoveTournamentC4(col) {
    const match = this.getCurrentTournamentMatch();
    if (!match || match.status !== "active" || match.game_type !== "connect4") return;
    if (match.game_state?.current_turn !== this.user.id) return;
    this.sendAction("tournament_match_action", {
      match_id: match.match_id,
      sub_action: "move",
      sub_data: { col: col }
    });
  }

  makeMoveTournamentRPS(choice) {
    const match = this.getCurrentTournamentMatch();
    if (!match || match.status !== "active" || match.game_type !== "rps") return;
    this.el.tourneyRpsBtns.forEach(btn => {
      btn.classList.toggle("selected", btn.dataset.tourneyRps === choice);
    });
    this.sendAction("tournament_match_action", {
      match_id: match.match_id,
      sub_action: "pick",
      sub_data: { choice: choice }
    });
  }

  spawnFloatingCheer(name, emote) {
    if (!this.el.tourneyCheerOverlay) return;
    const cheerEl = document.createElement("div");
    cheerEl.className = "floating-cheer";
    const leftPercent = Math.floor(15 + Math.random() * 70);
    cheerEl.style.left = `${leftPercent}%`;
    cheerEl.innerHTML = `
      <span>${emote}</span>
      <span class="floating-cheer-name">${name}</span>
    `;
    this.el.tourneyCheerOverlay.appendChild(cheerEl);
    setTimeout(() => {
      if (cheerEl.parentNode) cheerEl.remove();
    }, 2400);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  window.app = new TanjunActivityClient();
  window.app.init();
});
