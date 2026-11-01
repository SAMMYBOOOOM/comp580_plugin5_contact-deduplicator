# Contact Deduplicator
A `nanoagent.plugin/v0001` plugin.

## Tools
| Tool | Does | Code |
|---|---|---|
| `deduplicate_contacts` | Identifies duplicate contacts through normalized email or phone matches and returns deterministic groups of original contact indices. | `src/plugin/deduplicate_contacts.py` |
### Tasks
| Task | Does | Runner |
|---|---|---|
| `deduplicate-contacts` | Groups contacts sharing a non-empty normalized email address or phone number. | `tool`, with `deduplicate_contacts` |
## Layout
```text
.
├── nanoagent.yaml
├── contract.py
├── README.md
├── LICENSE
├── pyproject.toml
├── uv.lock
├── .gitignore
├── .env
├── src/plugin/
├── tests/
├── ui/
├── product/
└── verifier/
```

`contract.py` is the one place a value's shape is declared. Its Output classes are the JSON Schemas the server offers and the agent sees, and every input and output is built into its class on the way in and out. A tool that fails raises; NanoAgent sees an MCP error.

## Develop and run

```
uv sync --extra dev
uv run pytest
```

Publishing checks every plugin rule: push the plugin to a public GitHub repository and run:

```
rush publish <server> <github-url>
```