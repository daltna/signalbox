# signalbox

A data-driven Gmail filter generator. Edit YAML, get valid XML — no manual escaping, no character limit guessing.

## The problem with hand-written Gmail filters

Gmail's filter import format has several sharp edges:

- **`from` field uses space-separated domains, not `OR`** — `delta.com OR united.com` silently breaks; `delta.com united.com` works
- **480-char field limit** — exceeding it causes silent import failure with no error message
- **`&quot;` escaping** — multi-word phrases in `hasTheWords` require XML-escaped quotes; easy to get wrong by hand
- **No validation step** — Gmail just ignores malformed filters on import

`signalbox` handles all of this automatically.

---

## How it works

```
filters/*.yaml  →  generate.py  →  mailFilters.xml  →  Gmail import
```

The YAML files are the only thing you ever edit. `generate.py` reads them, validates field lengths, auto-splits oversized `from_domains` lists into multiple filter entries, and emits valid XML using Python's `xml.etree.ElementTree` (not string templates).

---

## Quickstart

```bash
# Install the one dependency
pip install pyyaml

# Generate mailFilters.xml from the filter definitions
python generate.py

# Preview without writing a file
python generate.py --dry-run

# Write to a custom path
python generate.py --out ~/Desktop/mailFilters.xml
```

Then in Gmail: **Settings → See all settings → Filters and Blocked Addresses → Import filters → upload mailFilters.xml → Create filters**

---

## Adding or editing filters

Open any file in `filters/` and edit the lists. Example — adding a domain to Deals:

```yaml
# filters/deals.yaml
from_domains:
  - delta.com
  - mynewtarget.com   # ← just add it here
```

Then run `python generate.py`. That's it.

To add a new filter category, create a new YAML file:

```yaml
# filters/finance.yaml
label: Finance
archive: true

from_domains:
  - chase.com
  - fidelity.com
  - vanguard.com

has_words:
  - "statement"
  - "balance"
  - "transaction"
```

---

## Filter taxonomy

| Label | Routing | Strategy |
|-------|---------|----------|
| **Deals** | `from_domains` + `has_words` | Domain AND keyword — avoids misfiring on transactional mail from same senders |
| **Logistics** | `has_words` only | Keyword-only — transactional mail arrives from thousands of domains |
| **Insights** | `from_domains` only | Domain-only — these senders only send editorial content |
| **Careers** | `from_domains` + `has_words` | Domain AND keyword — LinkedIn also sends connection requests; keyword gates job-specific mail |

---

## YAML schema

```yaml
label: string           # Gmail label name (created automatically on import)
archive: bool           # true = skip inbox (default: true)

from_domains:           # optional — list of sender domains (space-joined, auto-split)
  - example.com

has_words:              # optional — list of keywords/phrases (joined with OR)
  - "exact phrase"      # multi-word → wrapped in quotes in output
  - singleword          # single word → bare in output
```

At least one of `from_domains` or `has_words` is required.

---

## CI/CD

`.github/workflows/generate.yml` automatically regenerates `mailFilters.xml` and commits it whenever `filters/` or `generate.py` changes on `main`. The committed XML stays in sync with the YAML at all times.

---

## The inbox model this was built for

Three manual labels (`Needs Reply`, `Waiting On`, `To Read`) handled by you.  
Four automated labels (`Deals`, `Logistics`, `Insights`, `Careers`) handled by signalbox.  

Everything automated skips the inbox entirely. The inbox is exclusively for things that require a human decision.
