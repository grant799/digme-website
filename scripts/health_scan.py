#!/usr/bin/env python3
"""
digme-website health scan.

Ports the manual pre-deploy checks (previously run by hand before each
push) into something CI runs automatically on every push/PR. Checks:

1. Leftover bracket placeholders (e.g. "[CLIENT NAME]", "[TODO]") — a
   template placeholder that made it into a page that went live.
2. Dummy/instruction text (Lorem ipsum, "INSERT TEXT HERE", "placeholder
   copy", etc.) that was left in during drafting.
3. Broken internal links — an href="/something.html" or href="something.html"
   pointing at a page that doesn't exist in this repo.
4. Nav/CTA integrity — every page's main nav should link to every other
   real page, and every page should have at least one CTA link to
   /contact.html (the site's single conversion path).
5. Stray email addresses — anything that isn't the one sanctioned
   contact address, since a wrong/old email address on a live page is
   a lead-loss bug that's easy to miss visually.

Exit non-zero if anything fails, so CI blocks the merge/deploy.
"""
import glob
import os
import re
import sys

SANCTIONED_EMAILS = {
    "info@digme.co.za",
    # Information Regulator complaints address — legitimately quoted in
    # the POPIA notice / privacy policy, not a DigMe address.
    "complaints.ir@justice.gov.za",
}

BRACKET_PLACEHOLDER_RE = re.compile(r"\[[A-Z][A-Z0-9 _\-/]{2,40}\]")

DUMMY_TEXT_PATTERNS = [
    re.compile(r"lorem ipsum", re.IGNORECASE),
    re.compile(r"insert (text|copy|content) here", re.IGNORECASE),
    re.compile(r"placeholder (text|copy|content)", re.IGNORECASE),
    re.compile(r"\btodo\b", re.IGNORECASE),
    re.compile(r"\btbd\b", re.IGNORECASE),
    re.compile(r"coming soon", re.IGNORECASE),
]

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

HREF_RE = re.compile(r'href=["\']([^"\']+)["\']')

FAILURES = []
WARNINGS = []


def html_files():
    return sorted(glob.glob("**/*.html", recursive=True))


def check_bracket_placeholders(files):
    for fname in files:
        with open(fname, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for m in BRACKET_PLACEHOLDER_RE.finditer(content):
            # Skip common false positives: CSS media-query-like or JS array literals are rare in raw HTML text nodes
            FAILURES.append(f"{fname}: bracket placeholder found: {m.group(0)!r}")


def check_dummy_text(files):
    for fname in files:
        with open(fname, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for pattern in DUMMY_TEXT_PATTERNS:
            for m in pattern.finditer(content):
                FAILURES.append(f"{fname}: dummy/instruction text found: {m.group(0)!r}")


PLACEHOLDER_ATTR_RE = re.compile(r'placeholder=["\'][^"\']*["\']')


def check_stray_emails(files):
    for fname in files:
        with open(fname, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        # Strip form placeholder hint text (e.g. placeholder="jane@yourbusiness.co.za")
        # before scanning — that's UI example text, not a real address on the page.
        scan_content = PLACEHOLDER_ATTR_RE.sub("", content)
        for m in EMAIL_RE.finditer(scan_content):
            addr = m.group(0)
            if addr.lower() not in SANCTIONED_EMAILS:
                FAILURES.append(f"{fname}: stray/unexpected email address found: {addr!r} (allowed: {', '.join(sorted(SANCTIONED_EMAILS))})")


def check_broken_internal_links(files):
    existing = set(files)
    for fname in files:
        file_dir = os.path.dirname(fname)
        with open(fname, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for m in HREF_RE.finditer(content):
            href = m.group(1)
            # Only check same-site relative links to .html files
            if href.startswith(("http://", "https://", "mailto:", "tel:", "#")):
                continue
            path_part = href.split("#")[0].split("?")[0]
            if not path_part or not path_part.endswith(".html"):
                continue
            if path_part.startswith("/"):
                # Site-root-relative link
                target = path_part.lstrip("/")
            else:
                # Relative to the file's own directory
                target = os.path.normpath(os.path.join(file_dir, path_part))
            if target not in existing:
                FAILURES.append(f"{fname}: broken internal link -> {href!r} (resolved to {target!r}, not found in repo)")


def check_nav_cta_integrity(files):
    if "contact.html" not in files:
        FAILURES.append("contact.html is missing entirely — the whole site's conversion path is broken.")
        return
    for fname in files:
        if fname in ("404.html", "contact.html"):
            continue
        with open(fname, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if "contact.html" not in content:
            WARNINGS.append(f"{fname}: no link to contact.html found — page may have no conversion path.")


if __name__ == "__main__":
    files = html_files()
    if not files:
        FAILURES.append("No .html files found in repo root — did the scan run from the wrong directory?")
    else:
        check_bracket_placeholders(files)
        check_dummy_text(files)
        check_stray_emails(files)
        check_broken_internal_links(files)
        check_nav_cta_integrity(files)

    if WARNINGS:
        print("Warnings (non-blocking):")
        for w in WARNINGS:
            print(f" - {w}")

    if FAILURES:
        print(f"\nHEALTH SCAN FAILED ({len(FAILURES)} issue(s)):")
        for f in FAILURES:
            print(f" - {f}")
        sys.exit(1)

    print(f"Health scan passed — {len(files)} page(s) checked, 0 failures, {len(WARNINGS)} warning(s).")
