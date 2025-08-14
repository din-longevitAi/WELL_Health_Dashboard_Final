#!/usr/bin/env python3
from pathlib import Path
import re

DASHBOARD_PATH = Path(__file__).with_name("executive_dashboard.html")
OUTPUT_PATH = Path(__file__).with_name("executive_dashboard_standalone.html")
PLOTS_DIR = Path(__file__).with_name("plots")

IFRAME_PATTERN = re.compile(r'<iframe[^>]*src="(?P<src>plots/[^"]+)"[^>]*></iframe>')


def inline_dashboard():
    if not DASHBOARD_PATH.exists():
        raise FileNotFoundError(f"Dashboard HTML not found: {DASHBOARD_PATH}")
    if not PLOTS_DIR.exists():
        raise FileNotFoundError(f"Plots directory not found: {PLOTS_DIR}")

    html = DASHBOARD_PATH.read_text(encoding="utf-8")

    def replace_iframe(match: re.Match) -> str:
        rel_src = match.group("src")
        plot_path = PLOTS_DIR / Path(rel_src).name
        if not plot_path.exists():
            print(f"[WARN] Missing plot file referenced in dashboard: {rel_src}")
            # Keep original iframe so at least structure remains
            return match.group(0)
        plot_html = plot_path.read_text(encoding="utf-8")
        # Extract only the <body> content to avoid duplicating <html>/<head>
        body_match = re.search(r"<body[^>]*>([\s\S]*?)</body>", plot_html, re.IGNORECASE)
        inner = body_match.group(1) if body_match else plot_html
        # Wrap in a container to maintain layout; ensure full width
        wrapped = (
            '<div class="embedded-plot" style="width:100%; min-height:560px;">\n'
            + inner +
            '\n</div>'
        )
        return wrapped

    inlined = IFRAME_PATTERN.sub(replace_iframe, html)

    # Add a small note in HTML that this is a standalone build
    inlined = inlined.replace(
        "</head>",
        "\n    <!-- Standalone build: all plots embedded inline -->\n</head>",
    )

    # Write output
    OUTPUT_PATH.write_text(inlined, encoding="utf-8")
    print(f"✅ Wrote standalone dashboard: {OUTPUT_PATH}")


if __name__ == "__main__":
    inline_dashboard()
