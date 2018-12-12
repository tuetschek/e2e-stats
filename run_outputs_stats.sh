#!/bin/bash

set -e  # exit on error

## assuming dataset stats script has already run and created
## the necessary stuff
#ls dlevel lca morphodita >/dev/null 


## Download system outputs
#mkdir sys_outputs
#cd sys_outputs
#wget https://github.com/tuetschek/e2e-eval/archive/v1.0.0.tar.gz
#tar xf v1.0.0.tar.gz
#mv e2e-eval-1.0.0/system_outputs/primary/*.tsv .
#rm -r e2e-eval-1.0.0 v1.0.0.tar.gz

## get test set refs (all + random)
#wget "https://github.com/tuetschek/e2e-dataset/archive/master.zip"
#unzip master.zip
#mv e2e-dataset-master/testset_w_refs.csv testset-all.csv
#rm -r e2e-dataset-master master.zip 
#python2 -c 'import pandas as pd; data = pd.read_csv("testset-all.csv", encoding="UTF-8"); data = data.rename(index=str, columns={"mr": "MR", "ref": "output"}); data.to_csv("testset-all.tsv", sep="\t", encoding="UTF-8", index=False)'
#rm testset-all.csv
#cat testset-all.tsv | perl -e 'my $cur_mr = ""; my @refs = (); while (1){ my $line = <>; chomp $line; my ($mr, $ref) = split /\t/, $line; if (!$mr or ($cur_mr and $cur_mr ne $mr)){ print $cur_mr, "\t", $refs[rand @refs], "\n"; @refs = (); } push @refs, $ref; $cur_mr = $mr; if (!$line){ last; } }' > testset-rand.tsv
#cd ..

## Run basic analysis (+ delexicalization + tagging)
#./nlg_output_stats.py -o primary_systems-stats.csv sys_outputs/*.tsv

## Run LCA
#cd lca
#python2 folder-lc.py ../sys_outputs/*.tag.lca.txt | tee ../primary_systems-lca.csv
#cd ..

## Parse & run d-level analysis
#cd dlevel/COLLINS-PARSER
#for file in ../../sys_outputs/*.tag.collins*; do newname=`echo $file | sed 's/tag.collins.*/parse.txt/'`; echo $file $newname; gunzip -c models/model2/events.gz | code/parser $file models/model2/grammar 10000 1 1 1 1 >> $newname; done
#cd ..
#python2 d-level-directory.py ../sys_outputs/*.parse.txt > ../primary_systems-dlevel.csv
#cd ..


# BLEU etc. similarity
cd sys_outputs
cat <<EOF | python
import pandas as pd
from tgen.data import DA
import codecs

data = pd.read_csv('testset-all.tsv', encoding='UTF-8', sep="\t")
mrs = [DA.parse_diligent_da(mr) for mr in data['MR']]
with codecs.open('testset-all.delex.txt', 'r', 'UTF-8') as fh: 
    refs = fh.readlines()
with codecs.open('testset-all_multiref.delex.txt', 'w', 'UTF-8') as fh:
    last_mr = None
    for mr, ref in zip(mrs, refs):
        if last_mr and last_mr != mr:
            fh.write("\n")
        fh.write(ref)
        last_mr = mr
EOF
cd ..
