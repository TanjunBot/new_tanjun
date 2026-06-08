# Doc screenshots (Playwright)

Automated captures for documentation images using a **real Discord user account** in Chromium—not the bot token. The bot only needs to be in the same test server and respond to slash commands.

## One-time setup

### 1. Discord test account

Create a dedicated Discord account (or use a spare) for automation only:

- Enable a password; note 2FA if you use it (you log in manually once).
- Do **not** use your personal main account if you can avoid it.
- Discord’s Terms restrict self-bots and automating user accounts; this flow is for **local doc maintenance**, not production scraping at scale.

### 2. Test server

1. Create a private **documentation / QA** guild (only you and the test user need access).
2. Invite **Tanjun** (production or staging bot) with permissions to use slash commands in a text channel.
3. Copy IDs (Developer Mode → right‑click → Copy ID):

| ID | Env var |
|----|---------|
| Server | `DOC_SCREENSHOT_GUILD_ID` |
| Channel used for captures | `DOC_SCREENSHOT_CHANNEL_ID` |
| Tanjun bot **user** id (not application id) | `DOC_SCREENSHOT_BOT_USER_ID` |

The test user must be able to run slash commands in that channel (no extra roles required beyond normal member access).

### 3. Python dependencies

```bash
pip install -e ".[dev,docs-screenshots]"
playwright install chromium
```

### 4. Environment

Add to `.env` (see `.env.example`):

```env
DOC_SCREENSHOT_GUILD_ID=
DOC_SCREENSHOT_CHANNEL_ID=
DOC_SCREENSHOT_BOT_USER_ID=
# optional:
# DOC_SCREENSHOT_AUTH_STATE=.discord-doc-auth.json
# DOC_SCREENSHOT_HEADLESS=true
```

### 5. Save login session (once per account / when session expires)

```bash
python scripts/generate_doc_screenshots.py login
```

A browser opens → log in as the test user → return to the terminal and press Enter. Session is stored in `.discord-doc-auth.json` (gitignored).

## Capture images

```bash
python scripts/generate_doc_screenshots.py generate
python scripts/generate_doc_screenshots.py generate --only help-overview
python scripts/generate_doc_screenshots.py generate --headed
```

Outputs are written to paths in `docs/screenshots.manifest.yaml`. Reference them in markdown once:

```markdown
![Help command](../assets/screenshots/help-overview.png)
```

## Manifest

Edit `docs/screenshots.manifest.yaml`:

```yaml
shots:
  - id: logs-setup
    slash_command: "/logs setup"
    output: docs/assets/screenshots/logs-setup.png
    wait_ms: 8000
```

Re-run `generate` after bot UI changes; commit updated PNGs.

## Troubleshooting

| Problem | What to try |
|---------|-------------|
| Session expired | Run `login` again |
| Bot reply not detected | Confirm `DOC_SCREENSHOT_BOT_USER_ID` is the **user** id; increase `wait_ms` |
| Slash command missing | Sync commands in the test guild; run the command manually once |
| Input box not found | Discord UI changed—update selectors in `scripts/doc_screenshots/playwright_runner.py` |
| Flaky captures | `generate --headed`, slower network, higher `default_wait_ms` |
