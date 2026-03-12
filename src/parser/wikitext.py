"""Core wikitext infobox parser.

Extracts key-value pairs from MediaWiki infobox templates.
"""

import re
import logging

logger = logging.getLogger(__name__)


def extract_infobox(content, template_name):
    """Extract infobox fields from wikitext content.

    Handles nested braces and multi-line values.

    Args:
        content: Raw wikitext string
        template_name: e.g. "Infobox_Criatura" or "Infobox Criatura"

    Returns:
        dict of {field_name: raw_value} or None if template not found
    """
    if not content:
        return None

    # Normalize template name variants (underscore vs space)
    pattern_name = template_name.replace("_", "[_ ]")
    match = re.search(r"\{\{" + pattern_name + r"\s*\|", content, re.IGNORECASE)
    if not match:
        return None

    start = match.start()

    # Find matching closing }} by tracking brace depth
    depth = 0
    i = start
    while i < len(content):
        if content[i:i+2] == "{{":
            depth += 1
            i += 2
        elif content[i:i+2] == "}}":
            depth -= 1
            if depth == 0:
                break
            i += 2
        else:
            i += 1

    if depth != 0:
        logger.warning("Unbalanced braces in template %s", template_name)
        return None

    # Extract the content between the opening {{ and closing }}
    inner = content[match.end():i]

    # Split by top-level pipe characters (not inside nested {{ }})
    fields = _split_by_top_level_pipe(inner)

    result = {}
    for field in fields:
        # Skip template parameters like {{{1|}}} and {{{GetValue|}}}
        if field.strip().startswith("{{{"):
            continue

        # Split on first '=' to get key and value
        if "=" not in field:
            continue

        key, _, value = field.partition("=")
        key = key.strip().lower()
        value = value.strip()

        # Skip empty keys or template control params
        if not key or key in ("list", "getvalue"):
            continue

        result[key] = value

    return result


def _split_by_top_level_pipe(text):
    """Split text by | characters that are not inside {{ }} or [[ ]]."""
    parts = []
    current = []
    depth_brace = 0
    depth_bracket = 0
    i = 0

    while i < len(text):
        ch = text[i]

        if text[i:i+2] == "{{":
            depth_brace += 1
            current.append("{{")
            i += 2
            continue
        elif text[i:i+2] == "}}":
            depth_brace -= 1
            current.append("}}")
            i += 2
            continue
        elif text[i:i+2] == "[[":
            depth_bracket += 1
            current.append("[[")
            i += 2
            continue
        elif text[i:i+2] == "]]":
            depth_bracket -= 1
            current.append("]]")
            i += 2
            continue
        elif ch == "|" and depth_brace == 0 and depth_bracket == 0:
            parts.append("".join(current))
            current = []
            i += 1
            continue

        current.append(ch)
        i += 1

    if current:
        parts.append("".join(current))

    return parts


def clean_wikilinks(text):
    """Remove wiki markup from text.

    [[Link|Display]] -> Display
    [[Link]] -> Link
    Strips <noinclude>, <ref>, HTML tags.
    """
    if not text:
        return text

    # Remove <noinclude>...</noinclude>
    text = re.sub(r"<noinclude>.*?</noinclude>", "", text, flags=re.DOTALL)

    # Remove <ref>...</ref>
    text = re.sub(r"<ref[^>]*>.*?</ref>", "", text, flags=re.DOTALL)
    text = re.sub(r"<ref[^/]*/?>", "", text)

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # [[Link|Display]] -> Display
    text = re.sub(r"\[\[[^\]]*\|([^\]]*)\]\]", r"\1", text)

    # [[Link]] -> Link
    text = re.sub(r"\[\[([^\]]*)\]\]", r"\1", text)

    # Remove remaining {{ }} templates (simple ones)
    text = re.sub(r"\{\{[^}]*\}\}", "", text)

    return text.strip()


def parse_boolean(value):
    """Parse Portuguese boolean values.

    'sim' -> True, 'não'/'no' -> False, '' -> None
    """
    if not value or not value.strip():
        return None
    v = value.strip().lower()
    if v in ("sim", "yes", "true", "1"):
        return True
    if v in ("não", "nao", "no", "false", "0"):
        return False
    return None


def parse_int(value):
    """Parse an integer value, handling common wiki formatting."""
    if not value or not value.strip():
        return None
    v = value.strip()
    # Remove % suffix
    v = v.rstrip("%").strip()
    # Remove comma separators
    v = v.replace(",", "").replace(".", "")
    # Remove leading/trailing non-numeric chars
    v = re.sub(r"[^\d\-]", "", v)
    if not v:
        return None
    try:
        return int(v)
    except ValueError:
        return None


def parse_float(value):
    """Parse a float value."""
    if not value or not value.strip():
        return None
    v = value.strip()
    v = v.replace(",", ".")
    v = re.sub(r"[^\d.\-]", "", v)
    if not v:
        return None
    try:
        return float(v)
    except ValueError:
        return None
