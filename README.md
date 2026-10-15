# Hanyu Arcade

Одностраничный сайт о системе для изучения китайского: пять материалов к уроку, учебный конспект и словарь.

Опубликован на GitHub Pages: https://salutgleb.github.io/hanyu-arcade/

## Пересборка

```
python3 -I src/build.py src ~/.codex/skills/hanyu/scripts/_vendor/hanzi-writer index.html ~/Documents/ChatGPT/Китайский/conspect-web/src/content.json
```

- `src/template.html` — разметка, стили и скрипт страницы.
- `src/strokes_dl/` — данные порядка черт (Hanzi Writer data, MIT).
- Конспект и словарь берутся из учебной копии `conspect-web/src/content.json`, где личные разборы уже убраны.
- Библиотека Hanzi Writer 3.7.3 (MIT) встраивается в `index.html`, поэтому страница работает без внешних скриптов.
