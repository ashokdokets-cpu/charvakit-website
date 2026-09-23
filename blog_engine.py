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


def _get_post_raw(slug: str) -> Optional[Dict]:
    """Internal: load post dict (no wrapping). Returns None if not found."""
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
        title = fm.get("title", slug.replace("-", " ").title())
        return {
            "slug": slug,
            "title": title,
            "seo_title": title + " — Charvak Blog",
            "description": fm.get("description", ""),
            "date": fm.get("date", ""),
            "author": fm.get("author", "Charvak Team"),
            "tags": fm.get("tags", []),
            "content_html": rendered,
        }
    except Exception as e:
        logger.error(f"Failed to load post {slug}: {e}")
        return None


def get_post(slug: str) -> Dict:
    """Return {status, post, related} — legacy contract used by /blog/{slug} route."""
    post = _get_post_raw(slug)
    if not post:
        return {"status": "error", "message": "Post not found"}

    enriched = _enrich_post(post)
    enriched["content"] = post.get("content_html", "")

    # Related: 3 other posts, prefer same category/tag
    all_posts = [_enrich_post(p) for p in list_posts()]
    related = []
    cat = enriched.get("category", "")
    for p in all_posts:
        if p["slug"] == slug:
            continue
        if cat and cat in (p.get("tags") or []):
            related.insert(0, p)
        else:
            related.append(p)
    related = related[:3]

    return {"status": "success", "post": enriched, "related": related}


def get_post_simple(slug: str) -> Optional[Dict]:
    """Return the raw post dict (no wrapping). Used internally."""
    return _get_post_raw(slug)


def _enrich_post(p: Dict) -> Dict:
    """Add fields expected by existing blog templates/routes."""
    enriched = dict(p)
    # Alias description -> excerpt
    enriched.setdefault("excerpt", p.get("description", ""))
    # Alias date -> published_at (ISO with time)
    d = p.get("date") or ""
    enriched.setdefault("published_at", (d + "T00:00:00") if d else "")
    # Category — first tag as category, or 'general'
    tags = p.get("tags") or []
    enriched.setdefault("category", tags[0] if tags else "general")
    # Estimated reading time from word count
    try:
        raw = (BLOG_DIR / f"{p['slug']}.md").read_text(encoding="utf-8")
        _, body = _parse_frontmatter(raw)
        words = len(body.split())
        enriched.setdefault("read_time", f"{max(1, words // 200)} min")
    except Exception:
        enriched.setdefault("read_time", "5 min")
    return enriched


def get_all_posts(category=None, tag=None):
    """Return {count, posts} — legacy API with enriched fields."""
    posts = [_enrich_post(p) for p in list_posts()]
    filter_val = category or tag
    if filter_val:
        posts = [p for p in posts if filter_val in (p.get("tags") or []) or filter_val == p.get("category")]
    return {"count": len(posts), "posts": posts}


def get_post_legacy(slug):
    """Return {status, post, related} — matches existing /blog/{slug} contract."""
    return get_post(slug)


def get_post_by_slug(slug):
    """Legacy alias — returns post dict directly (unwrapped)."""
    return _get_post_raw(slug)


class BlogEngine:
    list_posts = staticmethod(list_posts)
    get_post = staticmethod(get_post)
    get_post_simple = staticmethod(get_post_simple)
    get_post_legacy = staticmethod(get_post_legacy)
    get_all_posts = staticmethod(get_all_posts)
    get_post_by_slug = staticmethod(get_post_by_slug)


blog_engine = BlogEngine()