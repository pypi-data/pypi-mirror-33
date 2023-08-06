import shutil
from copy import deepcopy
from pathlib import Path

import yaml


class Scanner:
    """Scans a given path to create a structure file from it.
    Basically this does the reverse of SetUp and is usefull to create initial uppersetter infos for a given project.
    """
    def __init__(self, to_scan, out_dir, inline_content=False):
        self.to_scan = Path(to_scan)
        self.out_dir = Path(out_dir)
        self.inline_content = inline_content
        self.template_folder = self.out_dir.joinpath('templates')
        self.structure = {}

    def scan(self):
        self.template_folder.mkdir()
        self._scan_dir(deepcopy(self.to_scan), self.structure)
        with self.out_dir.joinpath('structure.yaml').open('w+') as f:
            yaml.safe_dump(self.structure, f)

    def _add_file(self, entry, parent):
        if 'files' not in parent:
            parent['files'] = []
        if self.inline_content:
            file = {'content': entry.read_text()}
        else:
            full_name = str(entry.parent).replace('/', '_').replace('\\', '_') + '-' + entry.name
            shutil.copy(str(entry), str(self.template_folder.joinpath(full_name)))
            file = {'template': full_name}
        parent['files'].append({entry.name: file})

    def _scan_dir(self, directory, parent: dict):
        for entry in directory.iterdir():
            parent.setdefault(entry.parent.name, {})
            if entry.is_dir():
                self._scan_dir(entry, parent[entry.parent.name])
            else:
                self._add_file(entry, parent[entry.parent.name])
