#!/usr/bin/env python

# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Analyze an entire project using pytype."""

from __future__ import print_function

import logging
import sys

import importlab.environment
import importlab.fs
import importlab.graph
import importlab.output

from pytype import file_utils
from pytype import io
from pytype import utils
from pytype.tools import environment
from pytype.tools import tool_utils
from pytype.tools.analyze_project import config
from pytype.tools.analyze_project import parse_args
from pytype.tools.analyze_project import pytype_runner


class PytdFileSystem(importlab.fs.ExtensionRemappingFileSystem):
  """File system that remaps .py file extensions to pytd."""

  def __init__(self, underlying):
    super(PytdFileSystem, self).__init__(underlying, 'pytd')


def create_importlab_environment(conf, typeshed):
  """Create an importlab environment from the python version and path."""
  python_version = utils.split_version(conf.python_version)
  path = importlab.fs.Path()
  for p in conf.pythonpath:
    path.add_path(p, 'os')
  for p in typeshed.get_pytd_paths(python_version):
    path.add_fs(PytdFileSystem(importlab.fs.OSFileSystem(p)))
  for p in typeshed.get_typeshed_paths(python_version):
    path.add_path(p, 'pyi')
  return importlab.environment.Environment(path, python_version)


def main():
  parser = parse_args.make_parser()
  args = parser.parse_args(sys.argv[1:])

  if args.version:
    print(io.get_pytype_version())
    sys.exit(0)

  tool_utils.setup_logging_or_die(args.verbosity)

  if args.generate_config:
    config.generate_sample_config_or_die(args.generate_config)
    sys.exit(0)

  args.filenames = file_utils.expand_source_files(args.filenames)
  conf = parser.config_from_defaults()
  # File options overwrite defaults.
  file_config = config.read_config_file_or_die(args.config)
  parser.postprocess(file_config, from_strings=True)
  conf.populate_from(file_config)
  # Command line arguments overwrite file options.
  conf.populate_from(args)
  if not conf.pythonpath:
    conf.pythonpath = environment.compute_pythonpath(args.filenames)
  logging.info('\n  '.join(['Configuration:'] + str(conf).split('\n')))

  if not args.filenames:
    parser.parser.print_usage()
    sys.exit(0)

  # Importlab needs the python exe, so we check it as early as possible.
  environment.check_python_exe_or_die(conf.python_version)

  typeshed = environment.initialize_typeshed_or_die()
  env = create_importlab_environment(conf, typeshed)
  try:
    import_graph = importlab.graph.ImportGraph.create(env, args.filenames)
  except Exception as e:  # pylint: disable=broad-except
    logging.critical('Cannot parse input files:\n%s', str(e))
    sys.exit(1)

  if args.tree:
    print('Source tree:')
    importlab.output.print_tree(import_graph)
    sys.exit(0)

  if args.unresolved:
    print('Unresolved dependencies:')
    for imp in sorted(import_graph.get_all_unresolved()):
      print(' ', imp.name)
    sys.exit(0)

  logging.info('Source tree:\n%s',
               importlab.output.formatted_deps_list(import_graph))
  tool_utils.makedirs_or_die(conf.output, 'Could not create output directory')
  deps = pytype_runner.deps_from_import_graph(import_graph)
  runner = pytype_runner.PytypeRunner(args.filenames, deps, conf)
  runner.run()


if __name__ == '__main__':
  sys.exit(main())
