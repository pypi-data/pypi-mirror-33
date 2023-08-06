#!/usr/bin/env python3
"""
Makes UCL PHAS results better
"""

__author__ = "Hayk Khachatryan"
__version__ = "0.1.8"
__license__ = "MIT"

import argparse
import csv
import sys
import itertools
import pathlib as pathlib
import inquirer

import resultr_format
import resultr_plot

#########################
#                       #
#                       #
#      functions        #
#                       #
#                       #
#########################

def askInitial():
    '''Asks the user for what it wants the script to do

    Returns:
        [dictionary] -- answers to the questions
    '''
    return inquirer.prompt([
        inquirer.Text(
            'inputPath', message="What's the path of your input file (eg input.csv)"),
        inquirer.List(
            'year',
            message="What year are you in",
                    choices=[1, 2, 3, 4]
        ),
        inquirer.Checkbox(
            'whatToDo',
            message="What can I do for you (select with your spacebar)",
            choices=[
                "Get your weighted average",
                "Get your rank in the year",
                "Reformat results by module and output to csv",
                "Plot the results by module"

            ]),
    ])


def main(args):
    '''main entry point of app
    
    Arguments:
        args {namespace} -- arguments provided in cli
    '''
    
    print("\nNote it's very possible that this doesn't work correctly so take what it gives with a bucketload of salt\n")

    #########################
    #                       #
    #                       #
    #         prompt        #
    #                       #
    #                       #
    #########################

    if not len(sys.argv) > 1:
        initialAnswers = askInitial()

        inputPath = pathlib.Path(initialAnswers['inputPath'])
        year = int(initialAnswers['year'])
        # create a list from every row
        badFormat = resultr_format.badFormater(inputPath)  # create a list from every row
        howManyCandidates = len(badFormat) - 1

        length = int(len(badFormat['Cand'])/2)
        finalReturn = []

        if "Get your rank in the year" in initialAnswers['whatToDo']:
            candidateNumber = resultr_format.askCandidateNumber()
            weightedAverage = resultr_format.myGrades(year, candidateNumber, badFormat, length)
            rank = resultr_format.myRank(weightedAverage, badFormat, year, length)

            if "Get your weighted average" in initialAnswers['whatToDo']:
                finalReturn.append('Your weighted average for the year is: {:.2f}%'.format(
                    weightedAverage))

            finalReturn.append('Your rank is {}th of {} ({:.2f} percentile)'.format(
                rank, howManyCandidates, (rank * 100) / howManyCandidates))
        elif "Get your weighted average" in initialAnswers['whatToDo']:
            candidateNumber = resultr_format.askCandidateNumber()
            weightedAverage = resultr_format.myGrades(year, candidateNumber, badFormat, length)
            finalReturn.append('Your weighted average for the year is: {:.2f}%'.format(
                weightedAverage))

        if "Reformat results by module and output to csv" in initialAnswers['whatToDo']:

            formatOutputPath = pathlib.Path(resultr_format.askFormat())

            goodFormat = resultr_format.goodFormater(badFormat, formatOutputPath, year, length)

            if "Plot the results by module" in initialAnswers['whatToDo']:
                resultr_plot.howPlotAsk(goodFormat)

        elif "Plot the results by module" in initialAnswers['whatToDo']:
            goodFormat = resultr_format.goodFormater(badFormat, None, year, length)
            resultr_plot.howPlotAsk(goodFormat)

        [print('\n', x) for x in finalReturn]

    #########################
    #                       #
    #          end          #
    #         prompt        #
    #                       #
    #                       #
    #########################

    #########################
    #                       #
    #                       #
    #       run with        #
    #       cli args        #
    #                       #
    #########################

    if len(sys.argv) > 1:
        if not args.input:
            inputPath = pathlib.Path(askInput())
        else:
            inputPath = pathlib.Path(args.input)
        if not args.year:
            year = int(askYear())
        else:
            year = int(args.year)

        # create a list from every row
        badFormat = resultr_format.badFormater(inputPath)  # create a list from every row
        howManyCandidates = len(badFormat) - 1

        length = int(len(badFormat['Cand'])/2)
        finalReturn = []

        if args.rank:
            if not args.candidate:
                candidateNumber = resultr_format.askCandidateNumber()
            else:
                candidateNumber = args.candidate

            weightedAverage = resultr_format.myGrades(year, candidateNumber, badFormat, length)
            rank = resultr_format.myRank(weightedAverage, badFormat, year, length)

            if args.my:
                finalReturn.append('Your weighted average for the year is: {:.2f}%'.format(
                    weightedAverage))

            finalReturn.append('Your rank is {}th of {} ({:.2f} percentile)'.format(
                rank, howManyCandidates, (rank * 100) / howManyCandidates))

        elif args.my:
            if not args.candidate:
                candidateNumber = resultr_format.askCandidateNumber()
            else:
                candidateNumber = args.candidate

            weightedAverage = resultr_format.myGrades(year, candidateNumber, badFormat, length)
            finalReturn.append('Your weighted average for the year is: {:.2f}%'.format(
                weightedAverage))

        if args.format is not None:
            formatOutputPath = pathlib.Path(args.format)
            goodFormat = resultr_format.goodFormater(badFormat, formatOutputPath, year, length)

            if args.plot:
                resultr_plot.howPlotArgs(goodFormat)
        elif args.plot:
            goodFormat = resultr_format.goodFormater(badFormat, None, year, length)
            resultr_plot.howPlotArgs(goodFormat)

        [print('\n', x) for x in finalReturn]

    #########################
    #                       #
    #         end           #
    #       run with        #
    #       cli args        #
    #                       #
    #########################

    print('')



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


if __name__ == '__main__':

    #########################
    #                       #
    #                       #
    #       argparse        #
    #                       #
    #                       #
    #########################

    parser = argparse.ArgumentParser(
        description='Makes UCL PHAS results better')
    parser.add_argument('--input', '-i',
                        type=str, help="csv file to import")
    parser.add_argument('--format', '-f', type=str,
                        help="reformats results by module and exports it to file specified")
    parser.add_argument('--plot', '-p', action='store_true',
                        help="plot the module results")
    parser.add_argument('--exportplots', '-ep', type=str,
                        help="export all plots to /path/you/want/")
    parser.add_argument('--showplots', '-sp',
                        action='store_true', help="show all plots")
    parser.add_argument(
        '--my', '-m', action="store_true", help="returns your weighted average for the year")
    parser.add_argument('--year', '-y', help="specify your year")
    parser.add_argument('--rank', '-r', action='store_true',
                        help="returns your rank in the year")
    parser.add_argument('--candidate', '-c',
                        help="specify your candidate number")
    args = parser.parse_args()

    #########################
    #                       #
    #         end           #
    #       argparse        #
    #                       #
    #                       #
    #########################
    main(args)

