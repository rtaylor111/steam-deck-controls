"""Check a public GitHub repo and replace the app files.

shortcuts.json, controller files and backups are never replaced.
The repo is empty until Ross names owner/name. No extra package.
"""

import io
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import PurePosixPath
from pathlib import Path

REPO = "rtaylor111/steam-deck-controls"
BRANCH = "main"
ZIP_FILES = (
    "deck_app.py",
    "layout.py",
    "library.py",
    "update.py",
    "Shortcuts.desktop",
)
REQUIRED = ("deck_app.py", "layout.py", "library.py", "update.py")
_REPO_NAME = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_SHA = re.compile(r"^[0-9a-f]{40}$")
_HOSTS = ("api.github.com", "codeload.github.com")
HERE = Path(__file__).resolve().parent


def request_headers(token):
    headers = {
        "User-Agent": "steam-deck-shortcuts",
        "Accept": "application/vnd.github+json",
    }
    if token:
        headers["Authorization"] = "Bearer " + token.strip()
    return headers


def _read_token(folder):
    path = Path(folder) / "github.token"
    try:
        if not path.is_file() or path.is_symlink():
            return ""
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def fetch(url, timeout=8):
    """GET a GitHub URL. A token is sent only to GitHub hosts."""
    host = urllib.parse.urlparse(url).hostname
    token = _read_token(HERE) if host in _HOSTS else ""
    req = urllib.request.Request(url, headers=request_headers(token))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


def local_sha(folder):
    path = Path(folder) / "version.txt"
    try:
        if not path.is_file() or path.is_symlink():
            return ""
        text = path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""
    return text if _SHA.fullmatch(text) else ""


def parse_sha(body):
    try:
        sha = json.loads(body.decode("utf-8")).get("sha", "")
    except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
        return ""
    if isinstance(sha, str) and _SHA.fullmatch(sha):
        return sha
    return ""


def available(folder, fetch, repo=None):
    """Return (message, ready, sha). fetch(url) returns (status, body)."""
    repo = REPO if repo is None else repo
    if not _REPO_NAME.fullmatch(repo or ""):
        return "No update place set.", False, ""
    url = "https://api.github.com/repos/%s/commits/%s" % (repo, BRANCH)
    try:
        code, body = fetch(url)
    except Exception:
        return "Could not check for updates.", False, ""
    if code != 200:
        return "Could not check for updates.", False, ""
    sha = parse_sha(body)
    if not sha:
        return "Could not check for updates.", False, ""
    if sha == local_sha(folder):
        return "Already this copy.", False, sha
    return "An update is ready.", True, sha


def download(repo, sha, fetch):
    if not _REPO_NAME.fullmatch(repo or "") or not _SHA.fullmatch(sha or ""):
        return None, "Could not download the update."
    url = "https://codeload.github.com/%s/zip/%s" % (repo, sha)
    try:
        code, body = fetch(url)
    except Exception:
        return None, "Could not download the update."
    if code != 200 or not body:
        return None, "Could not download the update."
    return body, ""


def _hostile(name):
    if not name or name.startswith("/") or name.startswith("\\") or "\\" in name:
        return True
    return ".." in PurePosixPath(name).parts


def files_from_zip(blob):
    """Return (files, message). files is None when the zip is refused."""
    try:
        zf = zipfile.ZipFile(io.BytesIO(blob))
    except zipfile.BadZipFile:
        return None, "Could not download the update."
    found = {}
    for info in zf.infolist():
        name = info.filename
        if _hostile(name):
            return None, "That file points outside this folder."
        if name.endswith("/"):
            continue
        parts = PurePosixPath(name).parts
        if len(parts) > 2 or parts[-1] not in ZIP_FILES:
            continue
        if parts[-1] in found:
            return None, "The update did not include the app."
        found[parts[-1]] = zf.read(info)
    if any(name not in found for name in REQUIRED):
        return None, "The update did not include the app."
    return found, ""


def _outside(folder, path):
    root = Path(folder).resolve()
    try:
        Path(path).resolve().relative_to(root)
    except (OSError, ValueError):
        return True
    return False


def _replace(path, data):
    path = Path(path)
    mode = path.stat().st_mode if path.is_file() else None
    temporary = Path(str(path) + ".updating")
    temporary.write_bytes(data)
    if mode is not None:
        os.chmod(temporary, mode)
    try:
        os.replace(temporary, path)
    except OSError:
        temporary.unlink(missing_ok=True)
        raise


def _restore(path, data):
    if data is None:
        Path(path).unlink(missing_ok=True)
        return
    _replace(path, data)


def apply_files(folder, files, sha):
    """Replace the app files. Return (message, applied)."""
    folder = Path(folder)
    if not _SHA.fullmatch(sha or ""):
        return "Could not update. The app was left as it was.", False
    if any(name not in ZIP_FILES for name in files):
        return "The update did not include the app.", False
    if any(name not in files for name in REQUIRED):
        return "The update did not include the app.", False
    names = list(files) + ["version.txt"]
    for name in names:
        path = folder / name
        if path.is_symlink() or _outside(folder, path):
            return "That file points outside this folder.", False
    previous = {}
    for name in names:
        path = folder / name
        previous[name] = path.read_bytes() if path.is_file() else None
    written = []
    try:
        for name, data in files.items():
            _replace(folder / name, data)
            written.append(name)
        _replace(folder / "version.txt", (sha + "\n").encode("utf-8"))
        written.append("version.txt")
    except OSError:
        for name in reversed(written):
            try:
                _restore(folder / name, previous[name])
            except OSError:
                pass
        return "Could not update. The app was left as it was.", False
    return "Updated. Open Deck Controls again.", True
