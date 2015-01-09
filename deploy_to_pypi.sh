#!/bin/bash
#
# Deploy to PyPI for both source and wheel
#
rm -Rf build/ dist/ mogwai.egg-info/ || true
python setup.py sdist upload || true
export WHEEL_TOOL=`which wheel` && python setup.py bdist_wheel --universal upload || true
rm -Rf build/ dist/ mogwai.egg-info/ || true
