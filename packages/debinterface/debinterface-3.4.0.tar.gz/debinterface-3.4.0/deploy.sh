#!/bin/bash
set -e

echo "Remember to update version in :"
echo "    - debinterface/__init__.py"
echo "    - setup.py"
echo "    - git tag"

# Test
py.test --cov=debinterface test

# Cleanup
rm -rf debinterface.egg-info
rm -rf build
rm -rf dist

# check
check-manifest -u -v

# Build packages
python setup.py sdist
python setup.py bdist_wheel  # Not universal

# Deploy with gpg
twine upload dist/* -r pypitest --sign --skip-existing
twine upload dist/* --sign
