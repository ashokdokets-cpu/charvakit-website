"""
Charvak Blog Engine (Y5)
Reads markdown posts from blog/posts/, parses frontmatter, renders HTML.
"""
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.blog")

BLOG_DIR = Path("blog/posts")

try:
    import markdown as md_lib
    _MD_AVAILABLE = True
except ImportError:
    _MD_AVAILABLE = False
    logger.warning("markdown library missing — blog posts will render as plain text")


def _parse_frontmatter(raw: str) -> tuple:
    """Return (frontmatter: dict, body: str)."""
    # Normalize: strip UTF-8 BOM, normalize newlines, strip leading whitespace
    raw = raw.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n").lstrip()
    if not raw.startswith("---"):
        return {}, raw
    parts = raw.split("---", 2)
    if len(parts) < 3:
        return {}, raw
    fm_text = parts[1].strip()
    body = parts[2].strip()

    fm = {}
    for line in fm_text.split("\n"):
        line = line.rstrip()
        if not line:
            continue
        m = re.match(r"^([a-zA-Z_]+):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            elif val.startswith("'") and val.endswith("'"):
                val = val[1:-1]
            if val.startswith("[") and val.endswith("]"):
                inner = val[1:-1]
                fm[key] = [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]
            else:
                fm[key] = val
    return fm, body


def _render_markdown(body: str) -> str:
    """Render markdown to HTML with sane extensions."""
    if not _MD_AVAILABLE:
        return "<pre>" + body.replace("<", "&lt;").replace(">", "&gt;") + "</pre>"
    return md_lib.markdown(
        body,
        extensions=["fenced_code", "tables", "toc", "sane_lists"],
        output_format="html5",
    )


def list_posts() -> List[Dict]:
    """Return metadata for all posts, newest first."""
    if not BLOG_DIR.exists():
        return []

    posts = []
    for path in sorted(BLOG_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            raw = path.read_text(encoding="utf-8")
            fm, body = _parse_frontmatter(raw)
            slug = path.stem
            posts.append({
                "slug": slug,
                "title": fm.get("title", slug.replace("-", " ").title()),
                "description": fm.get("description", ""),
                "date": fm.get("date", ""),
                "author": fm.get("author", "Charvak Team"),
                "tags": fm.get("tags", []),
            })
        except Exception as e:
            logger.warning(f"Failed to load {path.name}: {e}")

    def sort_key(p):
        try:
            return datetime.strptime(p.get("date", ""), "%Y-%m-%d")
        except Exception:
            return datetime.min
    posts.sort(key=sort_key, reverse=True)
    return posts


def get_post(slug: str) -> Optional[Dict]:
    """Return a single post with rendered HTML body, or None."""
    if not BLOG_DIR.exists():
        return None
    if "/" in slug or "\\" in slug or ".." in slug:
        return None

    path = BLOG_DIR / f"{slug}.md"
    if not path.exists():
        return None

    try:
        raw = path.read_text(encoding="utf-8")
        fm, body = _parse_frontmatter(raw)
        rendered = _render_markdown(body)
        return {
            "slug": slug,
            "title": fm.get("title", slug.replace("-", " ").title()),
            "description": fm.get("description", ""),
            "date": fm.get("date", ""),
            "author": fm.get("author", "Charvak Team"),
            "tags": fm.get("tags", []),
            "content_html": rendered,
        }
    except Exception as e:
        logger.error(f"Failed to load post {slug}: {e}")
        return None


blog_engine = type("BlogEngine", (), {
    "list_posts": staticmethod(list_posts),
    "get_post": staticmethod(get_post),
})()