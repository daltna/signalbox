# signalbox

Gmail filters for a low-noise inbox. Download `mailFilters.xml` and import it directly into Gmail.

---

## Import into Gmail

1. Download [`mailFilters.xml`](mailFilters.xml)
2. **Gmail → Settings → See all settings → Filters and Blocked Addresses → Import filters**
3. Upload the file → **Create filters**

Done. Gmail creates all labels and filter rules automatically.

---

## What gets filtered

| Label | What lands here | Auto-archived? |
|-------|----------------|---------------|
| **Deals** | Promotional mail from retail, travel, food delivery, entertainment | Yes |
| **Logistics** | Receipts, order confirmations, shipping tracking, 2FA codes, invoices | Yes |
| **Insights** | Newsletters and research from editorial publishers | Yes |
| **Careers** | Job alerts, application updates, certifications from job boards | Yes |
| **Stream** | Notifications from tools you work in (GitHub, Slack, Notion, Figma, etc.) | Yes |

Everything that doesn't match a filter lands in your raw inbox for manual triage.

**Suggested manual labels to pair with these:**
- `Needs Reply` — email requires a response from you
- `Waiting On` — you sent something and are waiting for a reply
- `To Read` — something you want to read on your own schedule

---

## Update the filters

### Quick edit — modify the XML directly

Open `mailFilters.xml` and edit the `value=` fields. Each filter entry looks like:

```xml
<apps:property name="from" value="delta.com united.com aa.com" />
<apps:property name="hasTheWords" value="sale OR discount OR coupon" />
```

- **`from`** — space-separated sender domains (space = OR)
- **`hasTheWords`** — keywords joined with `OR`; multi-word phrases go as-is (`order confirmation` = both words must appear)

Commit and re-import in Gmail.

### Cleaner edit — use the YAML files + generator

The `filters/` folder has human-readable YAML definitions. Edit those, then run the generator to produce a clean `mailFilters.xml`:

```bash
pip install pyyaml
python generate.py
```

Commit both the YAML and the updated `mailFilters.xml`.

### Add a new domain to Deals

```yaml
# filters/deals.yaml
from_domains:
  - delta.com
  - mynewairline.com   # ← add here
```

```bash
python generate.py
git add -A && git commit -m "add mynewairline.com to Deals"
```

### Add a new filter category

```yaml
# filters/finance.yaml
label: Finance
archive: true

from_domains:
  - chase.com
  - fidelity.com

has_words:
  - statement
  - transaction alert
  - balance available
```

```bash
python generate.py
git add -A && git commit -m "add Finance filter"
```

---

## File structure

```
signalbox/
├── mailFilters.xml      ← download and import this
├── filters/
│   ├── deals.yaml       ← edit to add/remove senders and keywords
│   ├── logistics.yaml
│   ├── insights.yaml
│   ├── careers.yaml
│   └── stream.yaml
├── generate.py          ← run locally to regenerate mailFilters.xml from YAML
└── requirements.txt     ← pyyaml
```
