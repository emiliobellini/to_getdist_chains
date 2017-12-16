import os
import re
import sys
import numpy as np
import fnmatch
import argparse


def argument_parser():
    """ Parse the command-line arguments

    Returns:
        a class with the given arguments

    """

    parser = argparse.ArgumentParser(
    'Take as input chains generated with Cosmosis, and reurn them with\n'
    'the column order changed so they are compatible with GetDist.\n'
    )

    #Arguments
    parser.add_argument('--input-folder', '-i', type=str, default = None,
    help='Input folder')
    parser.add_argument('--output-folder', '-o', type=str, default = None,
    help='Output folder')

    args = parser.parse_args()

    return args


def folder_exists_or(fname, mod = 'error'):
    """
    Check if a folder exists.
    If it exists return the absolute path,
    otherwise raise an error or create it
    (depending on the mode)
    """

    #Absolute path of the folder
    abs_path = os.path.abspath(fname) + '/'

    #Check if file exists
    if not os.path.isdir(abs_path):
        if mod == 'create':
            os.makedirs(abs_path)
        else:
            raise IOError(abs_path + 'does not exist!')

    return abs_path


def read_chain(fname):

    with open(fname, 'r') as f:
        headers = f.readline().strip()
        headers = re.sub('#', '', headers)
        headers = re.sub('\s+', ' ', headers)
        headers = headers.split()
        values = np.genfromtxt(f)

    return headers, values


def write_chain(headers, values, fname):

    #Join headers in a single string
    headers = '    '.join(headers)

    np.savetxt(fname, values, header=headers, delimiter='    ')

    return


# -----------------MAIN-CALL---------------------------------------------
if __name__ == '__main__':

    #Parse command-line arguments
    args = argument_parser()

    folders = {}
    if args.input_folder is None:
        folders['input'] = 'input/'
    else:
        folders['input'] = args.input_folder
    if args.output_folder is None:
        folders['output'] = 'output/'
    else:
        folders['output'] = args.output_folder

    folders['input'] = folder_exists_or(folders['input'], mod = 'error')
    folders['output'] = folder_exists_or(folders['output'], mod = 'create')

    chains = fnmatch.filter(os.listdir(folders['input']), '*.txt')


    for chain in chains:

        #Read chain
        headers, values = read_chain(folders['input'] + chain)

        #Add weight to the last column
        headers.append('weight')
        new_values = [[1] for x in range(len(values))]
        values = np.append(values, new_values, axis=1)

        #Change column order
        last_col = len(headers)-1
        permutation = np.append([last_col,last_col-1],range(last_col-1))
        values = values[:,permutation]
        headers = [headers[i] for i in permutation]

        #Write chain
        write_chain(headers, values, folders['output'] + chain)

    sys.exit()
