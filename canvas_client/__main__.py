# __main__.py

# How to run module as script, from the root dir:
#   > python -m canvas_client -h

import argparse
import os
from configparser import ConfigParser
from canvas_client.client import Client
from canvas_client import util

config_path = os.path.join(".", "config.json")
if not os.path.isfile(config_path):
    init = util.query_yes_no("No config file found in the current folder.\nWould you like to initialize it now?")
    if not init:
        print("Please go to a folder with a valid config file or initialize one here")
        exit(0)
    else:
        with open(config_path, 'w') as f:
            f.write('{\n' +
                    '  "url" : "<canvas_url>",\n'+
                    '  "access_token" : "<acces_token>",\n'+
                    '  "course_id" : <course_id>,\n'+
                    '  "labs" : {\n'+
                    '    "<1st_assignment_name (choose a name)>: {"assignment_id": <id>},\n'+
                    '    "<2nd_assignment_name>: {"assignment_id": <id>}\n'+
                    '  }\n'+
                    '}\n')
        print("Config file created. Please fill it properly.")
        exit(0)

config = util.load_json('./config.json')
labs = list(config['labs'].keys())

parser = argparse.ArgumentParser(description='Canvas grader')
parser.add_argument('lab', choices=labs,
                    help = 'The lab which you want to grade')
parser.add_argument('-d', '--download', action='store_true',
                    help = 'Download the not graded subissions.')
parser.add_argument('-u', '--upload', action='store_true',
                    help = 'Upload grades and comments to canvas from excel.')
parser.add_argument('-a', '--all', action='store_true',
                    help = 'Download all subissions.')
parser.add_argument('-m', '--moss', type = str,
                    help = 'Copy files with the given regex from the latest subbmission into a folder.')

args = parser.parse_args()

def main():
    if not args.all and not args.download and not args.upload and (args.moss is None):
        print("No optional argument selected. Please select one.")
        return
    if sum([ args.all, args.download, args.upload, (args.moss is not None) ]) != 1:
        print("Please select only one optional argument.")
        return
    ac_grader = Client(args.lab)
    if args.all:
        ac_grader.download_submissions(workflow_state = [ 'submitted', 'graded' ])
    if args.download:
        ac_grader.download_submissions(workflow_state = [ 'submitted' ])
    if args.upload:
        ac_grader.upload_grades_from_excel()
    if args.moss is not None:
        moss_dir = f"{ac_grader.assignments_dir}_MOSS"
        util.copy_submissions(ac_grader.assignments_dir, moss_dir, args.moss)

if __name__ == "__main__":
    main()
