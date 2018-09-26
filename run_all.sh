#!/bin/bash

#
# 1. install python libraries
#

pip2 install --user pandas ufal.morphodita
git clone https://github.com/UFAL-DSG/tgen
cd tgen
pip install --user -e .
cd ..

#
# 2. download the datasets
#

mkdir data-tmp data

cd data-tmp

# SF Rest
wget 'https://www.repository.cam.ac.uk/bitstream/handle/1810/251304/data.zip?sequence=1&isAllowed=y' -O data.zip
unzip data.zip
tail +6 dat/sfxrestaurant/train+valid+test.json > sfrest.json
rm -r dat data.zip
../tgen/sfx-restaurant/input/convert.py -m -n -i sfrest.json sfrest

cp sfrest-das.txt ../data/sfrest-mrs.txt
cat sfrest-text.txt | sed 's/\(^\|\. \)\(.\)/\1\u\2/g;s/ \(['"'"'?!.,;]\)/\1/g;s/\([Cc]\)hild -s/\1hildren/g;s/ -s/s/g;s/ -ly/ly/g' > ../data/sfrest-refs.txt
rm *

# BAGEL
wget "http://farm2.user.srcf.net/research/bagel/ACL10-inform-training.txt"
../convert_bagel.py ACL10-inform-training.txt ../data/bagel-mrs.txt ../data/bagel-refs.txt
rm *

# E2E
wget "https://github.com/tuetschek/e2e-dataset/archive/master.zip"
../convert_e2e.py e2e-dataset-master/{trainset,devset,testset_w_refs}.csv ../data/e2e-mrs.txt ../data/e2e-refs.txt
rm *

rmdir data-tmp

#
# 3. install the tools (note the patching!)
#

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
cd COLLINS-PARSER/code
make
cd ../..
rm PARSER.tar.gz
cd ..

#
# 4. obtain the stats
#

# tag everything
./tag_datasets.py -f ngram data/bagel-refs.txt data/bagel-refs.tag.ngram.txt
./tag_datasets.py -f ngram data/sfrest-refs.txt data/sfrest-refs.tag.ngram.txt
./tag_datasets.py -f ngram data/e2e-refs.txt data/e2e-refs.tag.ngram.txt

./tag_datasets.py -f lca data/bagel-refs.txt data/bagel-refs.tag.lca.txt
./tag_datasets.py -f lca data/sfrest-refs.txt data/sfrest-refs.tag.lca.txt
./tag_datasets.py -f lca data/e2e-refs.txt data/e2e-refs.tag.lca.txt

./tag_datasets.py -f collins data/bagel-refs.txt data/bagel-refs.tag.collins.txt
./tag_datasets.py -f collins data/sfrest-refs.txt data/sfrest-refs.tag.collins.txt
./tag_datasets.py -f collins data/e2e-refs.txt data/e2e-refs.tag.collins.txt

# run basic stats (+delexicalize)
./nlg_dataset_stats.py | tee stats-basic.txt

# run LCA
cd lca
python2 folder-lc.py ../data/*.tag.lca.txt > ../stats-lca.csv
cd ..

# run parser (NB: this takes hours!)
cd dlevel/COLLINS-PARSER
for file in ../../data/bagel-refs.tag.collins-*; do
    gunzip -c models/model2/events.gz | code/parser $file models/model2/grammar 10000 1 1 1 1 >> ../../data/bagel-refs.parse.txt
done
for file in ../../data/sfrest_inform-refs.tag.collins-*; do
    gunzip -c models/model2/events.gz | code/parser $file models/model2/grammar 10000 1 1 1 1 >> ../../data/sfrest_inform-refs.parse.txt
done
for file in ../../data/sfrest-refs.tag.collins-*; do
    gunzip -c models/model2/events.gz | code/parser $file models/model2/grammar 10000 1 1 1 1 >> ../../data/sfrest-refs.parse.txt
done
for file in ../../data/e2e-refs.tag.collins-*; do
    gunzip -c models/model2/events.gz | code/parser $file models/model2/grammar 10000 1 1 1 1 >> ../../data/e2e-refs.parse.txt
done
cd ..

# run d-level analysis
python2 d-level-directory.py ../data/*.parse.txt > ../stats-dlevel.csv
