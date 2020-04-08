# __main__.py

import argparse
import os

import canvas_client
from canvas_client.client import Client
from canvas_client import util

#TODO add progress bar

config = util.load_json('config.json')
labs = list(config['labs'].keys())

parser = argparse.ArgumentParser(description='Canvas grader')
parser.add_argument('lab', choices=labs,
                    help='The lab which you want to test')
parser.add_argument('-d', '--download_submissions', action='store_true', 
                    help='Download the subissions')
parser.add_argument('-u', '--upload', action='store_true', 
                    help='Upload grades and comments to canvas from excel.')


args = parser.parse_args()

def main():

    if args.download_submissions:
        ac_grader = Client(args.lab)
        ac_grader.download_submissions()
        return

    if args.upload:
        ac_grader = Client(args.lab)
        #upload grades to canvas
        ac_grader.upload_grades_from_excel()
        return


if __name__ == "__main__":
    main()