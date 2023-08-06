# Example Package

This is a simple example package, for more detail please follow this guide: https://packaging.python.org/tutorials/packaging-projects/

## Installing virtualenv
```
python3 -m pip install --user virtualenv
python3 -m virtualenv env
source env/bin/activate
```
## Upload package to pypi
```
pip install twine
python3 setup.py sdist bdist_wheel
twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
```
