#!/usr/bin/env python3
"""Test Suite for Harness Course — HTML validation + link checking.
Zero external dependencies — uses Python stdlib only.
"""

import os
import re
import sys
import html.parser
import urllib.request
import urllib.error
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
HTML_FILES = list(PROJECT.rglob("*.html"))
EXCLUDE_DIRS = {".git", "node_modules", "target"}

# Filter out excluded dirs
HTML_FILES = [f for f in HTML_FILES if not any(d in f.parts for d in EXCLUDE_DIRS)]

errors = []
warnings = []


# ── Test 1: HTML Parse Validation ──────────────────────────────────

class HTMLValidator(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.errors = []
        self.tag_stack = []
        self.void_elements = {
            "area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "param", "source", "track", "wbr",
        }

    def handle_starttag(self, tag, attrs):
        if tag not in self.void_elements:
            self.tag_stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.void_elements:
            return
        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()
        elif tag in self.tag_stack:
            while self.tag_stack and self.tag_stack[-1] != tag:
                self.tag_stack.pop()
            if self.tag_stack:
                self.tag_stack.pop()
        else:
            self.errors.append(f"  Unexpected closing tag: </{tag}>")


def test_html_parse(filepath):
    """Verify HTML parses without unclosed tags or syntax errors."""
    content = filepath.read_text(encoding="utf-8", errors="replace")
    validator = HTMLValidator()
    try:
        validator.feed(content)
    except html.parser.HTMLParseError as e:
        errors.append(f"  PARSE ERROR: {filepath.relative_to(PROJECT)} — {e}")
        return False

    unclosed = [t for t in validator.tag_stack if t not in {"html", "head", "body", "p", "li", "td", "th", "tr", "option"}]
    if unclosed:
        warnings.append(f"  {filepath.relative_to(PROJECT)}: unclosed tags: {unclosed}")
        return False
    
    # Check for DOCTYPE
    if "<!DOCTYPE html" not in content and "<!doctype html" not in content:
        warnings.append(f"  {filepath.relative_to(PROJECT)}: missing DOCTYPE")
        return False
    
    return True


# ── Test 2: Internal Link Checker ──────────────────────────────────

def find_local_links(filepath):
    """Extract local href references from HTML."""
    content = filepath.read_text(encoding="utf-8", errors="replace")
    links = re.findall(r'href=[\'"]([^\'"]+)[\'"]', content)
    # Filter to local links
    local = []
    for link in links:
        if link.startswith("http") or link.startswith("#") or link.startswith("mailto:"):
            continue
        if link.startswith("/"):
            link = link.lstrip("/")
        # Strip GitHub Pages base path prefix
        if link.startswith("harness-course/"):
            link = link[len("harness-course/"):]
        local.append(link.split("#")[0].split("?")[0])
    return local


def test_links(filepath):
    """Verify all internal links in a file resolve to existing targets."""
    local_links = find_local_links(filepath)
    file_errors = 0
    for link in local_links:
        if not link:
            continue
        target = (PROJECT / link).resolve()
        if not target.exists():
            # Try with index.html
            alt = (PROJECT / link / "index.html").resolve()
            if not alt.exists():
                errors.append(f"  BROKEN LINK in {filepath.relative_to(PROJECT)}: '{link}' → not found")
                file_errors += 1
    return file_errors == 0


# ── Test 3: H1 Uniqueness ─────────────────────────────────────────

def test_h1_uniqueness(filepath):
    """Verify each page has exactly one <h1>."""
    content = filepath.read_text(encoding="utf-8", errors="replace")
    h1_count = len(re.findall(r'<h1[>\s]', content, re.IGNORECASE))
    if h1_count == 0:
        warnings.append(f"  {filepath.relative_to(PROJECT)}: no <h1> found")
        return False
    elif h1_count > 1:
        warnings.append(f"  {filepath.relative_to(PROJECT)}: {h1_count} <h1> tags (expected 1)")
        return False
    return True


# ── Test 4: No Hardcoded Secrets ──────────────────────────────────

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


# ── Main ───────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*60}")
    print(f"  Harness Course Test Suite")
    print(f"  {len(HTML_FILES)} HTML files to check")
    print(f"{'='*60}\n")

    # Filter HTML files (not in .git, etc.)
    html_files = [f for f in HTML_FILES if f.suffix == ".html"]
    
    passed = 0
    failed = 0

    # Test 1: HTML Parse
    print("📄 HTML Parse Validation...")
    for f in html_files:
        if test_html_parse(f):
            passed += 1
        else:
            failed += 1
    print(f"  ✓ {passed}/{len(html_files)} files parsed\n")

    # Test 2: Internal Links
    print("🔗 Internal Link Check...")
    link_ok = 0
    link_fail = 0
    for f in html_files:
        if test_links(f):
            link_ok += 1
        else:
            link_fail += 1
    print(f"  ✓ {link_ok}/{len(html_files)} files checked\n")

    # Test 3: H1 Uniqueness
    print("📌 H1 Uniqueness Check...")
    h1_ok = 0
    for f in html_files:
        if test_h1_uniqueness(f):
            h1_ok += 1
    print(f"  ✓ {h1_ok}/{len(html_files)} pass\n")

    # Test 4: Secrets
    print("🔒 Secrets Check...")
    all_files = list(PROJECT.rglob("*"))
    all_files = [f for f in all_files if f.is_file() and not any(d in f.parts for d in EXCLUDE_DIRS)]
    secret_ok = 0
    for f in all_files:
        if test_no_secrets(f):
            secret_ok += 1
    print(f"  ✓ {secret_ok}/{len(all_files)} files clean\n")

    # Summary
    print(f"{'='*60}")
    total_errors = len(errors)
    total_warnings = len(warnings)

    if total_errors > 0:
        print(f"\n❌ {total_errors} ERROR(S):")
        for e in errors:
            print(f"  {e}")
    
    if total_warnings > 0:
        print(f"\n⚠️  {total_warnings} WARNING(S):")
        for w in warnings:
            print(f"  {w}")

    print(f"\n{'='*60}")
    if total_errors == 0:
        print(f"  ✅ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print(f"  ❌ {total_errors} error(s), {total_warnings} warning(s)")
        sys.exit(1)


if __name__ == "__main__":
    main()
