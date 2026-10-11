#!/usr/bin/env python3
"""Validate full MCP discovery, OAuth scopes, and local skill resources, offline."""

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REAL_OPERATIONS = {"trading_order_place", "trading_order_replace", "trading_order_cancel", "trading_order_confirm"}
SIM_WRITES = {"sim_trade_input_order", "sim_trade_modify_order", "sim_trade_cancel_order"}
SCOPES = {"quote:read", "quote:write", "trade:read", "trade:write", "accid:*"}
CRYPTO_OPERATIONS = {"crypto_account_create_order", "crypto_account_modify_order", "crypto_account_cancel_order"}
WORKFLOWS = {f"workflow-{name}.md" for name in ("quote", "screen", "news", "account", "crypto", "order-draft")}
PARAMETER_REFERENCES = {
    "quote-realtime.md", "quote-tick.md", "quote-watchlist.md", "quote-screening.md",
    "quote-options.md", "quote-futures-warrants.md", "quote-news.md", "quote-financials.md",
    "quote-research.md", "quote-shareholders.md", "quote-corporate-actions.md", "quote-capital.md",
    "quote-short-broker.md", "trading-real.md", "trading-real-order.md", "trading-sim.md",
}


def documented_tools():
    names = set()
    for p in (ROOT / "skills").rglob("*.md"):
        text = p.read_text()
        names.update(re.findall(r"`((?:quote|account|sim_trade|trading_order|crypto_account)_[a-z0-9_]+)`", text))
        for heading in re.findall(r"^#{1,4} (.+)$", text, re.M):
            names.update(re.findall(r"\b(?:quote|account|sim_trade|trading_order|crypto_account)_[a-z0-9_]+\b", heading))
    return names


def local_path(value, base=ROOT):
    assert value.startswith("./"), f"Path must start with ./: {value}"
    p = (base / value).resolve()
    assert p.is_relative_to(ROOT), f"Path outside package: {value}"
    assert p.exists(), f"Missing resource: {value}"
    return p


def main():
    for p in ROOT.rglob("*.json"):
        if ".git" not in p.parts:
            json.loads(p.read_text())
    manifest = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())
    assert manifest["name"] == "futu-personal"
    skills_dir = local_path(manifest["skills"])
    mcp = json.loads(local_path(manifest["mcpServers"]).read_text())
    server = mcp["mcpServers"]["futu-personal"]
    assert server["url"] == "https://mcp.futunn.com/mcp"
    assert "enabled_tools" not in server, "Full discovery must not use an allowlist"
    assert "disabled_tools" not in server, "Full discovery must not use a denylist"
    assert not server.get("tools"), "Full discovery must not disable individual tools"
    assert set(server["scopes"]) == SCOPES and len(server["scopes"]) == len(SCOPES)
    assert server["default_tools_approval_mode"] == "prompt"
    assert REAL_OPERATIONS | SIM_WRITES | CRYPTO_OPERATIONS | {"quote_modify_user_security", "sim_trade_history_order_list", "quote_combo_option_quote", "quote_option_strategy", "quote_option_strategy_spread"} <= documented_tools()
    marketplace = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
    assert marketplace["name"] == "futu-personal-local"
    entry, = marketplace["plugins"]
    assert entry["name"] == manifest["name"]
    assert entry["source"]["source"] == "local"
    assert local_path(entry["source"]["path"]) == ROOT
    names = set()
    for skill in sorted(skills_dir.rglob("SKILL.md")):
        text = skill.read_text()
        front = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
        assert front, f"Missing frontmatter: {skill}"
        name = re.search(r"^name: ([a-z0-9-]+)$", front[1], re.M)[1]
        assert name == skill.parent.name and name not in names
        assert re.search(r"^description: .+", front[1], re.M)
        names.add(name)
        for ref in re.findall(r"reference/[a-z0-9-]+\.md", text):
            assert (skill.parent / ref).is_file(), f"Missing {ref} in {name}"
        assert not skill.parent.is_symlink()
    assert names == {"futu-personal"}, names
    assert list(skills_dir.rglob("SKILL.md")) == [skills_dir / "futu-personal/SKILL.md"]
    references = skills_dir / "futu-personal/reference"
    assert {p.name for p in references.glob("*.md")} == WORKFLOWS | PARAMETER_REFERENCES
    for p in skills_dir.rglob("*.md"):
        text = p.read_text()
        targets = re.findall(r"\[[^\]]*\]\(([^)]+)\)", text)
        targets += re.findall(r"`((?:reference/|\./|\.\./)[^`]+\.md)`", text)
        for target in targets:
            if re.match(r"[a-z]+://", target) or target.startswith("#"):
                continue
            resource = (p.parent / target.split("#", 1)[0]).resolve()
            assert resource.is_relative_to(ROOT), f"Reference outside package: {p}: {target}"
            assert resource.is_file(), f"Broken reference: {p}: {target}"
        if p.name != "SKILL.md":
            assert not re.match(r"\A---\nname:", text), f"Workflow exposed as skill: {p}"
    for p in (ROOT / "scripts").glob("*.py"):
        ast.parse(p.read_text(), filename=str(p))
    assert "Copyright (c) 2026 Futu" in (ROOT / "LICENSE").read_text()
    prefs = json.loads((ROOT / "preferences.json").read_text())
    assert "order_execution" not in prefs
    assert prefs["operation_confirmation"] == "each_write_operation"
    assert prefs["max_pages"] > 0 and prefs["max_rows"] > 0
    print(f"PASS: plugin, marketplace, {len(names)} skill, {len(WORKFLOWS)} workflows, {len(PARAMETER_REFERENCES)} parameter references, links, full tool discovery, {len(SCOPES)} requested OAuth scopes")


if __name__ == "__main__":
    main()
