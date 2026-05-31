"""
generate.py — signalbox Gmail filter generator

Reads YAML filter definitions from ./filters/*.yaml and produces a valid
Gmail-importable mailFilters.xml.

Key behaviors:
- Uses xml.etree.ElementTree to build XML (no string templates)
- Auto-splits `from_domains` lists that exceed Gmail's ~480-char field limit
- Validates every field before writing
- Exits non-zero on any validation failure (safe for CI)

Usage:
    python generate.py                    # writes mailFilters.xml
    python generate.py --dry-run          # prints XML to stdout, no file written
    python generate.py --out custom.xml   # custom output path
"""

import argparse
import sys
import textwrap
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

# Gmail enforces a hard limit on filter field values.
# 480 is conservative to account for encoding overhead.
GMAIL_FIELD_CHAR_LIMIT = 480

ATOM_NS = "http://www.w3.org/2005/Atom"
APPS_NS = "http://schemas.google.com/apps/2006"

# Unique numeric suffix base for filter IDs — avoids collisions on re-import
FILTER_ID_BASE = 1500000000000


def load_filters(filters_dir: Path) -> list[dict]:
    """Load and return all YAML filter definitions, sorted by filename."""
    configs = []
    for path in sorted(filters_dir.glob("*.yaml")):
        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
            data["_source"] = path.name
            configs.append(data)
    return configs


def build_from_value(domains: list[str]) -> str:
    """Join domains with spaces (Gmail implicit OR — no OR keyword in from field)."""
    return " ".join(domains)

def build_has_words_value(words: list[str]) -> str:
    """
    Join keyword phrases with OR — no quoting.

    Gmail's XML import parser does NOT decode &quot; entities inside attribute
    values, so wrapping phrases in literal quote characters causes ElementTree
    to emit &quot; in the file, which Gmail then reads as the literal string
    &quot; — silently malforming or dropping the hasTheWords field entirely.

    Without quotes:
    - Single words match as-is: shipped, receipt, fedex
    - Multi-word phrases (e.g. "order confirmation") match as an implicit AND:
      Gmail requires both words present, which is a tighter and equally
      reliable signal than a loose keyword match.
    """
    return " OR ".join(words)


def split_domains(domains: list[str], limit: int = GMAIL_FIELD_CHAR_LIMIT) -> list[list[str]]:
    """
    Split a domain list into chunks where each joined chunk stays under `limit` chars.
    Each chunk will become a separate filter entry in the XML.
    """
    return _split_by_length(domains, sep=" ", limit=limit)


def split_words(words: list[str], limit: int = GMAIL_FIELD_CHAR_LIMIT) -> list[list[str]]:
    """
    Split a has_words list into chunks where each joined chunk stays under `limit` chars.
    Each chunk becomes a separate filter entry (entries are OR'd at the filter level).
    """
    return _split_by_length(words, sep=" OR ", limit=limit)


def _split_by_length(items: list[str], sep: str, limit: int) -> list[list[str]]:
    """Generic splitter: groups items so that sep.join(chunk) stays under limit chars."""
    chunks: list[list[str]] = []
    current: list[str] = []
    current_len = 0

    for item in items:
        added_len = len(item) + (len(sep) if current else 0)
        if current and current_len + added_len > limit:
            chunks.append(current)
            current = [item]
            current_len = len(item)
        else:
            current.append(item)
            current_len += added_len

    if current:
        chunks.append(current)

    return chunks


def validate_field(name: str, value: str, source: str) -> list[str]:
    """Return a list of error strings. Empty list = valid."""
    errors = []
    if len(value) > GMAIL_FIELD_CHAR_LIMIT:
        errors.append(
            f"[{source}] Field '{name}' is {len(value)} chars "
            f"(limit {GMAIL_FIELD_CHAR_LIMIT}): {value[:80]}..."
        )
    return errors


def make_entry(
    feed: ET.Element,
    filter_id: int,
    label: str,
    archive: bool,
    from_value: str | None,
    has_words_value: str | None,
    timestamp: str,
    source: str,
) -> list[str]:
    """
    Append a single <entry> to `feed`. Returns a list of validation errors.
    """
    errors: list[str] = []

    entry = ET.SubElement(feed, f"{{{ATOM_NS}}}entry")
    ET.SubElement(entry, f"{{{ATOM_NS}}}category", term="filter")
    ET.SubElement(entry, f"{{{ATOM_NS}}}title").text = "Mail Filter"
    ET.SubElement(entry, f"{{{ATOM_NS}}}id").text = f"tag:mail.google.com,2008:filter:{filter_id}"
    ET.SubElement(entry, f"{{{ATOM_NS}}}updated").text = timestamp

    def prop(name: str, value: str) -> None:
        ET.SubElement(
            entry,
            f"{{{APPS_NS}}}property",
            name=name,
            value=value,
        )

    if from_value:
        errors.extend(validate_field("from", from_value, source))
        prop("from", from_value)

    if has_words_value:
        errors.extend(validate_field("hasTheWords", has_words_value, source))
        prop("hasTheWords", has_words_value)

    prop("label", label)

    if archive:
        prop("shouldArchive", "true")

    return errors


def build_feed(configs: list[dict]) -> tuple[ET.Element, list[str]]:
    """Build the full Atom feed element. Returns (root, errors)."""
    # Fixed timestamp: Gmail requires a valid ISO 8601 date but doesn't use it
    # functionally. Using a fixed value keeps the output deterministic across
    # runs, which is required for the CI diff check to pass.
    timestamp = "2026-01-01T00:00:00Z"
    all_errors: list[str] = []
    filter_id_counter = FILTER_ID_BASE + 1

    ET.register_namespace("", ATOM_NS)
    ET.register_namespace("apps", APPS_NS)

    feed = ET.Element(f"{{{ATOM_NS}}}feed")
    ET.SubElement(feed, f"{{{ATOM_NS}}}title").text = "Mail Filters"
    ET.SubElement(feed, f"{{{ATOM_NS}}}id").text = "tag:mail.google.com,2008:filters:"
    ET.SubElement(feed, f"{{{ATOM_NS}}}updated").text = timestamp

    for config in configs:
        source = config.get("_source", "unknown")
        label = config["label"]
        archive = config.get("archive", True)
        domains: list[str] = config.get("from_domains", [])
        keywords: list[str] = config.get("has_words", [])

        has_words_value = build_has_words_value(keywords) if keywords else None

        if domains:
            # Split domains into chunks to respect Gmail's field length limit.
            # has_words is replicated across all domain chunks (AND logic: domain + keyword).
            chunks = split_domains(domains)
            for chunk in chunks:
                from_value = build_from_value(chunk)
                errors = make_entry(
                    feed=feed,
                    filter_id=filter_id_counter,
                    label=label,
                    archive=archive,
                    from_value=from_value,
                    has_words_value=has_words_value,
                    timestamp=timestamp,
                    source=source,
                )
                all_errors.extend(errors)
                filter_id_counter += 1
        elif keywords:
            # No domains — keyword-only filter (e.g. Logistics).
            # Split has_words into chunks to respect Gmail's field length limit.
            # Multiple entries are OR'd at the filter level: an email matching
            # any chunk gets the label.
            word_chunks = split_words(keywords)
            for chunk in word_chunks:
                chunk_value = build_has_words_value(chunk)
                errors = make_entry(
                    feed=feed,
                    filter_id=filter_id_counter,
                    label=label,
                    archive=archive,
                    from_value=None,
                    has_words_value=chunk_value,
                    timestamp=timestamp,
                    source=source,
                )
                all_errors.extend(errors)
                filter_id_counter += 1
        else:
            print(f"Warning: [{source}] has neither from_domains nor has_words — skipping.", file=sys.stderr)

    return feed, all_errors


def pretty_print(element: ET.Element) -> str:
    """Return indented XML string with declaration."""
    ET.indent(element, space="  ")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        + ET.tostring(element, encoding="unicode", xml_declaration=False)
        + "\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate Gmail mailFilters.xml from YAML filter definitions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Examples:
              python generate.py
              python generate.py --dry-run
              python generate.py --out ~/Desktop/mailFilters.xml
        """),
    )
    parser.add_argument(
        "--filters-dir",
        type=Path,
        default=Path("filters"),
        help="Directory containing *.yaml filter definitions (default: ./filters)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("mailFilters.xml"),
        help="Output XML file path (default: ./mailFilters.xml)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print generated XML to stdout instead of writing a file",
    )
    args = parser.parse_args()

    filters_dir: Path = args.filters_dir
    if not filters_dir.is_dir():
        print(f"Error: filters directory '{filters_dir}' not found.", file=sys.stderr)
        return 1

    configs = load_filters(filters_dir)
    if not configs:
        print(f"Error: no *.yaml files found in '{filters_dir}'.", file=sys.stderr)
        return 1

    print(f"Loaded {len(configs)} filter config(s): {[c['_source'] for c in configs]}")

    feed, errors = build_feed(configs)

    if errors:
        print("\nValidation errors -- fix these before importing into Gmail:\n", file=sys.stderr)
        for e in errors:
            print(f"  • {e}", file=sys.stderr)
        return 1

    xml_output = pretty_print(feed)

    if args.dry_run:
        print(xml_output)
    else:
        args.out.write_text(xml_output, encoding="utf-8")
        print(f"OK: Written to {args.out.resolve()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
