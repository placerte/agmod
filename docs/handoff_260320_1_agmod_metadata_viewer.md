# handoff_260320_1_agmod_metadata_viewer

## General Description / Context

This iteration upgrades `agmod` from a simple metadata info panel to a **document-driven viewer**.

The right pane of the TUI becomes a **Markdown-based inspection viewer**.

Key goals:
- Support canonical LLM block metadata (frontmatter-driven)
- Provide a clean, structured, and pleasant visual layout
- Unify rendering across file types
- Keep everything **in-memory only** (no file writes, no exports)

Out of scope:
- Presets functionality
- File export (md/pdf)
- Editing or modifying source files

---

## Non-Goals / Do Not Touch

- Do not implement preset execution or resolution
- Do not write any markdown or output files to disk
- Do not modify existing source files
- Do not redesign the left tree navigation

---

## Specs

### S-260320-1 Rendering Modes

The viewer must support 3 rendering modes:

#### S-260320-1.1 Canonical Block Mode
Trigger:
- File is `.md`
- Contains valid canonical metadata (required fields present)

Behavior:
- Parse frontmatter into structured block model
- Generate **in-memory markdown document** from metadata + preview
- Render using Textual Markdown widget

---

#### S-260320-1.2 Plain Markdown Mode
Trigger:
- File is `.md`
- No valid canonical metadata

Behavior:
- Read raw markdown
- Truncate to preview length (see S-260320-3)
- Render directly in Markdown widget

---

#### S-260320-1.3 Generic Text Mode
Trigger:
- File is not `.md`

Behavior:
- Read content
- Wrap into simple markdown structure:

```
# {filename}

_Path: {relative_path}_

---

```text
{excerpt}
```
```

- Render in Markdown widget

---

### S-260320-2 Canonical Metadata Detection

#### S-260320-2.1 Required Fields

Canonical mode is enabled only if ALL required fields are present:

- id
- name
- type
- scope
- version
- status
- revised
- summary

#### S-260320-2.2 Partial Metadata Handling

If frontmatter exists but is incomplete:
- Still use Canonical Mode
- Display available fields only
- Add warning line at top:

```
> ⚠ Incomplete metadata
```

---

### S-260320-3 Preview Size

Preview for non-full rendering must be:
- Fixed number of lines: 30
- No adaptive resizing in this iteration

---

### S-260320-4 Canonical Layout (Option B Locked)

Generated markdown must follow EXACT structure:

```
# {name}

> ID: {id}  
> Type: {type} | Scope: {scope}  
> Status: {status} | Version: {version} | Revised: {revised}

---

{summary}

---

### Tags
`tag1` `tag2` `tag3`

---

### Preview
{excerpt}

---
_Path: {relative_path}_
```

#### Rules:
- Do not show empty fields
- Do not insert placeholders
- Tags section only if tags exist
- Summary is always shown (required field)

---

### S-260320-5 Viewer Behavior

- Viewer always resets scroll to top on selection
- Single Markdown widget used for all rendering modes
- No multiple widgets or layout switching

---

### S-260320-6 Rendering Strategy

Pipeline:

```
file → detect type → detect metadata → choose mode → build markdown → render
```

---

### S-260320-7 simdoc Usage

- simdoc is OPTIONAL but recommended
- Used only as in-memory markdown builder
- Must NOT:
  - write files
  - be required for core functionality

---

## Implementation

### I-260320-1 Metadata Parsing

- Extend existing parser to extract full frontmatter
- Map fields into a structured `Block` model

---

### I-260320-2 Mode Detection

Implement detection function:

```
detect_mode(file) -> canonical | markdown | text
```

---

### I-260320-3 Markdown Renderer

Create renderer module:

```
render_block(block) -> str
render_markdown(file) -> str
render_text(file) -> str
```

---

### I-260320-4 TUI Integration

- Replace existing info panel logic
- Inject markdown string into Textual Markdown widget
- Ensure refresh on selection change

---

### I-260320-5 Preview Extraction

- Read first N lines (30)
- Preserve formatting

---

## Tests

### T-260320-1 Canonical Block Rendering

- Input: valid block file
- Expect: structured layout with metadata + summary + preview

---

### T-260320-2 Incomplete Metadata

- Input: missing one required field
- Expect: canonical layout + warning

---

### T-260320-3 Plain Markdown

- Input: md without metadata
- Expect: truncated raw markdown

---

### T-260320-4 Text File

- Input: .txt file
- Expect: wrapped markdown with header + code block

---

### T-260320-5 Large File

- Ensure preview is capped at 30 lines

---

## Definition of Done

### DoD-260320-1

- All 3 rendering modes work
- Canonical layout matches spec exactly
- No file writes occur

### DoD-260320-2

- TUI uses a single Markdown viewer
- Switching files updates view correctly

### DoD-260320-3

- Metadata parsing supports canonical fields
- Missing fields handled gracefully

### DoD-260320-4

- Preview truncation enforced

---

## Notes

This iteration establishes the foundation for:
- future export (`--md`, `--pdf`)
- richer block tooling
- potential simdoc-based rendering reuse

No further scope should be added in this iteration.

