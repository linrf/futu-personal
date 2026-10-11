#!/usr/bin/env python3
"""Validate the local package and its declared tool boundary, offline."""

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOCKED = {"trading_order_place", "trading_order_replace", "trading_order_cancel", "trading_order_confirm"}
SIM_WRITES = {"sim_trade_input_order", "sim_trade_modify_order", "sim_trade_cancel_order"}


def documented_tools():
    names = set()
    for p in (ROOT / "skills").rglob("*.md"):
        text = p.read_text()
        if p.name == "SKILL.md":
            names.update(re.findall(r"`((?:quote|account|sim_trade)_[a-z0-9_]+)`", text))
        else:
            for heading in re.findall(r"^#{1,4} (.+)$", text, re.M):
                names.update(re.findall(r"\b(?:quote|account|sim_trade)_[a-z0-9_]+\b", heading))
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
    allowed = set(server["enabled_tools"])
    assert allowed and len(allowed) == len(server["enabled_tools"])
    assert not allowed & BLOCKED
    assert BLOCKED <= set(server["disabled_tools"])
    assert SIM_WRITES <= allowed
    assert "quote_modify_user_security" not in allowed
    assert server["default_tools_approval_mode"] == "prompt"
    assert all(re.fullmatch(r"(?:quote|account|sim_trade)_[a-z0-9_]+", name) for name in allowed)
    assert allowed <= documented_tools(), f"Undocumented tool names: {allowed - documented_tools()}"
    marketplace = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
    assert marketplace["name"] == "futu-personal-local"
    entry, = marketplace["plugins"]
    assert entry["name"] == manifest["name"]
    assert entry["source"]["source"] == "local"
    assert local_path(entry["source"]["path"]) == ROOT
    names = set()
    for skill in sorted(skills_dir.glob("*/SKILL.md")):
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
    assert len(names) == 5, names
    for p in (ROOT / "scripts").glob("*.py"):
        ast.parse(p.read_text(), filename=str(p))
    assert "Copyright (c) 2026 Futu" in (ROOT / "LICENSE").read_text()
    prefs = json.loads((ROOT / "preferences.json").read_text())
    assert prefs["order_execution"] == "manual"
    assert prefs["max_pages"] > 0 and prefs["max_rows"] > 0
    print(f"PASS: plugin, marketplace, {len(names)} skills, references, {len(allowed)} allowed tool names; live execution excluded")


if __name__ == "__main__":
    main()
