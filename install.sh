#!/bin/bash
echo "Installing python package requirements..."
pip install -r requirements.txt
echo

echo "Initializing submodules..."
git submodule update --init
echo

echo "Install G2P backends..."
sudo apt-get install festival espeak-ng mbrola
echo

echo "Installing phonemizer..."
cd phonemizer && python setup.py build && python setup.py install && cd ..
cd phonemizer && python setup.py test && cd ..  # optionally run the tests
echo

echo "Installing text frontend..."
python setup.py install
