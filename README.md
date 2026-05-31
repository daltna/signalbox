# signalbox

> Lowest noise. Highest signal. A data-driven Gmail filter system.

Edit YAML. Run one command. Import XML. Done.

```
filters/*.yaml  →  python generate.py  →  mailFilters.xml  →  Gmail import
```

---

## The inbox problem

Most inboxes fail for the same reason: they are treated as **storage**, not a **decision queue**.

When the inbox holds everything — promotional mail, shipping notifications, newsletters, job alerts, and actual human correspondence — your brain has to triage every item on every visit. That cognitive tax compounds across every session, every day. The inbox stops feeling like a tool and starts feeling like a burden.

The fix is not "inbox zero." Inbox zero is a behavior hack. The fix is a structural one: **make the inbox exclusively contain things that require a human decision**. Everything else routes elsewhere automatically, silently, before you ever see it.

That's what signalbox does.

---

## The mental model: nouns vs. verbs

Labels in this system split into two types with different jobs.

### Automated labels (nouns) — *what the email IS*

Nouns describe categories of content. They are assigned by filters, require no human judgment, and skip the inbox entirely.

| Label | What it is |
|-------|-----------|
| **Deals** | Promotional mail. Discounts, offers, sale events from retailers, travel, food delivery. |
| **Logistics** | Transactional mail. Receipts, order confirmations, shipping tracking, 2FA codes, invoices, billing statements. |
| **Insights** | Editorial mail. Newsletters, research, industry media, thought leadership. Things you read when you have capacity — not things that block anyone. |
| **Careers** | Professional advancement mail. Job alerts, application updates, certification notices, recruiter outreach from job boards. |

Nouns are passive. Nothing in the noun labels requires you to act *now*. They are reference material, not a task queue.

### Manual labels (verbs) — *what you need to DO*

Verbs describe actions. They are applied by you, manually, to emails that need something from you. They live in the top panels of your inbox.

| Label | What it means |
|-------|--------------|
| **Needs Reply** | You owe someone a response. The ball is in your court. |
| **Waiting On** | You sent something and are blocked on their response. You are tracking it. |
| **To Read** | Long-form content you've chosen to save — not auto-routed, manually curated. |

Verbs are active. They represent open loops you are tracking.

**Why this split matters:** When everything in your inbox is verb-labeled, every item has a clear next action. When noun-labeled mail is archived automatically, you never have to decide what to do with it in the moment — you consult it when you need it.

---

## The filter decision tree

Every incoming email runs through this logic. Filters are evaluated in order; an email can match multiple filters and receive multiple labels.

```
Incoming email
│
├── Does it come from a known deal/promo sender?
│   AND does it contain promotional keywords?
│   └── YES → label:Deals, skip inbox
│
├── Does it contain transactional keywords?
│   (receipt, shipped, tracking number, 2FA code, invoice, etc.)
│   └── YES → label:Logistics, skip inbox
│
├── Does it come from a known editorial/newsletter domain?
│   └── YES → label:Insights, skip inbox
│
├── Does it come from a job board/ATS platform?
│   AND does it contain job-specific keywords?
│   └── YES → label:Careers, skip inbox
│
└── None of the above → hits your inbox (the triage zone)
    │
    ├── Noise/junk? → Delete or unsubscribe
    ├── Quick response (< 2 min)? → Reply immediately → archive (no label)
    ├── Needs real work (> 2 min)? → apply label:Needs Reply → archive
    ├── Sent something, waiting for reply? → find it in Sent → apply label:Waiting On → archive
    └── Long-form to read later? → apply label:To Read → archive
```

### Why some filters use BOTH domain + keyword (AND logic)

Gmail filter logic: when `from` AND `hasTheWords` are both specified, **both must match**. This is intentional for two filters:

**Deals uses AND because:** Amazon, Best Buy, and Target also send order confirmations. Without the keyword gate, a shipping notification from amazon.com would be mislabeled as a Deal. With AND logic: promotional email from Amazon → Deals. Shipping confirmation from Amazon → Logistics (caught by keyword filter). Clean separation.

**Careers uses AND because:** LinkedIn also sends connection requests, profile view alerts, and "people you may know" nudges. Without the keyword gate, those would all be labeled Careers. With AND logic: only job alerts and application updates from LinkedIn hit the Careers label. Social activity from LinkedIn reaches the inbox or is handled separately.

### Why Insights uses domain-only (no keyword gate)

The domains in Insights are pure editorial senders — HBR, McKinsey, TechCrunch, Wired, Product Hunt. These publishers **only** send newsletter content; they do not send you task assignments or things that require a response. A keyword gate would be redundant and would cause misses when the newsletter subject line doesn't contain any predictable keyword.

### Why Logistics uses keyword-only (no domain gate)

Transactional mail arrives from thousands of different domains. Your bank, your dentist, your landlord, your insurance carrier, random e-commerce vendors. You cannot enumerate them all. The content is the signal — "receipt," "invoice," "tracking number," "your package" — regardless of who sent it.

---

## The four automated filters in detail

### Deals

**Logic:** Domain AND keyword required (both must match)

**What gets caught:** Promotional campaigns, sale announcements, discount codes, limited-time offers from known retail, travel, food delivery, and entertainment brands.

**What doesn't get caught:** Transactional mail from the same senders (order confirmations, shipping updates). These route to Logistics instead.

**When to check it:** When you want to find a discount code before buying something, or when you're planning travel and want to see what offers have come in.

**When to add a domain:** When you start getting promotional mail from a new sender you didn't have before (new subscription box, new airline, new streaming service).

---

### Logistics

**Logic:** Keyword-only, no domain list

**What gets caught:** Order confirmations, shipping notifications, delivery updates, invoices, billing statements, 2FA codes, one-time passwords, sign-in alerts, password resets, payment receipts.

**What doesn't get caught:** Mail with no transactional keywords. If a company sends you a non-transactional email (like a newsletter from a service you use), it may hit the inbox or be caught by Insights.

**When to check it:** When you need to find a tracking number, a receipt, a verification code, or a payment confirmation.

**Known tradeoff:** `"charge"` was intentionally excluded from the keyword list. The word "charge" appears in too many non-transactional contexts (charging documents, charge of leadership, etc.) and creates false positives. Specific payment phrases like "payment received" and "payment successful" cover the real use case with less noise.

---

### Insights

**Logic:** Domain-only, no keyword gate

**What gets caught:** Newsletters, research reports, trend pieces, product launch announcements from pure editorial sources.

**What doesn't get caught (intentionally):** Mail from operational tools like GitHub, Slack, Zoom, Notion, Figma, Linear, Asana, ClickUp, Monday.com, Salesforce. These tools send task assignments, PR review requests, meeting invites, and direct messages. **Archiving those would cause you to miss action items.** They are explicitly excluded.

**When to check it:** During scheduled reading time — not reactively. This is the one label where you set aside time to consume rather than respond.

**When to add a domain:** When you subscribe to a new newsletter or research service that you want to read on your own schedule rather than have it interrupt your triage flow.

---

### Careers

**Logic:** Domain AND keyword required (both must match)

**What gets caught:** Job alerts, application status updates, credential and certification notices, recruiter outreach — but only when it comes from a known job platform.

**What doesn't get caught:** A LinkedIn connection request (domain matches, but no job keyword). A recruiter emailing you directly from a company domain (not a known job board domain). These reach the inbox.

**When to check it:** When you're actively job searching or tracking certifications. When you're not, you can ignore it entirely.

---

## Filter quality checklist

Before adding a domain or keyword to any filter, ask:

| Question | If YES | If NO |
|----------|--------|-------|
| Could this sender ever email you something that requires action? | Do NOT add to Insights or use domain-only | Safe to route automatically |
| Is this a domain that sends both promotional AND transactional mail? | Use domain + keyword (AND logic) for Deals | Domain-only is fine |
| Is the keyword too common to be a reliable signal? | Don't add it | Add it |
| Does the sender use a different domain for marketing vs. transactional? | Add both domains to appropriate filters | One domain is enough |

---

## Gmail settings to pair with these filters

These settings make the system work. Without them, Gmail's own algorithms will override your filters.

| Setting | Value | Why |
|---------|-------|-----|
| Inbox type | Multiple Inboxes | Separates verb-labeled emails into persistent top panels |
| Multiple Inbox position | Above the inbox | Action items (verbs) are always visible above the triage zone |
| Filtered mail override | Don't override filters | Stops Gmail's importance algorithm from re-routing your filter output |
| Importance markers | No markers | Disables Gmail's automated "important" guessing |
| Auto-advance | On | After archiving, opens next email — no context-switch back to list |
| Conversation view | On | Keeps full thread history in one block |

**Multiple Inbox panel configuration:**

| Panel | Search query | Label name |
|-------|-------------|------------|
| Section 1 | `label:needs-reply` | Action Required |
| Section 2 | `label:waiting-on` | Blocked / Waiting |
| Section 3 | `label:to-read` | Reading List |

---

## Quickstart

```bash
# 1. Install the one dependency
pip install pyyaml

# 2. Edit any filter in ./filters/*.yaml

# 3. Generate and validate
python generate.py

# 4. Preview without writing (optional)
python generate.py --dry-run

# 5. Import mailFilters.xml into Gmail
# Gmail → Settings → See all settings → Filters and Blocked Addresses
# → Import filters → upload mailFilters.xml → Create filters
```

---

## Adding or editing filters

### Add a domain to an existing filter

Open the YAML file, add the domain, run the generator:

```yaml
# filters/deals.yaml
from_domains:
  - delta.com
  - mynewairline.com   # ← add it here
```

```bash
python generate.py
```

Then re-import `mailFilters.xml` into Gmail. Gmail will not duplicate existing filters on import — it adds new ones.

### Add a new filter category

Create a new YAML file in `./filters/`:

```yaml
# filters/finance.yaml
label: Finance
archive: true

from_domains:
  - chase.com
  - fidelity.com
  - vanguard.com
  - schwab.com

has_words:
  - "statement"
  - "balance available"
  - "transaction alert"
```

Run `python generate.py`. The new label will be created in Gmail on import.

### YAML schema reference

```yaml
label: string        # Gmail label name — created automatically on import
archive: bool        # true = skip inbox (default: true)

from_domains:        # optional — space-joined, auto-split if > 480 chars
  - example.com

has_words:           # optional — OR-joined; multi-word phrases quoted automatically
  - "exact phrase"   # becomes: "exact phrase"
  - singleword       # becomes: singleword (no quotes)
```

At least one of `from_domains` or `has_words` is required per filter.

**AND vs OR behavior:**
- Both `from_domains` AND `has_words` present → Gmail requires **both** to match
- Only `from_domains` → any email from those domains is caught
- Only `has_words` → any email containing those words is caught, regardless of sender

---

## CI/CD: auto-regenerate on push

`.github/workflows/generate.yml` runs `generate.py` automatically whenever `filters/` or `generate.py` changes on `main`. The committed `mailFilters.xml` always reflects the current YAML — no manual re-generation needed after a push.

---

## Project structure

```
signalbox/
├── filters/
│   ├── deals.yaml       # Promotional mail — domain + keyword
│   ├── logistics.yaml   # Transactional mail — keyword only
│   ├── insights.yaml    # Editorial mail — domain only
│   └── careers.yaml     # Job board mail — domain + keyword
├── generate.py          # Reads YAML → builds valid Gmail XML
├── mailFilters.xml      # Generated output — import this into Gmail
├── requirements.txt     # pyyaml
└── .github/
    └── workflows/
        └── generate.yml # Auto-regenerates XML on push to main
```
