# Design note

This copilot serves support engineers (ticket triage) and TAMs (account briefs). OpenAI writes classifications and prose. Routing, retrieval ranking, risk flags, and the 90-day ticket window are deterministic code. That split is the production bet.

## Failure modes

**Wrong urgency on an ambiguous ticket.** A timeout affecting many users can look like P1 or P2; a two-product complaint can be tagged as the wrong product. Detection: sample P1s daily; keep an eval case for ambiguous tickets. Mitigation: the model never picks the responder team (a rules table does); allow `Unknown` when two products are named; require a human confirm before paging on P1.

**Missed or wrong knowledge-base article.** Keyword search overfits to repeated words (“pipeline”) and can miss a single error code. We saw `ERR_CONNECTION_TIMEOUT` retrieve a throughput article before the timeout section. Detection: eval cases that require a path substring such as `databridge-pro`. Mitigation: boost exact error-code hits, drop other products’ docs when the ticket names a product, and take matches from the retriever so the model cannot invent paths.

**Hallucinated churn.** An LLM asked to “find risk” will invent a competitor quote. Detection: every flag must include a verbatim quote; evals fail empty quotes and check that a known churn phrase appears for `ACC-2944`. Mitigation: extract flags with regex over tickets and `escalation_notes` *before* the LLM call. The model only writes the summary and talking points.

## Latency vs quality

The trade-off: **one structured LLM call plus BM25**, not embeddings and not a multi-agent graph. The knowledge base is nine Markdown files. BM25 with error-code and product rules is local and good enough for code lookup. A second “verify” call or an embedding index would help paraphrases and add hundreds of milliseconds plus another dependency.

If latency were the hard constraint (a ~1s chat widget), I would skip the LLM when an error code already matches: return the top chunk and a template reply, and call the model only for P1/P2 or unmatched text. I would also use `top_k=2` and a shorter first response. Briefs can stay slower; TAMs run them before a QBR, not on a live call.

## Data sensitivity

Ticket bodies and account notes can contain names, emails, and vendor opinions. The live path sends that text to OpenAI. That is a real leak surface.

What we do now: keys live only in `.env` (gitignored); `.env.example` has no secrets; we do not log raw bodies; retrieval is local BM25 (no embedding vendor); quotes are sliced from source text. The dataset is synthetic, which is why a hosted LLM was acceptable here.

Before production: redact emails, phones, and named contacts before the API call; send role instead of `primary_contact.name`; offer a local-model switch for VPC-only tenants; keep prompts in an access-controlled audit store, not application logs.

## Scaling to 10× ticket volume

At 5,000 tickets, **synchronous OpenAI calls on the request path break first**. Each triage is one completion; a burst of inbound email hits rate limits and tail latency, not JSON reads.

Next: process-local BM25 and JSON behind `lru_cache`. Fine for one CLI/Streamlit process. Ten workers would each rebuild the index. The company-name join is cheap at 5,000 rows and the wrong model at 500,000.

The fix is a queue (one job per ticket), a persisted index, and a database with `(company, created_at)` indexes. The LLM and the rules stay the same; the I/O shape changes.
