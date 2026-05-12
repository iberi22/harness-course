#!/usr/bin/env python3
"""HTML Structure Validation Tests for Harness Course.
Validates HTML parse structure, DOCTYPE presence, unclosed tags, and H1 uniqueness.
"""
import os
import re
import html.parser
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
HTML_FILES = [f for f in PROJECT.rglob("*.html")
              if not any(d in f.parts for d in {".git", "node_modules", "target"})]
EXCLUDE_DIRS = {".git", "node_modules", "target"}

errors = []
warnings = []


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

    unclosed = [t for t in validator.tag_stack
                if t not in {"html", "head", "body", "p", "li", "td", "th", "tr", "option"}]
    if unclosed:
        warnings.append(f"  {filepath.relative_to(PROJECT)}: unclosed tags: {unclosed}")
        return False

    if "<!DOCTYPE html" not in content and "<!doctype html" not in content:
        warnings.append(f"  {filepath.relative_to(PROJECT)}: missing DOCTYPE")
        return False

    return True


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


def main():
    print(f"\n{'='*60}")
    print(f"  HTML Validation Tests — {len(HTML_FILES)} files")
    print(f"{'='*60}\n")

    html_files = [f for f in HTML_FILES if f.suffix == ".html"]
    parse_ok = 0
    h1_ok = 0

    print("📄 HTML Parse Validation...")
    for f in html_files:
        if test_html_parse(f):
            parse_ok += 1
    print(f"  ✓ {parse_ok}/{len(html_files)} files parsed\n")

    print("📌 H1 Uniqueness Check...")
    for f in html_files:
        if test_h1_uniqueness(f):
            h1_ok += 1
    print(f"  ✓ {h1_ok}/{len(html_files)} files pass\n")

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
        print(f"  ✅ ALL HTML VALIDATION TESTS PASSED")
        return True
    else:
        print(f"  ❌ {total_errors} error(s), {total_warnings} warning(s)")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
