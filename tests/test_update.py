import io
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import update

SHA = "a" * 40
OTHER = "b" * 40


def _zip(members):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, data in members.items():
            zf.writestr(name, data)
    return buf.getvalue()


def _app_zip(extra=None, prefix="shortcuts-main/"):
    members = {
        prefix + "deck_app.py": b"deck\n",
        prefix + "layout.py": b"layout\n",
        prefix + "library.py": b"library\n",
        prefix + "update.py": b"update\n",
        prefix + "Shortcuts.desktop": b"[Desktop Entry]\n",
    }
    if extra:
        members.update(extra)
    return _zip(members)


class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_empty_repo_does_not_fetch(self):
        def fetch(_url):
            raise AssertionError("fetch")

        message, ready, sha = update.available(self.tmp, fetch, repo="")
        self.assertEqual(message, "No update place set.")
        self.assertFalse(ready)
        self.assertEqual(sha, "")

    def test_same_sha_is_not_offered(self):
        (self.tmp / "version.txt").write_text(SHA + "\n", encoding="utf-8")

        def fetch(_url):
            return 200, ('{"sha":"%s"}' % SHA).encode()

        message, ready, sha = update.available(self.tmp, fetch, repo="owner/shortcuts")
        self.assertEqual(message, "Already this copy.")
        self.assertFalse(ready)
        self.assertEqual(sha, SHA)

    def test_newer_sha_is_offered(self):
        def fetch(_url):
            return 200, ('{"sha":"%s"}' % OTHER).encode()

        message, ready, sha = update.available(self.tmp, fetch, repo="owner/shortcuts")
        self.assertEqual(message, "An update is ready.")
        self.assertTrue(ready)
        self.assertEqual(sha, OTHER)

    def test_token_header_is_only_added_when_set(self):
        self.assertNotIn("Authorization", update.request_headers(""))
        headers = update.request_headers("test-token")
        self.assertEqual(headers["Authorization"], "Bearer test-token")

    def test_apply_replaces_app_files_and_leaves_shortcuts(self):
        kept = self.tmp / "shortcuts.json"
        kept.write_text('[{"name":"keep"}]', encoding="utf-8")
        (self.tmp / "controller_neptune.vdf").write_bytes(b"live")
        files, reason = update.files_from_zip(_app_zip({
            "shortcuts-main/shortcuts.json": b'[{"name":"wipe"}]',
            "shortcuts-main/controller_neptune.vdf": b"wipe",
        }))
        self.assertEqual(reason, "")
        message, applied = update.apply_files(self.tmp, files, OTHER)
        self.assertTrue(applied, message)
        self.assertEqual((self.tmp / "deck_app.py").read_bytes(), b"deck\n")
        self.assertEqual((self.tmp / "version.txt").read_text(encoding="utf-8"), OTHER + "\n")
        self.assertEqual(kept.read_text(encoding="utf-8"), '[{"name":"keep"}]')
        self.assertEqual((self.tmp / "controller_neptune.vdf").read_bytes(), b"live")
        self.assertFalse((self.tmp / "shortcuts.json").read_text(encoding="utf-8").find("wipe") >= 0)

    def test_escape_writes_nothing(self):
        (self.tmp / "deck_app.py").write_bytes(b"old\n")
        files, reason = update.files_from_zip(_app_zip({"../deck_app.py": b"bad\n"}))
        self.assertIsNone(files)
        self.assertEqual(reason, "That file points outside this folder.")
        self.assertEqual((self.tmp / "deck_app.py").read_bytes(), b"old\n")
        self.assertFalse((self.tmp / "version.txt").exists())

    def test_missing_app_file_writes_nothing(self):
        blob = _zip({"shortcuts-main/deck_app.py": b"deck\n"})
        files, reason = update.files_from_zip(blob)
        self.assertIsNone(files)
        self.assertEqual(reason, "The update did not include the app.")

    def test_failed_replace_puts_the_old_file_back(self):
        (self.tmp / "deck_app.py").write_bytes(b"old\n")
        files, reason = update.files_from_zip(_app_zip())
        self.assertEqual(reason, "")
        real = update.os.replace
        calls = {"n": 0}

        def fail(src, dst):
            calls["n"] += 1
            if calls["n"] == 2:
                raise OSError("pulled")
            return real(src, dst)

        update.os.replace = fail
        try:
            message, applied = update.apply_files(self.tmp, files, OTHER)
        finally:
            update.os.replace = real
        self.assertFalse(applied)
        self.assertEqual(message, "Could not update. The app was left as it was.")
        self.assertEqual((self.tmp / "deck_app.py").read_bytes(), b"old\n")
        self.assertFalse((self.tmp / "version.txt").exists())

    def test_symlink_outside_is_refused(self):
        outside = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, outside, True)
        victim = outside / "deck_app.py"
        victim.write_bytes(b"keep\n")
        (self.tmp / "deck_app.py").symlink_to(victim)
        files, _reason = update.files_from_zip(_app_zip())
        message, applied = update.apply_files(self.tmp, files, OTHER)
        self.assertFalse(applied)
        self.assertEqual(message, "That file points outside this folder.")
        self.assertEqual(victim.read_bytes(), b"keep\n")
        self.assertFalse((self.tmp / "version.txt").exists())

    def test_apply_preserves_existing_file_mode(self):
        import os
        import stat

        desktop = self.tmp / "Shortcuts.desktop"
        desktop.write_bytes(b"[Desktop Entry]\n")
        if os.name != "nt":
            desktop.chmod(0o755)
            expected = stat.S_IMODE(desktop.stat().st_mode)
        else:
            expected = stat.S_IMODE(desktop.stat().st_mode)
        files, reason = update.files_from_zip(_app_zip())
        self.assertEqual(reason, "")
        _message, applied = update.apply_files(self.tmp, files, OTHER)
        self.assertTrue(applied)
        self.assertEqual(stat.S_IMODE(desktop.stat().st_mode), expected)


if __name__ == "__main__":
    unittest.main()
