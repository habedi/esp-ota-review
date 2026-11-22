import hashlib
import json
from pathlib import Path
import runpy
import shutil
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch


class QemuInstallTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        project = root / "tests/reproduce-bugs"
        project.mkdir(parents=True)
        self.installer = project / "install_qemu.py"
        shutil.copyfile(Path(__file__).resolve().parents[1] / self.installer.name, self.installer)
        self.contents = b"verified archive"
        release = {
            "url": "https://example.invalid/qemu.tar.xz",
            "sha256": hashlib.sha256(self.contents).hexdigest(),
        }
        manifest = {"tools": [
            {"name": "another-tool"},
            {"name": "qemu-xtensa", "versions": [
                {"status": "supported"},
                {"status": "recommended", "linux-amd64": release},
            ]},
        ]}
        manifest_path = root / "external/esp-idf-v6.1.1/tools/tools.json"
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_text(json.dumps(manifest))
        self.build = root / "build/ota-qemu"
        self.archive = self.build / "tools/dist/qemu.tar.xz"
        self.archive.parent.mkdir(parents=True)

    def test_interrupted_download_and_corrupt_cache_can_be_retried(self):
        def interrupted_download(_url, path):
            path.write_bytes(b"partial download")
            raise OSError("interrupted download")

        with patch("urllib.request.urlretrieve", side_effect=interrupted_download):
            with self.assertRaisesRegex(OSError, "interrupted download"):
                runpy.run_path(str(self.installer))
        self.assertFalse(self.archive.exists())

        self.archive.write_bytes(b"corrupt cached download")
        stale = self.build / "qemu/old-library"
        with patch("urllib.request.urlretrieve") as download, patch("subprocess.run"):
            download.side_effect = lambda _url, path: path.write_bytes(self.contents)
            runpy.run_path(str(self.installer))
            stale.touch()
            runpy.run_path(str(self.installer))
        self.assertFalse(stale.exists())
        self.assertEqual(self.archive.read_bytes(), self.contents)
        self.assertEqual(download.call_count, 1)

    def test_symlink_destination_stops_install_before_extraction(self):
        self.archive.write_bytes(self.contents)
        target = self.build / "another-install"
        target.mkdir()
        (self.build / "qemu").symlink_to(target, target_is_directory=True)
        with patch("subprocess.run") as run:
            with self.assertRaises(OSError):
                runpy.run_path(str(self.installer))
        run.assert_not_called()
