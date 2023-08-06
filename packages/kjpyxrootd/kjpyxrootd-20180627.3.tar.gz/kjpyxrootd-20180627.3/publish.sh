rm -r dist
python setup.py sdist
twine upload dist/* -u xrootduser -p xrootdpass
rm -r dist *.egg-info
