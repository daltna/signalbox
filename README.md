# signalbox

> Lowest noise. Highest signal. A data-driven Gmail filter system.

Edit YAML. Run one command. Import XML.

```
filters/*.yaml  →  python generate.py  →  mailFilters.xml  →  Gmail import
```

---

## The problem

Most inboxes fail structurally, not behaviorally. The inbox becomes a storage warehouse — promotional mail, shipping notifications, newsletters, job alerts, and actual human correspondence all arrive in the same place. Every visit requires triage. Every triage is cognitive overhead. Compounded daily, this is a significant drain.

The fix is architectural: **make the inbox exclusively contain things that require a human decision**. Everything else — promotional noise, transactional documents, editorial content, tool notifications — routes elsewhere automatically, silently, before you ever see it.

That's what signalbox does.

---

## The two-layer system

signalbox uses Gmail filters as a first pass, then hands off to an AI agent for the second pass.

```
All incoming email
        │
        ▼
┌───────────────────────────────────┐
│   Layer 1: Gmail XML Filters      │  ← server-side, instant, free
│   Runs on every email, always     │    handles ~80–90% of daily volume
└───────────────────────────────────┘
        │                       │
        │ matched                │ not matched
        ▼                       ▼
  Auto-archived            Raw inbox
  with label          ─────────────────────────────────────────────────┐
  (Deals,              │   Layer 2: Gemini Flow (AI)                   │
  Logistics,           │   Reads only inbox items                      │
  Insights,            │   Classifies what needs a response            │
  Careers,             │   Scans Sent for unreplied threads (Waiting On)│
  Stream)              └────────────────────────────────────────────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
             Needs Reply   Waiting On   (no label)
             applied       applied       → archive
```

**Why filters run first:** Gmail XML filters are free, instant, and handle pure signal-vs-noise decisions that don't require AI judgment. An email from delta.com with "sale" in the subject is always a Deal — no intelligence needed. By eliminating that volume before the AI runs, Gemini Flow only processes the small, high-quality set of emails that actually warrant classification.

---

## The label taxonomy

Labels split into two categories based on who applies them and what they represent.

### Automated labels (nouns) — *what the email IS*

Applied by Gmail filters. Skip the inbox. You consult them when you need to, not reactively.

| Label | Logic | What's in it | When you open it |
|-------|-------|-------------|-----------------|
| **Deals** | Domain + keyword | Promotional mail from known retail, travel, food, and entertainment brands | When you want a discount code or travel offer |
| **Logistics** | Keyword only | Receipts, order confirmations, shipping tracking, 2FA codes, invoices, billing statements | When you need a receipt, tracking number, or verification code |
| **Insights** | Domain only | Newsletters and research from editorial publishers — TechCrunch, McKinsey, HBR, Wired | When you have time to read and want industry context |
| **Careers** | Domain + keyword | Job alerts, application updates, certification notices from job boards and ATS platforms | When you're actively job searching or tracking credentials |
| **Stream** | Domain only | All operational tool notifications — GitHub, Slack, Notion, Figma, Linear, Zoom, Asana, etc. | Once daily, as a feed — not reactively |

### Action labels (verbs) — *what you need to DO*

Applied by Gemini Flow (AI) or manually. These are your active work queue.

| Label | Applied by | Trigger | Exit condition |
|-------|-----------|---------|---------------|
| **Needs Reply** | Gemini Flow | Email arrives in inbox; AI determines it requires a response | You reply → archive |
| **Waiting On** | Gemini Flow (scheduled) | You sent an email; no reply received after 4 days | Reply arrives → label auto-removed, thread archived |
| **To Read** | You, manually | You see any email (in inbox or any label) and decide it's worth focused reading time | You read it → archive |

**Why nouns for automated, verbs for action:**
Noun labels answer *what is this?* — a question that can be answered by rules.
Verb labels answer *what do I do?* — a question that requires judgment.
Rules handle nouns. AI handles verbs. You handle nothing that shouldn't need you.

---

## The filter decision tree

```
Incoming email
│
├─ FROM: known retail/travel/food/entertainment domain?
│  AND CONTAINS: promotional keyword (sale, discount, coupon, etc.)?
│  └─ YES → label:Deals, skip inbox
│
├─ CONTAINS: transactional keyword?
│  (receipt, shipped, invoice, 2FA code, tracking number, bill due, etc.)
│  └─ YES → label:Logistics, skip inbox
│
├─ FROM: known editorial publisher or research firm?
│  (TechCrunch, McKinsey, HBR, Wired, CBInsights, etc.)
│  └─ YES → label:Insights, skip inbox
│
├─ FROM: known job board or ATS platform?
│  AND CONTAINS: job-specific keyword?
│  (job alert, application received, viewed your resume, etc.)
│  └─ YES → label:Careers, skip inbox
│
├─ FROM: known operational tool domain?
│  (GitHub, Slack, Notion, Figma, Linear, Zoom, Asana, etc.)
│  └─ YES → label:Stream, skip inbox
│
└─ None of the above → hits raw inbox
   │
   ├─ Gemini Flow reads it
   │  ├─ Requires response? → apply label:Needs Reply
   │  └─ Informational / no action? → archive (no label)
   │
   └─ You see it in inbox
      └─ Worth reading later? → apply label:To Read manually
```

---

## Filter design decisions

### Why Deals AND Logistics can both catch Amazon

Amazon sends promotional emails ("20% off your next order") AND transactional emails (order confirmations, shipping updates). Because the Deals filter requires **both** the Amazon domain AND a promotional keyword, a shipping confirmation from Amazon doesn't match Deals — it has no promotional keyword. It falls through to Logistics instead, where "tracking number" or "your order has been received" catches it.

Result: Amazon promotional email → Deals. Amazon shipping notification → Logistics. Clean separation.

### Why Careers uses domain + keyword (AND logic)

LinkedIn also sends connection requests, profile view alerts, and "people you may know" suggestions. Without the keyword gate, all of those would land in Careers. With AND logic: only emails from LinkedIn that contain "job alert," "application received," "recruiter is interested," etc. hit Careers. Everything else from LinkedIn hits the inbox.

### Why Logistics is keyword-only (no domain list)

Transactional email arrives from thousands of different senders — your bank, dentist, insurance carrier, random e-commerce vendors, local restaurants. You cannot enumerate them. The content is the reliable signal: "receipt," "invoice," "tracking number" appear regardless of who sent it.

### Why Stream uses domain-only (no keyword gate)

Tool notifications from GitHub, Slack, Notion, etc. are all signal-adjacent but high-volume. A keyword gate would require maintaining a list of every notification pattern across every tool — an unmaintainable whitelist. Domain-only routing routes all tool volume to Stream, where you check it as a feed once a day rather than having 30 comment notifications interrupt your triage flow.

**The trade-off:** A direct PR review request from GitHub goes to Stream rather than the inbox. In a personal inbox context (not a work email), the cost of a few-hour delay is acceptable. The benefit is a permanently cleaner inbox that the AI can process with higher quality signal.

### Why Insights excludes operational tool domains

Operational tools like GitHub, Slack, Figma, and Notion also publish newsletters and changelogs. But they also send task assignments, @mentions, PR requests, and comment notifications that require action. Routing all GitHub mail to Insights would silently archive those action items. Instead:
- GitHub notifications → Stream (all tool notifications, checked as a feed)
- TechCrunch, Wired, McKinsey → Insights (pure editorial publishers who never send action-requiring mail)

The rule: **if the domain could ever send you something that blocks someone else, it does not belong in Insights.**

---

## Gmail settings

These settings complete the system. Without them, Gmail's own algorithms will partially override your filters.

| Setting | Value | Why |
|---------|-------|-----|
| Inbox type | Multiple Inboxes | Keeps action labels visible as persistent top panels |
| Multiple Inbox position | Above the inbox | Needs Reply and Waiting On are always visible above the triage zone |
| Filtered mail override | Don't override filters | Prevents Gmail's importance algorithm from re-routing filter output |
| Importance markers | No markers | Disables Gmail's automated "important" guessing |
| Auto-advance | On | After archiving, opens next email — no context switch back to list |
| Conversation view | On | Full thread history in one block |

**Multiple Inbox panel configuration:**

| Panel | Search query | Display name |
|-------|-------------|-------------|
| Section 1 | `label:needs-reply` | Action Required |
| Section 2 | `label:waiting-on` | Waiting On |
| Section 3 | `label:to-read` | Reading List |

---

## Quickstart

```bash
# 1. Install the one dependency
pip install pyyaml

# 2. Generate mailFilters.xml from the YAML filter definitions
python generate.py

# 3. Preview without writing (optional)
python generate.py --dry-run

# 4. Import into Gmail
# Settings → See all settings → Filters and Blocked Addresses
# → Import filters → upload mailFilters.xml → Create filters
```

---

## Adding or editing filters

### Add a domain to an existing label

```yaml
# filters/deals.yaml
from_domains:
  - delta.com
  - mynewairline.com   # ← add here, run generate.py
```

### Add a new tool to Stream

```yaml
# filters/stream.yaml
from_domains:
  - github.com
  - newprojecttool.com   # ← add here
```

### Add a new filter category

Create a new YAML file in `./filters/`:

```yaml
# filters/finance.yaml
label: Finance
archive: true

from_domains:
  - chase.com
  - fidelity.com

has_words:
  - "statement"
  - "transaction alert"
  - "balance available"
```

Run `python generate.py`. The label is created in Gmail on import.

### YAML schema

```yaml
label: string        # Gmail label name — created on import if it doesn't exist
archive: bool        # true = skip inbox (default: true)

from_domains:        # optional — space-joined, auto-split if > 480 chars
  - example.com

has_words:           # optional — OR-joined; multi-word phrases auto-quoted
  - "exact phrase"   # → "exact phrase" in output
  - singleword       # → singleword in output (no quotes)
```

**Filter matching behavior:**
- Both `from_domains` + `has_words` → Gmail requires **both** to match (AND)
- `from_domains` only → any email from those domains is caught
- `has_words` only → any email with those words is caught, any sender

---

## Auto-regenerate on push

`.github/workflows/generate.yml` runs `generate.py` on every push that touches `filters/` or `generate.py`. The committed `mailFilters.xml` stays in sync automatically. You never manually regenerate after committing a YAML edit.

---

## Project structure

```
signalbox/
├── filters/
│   ├── deals.yaml       # Promotional mail — domain + keyword (AND)
│   ├── logistics.yaml   # Transactional mail — keyword only
│   ├── insights.yaml    # Editorial mail — domain only
│   ├── careers.yaml     # Job board mail — domain + keyword (AND)
│   └── stream.yaml      # Operational tool notifications — domain only
├── generate.py          # Reads YAML → builds valid Gmail XML via ElementTree
├── mailFilters.xml      # Generated output — import this into Gmail
├── requirements.txt     # pyyaml
└── .github/
    └── workflows/
        └── generate.yml # Auto-regenerates XML on push to main
```
