import re
from dataclasses import dataclass

ANSI_REGEX = re.compile(r"\x1b\[([0-9;]*)m")

COLOR_MAP = {
    30: "#000000",
    31: "#cc0000",
    32: "#00aa00",
    33: "#aa8800",
    34: "#0000aa",
    35: "#aa00aa",
    36: "#00aaaa",
    37: "#aaaaaa",

    90: "#555555",
    91: "#ff5555",
    92: "#55ff55",
    93: "#ffff55",
    94: "#5555ff",
    95: "#ff55ff",
    96: "#55ffff",
    97: "#ffffff",
}

@dataclass
class Style:
    color: str | None = None
    bold: bool = False
    underline: bool = False

    def to_css(self):
        css = []
        if self.color:
            css.append(f"color:{self.color}")
        if self.bold:
            css.append("font-weight:bold")
        if self.underline:
            css.append("text-decoration:underline")
        return ";".join(css)

    def reset(self):
        self.color = None
        self.bold = False
        self.underline = False


def ansi_to_html(text: str) -> str:
    style = Style()
    output = []
    last = 0

    for match in ANSI_REGEX.finditer(text):
        output.append(escape(text[last:match.start()]))

        codes = match.group(1)
        for code in map(int, filter(None, codes.split(";") or ["0"])):
            if code == 0:
                style.reset()
            elif code == 1:
                style.bold = True
            elif code == 4:
                style.underline = True
            elif code in COLOR_MAP:
                style.color = COLOR_MAP[code]

        span_start = f'<span style="{style.to_css()}">' if style.to_css() else ""
        span_end = "</span>" if span_start else ""

        output.append(span_start)
        last = match.end()

    output.append(escape(text[last:]))

    return "<pre>" + "".join(output) + "</pre>"

def escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
    )