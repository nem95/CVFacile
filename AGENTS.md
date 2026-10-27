# CVfacile: instructions for AI agents

CVfacile builds PDF CVs (LaTeX) from a JSON file. You never write LaTeX: edit the JSON, then build.

## Two ways to use it

- **MCP tools** (if your client loads them from `.mcp.json`): `check_cv`, `build_cv`, `list_templates`, `get_schema`.
- **Command line** (always available): add `--json` for machine-readable output.

```sh
./cvfacile doctor --json                 # available tools (LaTeX engine, images)
./cvfacile setup                         # if doctor finds no engine: installs Tectonic into ./.bin
./cvfacile init cv.json                  # create an example CV to fill in
./cvfacile check cv.json --json          # validate without compiling
./cvfacile build cv.json --json          # build -> out/<name>-<lang>.pdf + .png
./cvfacile build cv.json --lang fr --variant no-phone --hide photo,projects --json
./cvfacile build cv.json --template all --json   # one PDF per template, to compare
./cvfacile templates --json              # template names and descriptions
```

Templates: see `examples/README.md` for a render of each one.

## Format

- Full schema: `schema/cv.schema.json`. Full example: `examples/example.json`.
- Any text can be translated: `"label": { "en": "Engineer", "fr": "Développeur" }`. Lists too: `"highlights": { "en": [...], "fr": [...] }`.
- Inline formatting in text: `**bold**` and `[text](https://url)`. Nothing else. Special characters (`&`, `%`, `_`…) are escaped automatically.
- Variants: `"variants": { "name": { ...changes... } }`. Objects are merged, lists replaced, and `hide` removes fields or sections.

## Recommended loop

1. Edit the JSON.
2. `check`: fix every `error` (the `path` field says where, e.g. `$.work[0].position`).
3. `build`: read `warnings`. If the text was reduced to 9pt, `pages` > 1, or there is another `layout` warning, shorten the content (bullets, summary, skills) and build again.
4. Look at the PNG output (or use `preview: true` over MCP) to check the result.

## Rules

- Never invent experience, degrees, numbers or skills: only use what the person provided. Ask them when something is missing.
- A CV fits on one page unless asked otherwise.
- Never put real personal data in `examples/`: this folder is public.

## Working on CVfacile

- Python 3.8+, standard library only (PyYAML and PyMuPDF are optional).
- Tests: `python3 -m unittest discover -s tests`.
- Adding a template: create a module in `src/cvfacile/templates/` with `NAME`, `DESCRIPTION`, `LABELS` and `render(cv, lang, photo_file) -> str`, then register it in `templates/__init__.py`. Build on `templates/common.py`: define the `\cv...` macros and the layout, and let `Context` emit the content (already escaped). Check it with your real-length CV, then run `python3 scripts/render_examples.py` and commit the new renders.
- Every source file starts with `# SPDX-License-Identifier: AGPL-3.0-or-later`.
- Code, comments, docs and messages are in English. CV content and section labels can be in any language.
