#!/usr/bin/env python
"""Command line quantorxs interface

"""
import os
import sys
import argparse


from quantorxs.main import run


parser = argparse.ArgumentParser(
    description='Quantify all the Carbon XANES spectra in a directory')
parser.add_argument(
    '--directory', default=os.getcwd(),
    help="Directory containing the XANES spectra in XXX format. "
    "The default is the current directory."
    "The extension of the files must be `.txt`")
parser.add_argument(
    '--results_directory',
    default="QUANTORXS results",
    help='Directory where to store the results relative to the '
    'spectra directory. If the directory exists, an incremental index is '
    'is appended. The default is "QUANTORXS results"')
parser.add_argument(
    '--fig_format', default="svg",
    help="The format of the figures. The default is svg.")
parser.add_argument(
    "--demo",
    help='Create a "QUANTORXS demo" folder in the directory'
    'specified by --directory containing example spectra '
    'and process them with QUANTORXS',
    action="store_true")


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    args = parser.parse_args()

    run(
        spectra_folder_path=args.directory,
        results_directory=args.results_directory,
        fig_format=args.fig_format,
        demo=args.demo)
