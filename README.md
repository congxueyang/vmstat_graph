# vmstat_graph

Cet outil permet de visualiser les informations renvoyées par vmstat sous forme graphique.

Veuillez lancer l'outil avec l'option --help pour connaître son fonctionnement:

```
$ ./vmstat_graph.py --help
usage: vmstat_graph.py [-h] [-l] [-d] [-s FILENAME] [-t INTEGER] [-r SIZE]
                       [-c STRING]
                       FILENAME

Plot a graph from some vmstat output

procs -----------memory---------- --swap- --io-- -system-- ------cpu-----
r  b  swpd    free  buff   cache  si   so bi  bo   in   cs us sy id wa st
2  0     0 5075832 29076 6839980   0    0 33 873 2669 5057  5  8 83  4  0

You can :
  - select the interesting columns
  - ask for a logarthmic scale for the data axis
  - tell the total RAM in order to get %-age instead of absolute numbers
  - give the vmstat time interval to get Y axis in time units instead of intervals.
  - get the graph in a GUI window and/or a saved svg file.

positional arguments:
  FILENAME              file with vmstat output, none or "-" means read from
                        stdandard input

optional arguments:
  -h, --help            show this help message and exit
  -l, --logarithmic     use a logarthmic scale for data axis
  -d, --display         display plot data
  -s FILENAME, --svg FILENAME
                        save plot data to .svg image file
  -t INTEGER, --time INTEGER
                        vmstat time interval (in seconds)
  -r SIZE, --ram SIZE   total size of RAM to normalize, if absent, do not
                        normalize, use size in MB. You can use GB, MB, KB,
                        suffixes.
  -c STRING, --columns STRING
                        comma-separated list of columns, defaults to show all
                        columns
```