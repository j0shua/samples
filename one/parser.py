#!/usr/bin/python

import argparse
import re
import os

DEBUG = False
OUTPUT_FILENAME = 'results.txt'


def parsefile(infile):
    if DEBUG:
        print 'opening file "%s"' % infile
    with open(infile, 'r') as f:
        return f.read()


def processline(line):
    ''' process a single line
    - creates 3 lists
      a) positions: to hold what is in each position of the input (int|str)
      b) alphas to hold the subset of strings from input
      c) numbers to hold the subset of numbers from input
    - record what is in each position in the input list
    - sort the sublists
    - use the position list to recompose a single list from the 2 sublists
      note: could save memory if we just output instead of creating a mixed list
    - return new ordered recombined list
    '''
    items = line.split()
    if len(items) == 0:
        return items

    # create a list to hold bools of what was in each index/position
    # and two more, to hold the subsets of numbers and strings
    # its faster to create list to size instead of appending n growing
    positions = [False] * len(items)
    alphas = []
    numbers = []
    for index, item in enumerate(items):
        # clean input, stripping junk chars
        cleaned = clean(item)

        isalpha = cleaned.isalpha()
        # record what is in the position for later
        positions[index] = isalpha

        # append to appropriate list
        if isalpha:
            alphas.append(cleaned)
        else:
            # cast to int so sorting works
            numbers.append(int(cleaned))

        if DEBUG:
            if index == 0:
                print '{0:100} {1:100} {2}'.format('input', 'cleaned', 'isalpha')
            print '{0:100} {1:100} {2}'.format(item, cleaned, isalpha)

    # now we just need to sort each list separately
    # then iterate thru the positions
    # and pull from the next index in the appropriate list
    alphas.sort()
    numbers.sort()
    mixed = []
    nextAlpha = nextNumber = 0

    # iterate thru position list and recompose from each sublist
    for index, isalpha in enumerate(positions):
        if isalpha:
            mixed.append(alphas[nextAlpha])
            nextAlpha = nextAlpha + 1
        else:
            # cast back to str to make output easy
            mixed.append(str(numbers[nextNumber]))
            nextNumber = nextNumber + 1

    if DEBUG:
        print 'alphas are:', alphas
        print 'numbers are:', numbers
        print 'combined:', mixed

    return mixed


def output(data, filename):
    '''
    outputs data into file 'filename'
    '''
    with open(filename, 'w') as f:
        f.write(data)


def clean(item):
    '''
    method to clean a string by stripping all non alpha numeric chars or dashes
    '''
    return re.sub(r'[^a-zA-Z0-9-]', r'', item)


def checkargs(args):
    ''' check args are valid '''
    if DEBUG:
        print 'infile is "%s"' % args.infile
        print 'outputdir is "%s"' % args.outputdir

    if not os.path.isfile(args.infile):
        print 'Error:input file "%s" does not exist. Aborting' % args.infile
        exit(1)

    if not os.path.isdir(args.outputdir):
        print 'Error:output dir "%s" does not exist. Aborting' % args.outputdir
        exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help='the file to read from')
    parser.add_argument(
        'outputdir',
        help='the directory for results file (OUTPUTDIR/results.txt)')

    args = parser.parse_args()
    checkargs(args)

    line = parsefile(args.infile)

    if len(line) is 0:
        print 'input file is empty, nothing to do.'
        exit(0)
        
    data = processline(line)
    output(' '.join(data), os.path.join(args.outputdir, OUTPUT_FILENAME))

    exit(0)
