# CVfacile

Clean PDF résumés, typeset with LaTeX from a single JSON file. Built for humans **and** AI agents (Claude Code, Cursor, Codex…).

Website: [nem95.github.io/CVFacile](https://nem95.github.io/CVFacile/) ([français](https://nem95.github.io/CVFacile/fr/), [llms.txt](https://nem95.github.io/CVFacile/llms.txt)).

- **One file, every version**: English and French, with or without a phone number, front-end or back-end focus… all from the same JSON.
- **No LaTeX to write**: text is escaped automatically, with just `**bold**` and `[links](https://…)`.
- **Fits on one page**: if the CV is a bit too long, the text is reduced from 10pt to 9pt automatically (and reported).
- **Agent-ready**: `--json` output, errors with their exact location, "fits on one page" check, PNG preview, MCP tools.
- **Nothing heavy to install**: Python 3.8+ is enough. No server, no required `pip install`.

## Quick start

```sh
git clone https://github.com/nem95/CVFacile.git && cd CVfacile
./cvfacile doctor          # check available tools
./cvfacile setup           # only if no LaTeX is found: installs Tectonic into ./.bin
./cvfacile init mycv.json  # create an example CV
./cvfacile build mycv.json
```

Output: `out/mycv-en.pdf` and `out/mycv-en.png`.

## Templates

10 templates, all from the same JSON file. Pick one with `--template <name>`, or build them all with `--template all`.

| | | | | |
|---|---|---|---|---|
| [<img src="examples/output/sidebar.png" width="160">](examples/output/sidebar.pdf) | [<img src="examples/output/classic.png" width="160">](examples/output/classic.pdf) | [<img src="examples/output/modern.png" width="160">](examples/output/modern.pdf) | [<img src="examples/output/minimal.png" width="160">](examples/output/minimal.pdf) | [<img src="examples/output/timeline.png" width="160">](examples/output/timeline.pdf) |
| `sidebar` | `classic` | `modern` | `minimal` | `timeline` |
| [<img src="examples/output/compact.png" width="160">](examples/output/compact.pdf) | [<img src="examples/output/dark.png" width="160">](examples/output/dark.pdf) | [<img src="examples/output/elegant.png" width="160">](examples/output/elegant.pdf) | [<img src="examples/output/banner.png" width="160">](examples/output/banner.pdf) | [<img src="examples/output/tech.png" width="160">](examples/output/tech.pdf) |
| `compact` | `dark` | `elegant` | `banner` | `tech` |

Full-size renders and descriptions: [`examples/`](examples/README.md).

## Commands

| Command | What it does |
|---|---|
| `build <cv>` | Build the PDF and images. Options: `--lang fr`, `--variant <name>`, `--hide phone,photo`, `--template <name\|all>`, `--out`, `--formats pdf,png,jpg`, `--dpi`, `--no-fit` |
| `check <cv>` | Validate the file without compiling |
| `init [file]` | Create an example CV |
| `templates` | List templates |
| `doctor` | Check LaTeX engines and image tools |
| `setup` | Install Tectonic locally (no admin rights) |
| `mcp` | MCP mode, started automatically by agents |

Every command accepts `--json`.

## The format

```json
{
  "lang": "en",
  "basics": {
    "name": "Camille Martin",
    "label": { "en": "Full-Stack Engineer", "fr": "Développeuse Full-Stack" },
    "email": "camille@example.com",
    "phone": "+33 6 00 00 00 00",
    "summary": { "en": "**5 years** of experience…", "fr": "**5 ans** d'expérience…" }
  },
  "work": [
    { "position": "Engineer", "company": "Example Inc.", "dates": "2023 - 2025",
      "highlights": ["Rebuilt the **customer area**."] }
  ],
  "variants": {
    "no-phone": { "hide": ["phone"] }
  }
}
```

- Any text can be translated: `{ "en": "...", "fr": "..." }`. Lists too.
- Variants patch the base CV: objects are merged, lists replaced, and `hide` removes fields or sections.

Full example: [`examples/example.json`](examples/example.json). Schema: [`schema/cv.schema.json`](schema/cv.schema.json). Add `"$schema"` at the top of your file to get autocompletion in VS Code. `.yaml` files also work if PyYAML is installed.

## With an AI agent

- **Claude Code, Cursor…**: `.mcp.json` declares the `check_cv`, `build_cv`, `list_templates` and `get_schema` tools. The agent starts `./cvfacile mcp` itself when needed: there is no server to run.
- **Any other agent**: it reads [`AGENTS.md`](AGENTS.md) and uses the CLI with `--json`.

Example prompt: *"Tailor mycv.json to this job offer, save it as a variant called "offer-x", and make sure it fits on one page."*

## LaTeX engines

CVfacile uses the first one available: `pdflatex` (TeX Live, MiKTeX), then Tectonic (`./.bin` or installed), then Docker (`texlive/texlive` image, if already pulled). Images are rendered with PyMuPDF (`pip install pymupdf`) or `pdftoppm`.

With Tectonic, the first build downloads the required LaTeX packages (about 2 minutes). Later builds take a few seconds.

## License

Copyright (C) 2026 Naïm Chatti. CVfacile is dual-licensed:

- **[AGPL-3.0](LICENSE)**: free for everyone, including for writing your own CV for work. If you build CVfacile into a product or service that you distribute or run online, you must publish that service's source code under the AGPL.
- **Commercial license**: to build CVfacile into a product or SaaS without publishing your code. See [COMMERCIAL.md](COMMERCIAL.md).

The CVs you generate are yours: the license does not apply to their content.

Contributions are welcome, see [CONTRIBUTING.md](CONTRIBUTING.md).
