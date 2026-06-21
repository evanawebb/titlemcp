# Summit County Auditor Ollama Sample

This sample starts a local MCP server with the Summit County Auditor tool
registered, then asks Ollama a natural Summit County auditor question. The
prompt does not name `summit_county_auditor_search`; the sample is meant to test
whether the model chooses that MCP tool from context. The tool returns canonical
`title_mcp.property_assessment_record` data, so the default sample stops after
the MCP tool result instead of asking Ollama to summarize it.

> **Status: needs-verification.** Summit County runs the Tyler iasWorld "Public
> Access" platform but serves a single unified `mode=realprop` search instead of
> the usual per-mode pages. The connector routes every search mode to
> `commonsearch.aspx?mode=realprop` via the shared `mode_map` knob, but the live
> realprop search form, `jur` district code, and parcel format were not
> confirmable during recon (the site was returning a maintenance page). See
> [`docs/OHIO_AUDITOR_EXPANSION.md`](../../docs/OHIO_AUDITOR_EXPANSION.md) for the
> open items. This sample still exercises tool selection and the canonical
> contract end to end.

## Prerequisites

- Python 3.12 or newer
- Ollama running locally
- An Ollama model with tool-calling support, such as `qwen3`

Install the project dependencies from the repo root:

```bash
python -m pip install -e packages/titlemcp
python -m pip install -e packages/platforms/iasworld
python -m pip install -e packages/jurisdictions/us/oh/auditor
```

Make sure the model is available:

```bash
ollama pull qwen3
```

## Run

From the repo root:

```bash
python samples/summit_auditor_ollama/ollama_client.py --model qwen3
```

The default prompt asks conversationally for the Summit County auditor record
for parcel `0000123`. To search a different parcel:

```bash
python samples/summit_auditor_ollama/ollama_client.py \
  --model qwen3 \
  --parcel-id 0000123
```

You can also test address or owner prompts:

```bash
python samples/summit_auditor_ollama/ollama_client.py \
  --model qwen3 \
  --scenario address \
  --address "100 EXAMPLE AVE"
```

```bash
python samples/summit_auditor_ollama/ollama_client.py \
  --model qwen3 \
  --scenario owner \
  --owner-name "DOE JANE A"
```

If Ollama answers without requesting the Summit Auditor MCP tool, the sample
raises an error. That makes it useful as a tool-trigger smoke test.

For more verbose logs:

```bash
python samples/summit_auditor_ollama/ollama_client.py --log-level DEBUG
```

The default behavior prints the canonical MCP tool result. To ask Ollama for a
natural-language summary after the canonical result comes back:

```bash
python samples/summit_auditor_ollama/ollama_client.py \
  --model qwen3 \
  --summarize-with-ollama
```

For faster smoke tests, keep the default `--num-predict 512` and default
thinking-disabled mode. If you want a reasoning model to think before answering,
pass `--think`.

## What This Uses

- `ollama_client.py` starts the standard `title_mcp.mcp.server` stdio server
  through the shared sample helper, exposes the Summit tool to Ollama, executes
  the model-requested tool call, and prints the canonical tool result. Passing
  `--summarize-with-ollama` sends the canonical result back to the model for a
  final answer.

The Summit Auditor tool is loaded from the `titlemcp-us-oh-auditor` package's
`title_mcp.toolsets` entry point. Install that package (and the shared iasWorld
platform package) in editable mode while developing so the standard server can
discover it from the local checkout.
