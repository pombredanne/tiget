#!/usr/bin/env python
import os, sys

if not __name__ == '__main__':
    raise RuntimeError('You are trying to import the wrapper script.')

project_root = os.path.normpath(os.path.dirname(sys.argv[0]))
sys.path.insert(0, project_root)
execfile(os.path.join(project_root, 'scripts', 'tiget'))
