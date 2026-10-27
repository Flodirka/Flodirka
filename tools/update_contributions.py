"""Render a dated contribution calendar from unauthenticated public GitHub HTML."""
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
import re
import urllib.request


class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.days = {}
        self.labels = {}
        self.label_for = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "td" and re.fullmatch(r"\d{4}-\d{2}-\d{2}", attrs.get("data-date", "")):
            self.days[attrs["id"]] = (date.fromisoformat(attrs["data-date"]), int(attrs.get("data-level", 0)))
        if tag == "tool-tip":
            self.label_for = attrs.get("for")

    def handle_endtag(self, tag):
        if tag == "tool-tip":
            self.label_for = None

    def handle_data(self, data):
        if self.label_for:
            self.labels[self.label_for] = self.labels.get(self.label_for, "") + data


request = urllib.request.Request("https://github.com/users/Flodirka/contributions", headers={"User-Agent": "Flodirka-public-profile"})
with urllib.request.urlopen(request, timeout=30) as response:
    source = response.read().decode("utf-8")
calendar = Calendar()
calendar.feed(source)
assert 350 <= len(calendar.days) <= 380, "Public calendar markup changed; no asset was updated"
first = min(day for day, _ in calendar.days.values())
last = max(day for day, _ in calendar.days.values())
palette = ["#27212f", "#693d23", "#a55b27", "#d97e2e", "#ee9a3a"]
rects = []
total = 0
for key, (day, level) in sorted(calendar.days.items(), key=lambda pair: pair[1][0]):
    label = calendar.labels.get(key, "").strip()
    count_match = re.match(r"([\d,]+) contributions?", label)
    count = int(count_match[1].replace(",", "")) if count_match else 0
    total += count
    week = (day - first).days // 7
    row = (day.weekday() + 1) % 7
    rects.append(f'<rect x="{92 + week * 19}" y="{84 + row * 19}" width="15" height="15" rx="3" fill="{palette[min(4, max(0, level))]}"><title>{day}: {count} contributions</title></rect>')
body = f'<rect width="1200" height="275" rx="20" fill="#110e16"/><text x="40" y="43" fill="#faf1cc" font-family="Arial,sans-serif" font-size="23" font-weight="700">{total:,} public contributions shown</text><text x="40" y="245" fill="#c9bd9a" font-family="Arial,sans-serif" font-size="15">Calendar through {last} · public GitHub data · github.com/Flodirka</text>'
for label, row in [("Mon", 1), ("Wed", 3), ("Fri", 5)]:
    body += f'<text x="40" y="{96 + row * 19}" fill="#c9bd9a" font-family="Arial,sans-serif" font-size="12">{label}</text>'
body += "".join(rects)
output = '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="275" viewBox="0 0 1200 275" role="img" aria-label="Public GitHub contribution calendar">' + body + '</svg>\n'
(Path(__file__).resolve().parent.parent / "assets/contributions.svg").write_text(output, encoding="utf-8")
print(f"Rendered {len(calendar.days)} public day cells. No authentication or private activity was requested.")
