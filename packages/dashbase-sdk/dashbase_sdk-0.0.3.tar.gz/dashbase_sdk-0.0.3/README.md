# Dashbase python-sdk


## DEV

```
pip install dashbase_sdk

# test pypi
pip install --index-url https://test.pypi.org/simple/ dashbase_sdk
```


### Build package

```
pipenv install --dev
pipenv shell

python3 setup.py sdist bdist_wheel

```

### Upload

```
twine upload  dist/*

# test pypi
twine upload --repository-url https://test.pypi.org/legacy/ dist/*

```