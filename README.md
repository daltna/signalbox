# signalbox

> Lowest noise. Highest signal. A structured email filter system for Gmail (and adaptable to Outlook).

Download [`mailFilters.xml`](mailFilters.xml) and import it directly into Gmail. Five filters, five labels, everything automated routes out of your inbox before you ever see it.

---

## Quick import (Gmail)

1. Download [`mailFilters.xml`](mailFilters.xml)
2. **Gmail → Settings (gear) → See all settings → Filters and Blocked Addresses → Import filters**
3. Upload the file → **Create filters**

Gmail creates all five labels and all filter rules automatically.

---

## The problem this solves

Most inboxes fail structurally, not behaviorally. Promotional mail, shipping notifications, newsletters, job alerts, and actual human correspondence all arrive in the same place. Every visit requires triage. Every triage is cognitive overhead. Compounded daily, this is a significant tax.

The fix is architectural: **make the inbox exclusively contain things that require a human decision.** Everything else — promotional noise, transactional documents, editorial content, tool notifications — routes elsewhere automatically, silently, before you ever see it.

That's what signalbox does.

---

## The two-layer inbox model

```
All incoming email
        │
        ▼
┌─────────────────────────────────┐
│   Layer 1: Filters (this repo)  │  server-side, instant, free
│   Catches ~80–90% of volume     │  handles the obvious stuff
└─────────────────────────────────┘
        │                    │
   matched                not matched
        ▼                    ▼
  Auto-archived          Raw inbox  ← only ~10–20% of email
  with a label           │
                         ▼
              You (or an AI assistant)
              decides what to do with it
```

The filters handle volume. Your inbox handles judgment.

---

## The label system: nouns vs. verbs

Labels split into two types with completely different jobs.

### Automated labels (nouns) — *what the email IS*

These are applied by filters. They skip the inbox. You consult them when you need to — not reactively.

| Label | What it contains | When you open it |
|-------|-----------------|-----------------|
| **Deals** | Promotional mail from retail, travel, food delivery, and entertainment brands | When you want a discount code or travel offer |
| **Logistics** | Receipts, order confirmations, shipping tracking, 2FA codes, invoices, billing statements | When you need a receipt, tracking number, or verification code |
| **Insights** | Newsletters and research from editorial publishers — TechCrunch, McKinsey, HBR, Wired, etc. | When you have time to read and want industry context |
| **Careers** | Job alerts, application updates, certifications, professional development, career guidance, industry events, salary reports, and learning platforms | When you're actively job searching, tracking credentials, or doing career development work |
| **Stream** | All notifications from tools you work in — GitHub, Slack, Notion, Figma, Zoom, Asana, etc. | Once daily, as a feed — not reactively |

**Why nouns?** Nouns describe categories of content. A noun label answers *what is this?* — a question that can be answered by a rule, not a human.

### Manual labels (verbs) — *what you need to DO*

These are applied by you (or an AI assistant like Gemini). They live in the top panels of your inbox and represent open loops.

| Label | What it means | Who applies it |
|-------|--------------|---------------|
| **Needs Reply** | You owe someone a response | You, or AI reading your inbox |
| **Waiting On** | You sent something and are pending their reply | You, or AI scanning your Sent folder |
| **To Read** | Something worth focused reading time | You, manually — pulled from any label |

**Why verbs?** Verbs describe actions. A verb label answers *what do I do?* — a question that requires judgment. When everything in your inbox is verb-labeled, every item has a clear next action.

---

## The filter decision tree

Every incoming email runs through this logic. Gmail evaluates all filters; an email can match multiple and receive multiple labels.

```
Incoming email
│
├─ FROM a known retail/travel/food/entertainment domain?
│  AND CONTAINS a promotional keyword?
│  (sale, discount, coupon, unsubscribe, free shipping, etc.)
│  └─ YES → label: Deals, skip inbox
│
├─ CONTAINS a transactional keyword?
│  (receipt, shipped, invoice, tracking number, 2FA code, bill due, etc.)
│  └─ YES → label: Logistics, skip inbox
│
├─ FROM a known editorial publisher or research firm?
│  (TechCrunch, McKinsey, HBR, Wired, OpenAI, Product Hunt, etc.)
│  └─ YES → label: Insights, skip inbox
│
├─ FROM a known job board, ATS, or professional development platform?
│  AND CONTAINS a career-related keyword?
│  (job alert, application received, certification, professional development,
│   career advice, career fair, industry event, salary report, etc.)
│  └─ YES → label: Careers, skip inbox
│
├─ FROM a known operational tool domain?
│  (GitHub, Slack, Notion, Figma, Linear, Zoom, Asana, etc.)
│  └─ YES → label: Stream, skip inbox
│
└─ None of the above → hits your raw inbox
   │
   ├─ Noise or junk? → Delete or unsubscribe
   ├─ Quick reply (< 2 min)? → Respond immediately → archive
   ├─ Needs real work? → Apply "Needs Reply" → archive
   ├─ Waiting on someone? → Apply "Waiting On" → archive
   └─ Worth reading later? → Apply "To Read" → archive
```

---

## Why each filter is designed the way it is

### Deals — domain AND keyword (both required)

Amazon, Best Buy, and Target send both promotional emails AND transactional emails (order confirmations, shipping updates). If the filter matched on domain alone, a shipping notification from Amazon would land in Deals.

**With AND logic:** Amazon promo email (has "sale") → **Deals**. Amazon shipping confirmation (no promo keyword) → falls through to **Logistics**. Clean separation, no manual work.

### Logistics — keyword only (no domain list)

Transactional email arrives from thousands of different senders — your bank, dentist, insurance carrier, landlord, random vendors. You cannot enumerate them all. The content is the only reliable signal: "receipt," "invoice," "tracking number" appear regardless of sender.

### Insights — domain only (no keyword gate)

The domains in Insights are pure editorial senders. They only send newsletter content — they never send you task assignments or things that require action. A keyword gate would be redundant and would cause misses when the newsletter subject line doesn't contain a predictable keyword.

**Critical:** Operational tools like GitHub, Slack, Figma, and Notion are intentionally excluded from Insights. They send PR review requests, task assignments, and @mentions that require action. Those go to Stream instead. **Rule: if the domain could ever email you something that blocks someone else, it does not belong in Insights.**

### Careers — domain AND keyword (both required), two filter entries

Careers is split into two filter entries covering two different aspects of your career:

**Entry 1 — Job search:** Job boards and ATS platforms (LinkedIn, Indeed, Glassdoor, Workday, Greenhouse, etc.) with job-specific keywords. LinkedIn also sends connection requests and profile nudges that don't belong here, so the keyword gate keeps only career-action emails in this label.

**Entry 2 — Professional development:** Learning platforms and certification bodies (Coursera, Udemy, PMI, SHRM, CompTIA, The Institutes, etc.) with development-specific keywords — certification, professional development, career advice, industry event, salary report, career fair, leadership programs. These are things related to *building* your career, not just searching for a job.

Both entries land in the same **Careers** label. You open Careers when you're doing career work — active job search, studying for a certification, reviewing a salary report, or tracking an industry event.

### Stream — domain only (no keyword gate)

Operational tool notifications come in too many patterns to filter by keyword (PR opened, comment added, @mention, task assigned, meeting recorded, etc.). Domain-only routing catches all of it. You check Stream as a daily feed — not reactively. In a personal inbox, the cost of a few-hour delay on a GitHub notification is lower than the cost of that notification interrupting your triage flow permanently.

---

## Gmail settings to pair with this

These settings complete the system. Without them, Gmail's own algorithms partially override your filters.

| Setting | Value | Why |
|---------|-------|-----|
| Inbox type | Multiple Inboxes | Keeps Needs Reply / Waiting On visible as persistent top panels |
| Multiple Inbox position | Above the inbox | Action items always visible above the triage zone |
| Filtered mail override | Don't override filters | Prevents Gmail's importance algorithm from re-routing your filtered mail |
| Importance markers | No markers | Disables Gmail's automated "important" guessing |
| Auto-advance | On | After archiving, opens the next email — no context switch back to list |
| Conversation view | On | Full thread history in one block |

**Multiple Inbox panel configuration:**

| Panel | Search query | Display name |
|-------|-------------|-------------|
| Section 1 | `label:needs-reply` | Action Required |
| Section 2 | `label:waiting-on` | Waiting On |
| Section 3 | `label:to-read` | Reading List |

---

## Updating the filters

### Add a sender domain

Find the relevant filter entry in `mailFilters.xml` and add the domain to the `from` value (space-separated):

```xml
<!-- Add mynewairline.com to Deals -->
<apps:property name="from" value="delta.com united.com aa.com mynewairline.com" />
```

### Add a keyword

Find the relevant filter entry and append to the `hasTheWords` value:

```xml
<!-- Add "clearance" to Deals keywords -->
<apps:property name="hasTheWords" value="sale OR discount OR coupon OR clearance" />
```

### Add a new filter category entirely

Copy an existing `<entry>` block and modify it:

```xml
<entry>
  <category term="filter"></category>
  <title>Mail Filter</title>
  <id>tag:mail.google.com,2008:filter:1500000000099</id>
  <updated>2026-01-01T00:00:00Z</updated>
  <apps:property name="from" value="chase.com fidelity.com vanguard.com schwab.com" />
  <apps:property name="hasTheWords" value="statement OR transaction OR balance" />
  <apps:property name="label" value="Finance" />
  <apps:property name="shouldArchive" value="true" />
</entry>
```

**Rules for editing the XML:**
- `from` value: space-separated domains, no `OR` keyword
- `hasTheWords` value: `OR` between terms; no quote marks needed — multi-word phrases like `order confirmation` match emails containing both words
- Give each filter a unique `<id>` number
- `shouldArchive` value `true` = skip inbox; remove the line entirely to keep in inbox with label only

Re-import in Gmail after editing. Gmail will not duplicate existing filters — it adds new ones.

---

## Using this with Outlook

Gmail's XML format does not import into Outlook. You need to recreate the rules manually, but the logic is identical.

**In Outlook: Home → Rules → Manage Rules & Alerts → New Rule**

### Deals (Outlook)
- **Condition:** `From` contains any of the deal domains (add one domain per line in Outlook's rule wizard)
- **AND condition:** `Subject or body` contains: `sale, discount, coupon, promo code, free shipping, unsubscribe`
- **Action:** Move to folder `Deals`

### Logistics (Outlook)
- **Condition:** `Subject or body` contains: `receipt, order confirmation, tracking number, shipped, delivered, invoice, payment received, verification code, password reset`
- **Action:** Move to folder `Logistics`

### Insights (Outlook)
- **Condition:** `From` contains any of the insight domains (techcrunch.com, hbr.org, mckinsey.com, etc.)
- **Action:** Move to folder `Insights`

### Careers (Outlook)
- **Condition:** `From` contains any of the job board domains (linkedin.com, indeed.com, etc.)
- **AND condition:** `Subject or body` contains: `job alert, application received, viewed your resume, job opening`
- **Action:** Move to folder `Careers`

### Stream (Outlook)
- **Condition:** `From` contains any of the tool domains (github.com, slack.com, notion.so, etc.)
- **Action:** Move to folder `Stream`

**Outlook tip:** Outlook rules run in order and stop at the first match by default. Put more specific rules (Careers, Deals) above broader ones (Logistics, Stream) so emails don't get misrouted.

---

## File structure

```
signalbox/
├── mailFilters.xml   ← the only file you need — download and import into Gmail
└── README.md         ← this file
```
