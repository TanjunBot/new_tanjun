# AI Features

Tanjun includes GPT-powered AI features for interactive conversations, image generation, and more.

## AI Chat

Engage in conversation with Tanjun's AI:

```
/ai chat <message>
```

The AI maintains context across messages and can be configured with custom "situation prompts" to adjust its personality and behavior.

### Features

- **Context-aware conversations** — The AI remembers recent conversation history
- **Custom situations** — Set a custom prompt to change how the AI responds
- **Multi-turn conversations** — Reply naturally in threads

## Custom Situation Prompts

Server admins can set a custom situation prompt to define the AI's behavior:

```
/ai situation set Your custom prompt here
```

For example:
- _You are a helpful coding assistant that explains concepts simply_
- _You are a friendly bot that speaks like a pirate_
- _You are a strict grammar teacher who corrects every message_

To clear the custom situation:

```
/ai situation clear
```

To view the current situation:

```
/ai situation view
```

## Token Management

The AI uses a token budget to control costs and prevent abuse:

- **Per-user limit** — Each user has a token allowance
- **Server-wide cap** — Optional daily token cap for the server
- **Reset** — Tokens refresh on a configurable schedule

Admins can check token usage:

```
/ai tokens
```

## Image Generation

Generate images using AI (if configured):

```
/ai imagine <description>
```

> **Note:** AI features require API keys to be configured in the `.env` file. See [Environment Variables](../infra/environment.md) for setup details.
