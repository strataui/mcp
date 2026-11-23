# Strata MCP Demo

Standalone example application and external JSON-RPC 2.0 Model Context Protocol (MCP) automation client for [Strata](https://github.com/strataui/strata).

## Overview

Every Strata desktop application automatically starts an in-process MCP dev bridge listener (`$XDG_RUNTIME_DIR/strata-dev.sock`) on launch. External AI agents and test tools connect through the [`strata-mcp`](https://github.com/strataui/strata/tree/main/crates/tooling/strata_mcp) stdio server to inspect UI layout elements, drive an emulated rendered Yaru cursor, send keyboard input, and capture rendered surface screenshots—without touching the user's real OS hardware mouse or keyboard.

This repository provides:

- **Target Application (`src/main.rs`):** A clean `720x520` Strata UI window featuring live reactive state (`Click Counter`, `Accent State`, `Increment +1`, `Toggle Accent`, `Reset`, and an `<input>` box).
- **External MCP Client (`mcp_click_test.py`):** A zero-dependency Python JSON-RPC 2.0 driver that spawns `strata-mcp` over stdio, discovers element coordinates dynamically via `strata_inspect_element`, clicks buttons, types into the focused input, and captures a screenshot via `strata_take_screenshot`.

## Quick Start

### 1. Build & Launch the Target App

```bash
cargo run --release
```

### 2. Drive It Externally via `strata-mcp`

Build or install `strata-mcp` from the `strata` workspace (or ensure `strata-mcp` is on your `PATH`), then run:

```bash
python3 mcp_click_test.py /tmp/mcp_demo_after.png
```

Optionally override the `strata-mcp` binary path:

```bash
STRATA_MCP_BIN=/path/to/strata-mcp python3 mcp_click_test.py /tmp/mcp_demo_after.png
```

## MCP Tools Exercised

- `strata_session_info` — Queries viewport dimensions, DPR, cursor theme, and active focus.
- `strata_inspect_element` — Probes layout bounds, tags, and text at `(x, y)` coordinates.
- `strata_mouse_click` — Dispatches synthetic clicks to buttons and input fields.
- `strata_keyboard_type` — Types text character-by-character into the focused input element.
- `strata_mouse_move` — Moves the rendered Yaru pointer overlay smoothly across the viewport.
- `strata_take_screenshot` — Captures the rendered surface PNG including the emulated cursor overlay.

## Verification

```bash
cargo check --all-targets
cargo build
```

## License

Licensed under the MIT License. See [LICENSE](LICENSE) for details.
