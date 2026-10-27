"""Keep the profile source limited to its reviewed files and static visuals."""
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET


root = Path(__file__).resolve().parent.parent
assets = {"hero.svg", "voicepanel-hero.svg", "support.svg", "boosty.svg", "patreon.svg", "donation-alerts.svg", "voicepanel.svg", "cv-builder.svg", "contributions.svg"}
allowed = {"README.md", "LICENSE", ".gitattributes", ".github/CODEOWNERS", ".github/workflows/profile.yml", "tools/check_profile.py", "tools/update_contributions.py"} | {"assets/" + x for x in assets}
actual = set(subprocess.check_output(["git", "ls-files", "-z"], cwd=root).decode().split("\0")) - {""}
assert actual == allowed, "Unexpected or missing public profile files"
text = (root / "README.md").read_text(encoding="utf-8")
for url in ("https://boosty.to/gdview_gdbrain/donate", "https://dalink.to/flodirka", "https://www.patreon.com/15806620/join"):
    assert url in text, "A reviewed support URL is missing"
assert "assets/contributions.svg" in text, "The public contribution calendar must remain visible"
for asset in assets:
    for item in ET.parse(root / "assets" / asset).getroot().iter():
        assert item.tag.split("}")[-1] not in {"script", "foreignObject"}, "Active SVG content"
        assert not any(k.lower().startswith("on") or k.endswith("href") for k in item.attrib), "External SVG content"
for path in actual:
    content = (root / path).read_text(encoding="utf-8")
    assert not re.search(r"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-(?:proj-)?[A-Za-z0-9_-]{24,})", content), "Credential format detected"
print("Profile inventory, static SVG assets, support URLs and contribution widget checked.")
