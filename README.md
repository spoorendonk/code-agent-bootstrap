# code-agent-bootstrap

Minimal CLAUDE.md template for agentic coding projects.

## Why

AI coding agents (Claude Code, Codex) read a project instruction file on startup.
Most of what agents need — language conventions, project structure, key types — they
discover by reading code. What they can't infer is your **workflow**: when to plan vs
execute, how to coordinate with other agents, and what your git policy is.

This template captures that workflow in ~50 lines. Everything else is noise.

## What's in the template

- **Build/test commands** — the only project-specific thing an agent truly needs upfront
- **Git policy** — no direct commits to main, linear history
- **Plan → Grind workflow** — agent plans first, then executes autonomously on approval
- **Fullgate** — end-to-end PR sequence (branch, sync, test, merge)
- **Claiming work** — `agent-wip` label prevents agents from double-picking issues
- **Teams** — worktree-based isolation for parallel sub-tasks

What's deliberately **not** included: project structure, key types, coding conventions,
architecture docs, dependencies. Agents discover these faster by reading code than
by reading a stale description in a markdown file.

## Usage

### Quick setup (recommended)

Run from your project directory:

```bash
python3 <(curl -fsSL https://raw.githubusercontent.com/spoorendonk/code-agent-bootstrap/master/setup.py)
```

The script will:
- Auto-detect your project type and name
- Prompt for build/test commands with sensible defaults
- Write `CLAUDE.md` and create an `AGENTS.md` symlink

If `CLAUDE.md` already exists, you can choose to overwrite, merge missing
workflow sections, or cancel.

### Manual setup

1. Copy `CLAUDE.md.template` into your repo as `CLAUDE.md`
2. Fill in `{{PROJECT_NAME}}`, `{{BUILD_COMMAND}}`, `{{TEST_COMMAND}}`
3. Add project-specific conventions only if they deviate from standard practice
4. Symlink for Codex: `ln -s CLAUDE.md AGENTS.md`

## Supported tools

| Tool | Entry Point |
|---|---|
| Claude Code | `CLAUDE.md` (auto-loaded) |
| OpenAI Codex | `AGENTS.md` (symlink → CLAUDE.md) |
