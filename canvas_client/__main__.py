# __main__.py

import argparse
import os
from configparser import ConfigParser

from canvas_client.client import Client
from canvas_client import util

#TODO add progress bar


config_path = os.path.join(".", "config.json")
if not os.path.isfile(config_path):
    
    init = util.query_yes_no(   "No config file found in the current folder.\n" +\
                                "Would you like to initialize it now?")
    if not init:
        print("Please go to a folder with a valid config file\
             or initialize one here")
        exit(0)
    else:
        with open(config_path, 'w') as f:
            f.write(    '{\n' +
                            '\t"url" : "<canvas_url>",\n'+
                            '\t"access_token" : "<acces_token>",\n'+
                            '\t"course_id" : <course_id>,\n'+
                            '\t"labs" : {\n'+
                                '\t\t"<1st_assignment_name (choose a name)>: {"assignment_id": <id>},\n'+
                                '\t\t"<2nd_assignment_name>: {"assignment_id": <id>}\n'+
                            '\t}\n'+
                        '}\n')
        print("Config file created. Please fill it properly.")
        exit(0)


config = util.load_json('./config.json')
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
    elif args.upload:
        ac_grader = Client(args.lab)
        #upload grades to canvas
        ac_grader.upload_grades_from_excel()
    else:
        print("No optional argument selected. Pleas select one.")


if __name__ == "__main__":
    main()