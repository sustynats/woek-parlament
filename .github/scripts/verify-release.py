"""Extract and verify a commit-bound public Parliament Pages release."""

import json
import re
import shutil
import sys
import tarfile
from pathlib import Path, PurePosixPath


MAX_FILE = 75 * 1024 * 1024
MAX_SITE = 900 * 1024 * 1024
MAX_ENTRIES = 100_000
DOMAIN = "parlament.wirkungsoekonomie.de"
REQUIRED_FILES = {
    ".nojekyll",
    "CNAME",
    "_woek-build-manifest.json",
    "index.html",
    "robots.txt",
    "wirkungsakten/index.html",
    "pruefstandard/quellen/index.html",
}


def verify_path(member):
    relative = PurePosixPath(member.name)
    parts = relative.parts
    if relative.is_absolute() or ".." in parts or "\\" in member.name:
        raise ValueError(f"Archive path escapes the publication root: {member.name}")
    if not parts and member.isdir():
        return relative
    if not parts or parts[0] == "api":
        raise ValueError(f"Invalid publication path: {member.name}")
    if any(part.startswith(".") for part in parts) and relative.as_posix() != ".nojekyll":
        raise ValueError(f"Unexpected hidden publication path: {member.name}")
    if relative.suffix == ".txt" and relative.as_posix() != "robots.txt":
        raise ValueError(f"Unexpected server navigation payload: {member.name}")
    if not member.isfile() and not member.isdir():
        raise ValueError(f"Non-regular publication entry: {member.name}")
    return relative


def extract_archive(archive, output):
    output.mkdir()
    files = set()
    total = 0
    with tarfile.open(archive, "r|gz") as contents:
        for count, member in enumerate(contents, 1):
            if count > MAX_ENTRIES:
                raise ValueError("Archive has too many entries")
            relative = verify_path(member)
            target = output / relative
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            key = relative.as_posix()
            if key in files or member.size > MAX_FILE:
                raise ValueError(f"Duplicated or oversized release file: {key}")
            total += member.size
            if total > MAX_SITE:
                raise ValueError("Public release exceeds the 900 MiB size guard")
            target.parent.mkdir(parents=True, exist_ok=True)
            source = contents.extractfile(member)
            if source is None:
                raise ValueError(f"Archive contains an unreadable entry: {key}")
            with source, target.open("xb") as stream:
                shutil.copyfileobj(source, stream)
            files.add(key)
    return files


def verify_release(archive, output, commit, fingerprint):
    if not re.fullmatch(r"[a-f0-9]{40}", commit) or not re.fullmatch(r"[a-f0-9]{64}", fingerprint):
        raise ValueError("Supply the full verified commit and fingerprint")
    files = extract_archive(archive, output)
    if missing := REQUIRED_FILES - files:
        raise ValueError(f"Missing publication files: {', '.join(sorted(missing))}")
    if (output / "CNAME").read_text().strip() != DOMAIN:
        raise ValueError("Archive targets the wrong Pages domain")
    manifest = json.loads((output / "_woek-build-manifest.json").read_text())
    expected = {
        "schema_version": "woek-static-public-build-v1",
        "canonical_origin": f"https://{DOMAIN}",
        "source_commit": commit,
        "source_fingerprint": fingerprint,
        "react_server_navigation_included": False,
        "server_runtime_included": False,
    }
    for field, value in expected.items():
        if manifest.get(field) != value:
            raise ValueError(f"Release manifest mismatch: {field}")
    if manifest.get("file_count") != len(files):
        raise ValueError("Release manifest file count does not match the archive")
    print(f"Verified public Parliament release {commit} with {len(files)} files")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        raise SystemExit("Usage: verify-release.py ARCHIVE OUTPUT COMMIT FINGERPRINT")
    verify_release(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4])
