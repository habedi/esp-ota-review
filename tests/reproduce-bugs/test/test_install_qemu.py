import hashlib
import json
from pathlib import Path
import runpy
import shutil
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch


class QemuInstallTests(unittest.TestCase):
    def test_interrupted_download_and_corrupt_cache_can_be_retried(self):
        contents = b"verified archive"
        release = {
            "url": "https://example.invalid/qemu.tar.xz",
            "sha256": hashlib.sha256(contents).hexdigest(),
        }

        def interrupted_download(_url, path):
            path.write_bytes(b"partial download")
            raise OSError("interrupted download")

        with TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "tests/reproduce-bugs"
            project.mkdir(parents=True)
            installer = project / "install_qemu.py"
            shutil.copyfile(Path(__file__).resolve().parents[1] / installer.name, installer)
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
            archive = root / "build/ota-qemu/tools/dist/qemu.tar.xz"

            with patch("urllib.request.urlretrieve", side_effect=interrupted_download):
                with self.assertRaisesRegex(OSError, "interrupted download"):
                    runpy.run_path(str(installer))
            self.assertFalse(archive.exists())

            archive.write_bytes(b"corrupt cached download")
            with patch("urllib.request.urlretrieve") as download, patch("subprocess.run"):
                download.side_effect = lambda _url, path: path.write_bytes(contents)
                runpy.run_path(str(installer))
                runpy.run_path(str(installer))
            self.assertEqual(archive.read_bytes(), contents)
            self.assertEqual(download.call_count, 1)
