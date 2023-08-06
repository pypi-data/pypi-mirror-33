#!/usr/bin/env python3
"""
Makes UCL PHAS results better
"""

__author__ = "Hayk Khachatryan"
__version__ = "0.1.0"
__license__ = "MIT"

import sys
import itertools
import pathlib as pathlib

import pandas as pd
import matplotlib.pyplot as plt
import inquirer
#########################
#                       #
#                       #
#      functions        #
#                       #
#                       #
#########################



def plotter(path, show, goodFormat):
    '''makes some plots

    creates binned histograms of the results of each module
    (ie count of results in ranges [(0,40), (40, 50), (50,60), (60, 70), (70, 80), (80, 90), (90, 100)])

    Arguments:
        path {str} --  path to save plots to
        show {boolean} -- whether to show plots using python
        goodFormat {dict} -- module : [results for module]

    output:
        saves plots to files/shows plots depending on inputs
    '''

    for module in goodFormat.items():  # for each module
        bins = [0, 40, 50, 60, 70, 80, 90, 100]
        # cut the data into bins
        out = pd.cut(module[1], bins=bins, include_lowest=True)
        ax = out.value_counts().plot.bar(rot=0, color="b", figsize=(10, 6), alpha=0.5,
                                         title=module[0])  # plot counts of the cut data as a bar

        ax.set_xticklabels(['0 to 40', '40 to 50', '50 to 60',
                            '60 to 70', '70 to 80', '80 to 90', '90 to 100'])

        ax.set_ylabel("# of candidates")
        ax.set_xlabel(
            "grade bins \n total candidates: {}".format(len(module[1])))

        if path is not None and show is not False:

            # if export path directory doesn't exist: create it
            if not pathlib.Path.is_dir(path.as_posix()):
                pathlib.Path.mkdir(path.as_posix())

            plt.savefig(path / ''.join([module[0], '.png']))
            plt.show()

        elif path is not None:

            # if export path directory doesn't exist: create it
            if not pathlib.Path.is_dir(path):
                pathlib.Path.mkdir(path)

            plt.savefig(path / ''.join([module[0], '.png']))
            plt.close()

        elif show is not False:
            plt.show()



def askPlot():
    '''Asks the user whether it wants the plots shown or saved

    Returns:
        [list] containing "Show" and/or "Save" if respectively selected
    '''
    return inquirer.prompt([
        inquirer.Checkbox(
            'plotQ',
            message="Shall I show the plots or save them (select with your spacebar)",
            choices=[
                "Show",
                "Save"
            ]),
    ])


def askSave():
    '''Asks the user where they want the plots to be saved

    Returns:
        [str] -- output path
    '''
    return inquirer.prompt([
        inquirer.Text(
            'savePath', message="Where shall I save the plots (eg plots/)")
    ])['savePath']

def howPlotAsk(goodFormat):
    '''plots using inquirer prompts

    Arguments:
        goodFormat {dict} -- module : [results for module]
    '''
    plotAnswer = askPlot()
    if "Save" in plotAnswer['plotQ']:
        exportPlotsPath = pathlib.Path(askSave())
        if "Show" in plotAnswer['plotQ']:
            plotter(exportPlotsPath, True, goodFormat)
        else:
            plotter(exportPlotsPath, False, goodFormat)
    elif "Show" in plotAnswer['plotQ']:
        plotter(None, True, goodFormat)

#########################
#                       #
#         end           #
#      functions        #
#                       #
#                       #
#########################

#########################
#                       #
#                       #
#      good stuff       #
#                       #
#                       #
#########################
