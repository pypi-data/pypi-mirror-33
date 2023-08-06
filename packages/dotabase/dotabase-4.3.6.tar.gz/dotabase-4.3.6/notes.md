
https://packaging.python.org/tutorials/distributing-packages/
https://stackoverflow.com/questions/26737222/pypi-description-markdown-doesnt-work?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
# update
```
rm -rf dist/
rm -rf dotabase.egg-info/
python setup.py sdist
twine upload --repository pypi dist/*
```
SnakeSoup!!