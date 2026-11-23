from pathlib import Path

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
MARKER = "<!-- @ROUNDS@ -->"
SECTIONS = ("probability", "statistics", "score")


def render_index() -> str:
    html = (FRONTEND / "index.html").read_text()
    parts = [
        (FRONTEND / "sections" / f"{name}.html").read_text()
        for name in SECTIONS
    ]
    return html.replace(MARKER, "\n".join(parts))
