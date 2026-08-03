agmod
=====

Local LLM block manager. Browse source block libraries, copy blocks into a
project `llm/` directory, and keep `AGENTS.md` in sync.

Install
-------

```bash
curl -fsSLO https://github.com/placerte/agmod/releases/latest/download/install.sh \
  && chmod +x install.sh \
  && sudo ./install.sh
```

The installer downloads the latest release asset and installs `agmod` to
`/usr/local/bin`. Override with `AGMOD_INSTALL_DIR=/path`.

Quick start
-----------

1) The installer creates `~/.config/agmod/config.toml` if it is missing:

```toml
[sources]
kb_llm = "~/llm-blocks/blocks/"

# Additional source examples:
# personal = "/home/you/llm"
# workflows = "/home/you/workflows"
```

Existing configuration is never overwritten. Edit the generated file if your
block libraries live elsewhere.

2) Run the app from your project root:

```bash
agmod
```

Blocks you add are copied into `./llm/` and `AGENTS.md` is updated automatically.
Preset blocks install their declared dependencies in order. Removing a preset
removes only the preset definition; shared dependency blocks remain available.

Update an installed release with:

```bash
sudo agmod --update
```

`sudo` is only required when the installation directory is not writable by your
user, such as the default `/usr/local/bin`.

Keybindings
-----------

- `l` add selected source block to the project
- `h` remove selected block from the project
- `space` toggle add/remove based on block state
- `enter` add selected source block
- `delete` remove selected project block
- `tab` switch panels
- `gg` move to the top of the focused tree
- `G` move to the bottom of the focused tree
- `r` refresh
- `q` quit

Development
-----------

- Setup: `uv sync`
- Run: `uv run agmod`
- Tests: `uv run pytest`
- Format: `uv run black .`

Release build
-------------

Generate the PyInstaller spec file:

```bash
uv sync --group build
uv run pyinstaller --onefile --name agmod --specpath . src/agmod/__main__.py
```

Build release assets:

```bash
scripts/build_release.sh
```
