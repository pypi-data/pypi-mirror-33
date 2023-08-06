#!/usr/bin/env python3
"""
Makes UCL PHAS results better
"""

__author__ = "Hayk Khachatryan"
__version__ = "0.1.0"
__license__ = "MIT"

import argparse
import csv
import sys
import itertools
import pathlib as pathlib
import inquirer

#########################
#                       #
#                       #
#      functions        #
#                       #
#                       #
#########################


def goodFormater(badFormat, outputPath, year, length):
    '''[summary]

    reformats the input results into a dictionary with module names as keys and their respective results as values

    outputs to csv if outputPath is specified

    Arguments:
        badFormat {dict} -- candNumber : [results for candidate]
        outputPath {str} -- the path to output to
        year {int} -- the year candidateNumber is in
        length {int} -- length of each row in badFormat divided by 2


    Returns:
        dictionary -- module : [results for module]
        saves to file if output path is specified

    '''

    devcom = 'PHAS' + badFormat['Cand'][0]

    goodFormat = {devcom: []}

    # ignore first row cause it's just 'Mark' & 'ModuleN'
    for row in list(badFormat.values())[1:]:
        goodFormat[devcom].append(int(row[0]))  # add first val to devcom

        for i in range(length-1):
            # if a key for that module doesn't exist, initialize with empt array
            goodFormat.setdefault(row[(2 * i) + 1], [])
            # add value of module to module
            goodFormat[row[(2*i)+1]].append(int(row[2*(i + 1)]))

    goodFormat.pop('0')

    goodFormat['Averages'] = everyonesAverage(year, badFormat, length)
    if outputPath is not None:  # if requested to reformat and save to file

        results = csv.writer(outputPath.open(mode='w'), delimiter=',')
        # write the keys (module names) as first row
        results.writerow(goodFormat.keys())
        # zip module results together, fill modules with less people using empty values
        # add row by row
        results.writerows(itertools.zip_longest(
            *goodFormat.values(), fillvalue=''))

    return goodFormat

def myGrades(year, candidateNumber, badFormat, length):
    '''returns final result of candidateNumber in year

    Arguments:
        year {int} -- the year candidateNumber is in
        candidateNumber {str} -- the candidateNumber of candidateNumber
        badFormat {dict} -- candNumber : [results for candidate]
        length {int} -- length of each row in badFormat divided by 2


    Returns:
        int -- a weighted average for a specific candidate number and year
    '''

    weights1 = [1, 1, 1, 1, 0.5, 0.5, 0.5, 0.5]
    weights2 = [1, 1, 1, 1, 1, 1, 0.5, 0.5]
    if year == 1:
        myFinalResult = sum([int(badFormat[candidateNumber][2*(i + 1)])
                             * weights1[i] for i in range(length-1)]) / 6
    elif year == 2 or year == 3:
        myFinalResult = sum([int(badFormat[candidateNumber][2*(i + 1)])
                             * weights2[i] for i in range(length-1)]) / 7
    elif year == 4:
        myFinalResult = sum([int(badFormat[candidateNumber][2*(i + 1)])
                             for i in range(length-1)]) / 8

    return myFinalResult

def myRank(grade, badFormat, year, length):
    '''rank of candidateNumber in year

    Arguments:
        grade {int} -- a weighted average for a specific candidate number and year
        badFormat {dict} -- candNumber : [results for candidate]
        year {int} -- year you are in
        length {int} -- length of each row in badFormat divided by 2



    Returns:
        int -- rank of candidateNumber in year
    '''
    return int(sorted(everyonesAverage(year, badFormat, length), reverse=True).index(grade) + 1)

def everyonesAverage(year, badFormat, length):
    ''' creates list of weighted average results for everyone in year

    Arguments:
        year {int}
        badFormat {dict} -- candNumber : [results for candidate]
        length {int} -- length of each row in badFormat divided by 2


    returns:
        list -- weighted average results of everyone in year
    '''
    return [myGrades(year, cand, badFormat, length) for cand in list(badFormat.keys())[1:]]

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
                "Reformat results by module and output to csv"
            ]),
    ])

def askYear():
    '''Asks the user for what year they're in

    Returns:
        [int] -- year
    '''
    return inquirer.prompt([
        inquirer.List(
            'year',
            message="What year are you in",
                    choices=[1, 2, 3, 4]
        )
    ])['year']

def askInput():
    '''Asks the user for input file path

    Returns:
        [str] -- input path
    '''
    return inquirer.prompt([
        inquirer.Text(
            'inputPath', message="What's the path of your input file (eg input.csv)")
    ])['inputPath']

def askFormat():
    '''Asks user for where to save formatted csv

    Returns:
        [str] -- output path
    '''
    return inquirer.prompt([
        inquirer.Text(
            'formatPath', message="Where shall I save the reformatted csv (eg output.csv)")
    ])['formatPath']

def askCandidateNumber():
    '''Asks the user for their candidate number

    Returns:
        [str] -- candidate number
    '''
    return inquirer.prompt([
        inquirer.Text('candidateNumber',
                      message="What is your candidate number")
    ])['candidateNumber']

def badFormater(input):
    return {row[0]: row[1:] for row in csv.reader(input.open(
            mode='r', newline=''), delimiter=',')}

def main(args):
    '''main entry point of app
    
    Arguments:
        args {namespace} -- arguments provided in cli
    '''
    
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
        badFormat = badFormater(inputPath)  # create a list from every row
        howManyCandidates = len(badFormat) - 1

        length = int(len(badFormat['Cand'])/2)
        finalReturn = []

        if "Get your rank in the year" in initialAnswers['whatToDo']:
            candidateNumber = askCandidateNumber()
            weightedAverage = myGrades(year, candidateNumber, badFormat, length)
            rank = myRank(weightedAverage, badFormat, year, length)

            if "Get your weighted average" in initialAnswers['whatToDo']:
                finalReturn.append('Your weighted average for the year is: {:.2f}%'.format(
                    weightedAverage))

            finalReturn.append('Your rank is {}th of {} ({:.2f} percentile)'.format(
                rank, howManyCandidates, (rank * 100) / howManyCandidates))
        elif "Get your weighted average" in initialAnswers['whatToDo']:
            candidateNumber = askCandidateNumber()
            weightedAverage = myGrades(year, candidateNumber, badFormat, length)
            finalReturn.append('Your weighted average for the year is: {:.2f}%'.format(
                weightedAverage))

        if "Reformat results by module and output to csv" in initialAnswers['whatToDo']:

            formatOutputPath = pathlib.Path(askFormat())

            goodFormat = goodFormater(badFormat, formatOutputPath, year, length)


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
        badFormat = badFormater(inputPath)  # create a list from every row
        howManyCandidates = len(badFormat) - 1

        length = int(len(badFormat['Cand'])/2)
        finalReturn = []

        if args.rank:
            if not args.candidate:
                candidateNumber = askCandidateNumber()
            else:
                candidateNumber = args.candidate

            weightedAverage = myGrades(year, candidateNumber, badFormat, length)
            rank = myRank(weightedAverage, badFormat, year, length)

            if args.my:
                finalReturn.append('Your weighted average for the year is: {:.2f}%'.format(
                    weightedAverage))

            finalReturn.append('Your rank is {}th of {} ({:.2f} percentile)'.format(
                rank, howManyCandidates, (rank * 100) / howManyCandidates))

        elif args.my:
            if not args.candidate:
                candidateNumber = askCandidateNumber()
            else:
                candidateNumber = args.candidate

            weightedAverage = myGrades(year, candidateNumber, badFormat, length)
            finalReturn.append('Your weighted average for the year is: {:.2f}%'.format(
                weightedAverage))

        if args.format is not None:
            formatOutputPath = pathlib.Path(args.format)
            goodFormat = goodFormater(badFormat, formatOutputPath, year, length)

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

