
E2E Stats
=========
_Helper scripts used to compute statistics for the E2E NLG dataset + other datasets from the restaurant domain (BAGEL, SFREST)_


These scripts compute various statistics used for the following datasets:
* [E2E NLG](http://www.macs.hw.ac.uk/InteractionLab/E2E/)
* [SF Restaurants](https://www.repository.cam.ac.uk/handle/1810/251304)
* [BAGEL](http://farm2.user.srcf.net/research/bagel/)

To run the scripts, just clone this repository and run:
```
./run_all.sh
```

Be sure to **read the `run_all.sh` script beforehand and check that it doesn't do any harm** to your setup! 
It will install several required Python libraries into userspace by default, and it will download 
several tools needed to compute the stats.

The script requires Python 2.7.


Author: [Ondrej Dusek](https://tuetschek.github.io/). Based on scripts by [Jekaterina Novikova](http://jeknov.tumblr.com/).
(c) Heriot-Watt University, 2018.
