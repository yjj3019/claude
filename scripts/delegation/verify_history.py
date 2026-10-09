#!/usr/bin/env python3
"""Verify the archived Git history without network or a source checkout."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / 'docs' / 'delegation-loop' / 'source-history'


def verify():
    manifest = json.loads((ARCHIVE / 'manifest.json').read_text(encoding='utf-8'))
    for name, expected in manifest['artifacts'].items():
        raw = (ARCHIVE / name).read_bytes()
        assert len(raw) == expected['bytes'], name
        assert hashlib.sha256(raw).hexdigest() == expected['sha256'], name
    with tempfile.TemporaryDirectory() as temporary:
        restored = Path(temporary) / 'source.git'
        subprocess.run(['git', 'clone', '--mirror', str(ARCHIVE / 'DelegationLoop.bundle'), str(restored)],
                       check=True, capture_output=True)

        def git(*args):
            return subprocess.check_output(['git', '-C', str(restored), *args])

        git('fsck', '--full')
        refs = dict(line.split(' ', 1)[::-1] for line in git('show-ref').decode().splitlines())
        assert refs == manifest['refs'], 'restored refs differ'
        assert set(git('rev-list', '--all').decode().splitlines()) == set(manifest['commits'])
        object_ids = [line.split()[0] for line in git('rev-list', '--objects', '--all').decode().splitlines()]
        batch = subprocess.check_output(['git', '-C', str(restored), 'cat-file', '--batch'],
                                        input=('\n'.join(object_ids) + '\n').encode())
        objects, counts, offset = {}, {}, 0
        for oid in object_ids:
            end = batch.index(b'\n', offset)
            found, kind, size = batch[offset:end].decode().split()
            assert found == oid
            offset = end + 1
            raw = batch[offset:offset + int(size)]
            objects[oid] = raw
            counts[kind] = counts.get(kind, 0) + 1
            offset += int(size) + 1
        assert counts == manifest['objects'], 'restored object counts differ'
        assert set(manifest['advertised_remote_refs'].values()).issubset(objects), 'advertised ref target missing'
        for ref, files in manifest['files'].items():
            actual = {line.split('\t', 1)[1]: line.split('\t', 1)[0].split()
                      for line in git('ls-tree', '-r', ref).decode().splitlines()}
            assert set(actual) == {entry['path'] for entry in files}
            for entry in files:
                mode, kind, oid = actual[entry['path']]
                assert mode == entry['mode'] and oid == entry['blob']
                assert hashlib.sha256(objects[oid]).hexdigest() == entry['sha256']
    print('History archive checksums, mirror restore, refs, commits, file bytes and fsck: PASS')


if __name__ == '__main__':
    verify()
