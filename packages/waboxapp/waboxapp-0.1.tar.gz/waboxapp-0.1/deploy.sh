#!/usr/bin/env bash
python setup.py sdist upload -r pypitest
python setup.py sdist upload -r pypi
# sources: https://stackoverflow.com/questions/45207128/failed-to-upload-packages-to-pypi-410-gone http://peterdowns.com/posts/first-time-with-pypi.html
