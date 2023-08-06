#!/usr/bin/env python3

"""pyconf - a project configuration utility.

pyconf attempts to replicate the role of the unix autoconf utility.
Where autoconf relies on .in and an autoconf.ac file pyconf relies on
.pin and a pyconf.yml file."""

import os
import re
import sys
import traceback

import yaml

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

# The text that wraps error messages
ERROR_MESSAGE = '''
-------------------------------------------------------------------------------
FATAL: {0}
-------------------------------------------------------------------------------
'''

# Extension for replaceable files
PYCONF_EXTENSION = '.pin'


# -----------------------------------------------------------------------------
def error(msg):
    """
    Reports and error and exits the application
    :param msg: the reason to exit the application
    """

    assert msg

    print(ERROR_MESSAGE.format(msg), file=sys.stderr)

    # Make sure that we raise an exception when unit testing instead of just
    # exiting
    for level in traceback.extract_stack():
        if 'unittest' in level[0]:
            if isinstance(msg, BaseException):
                raise msg
            else:
                raise RuntimeError(msg)

    sys.exit(1)


# -----------------------------------------------------------------------------
# Loader
# -----------------------------------------------------------------------------
class Loader:
    """This class loads the pyconf.yaml configuration file"""

    basename = 'pyconf'
    filename = None

    def __init__(self):
        """Loads the configuration file into memory"""
        self.workdir = os.getcwd()
        self.contents = None

        filename_yml = self.basename + '.yml'
        filename_yaml = self.basename + '.yaml'

        is_file_yml = os.path.isfile(filename_yml)
        is_file_yaml = os.path.isfile(filename_yaml)

        if is_file_yml and is_file_yaml:
            error("Found configuration file {0} with both extensions '.yml' "
                  "and '.yaml' in {1}. You can have one or the other, "
                  "but not both."
                  .format(self.basename, self.workdir))

        if not is_file_yml and not is_file_yaml:
            error("Missing configuration file {0} in working directory {1}"
                  .format(filename_yml, self.workdir))

        if is_file_yml:
            self.filename = filename_yml
        else:
            self.filename = filename_yaml

        with open(self.filename, 'r') as file:
            try:
                self.contents = yaml.load(file, Loader=yaml.loader.BaseLoader)
            except yaml.YAMLError as exc:
                error(exc)

        # Make sure we always have a 'files' section, even if it is empty
        if 'files' not in self.contents or not self.contents['files']:
            self.contents['files'] = []

    # -------------------------------------------------------------------------
    def get_contents(self):
        """Gets the safely loaded YAML file contents."""
        return self.contents

    # -------------------------------------------------------------------------
    def get_variables(self):
        """Gets the variables."""
        return self.contents['variables']

    # -------------------------------------------------------------------------
    def get_files(self):
        """Gets the file list."""
        return self.contents['files']

    # -------------------------------------------------------------------------
    def get_full_path(self):
        """
        :return: the full path of the configuration file
        """
        return os.path.join(self.workdir, self.filename)


# -----------------------------------------------------------------------------
# VariableCollector
# -----------------------------------------------------------------------------
class VariableCollector:
    """Works out the values of the variables, including references and
    embedded python code
    """

    # -------------------------------------------------------------------------
    @classmethod
    def assert_section(cls, variables_section):
        """
        Makes sure the given variable section is:
         1. A not empty dictionary
         2. All the keys are alphanumeric strings in upper case
        """
        assert isinstance(variables_section, dict)

        if not variables_section:
            error('Missing variables section in configuration file')

        variable_name_pattern = re.compile(r'[0-9A-Z_]+')
        invalid_names = []

        for name in variables_section:
            if not variable_name_pattern.fullmatch(name):
                invalid_names.append(name)

        if invalid_names:
            error('Invalid variable name found: {0}'.format(invalid_names))

    # -------------------------------------------------------------------------
    def __init__(self, variables_section):
        self.variables = dict()

        self.assert_section(variables_section)
        self.collect_variables(variables_section)

    # -------------------------------------------------------------------------
    def get_variables(self):
        """Returns collected variables."""
        return self.variables

    # -------------------------------------------------------------------------
    def collect_variables(self, variables_section):
        """
        Collects the variables from the definitions in the given section
        while resolving any back reference in their values

        :param variables_section: a dictionary with the variable definitions
        """
        reference_pattern = re.compile(r'\$\{([0-9a-zA-Z_]+)\}')

        # First collect all simple values
        for name in variables_section:
            value = variables_section[name]

            if not reference_pattern.match(value):
                self.variables[name] = value

        # Now collect all back references
        for name in variables_section:
            try:
                value = variables_section[name]

                references = reference_pattern.findall(value)
                if references:
                    for reference in references:
                        value = value.replace('${' + reference + '}',
                                              self.variables[reference])
                    self.variables[name] = value
            except KeyError as ex:
                error('Undefined variable referenced by {0}: {1}'.format(
                    name, ex))


# -----------------------------------------------------------------------------
# Interpreter
# -----------------------------------------------------------------------------
# class Interpreter:
#     """
#     Executes embedded python code
#     """
#
#     def __init__(self):
#         assert sys.executable
#
#     def execute(self, code):
#         """
#         Executes the given python code using the same binary that it is
#         executing us.
#
#         :param code: the code to execute
#         :return: the output of the execution
#         """
#         assert code
#
#         subprocess.run()


# -----------------------------------------------------------------------------
# Replacer
# -----------------------------------------------------------------------------
class Replacer:
    """Performs variable substitutions on the given text"""

    # -------------------------------------------------------------------------
    @classmethod
    def uniquefy(cls, items):
        """Returns a list from a given sequence without duplicates while
        preserving the original order

        :param items: the sequence to remove duplicates from
        :return: a copy of the input list but without duplicates
        """

        seen = set()
        return [xx for xx in items if xx not in seen and not seen.add(xx)]

    # -------------------------------------------------------------------------
    def __init__(self, variables):
        assert isinstance(variables, dict)

        self.variable_marker_pattern = re.compile(r'@([0-9A-Z_]+)@')
        self.variables = variables

    # -------------------------------------------------------------------------
    def find_variable_markers(self, contents):
        """
        Looks for variable placeholders in the given contents
        :param contents: the test where to look the variables to substitute
        :return: an iterator with the list of matching objects
        """

        return self.uniquefy(
            matcher.group(1)
            for matcher in self.variable_marker_pattern.finditer(contents))

    # -------------------------------------------------------------------------
    def do_variable_substitution(self, contents):
        """Performs the substitution of any variable marker found in contents
         with its corresponding value provided in the configuration

        :param contents: the text where to carry on the variable substitution
        :return: a copy of contents where every variable marker has been
        replaced by its corresponding value
        """

        missing = []
        for name in self.find_variable_markers(contents):
            marker = '@' + name + '@'
            value = None

            if name in self.variables:
                value = self.variables[name]
            elif name in os.environ:
                value = os.environ[name]

            if value is not None:
                contents = contents.replace(marker, value)
            else:
                missing.append(name)

        if missing:
            error('Missing variables {0}'.format(missing))

        return contents


# -----------------------------------------------------------------------------
# FileManager
# -----------------------------------------------------------------------------
class FileManager:
    """Takes care of writing the files with the new contents"""

    # -------------------------------------------------------------------------
    def __init__(self, files):
        """
        Creates an instance and maps each file to their source file

        :param files: the list of files to produce as a result of performing
        the variable substitution
        """
        if not files:
            error('Missing files to configure')
        self.targets = files
        self.mappings = dict((ff, ff + PYCONF_EXTENSION) for ff in files)

    # -------------------------------------------------------------------------
    def replace(self, replacer):
        """Calls replace_file on each file listed in the configuration"""
        try:
            for target in self.targets:
                FileManager.replace_file(
                    replacer,
                    self.mappings[target],
                    target)
        except Exception as ex:  # pylint: disable=W0703
            error(str(ex))

    # -------------------------------------------------------------------------
    @classmethod
    def replace_file(cls, replacer, input_filename, output_filename):
        """Performs the variable substitution via the replacer on the contents
        of the file pointed by input_filename and writes the result to a
        new file named after output_filename

        :param replacer: the Replacer instance that performs the variable
         substitution
        :param input_filename: the name of the file to read the contents from
        :param output_filename: the name of the file to write the replaced
        contents to
        """
        with open(input_filename, 'r') as input_file:
            with open(output_filename, 'w') as output_file:
                print("Creating {0}".format(output_filename))
                for line in input_file:
                    output_file.write(replacer.do_variable_substitution(line))


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
class Configuration:  # pylint: disable=too-few-public-methods
    """In-memory representation of the configuration
     and the logic to execute it.
     """

    # -------------------------------------------------------------------------
    def __init__(self):
        # Load the configuration file
        self.loader = Loader()

        if not self.loader.get_variables():
            error('Missing variables section in configuration file {0}'.format(
                self.loader.get_full_path()))

    # -------------------------------------------------------------------------
    def apply(self):
        """Applies the configuration by performing the variable substitution
         on the given files"""

        # Collect the variables and their values
        rendered_variables = VariableCollector(
            self.loader.get_variables()).get_variables()

        if self.loader.get_files():
            FileManager(self.loader.get_files()).replace(
                Replacer(rendered_variables))
        else:
            print("No files specified: no replacements to perform")


# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------
def main():
    """The console script entry-point. Called when pyconf is executed
    or form __main__.py, which is used by the installed console script.
    """
    Configuration().apply()
    print("Done.")


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    main()
