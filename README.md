# signalbox

Gmail filters for a low-noise inbox. Download `mailFilters.xml` and import it.

---

## Import

1. Download [`mailFilters.xml`](mailFilters.xml)
2. **Gmail → Settings → See all settings → Filters and Blocked Addresses → Import filters**
3. Upload → **Create filters**

Gmail creates all labels and rules automatically.

---

## What gets filtered

| Label | What lands here |
|-------|----------------|
| **Deals** | Promotional mail — retail, travel, food delivery, entertainment |
| **Logistics** | Receipts, order confirmations, shipping, 2FA codes, invoices |
| **Insights** | Newsletters and research from editorial publishers |
| **Careers** | Job alerts, application updates, certifications |
| **Stream** | Notifications from tools — GitHub, Slack, Notion, Figma, Zoom, etc. |

Everything else lands in your inbox for manual triage.

---

## Update the filters

Open `mailFilters.xml` and edit directly. To add a sender domain to an existing filter, find the relevant `from` property and add the domain:

```xml
<!-- before -->
<apps:property name="from" value="delta.com united.com aa.com" />

<!-- after — added mynewairline.com -->
<apps:property name="from" value="delta.com united.com aa.com mynewairline.com" />
```

To add a keyword to an existing filter:

```xml
<!-- before -->
<apps:property name="hasTheWords" value="sale OR discount OR coupon" />

<!-- after -->
<apps:property name="hasTheWords" value="sale OR discount OR coupon OR clearance" />
```

Commit the updated XML and re-import in Gmail.
