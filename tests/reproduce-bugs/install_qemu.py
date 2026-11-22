"""Download and verify the pinned Linux x86-64 QEMU archive."""

import hashlib
import json
import shutil
import subprocess
import urllib.request
from pathlib import Path
from tempfile import TemporaryDirectory


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


root = Path(__file__).resolve().parents[2]
manifest = json.loads((root / 'external/esp-idf-v6.1.1/tools/tools.json').read_text())
qemu = next(tool for tool in manifest['tools'] if tool['name'] == 'qemu-xtensa')
release = next(version['linux-amd64'] for version in qemu['versions']
               if version['status'] == 'recommended')
archive = root / 'build/ota-qemu/tools/dist' / release['url'].rsplit('/', 1)[1]
archive.parent.mkdir(parents=True, exist_ok=True)
if not archive.is_file() or sha256(archive) != release['sha256']:
    with TemporaryDirectory(dir=archive.parent) as directory:
        download = Path(directory) / archive.name
        urllib.request.urlretrieve(release['url'], download)
        if sha256(download) != release['sha256']:
            raise ValueError('QEMU archive checksum mismatch')
        download.replace(archive)
output = root / 'build/ota-qemu/qemu'
try:
    shutil.rmtree(output)
except FileNotFoundError:
    pass
output.mkdir()
subprocess.run(['tar', '-xf', str(archive), '-C', str(output), '--strip-components=1'], check=True)
subprocess.run([str(output / 'bin/qemu-system-xtensa'), '--version'], check=True)
