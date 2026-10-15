# -*- coding: utf-8 -*-
"""Собирает Hanyu Arcade: артефакт (библиотека с CDN) и автономный HTML (библиотека внутри)."""
import json
import sys
from pathlib import Path

CHARS = "除了汉语以外我还学英对很感兴趣"
CDN_TAG = '<script src="https://cdn.jsdelivr.net/npm/hanzi-writer@3.7.3/dist/hanzi-writer.min.js"></script>'
KEEP = ("strokes", "medians", "radStrokes")


def course_tag(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data.get("chapters"), list) or not isinstance(data.get("dictionary"), list):
        sys.exit("в content.json нет chapters или dictionary")
    for ch in data["chapters"]:
        if not {"id", "title", "html"} <= ch.keys():
            sys.exit("битый раздел конспекта: " + str(ch.get("id")))
    for w in data["dictionary"]:
        if not {"hanzi", "pinyin", "meaning", "topic"} <= w.keys():
            sys.exit("битое слово словаря: " + str(w))
    raw = json.dumps({"chapters": data["chapters"], "dictionary": data["dictionary"]}, ensure_ascii=False, separators=(",", ":"))
    raw = raw.replace("</", "<\\/").replace("<!--", "<\\u0021--")
    return '<script type="application/json" id="course-data">' + raw + "</script>"


def load_strokes(folder: Path) -> dict:
    data = {}
    for ch in CHARS:
        path = folder / ("%X.json" % ord(ch))
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw.get("strokes"), list) or not isinstance(raw.get("medians"), list):
            sys.exit("битые данные черт: " + ch)
        if len(raw["strokes"]) != len(raw["medians"]):
            sys.exit("strokes и medians не совпадают: " + ch)
        data[ch] = {k: raw[k] for k in KEEP if k in raw}
    return data


def main() -> None:
    base, vendor, standalone_out, course = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
    template = (base / "template.html").read_text(encoding="utf-8")
    strokes = json.dumps(load_strokes(base / "strokes_dl"), ensure_ascii=False, separators=(",", ":"))
    for marker in ("/*__STROKES__*/{}", "<!--__HANZI_WRITER__-->", "<!--__COURSE__-->"):
        if template.count(marker) != 1:
            sys.exit("маркер не найден ровно один раз: " + marker)
    page = template.replace("/*__STROKES__*/{}", strokes).replace("<!--__COURSE__-->", course_tag(course))

    artifact = page.replace("<!--__HANZI_WRITER__-->", CDN_TAG)
    (base / "hanyu-arcade.html").write_text(artifact, encoding="utf-8")

    lib = (vendor / "hanzi-writer.min.js").read_text(encoding="utf-8")
    inline = "<script>/* Hanzi Writer 3.7.3, MIT License, (c) David Chanin */\n" + lib + "\n</script>"
    body = page.replace("<!--__HANZI_WRITER__-->", inline)
    head_end = body.index("</style>") + len("</style>")
    standalone = (
        '<!doctype html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<meta name="robots" content="noindex, nofollow">\n'
        '<meta name="description" content="Как устроена система для изучения китайского: конспект, домашка, карточки Anki, прописи, разбор знаков и словарь.">\n'
        '<meta property="og:title" content="Система для изучения китайского">\n'
        '<meta property="og:description" content="Пять материалов к каждому уроку, весь учебный конспект и словарь на 772 слова.">\n'
        '<meta property="og:type" content="website">\n'
        + body[:head_end]
        + "\n<style>body{margin:0}img{max-width:100%}</style>\n</head>\n<body>\n"
        + body[head_end:]
        + "\n</body>\n</html>\n"
    )
    standalone_out.write_text(standalone, encoding="utf-8")
    print("артефакт:", len(artifact.encode()), "байт; автономный:", len(standalone.encode()), "байт")


if __name__ == "__main__":
    main()
