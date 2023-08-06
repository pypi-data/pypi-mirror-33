from contextlib import suppress
from pathlib import Path

import click
import dpath
import yaml

from upersetter.handler import FileHandler, RemoteHandler, ScriptHandler
from upersetter.utils import get_expanded, prompt_for_choice, get_list_input, prompt_for_input, check_if_safe, prompt_for_list


class SetUp:
    """Creates the basic structure from the given parameters.
    Replaces template placeholders in structure with given options. Files can be given as templates
    or as string content in the structure file.
    If they contain template placeholders they will be expanded with the options as well.
    :param structure: Can either be a dict or a filepath (string), this defines the basic structure of the project
    :param options: Can either be a dict or a filepath (string), this defines the options to be used as replacement for template strings
    :param templates: Directory to templates if any are used in the structure
    :param metadata: Can either be a dict or a filepath (string), If in interactive mode (see method setup) this will be used to add info to the user prompts
    :param out_dir: The path where the final project should be created
    :param unsafe: If true allows unsafe path expansion - by default (safe) only paths inside the specified out_path are allowed to be written
    """
    def __init__(self, structure):
        self.structure_hooks = [FileHandler, RemoteHandler, ScriptHandler]

        self._templates_path = Path('./templates')
        self._options = {}
        self._out_dir = Path('./')
        self._unsafe = False
        self._metadata = {}

        self.structure = structure

    @property
    def templates(self):
        return self.templates

    @templates.setter
    def templates(self, value):
        self._templates_path = Path(value)

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, value):
        try:
            self._options = yaml.safe_load(Path(value).read_text())
        except TypeError:
            self._options = value or {}

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        try:
            self._metadata = yaml.safe_load(Path(value).read_text())
        except TypeError:
            self._metadata = value

    @property
    def out_dir(self):
        return self._out_dir

    @out_dir.setter
    def out_dir(self, value):
        self._out_dir = Path(value).resolve()

    @property
    def unsafe(self):
        return self._unsafe

    @unsafe.setter
    def unsafe(self, value):
        self._unsafe = value

    def setup(self, interactive=False):
        """Entrypoint for creating the structure, if interactive is true the user will be prompted for entries.
        The metadata (if specified) will be used to add additional info to the prompt or allow only certain values.
        :param interactive: Set to true if the user should be asked for a value for every entry in the options file
        """
        if interactive:
            self._options = Interact(self._metadata, self._options).do_interaction()
        # Read the file if structure is a path-string, else use structure as is (dict)
        with suppress(TypeError):
            structure_path = Path(self.structure)
            expanded = get_expanded(str(structure_path.parent), structure_path.name, self._options)
            self.structure = yaml.safe_load(expanded)
        self._create_structure(self.structure)

    def _create_structure(self, structure, parent=None):
        for key, value in structure.items():
            # Check how we should treat the entry and execute appropriate hook
            for structure_hook in self.structure_hooks:
                sh = structure_hook(key, value, parent, self)
                if sh.check():
                    sh.create()
                    break
            # No special hook was found, create as path and execute again
            else:
                path = self._out_dir.joinpath(Path(parent), Path(key)) if parent else self._out_dir.joinpath(Path(key))
                if not self._unsafe:
                    check_if_safe(path, self._out_dir)
                self._out_dir.joinpath(path).mkdir(exist_ok=True)
                self._create_structure(value, str(path))


class Interact:
    """Defines interactive behaviour if setup is run in interactive mode."""
    def __init__(self, metadata, options):
        self._metadata = metadata
        self._options = options

    def do_interaction(self, options=None, parent=''):
        # Iterate through all options until we have a leaf node, then execute the prompt
        if parent == '':
            options = self._options
        try:
            for k, v in options.items():
                self.do_interaction(v, parent + '.' + k)
        except AttributeError:
            self._ask(parent, options)
        return self._options

    def _ask(self, parent, options):
        try:
            meta = dpath.get(self._metadata, parent, '.')
        except KeyError:
            meta = {}

        if '_help' in meta:
            click.secho(meta['_help'], bold=True)

        if '_choices' in meta:
            result = prompt_for_choice(meta['_choices'], parent)
        else:
            if isinstance(options, list):

                result = get_list_input(prompt_for_list(options, parent))
            else:
                result = prompt_for_input(options, parent)
        dpath.set(self._options, parent, result, separator='.')
