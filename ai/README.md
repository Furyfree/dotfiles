# AI Terminal Setup
**Claude + OpenCode + Gemini + Codex + Local Models**

---

## Overview
Turn your terminal into a full AI control center powered by **Claude Code** as the main orchestrator.
Connected to:
- **OpenCode** → unified multi-model access (Claude, GPT-5, Grok, etc.)
- **Gemini CLI** → free Google AI
- **OpenAI Codex CLI** → advanced code reasoning
- **Local Models (GPT-OSS-20B, Mistral, etc.)** → offline use
- **GitHub Copilot** → IDE completions (auto-linked to OpenCode)

---

## ⚙️ Installation

### 1. Install CLIs
```bash
sudo npm install -g @anthropic-ai/claude-code
sudo npm install -g @openai/codex
sudo npm install -g @google/gemini-cli
sudo npm i -g opencode-ai
```

### 2. Local models via Ollama
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gpt-oss:20b
ollama pull mistral:7b
```

### 3. Configure OpenCode
Symlink opencode config:
```bash
ln -sf ~/git/dotfiles/linux/.config/opencode ~/.config/
```

## Login / Authentication
Run all the CLI's to set them up:
```bash
claude
gemini
codex
```
