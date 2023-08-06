#!/bin/bash

startdir="$(pwd)"
mkdir xrootdbuild
cd xrootdbuild
cmake ../.
make
make install
cd bindings/python
python setup.py install
cd $startdir
rm -r xrootdbuild
