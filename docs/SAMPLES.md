# Samples

The `samples/` folder contains runnable examples that start a local MCP server,
ask Ollama a natural-language question, and log whether the model chooses the
expected tool.

Install the core package first:

```bash
.venv/bin/pip install -e packages/titlemcp
```

Make sure Ollama is running and a tool-capable model is available.

## Franklin County Auditor

Parcel search:

```bash
python samples/franklin_county_ollama/ollama_client.py \
  --scenario parcel \
  --parcel-id "010-000123-00"
```

Address search:

```bash
python samples/franklin_county_ollama/ollama_client.py \
  --scenario address \
  --address "100 Example Ave"
```

The prompt does not name `franklin_county_auditor_search`; the sample verifies
that the model chooses it. The tool returns
`title_mcp.property_assessment_record` and preserves the raw auditor payload
under `source_specific.iasworld_auditor`.

Install the shared iasWorld platform package and the Ohio auditor package in
editable mode so the standard server can load the `title_mcp.toolsets` entry
point:

```bash
.venv/bin/pip install -e packages/platforms/iasworld
.venv/bin/pip install -e packages/jurisdictions/us/oh/auditor
```

## Lake County Auditor

Parcel search:

```bash
python samples/lake_auditor_ollama/ollama_client.py \
  --scenario parcel \
  --parcel-id "00A0000000002"
```

Address search:

```bash
python samples/lake_auditor_ollama/ollama_client.py \
  --scenario address \
  --address "100 Example St"
```

The prompt does not name `lake_county_auditor_search`; the sample verifies that
the model chooses it. Lake County's auditor site identifies as iasWorld but
serves a single unified `realprop` search for parcel, owner, and address; a
`mode_map` routes every mode to that URL and `form_field_overrides` rename the two
POST fields it uses (`inpNumber` -> `inpNo`, `inpOwner` -> `inpOwner1`). The tool
returns `title_mcp.property_assessment_record` and preserves the raw auditor
payload under `source_specific.iasworld_auditor`. Lake's datalet detail layout is
a third variant the shared profiles do not yet fully parse, so it is
NEEDS-VERIFICATION (search + header-derived fields populate; deep detail
extraction is a follow-up). It uses the same editable installs as the Franklin
auditor sample above.

## Summit County Auditor

Parcel search:

```bash
python samples/summit_auditor_ollama/ollama_client.py \
  --scenario parcel \
  --parcel-id "0100000"
```

Owner search:

```bash
python samples/summit_auditor_ollama/ollama_client.py \
  --scenario owner \
  --owner "DOE JANE A"
```

The prompt does not name `summit_county_auditor_search`; the sample verifies that
the model chooses it. Summit's Fiscal Office site is iasWorld Public Access and,
like Lake, serves a single unified `realprop` search (behind a `Disclaimer.aspx`
gate) whose form renames the same two POST fields — so it reuses the identical
`mode_map` + `form_field_overrides` knobs (`inpNumber` -> `inpNo`, `inpOwner` ->
`inpOwner1`), confirmed live (an `inpOwner1` owner search returns results under
`jur=000`). The tool returns `title_mcp.property_assessment_record` and preserves
the raw payload under `source_specific.iasworld_auditor`. Summit shares Lake's
third-variant detail layout, so it is NEEDS-VERIFICATION (search verified; deep
detail extraction is the shared `LAKE` `DetailProfile` follow-up). Same editable
installs as the Franklin auditor sample above.

## HOA Contact Search

Search by HOA name and state:

```bash
python samples/hoa_serpapi_ollama/ollama_client.py \
  --hoa-name "Tartan Fields Homeowners Association" \
  --state Ohio
```

If `TITLE_MCP_SERPAPI_API_KEY` is missing, the tool should still be triggered
and return `requires_configuration`.

The tool returns `title_mcp.hoa_contact_search` with contact candidates,
websites, addresses, phone numbers, and email addresses when available.

## PACER Bankruptcy Search

Business search:

```bash
python samples/pacer_ollama/ollama_client.py \
  --scenario business \
  --business-name "Example Holdings LLC"
```

Person search:

```bash
python samples/pacer_ollama/ollama_client.py \
  --scenario person \
  --first-name John \
  --last-name Smith
```

If credentials are missing, the tool should still be triggered and return
`requires_configuration`.

## How To Read The Logs

Important log lines:

- `MCP tools discovered`: confirms the server exposed the expected tool.
- `Ollama requested tool`: confirms the model selected the tool.
- `Tool arguments`: shows what the model sent.
- `MCP result summary`: shows status, record count, warnings, and schema name.

The samples default to stopping after the MCP tool result. Pass
`--summarize-with-ollama` if you want the result sent back to the model for a
short narrative response.
