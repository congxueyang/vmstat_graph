#! /usr/bin/env python

import sys
import time
import datetime
import argparse

import matplotlib.pyplot as plt
import matplotlib.markers
from matplotlib import dates

import numpy as np

HUMAN_HEADERS = {
    'r': 'Runnable processes',
    'b': 'Blocked processes',
    'swpd': 'Swapped memory',
    'free': 'Free memory',
    'buff': 'I/O Buffers',
    'cache': 'FS cache',
    'si': 'Swapins',
    'so': 'Swapouts',
    'bi': 'I/O buffers in (reads)',
    'bo': 'I/O buffers out (writes)',
    'in': 'Interrupts',
    'cs': 'Context switches',
    'us': 'Userspace CPU %',
    'sy': 'Kernel CPU %',
    'id': 'Idle CPU %',
    'wa': 'I/O wait CPU %',
    'st': 'Stolen VM CPU %',
}

def plotit(dataset, timeaxis, image_file=None, display=False, normalized=False, intervalized=False):
    # Prepare marker list
    mks = set(matplotlib.markers.MarkerStyle().markers.keys())
    # Remove unwanted ones
    #~ mks -= set((None, 'None', '', ' ', '|', '_', '.', ',', '+', '-', 'd', 'x', '*'))
    #~ mks = ['<', '>', '^', 'v', 'o', 'D', 's', 'p', 'h', ]

    fig = plt.figure()

    plt.title('Graph of vmstat output')
    plt.rc('lines', linewidth=1, linestyle='-')

    ax = fig.add_subplot(1, 1, 1)

    if intervalized:
        ax.xaxis.set_major_locator(dates.MinuteLocator(interval=10))
        ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))

        # position of the labels
        xtk_loc = [datetime.datetime(2016, 1, 1, 0, 0) + 
                   datetime.timedelta(hours=i) for i in np.arange(0,12.1,1./6)]
        ax.set_xticks(xtk_loc)
        ax.tick_params(axis='both', direction='out', top='off', right='off')

        fig.autofmt_xdate(rotation=90, ha='center')

    ax.set_ylabel('Data', labelpad=10, fontsize=14)
    ax.set_xlabel('Time', labelpad=20, fontsize=14)

    # Experiment with logarithmic scale
    plotter = plt.semilogy
    #~ plotter = plt.plot

    for header, data in dataset.items():
        if header in HUMAN_HEADERS:
            plotter(timeaxis, data, marker=mks.pop(), label=HUMAN_HEADERS[header])

    # Give some horizontal room
    #xmin, xmax = plt.xlim()
    #plt.xlim(0, xmax * 1.1)

    # Put legend in top left corner
    plt.legend(loc=1)

    # Save an image of the plotted data
    if image_file:
        plt.savefig(image_file)

    # Display resulting figure
    if display:
        plt.show()

def normalize(dataset, total):
    return [d * 100 / total for d in dataset]

def read_input(fin):
    headers = None
    data = []
    for line in fin:
        elems = line.split()
        if elems[0] == 'procs':
            continue
        elems = tuple(elems)
        if elems[0] == 'r':
            if headers is None:
                headers = elems
        else:
            data.append(elems)
    return headers, data

def doit(datafile, cols, ram, interval, plotfile, display):
    if datafile is None or datafile == '-':
        headers, data = read_input(sys.stdin)
    else:
        with open(datafile) as fin:
            headers, data = read_input(fin)

    if not cols:
        cols = headers

    timeaxis = range(len(data))
    if interval:
        interval = int(interval)
        timeaxis = [datetime.datetime(2016, 1, 1, 0, 0) + datetime.timedelta(seconds=x * interval) for x in timeaxis]

    # Rearrange data columns into rows
    dataset = {header: [int(dataline[idx]) for dataline in data] for idx, header in enumerate(headers)}

    if ram:
        # Normalize to total RAM size
        for h in ('free', 'buff', 'cache', 'swpd'):
            dataset[h] = normalize(dataset[h], ram)
            HUMAN_HEADERS[h] += ' %'
    else:
        for h in ('free', 'buff', 'cache', 'swpd'):
            HUMAN_HEADERS[h] += ' (MB)'

    dataset_plot = {h: dataset[h] for h in cols}
    plotit(dataset_plot, timeaxis, image_file=plotfile, display=display, normalized=bool(ram), intervalized=bool(interval))

#~ procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
#~ r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
#~ 2  0      0 5075832  29076 6839980    0    0    33   873 2669 5057  5  8 83  4  0

def parse_args():
    parser = argparse.ArgumentParser(description='Graph vmstat output')

    parser.add_argument(dest='datafile', metavar='FILENAME', default='-',
                        help='file with vmstat output, none or "-" means read from stdandard input')

    parser.add_argument('-d', '--display', dest='display', action='store_true',
                        help='display plot data')
    parser.add_argument('-p', '--plot', dest='plot', metavar='FILENAME',
                        help='save plot data to .svg image file')
    parser.add_argument('-t', '--time', dest='time', metavar='INTEGER',
                        help='time interval')

    parser.add_argument('-r', '--ram', dest='ram', metavar='SIZE',
                        help='total size of RAM to normalize, if absent, do not normalize, use size in MB. You can use GB, MB, KB, suffixes.')

    parser.add_argument('-c', '--columns', dest='cols', metavar='STRING',
                        help='comma-separated list of columns, defaults to all columns')

    return parser

def main():
    parser = parse_args()
    args = parser.parse_args()

    cols = None
    if args.cols:
        cols = args.cols.split(',')

    ram = None
    if args.ram:
        try:
            ram = int(args.ram)
        except ValueError:
            if args.ram[-1] in ('B', 'o'):
                args.ram = args.ram[:-1]
            try:
                if args.ram[-1] in ('K', 'k'):
                    ram = int(args.ram[:-1]) * 1024
                elif args.ram[-1] in ('M', 'm'):
                    ram = int(args.ram[:-1]) * 1024 * 1024
                elif args.ram[-1] in ('G', 'g'):
                    ram = int(args.ram[:-1]) * 1024 * 1024 * 1024
                else:
                    ram = int(args.ram[:-1])
            except ValueError:
                print 'Cannot understand RAM size'
                print parser.print_help()
                sys.exit(1)
    if ram:
        ram /= 1024
        print 'Total RAM (MB):', ram

    doit(args.datafile, cols, ram, args.time, args.plot, args.display)

if __name__ == '__main__':
    main()
