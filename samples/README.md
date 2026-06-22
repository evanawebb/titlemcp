# TitleMCP Samples

This folder contains runnable examples for using TitleMCP from a local checkout.

## Franklin County Auditor with Ollama

See [franklin_county_ollama](franklin_county_ollama/) for a sample that starts an
MCP server exposing `franklin_county_auditor_search`, connects to it from an
Ollama client, and logs the model/tool exchange.

## Lake County Auditor with Ollama

See [lake_auditor_ollama](lake_auditor_ollama/) for a sample that starts an MCP
server exposing `lake_county_auditor_search` (Lake County's unified iasWorld
`realprop` search), connects to it from an Ollama client, and logs the model/tool
exchange.

## Summit County Auditor with Ollama

See [summit_auditor_ollama](summit_auditor_ollama/) for a sample that starts an MCP
server exposing `summit_county_auditor_search` (Summit County's unified iasWorld
`realprop` search, same renamed form fields as Lake), connects to it from an Ollama
client, and logs the model/tool exchange.

## HOA Contact Search with Ollama

See [hoa_serpapi_ollama](hoa_serpapi_ollama/) for a sample that asks Ollama a
natural HOA contact lookup question and verifies it triggers
`hoa_contact_search`.

## PACER Bankruptcy Search with Ollama

See [pacer_ollama](pacer_ollama/) for a sample that asks Ollama a natural
bankruptcy search question and verifies it triggers `pacer_bankruptcy_search`.
