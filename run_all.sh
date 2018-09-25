#!/bin/bash

# install python libraries

pip2 install --user pandas ufal.morphodita
git clone https://github.com/UFAL-DSG/tgen
cd tgen
pip install --user -e .

# get datasets

mkdir data-tmp data

cd data-tmp

# SFX
wget 'https://www.repository.cam.ac.uk/bitstream/handle/1810/251304/data.zip?sequence=1&isAllowed=y' -O data.zip
unzip data.zip
tail +6 dat/sfxrestaurant/train+valid+test.json > sfxrest.json
rm -r dat data.zip
../tgen/sfx-restaurant/input/convert.py 

cp sfrest-das.txt ../data/sfrest-mrs.txt
cat sfrest-text.txt | sed 's/\(^\|\. \)\(.\)/\1\u\2/g;s/ \(['"'"'?!.,;]\)/\1/g;s/\([Cc]\)hild -s/\1hildren/g;s/ -s/s/g;s/ -ly/ly/g' > ../data/sfrest-refs.txt
rm *

# BAGEL
# TODO


# E2E 
# TODO


rmdir data-tmp

# get tools

# lca
mkdir lca
cd lca
wget "http://www.personal.psu.edu/xxl13/downloads/lca.tgz"
tar xf lca.tgz
mv lca/bnc_all_filtered.txt lca/folder-lc.py .
patch folder-lc.py ../folder-lc.patch
cd ..

# d-level analyzer & collins parser
mkdir dlevel
cd dlevel
wget "http://www.personal.psu.edu/xxl13/downloads/d-level-analyzer-2013-03-22.tgz"
tar xf d-level-analyzer-2013-03-22.tgz
mv d-level-analyzer-2013-03-22/d-level-directory.py NOMLEX-2001.reg .
rm -r d-level-analyzer-2013-03-22 d-level-analyzer-2013-03-22.tgz
patch d-level-directory.py ../d-level-directory.patch
wget "http://people.csail.mit.edu/mcollins/PARSER.tar.gz"
tar xf PARSER.tar.gz
rm PARSER.tar.gz
cd ..


# run the stats

# tag stuff

# run basic stats

# run LCA

# run parser

# run d-level analysis
