#!/usr/bin/env python3
import json
import urllib.request
import xml.etree.ElementTree as ET
import re
import sys
from datetime import datetime, timezone

FEED_URL = "https://community.ui.com/rss/releases/UniFi-Network-Application/e6712595-81bb-4829-8e42-9e2630fabcfe"
DOCKERFILE = "Dockerfile"
README = "README.md"


def fetch(url: str) -> bytes:
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (GitHub Actions UniFi Updater)"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


FIRMWARE_API = (
    "https://fw-update.ubnt.com/api/firmware-latest"
    "?filter=eq~~product~~unifi-controller"
    "&filter=eq~~channel~~release"
)
VERSION_RE = re.compile(r"(\d+\.\d+\.\d+)")


def latest_debian_release(api_bytes):
    """
    Return the latest self-hosted Debian release published by Ubiquiti.

    The community RSS feed also announces releases that are not shipped as a
    self-hosted Linux package (e.g. UniFi OS only builds), so the firmware API
    is the source of truth for what can actually be installed.
    """
    data = json.loads(api_bytes)
    firmware = data.get("_embedded", {}).get("firmware", [])
    debs = [f for f in firmware if f.get("platform") == "debian"]
    if not debs:
        raise RuntimeError("No Debian release found in UniFi firmware API")

    fw = max(
        debs,
        key=lambda f: (f["version_major"], f["version_minor"], f["version_patch"]),
    )
    version = f"{fw['version_major']}.{fw['version_minor']}.{fw['version_patch']}"
    url = fw["_links"]["data"]["href"]
    if not url.startswith("https://") or not url.endswith(".deb"):
        raise RuntimeError(f"Unexpected Debian package URL from firmware API: {url}")

    date_str = (fw.get("created") or "")[:10]
    return {"version": version, "url": url, "date": date_str}


def changelog_link(feed_bytes, version):
    """Find the community release notes link for a given version in the RSS feed."""
    root = ET.fromstring(feed_bytes)
    for item in root.findall(".//item"):
        m = VERSION_RE.search(item.findtext("title") or "")
        if m and m.group(1) == version:
            return (item.findtext("link") or "").strip()
    return ""


def assert_downloadable(url: str) -> None:
    req = urllib.request.Request(
        url,
        method="HEAD",
        headers={"User-Agent": "Mozilla/5.0 (GitHub Actions UniFi Updater)"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Package URL returned HTTP {resp.status}: {url}")


def update_dockerfile(url: str) -> None:
    with open(DOCKERFILE, "r", encoding="utf-8") as f:
        src = f.read()

    new_src, subs = re.subn(
        r"ARG\s+PKGURL=.*",
        f"ARG PKGURL={url}",
        src,
        count=1,
    )

    if subs == 0:
        raise RuntimeError("Failed to update PKGURL in Dockerfile")

    if new_src != src:
        with open(DOCKERFILE, "w", encoding="utf-8") as f:
            f.write(new_src)


def update_readme(version: str, date_str: str, link: str) -> None:
    with open(README, "r", encoding="utf-8") as f:
        src = f.read()

    new_row = (
        f"| [`latest` `v{version}`](https://github.com/jsoyer/unifi-network-server/blob/master/Dockerfile) "
        f"| Current Stable: Version {version} as of {date_str} "
        f"| [Change Log {version}]({link}) |"
    )

    # Replace the first "latest" row in the Current Information table
    new_src, subs = re.subn(
        r"^\| \[`latest` `v[0-9.]+`\]\(.*?\) \| Current Stable: Version [0-9.]+ as of [0-9-]+ \| \[Change Log [0-9.]+\]\(.*?\) \|$",
        new_row,
        src,
        count=1,
        flags=re.MULTILINE,
    )

    if subs == 0:
        raise RuntimeError("Failed to update README row")

    if new_src != src:
        with open(README, "w", encoding="utf-8") as f:
            f.write(new_src)


def main() -> None:
    rel = latest_debian_release(fetch(FIRMWARE_API))
    version = rel["version"]
    assert_downloadable(rel["url"])

    try:
        link = changelog_link(fetch(FEED_URL), version)
    except Exception as exc:  # RSS is only used for the changelog link
        print(f"warning: could not read release RSS feed: {exc}", file=sys.stderr)
        link = ""
    if not link:
        link = f"https://community.ui.com/releases?q={version}"

    date_str = rel["date"] or datetime.now(timezone.utc).date().isoformat()

    update_dockerfile(rel["url"])
    update_readme(version, date_str, link)

    # Printed so GitHub Actions step can capture it
    print(version)


if __name__ == "__main__":
    main()
