"""HTML processing and conversion utilities for PDF report generation."""

import re
import logging
import markdown
from typing import Optional


def strip_code_fences(s: str) -> str:
    """Remove code fence markers from text."""
    if not s:
        return s
    s = s.strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z0-9]*\s*", "", s, count=1)
        s = re.sub(r"\s*```$", "", s, count=1)
    return s.strip()


def remove_html_wrappers(s: str) -> str:
    """Remove <!DOCTYPE>, <html>, <head>, and <body> wrappers if present; keep inner content."""
    if not s:
        return s

    # Extract body if present
    m = re.search(r"<body[^>]*>(.*?)</body\s*>", s, flags=re.IGNORECASE | re.DOTALL)
    if m:
        return m.group(1).strip()

    # Remove doctype
    s = re.sub(r"<!DOCTYPE[^>]*>\s*", "", s, flags=re.IGNORECASE)

    # Strip <html> and </html>
    s = re.sub(r"</?html[^>]*>", "", s, flags=re.IGNORECASE)

    # Remove <head>...</head>
    s = re.sub(r"<head[^>]*>.*?</head\s*>", "", s, flags=re.IGNORECASE | re.DOTALL)

    # If any <body ...> remains without closing tag (unlikely), strip it
    s = re.sub(r"<body[^>]*>", "", s, flags=re.IGNORECASE)
    s = re.sub(r"</body\s*>", "", s, flags=re.IGNORECASE)
    return s.strip()


def ensure_table_sections(html: str) -> str:
    """
    Best-effort: wrap table rows with <thead>/<tbody> if missing.
    Keeps it simple to avoid over-transforming already-correct tables.
    """
    def fix_one_table(tbl: str) -> str:
        # Already has thead/tbody
        if re.search(r"<thead\b", tbl, flags=re.IGNORECASE) and re.search(r"<tbody\b", tbl, flags=re.IGNORECASE):
            return tbl

        # Split rows
        rows = re.findall(r"<tr\b.*?</tr>", tbl, flags=re.IGNORECASE | re.DOTALL)
        if not rows:
            return tbl

        thead = rows[0]
        tbody = "".join(rows[1:]) if len(rows) > 1 else ""
        # Remove existing <tr>... from table to rebuild
        inner = re.sub(r"(?is)<tr\b.*?</tr>", "", tbl)
        # Remove existing thead/tbody tags if any stray
        inner = re.sub(r"(?is)</?(thead|tbody)\b[^>]*>", "", inner)
        # Insert our sections just before </table>
        fixed = re.sub(
            r"(?is)</table\s*>",
            f"<thead>{thead}</thead><tbody>{tbody}</tbody></table>",
            inner
        )
        return fixed

    return re.sub(
        r"(?is)<table\b.*?</table\s*>",
        lambda m: fix_one_table(m.group(0)),
        html
    )


def extract_html_body_fragment(text: str) -> str:
    """
    Normalize LLM output to a clean HTML *fragment* suitable to be injected into our styled wrapper.
    - If a full HTML document is present, return only the inner <body>...</body>.
    - If there's chatter before tags, trim to the first opening tag.
    - Strip code fences and language hints.
    - If no HTML tags at all, return empty string (caller can fallback).
    """
    if not text:
        return ""

    s = text.strip()

    # Strip code fences like ```html ... ```
    if s.startswith("```"):
        # remove starting fence
        s = re.sub(r"^```[a-zA-Z0-9]*\s*", "", s, count=1)
        # remove trailing fence
        s = re.sub(r"\s*```$", "", s, count=1)
        s = s.strip()

    # If a full HTML doc was returned, extract the body's inner HTML
    body_match = re.search(r"<body[^>]*>(.*?)</body>", s, flags=re.IGNORECASE | re.DOTALL)
    if body_match:
        return body_match.group(1).strip()

    # If there is any tag at all, trim everything before the first tag
    first_tag = re.search(r"<[a-zA-Z!/?]", s)
    if first_tag:
        s = s[first_tag.start():].strip()

    # If it's still a full doc without a body (rare), remove doctype/html/head wrappers
    # and keep best-effort inner content after </head>
    if re.search(r"<html[^>]*>", s, re.IGNORECASE):
        # try to cut off head
        after_head = re.split(r"</head\s*>", s, flags=re.IGNORECASE, maxsplit=1)
        if len(after_head) == 2:
            s = after_head[1].strip()
        # drop closing </html> if present
        s = re.sub(r"</html\s*>", "", s, flags=re.IGNORECASE).strip()

    # If no tags at all, signal to caller to fallback
    if not re.search(r"</?[a-zA-Z]+[^>]*>", s):
        return ""

    return s


def markdown_to_html_fallback(markdown_content: str) -> str:
    """
    Fallback method to convert markdown to HTML using the markdown library.
    """
    try:
        html = markdown.markdown(
            markdown_content,
            extensions=['tables', 'fenced_code', 'toc']
        )
        html = ensure_table_sections(html)
        return html
    except Exception as e:
        logging.error(f"Fallback markdown conversion failed: {e}")
        return f"<div><pre>{markdown_content}</pre></div>"


def validate_html_fragment(html: str) -> bool:
    """
    Validate that the provided string contains valid HTML tags.
    """
    return bool(re.search(r"</?[a-zA-Z]+[^>]*>", html))
