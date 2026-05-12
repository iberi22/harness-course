#!/usr/bin/env python3
"""Integrity Tests for Harness Course.
Checks internal link resolution and scans for hardcoded secrets.
"""
import os
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
HTML_FILES = [f for f in PROJECT.rglob("*.html")
              if not any(d in f.parts for d in {".git", "node_modules", "target"})]
ALL_FILES = [f for f in PROJECT.rglob("*")
             if f.is_file() and not any(d in f.parts for d in {".git", "node_modules", "target"})]

errors = []
warnings = []


def find_local_links(filepath):
    """Extract local href references from HTML."""
    content = filepath.read_text(encoding="utf-8", errors="replace")
    links = re.findall(r'href=[\'"]([^\'"]+)[\'"]', content)
    local = []
    for link in links:
        if link.startswith("http") or link.startswith("#") or link.startswith("mailto:"):
            continue
        if link.startswith("/"):
            link = link.lstrip("/")
        if link.startswith("harness-course/"):
            link = link[len("harness-course/"):]
        local.append(link.split("#")[0].split("?")[0])
    return local


def test_links(filepath):
    """Verify all internal links resolve to existing targets."""
    local_links = find_local_links(filepath)
    file_errors = 0
    for link in local_links:
        if not link:
            continue
        target = (PROJECT / link).resolve()
        if not target.exists():
            alt = (PROJECT / link / "index.html").resolve()
            if not alt.exists():
                errors.append(f"  BROKEN LINK in {filepath.relative_to(PROJECT)}: '{link}' → not found")
                file_errors += 1
    return file_errors == 0


SECRET_PATTERNS = [
    r'api[_-]?key["\']?\s*[:=]\s*["\'](?!YOUR_|your-)[A-Za-z0-9_\-]{16,}',
    r'token["\']?\s*[:=]\s*["\'](?!YOUR_|your-)[A-Za-z0-9_\-]{16,}',
    r'secret["\']?\s*[:=]\s*["\'](?!YOUR_|your-)[A-Za-z0-9_\-]{16,}',
]


def test_no_secrets(filepath):
    """Check for hardcoded API keys or tokens."""
    if filepath.name == ".env" or "secrets" in filepath.name:
        return True
    content = filepath.read_text(encoding="utf-8", errors="replace")
    for pattern in SECRET_PATTERNS:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            errors.append(f"  SECRET LEAK in {filepath.relative_to(PROJECT)}: matches '{pattern[:30]}...'")
            return False
    return True


def main():
    print(f"\n{'='*60}")
    print(f"  Integrity Tests — {len(HTML_FILES)} HTML files, {len(ALL_FILES)} total files")
    print(f"{'='*60}\n")

    html_files = [f for f in HTML_FILES if f.suffix == ".html"]

    print("🔗 Internal Link Check...")
    link_ok = 0
    for f in html_files:
        if test_links(f):
            link_ok += 1
    print(f"  ✓ {link_ok}/{len(html_files)} files checked\n")

    print("🔒 Secrets Check...")
    secret_ok = 0
    for f in ALL_FILES:
        if test_no_secrets(f):
            secret_ok += 1
    print(f"  ✓ {secret_ok}/{len(ALL_FILES)} files clean\n")

    total_errors = len(errors)
    total_warnings = len(warnings)

    if total_errors > 0:
        print(f"❌ {total_errors} ERROR(S):")
        for e in errors:
            print(f"  {e}")

    if total_warnings > 0:
        print(f"⚠️  {total_warnings} WARNING(S):")
        for w in warnings:
            print(f"  {w}")

    print(f"\n{'='*60}")
    if total_errors == 0:
        print(f"  ✅ ALL INTEGRITY TESTS PASSED")
        return True
    else:
        print(f"  ❌ {total_errors} error(s), {total_warnings} warning(s)")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
