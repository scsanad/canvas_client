import mosspy
import argparse
import os
import ntpath
from datetime import datetime
import logging

parser = argparse.ArgumentParser("Tool for detecting software similarity in AC submissions")
parser.add_argument('-i', '--input', type=str, required=True,
                    help='Folder path which contains one or more subfolders with the asm files')
parser.add_argument('-l', '--language', choices={'c', 'ascii'}, required=True,
                    help='Target language')
parser.add_argument('-t', '--target-dir', required=True, 
                    help='Target dir, results will be saved here')
parser.add_argument('--ignore_limit', type=int, default=10,
                    help="Ignore code if repeats more than this value.")

args = parser.parse_args()

def main():

    input = os.path.join(args.input)

    for root, subfolders, files in os.walk(input):

        if len(subfolders) != 0 and len(files) > 0:
            print("Warning: {} contains subfolders and files as well", root)
        
        if len(files) > 0:
            print("Processing folder: {}".format(root))

            # create moss client
            # userid from the moss website
            userid = 278243184
            m = mosspy.Moss(userid, args.language)

            # ignore limit - if a given code repeats multiple times, ingore it
            m.setIgnoreLimit(args.ignore_limit)
            # show this many mathings
            m.setNumberOfMatchingFiles(500)

            # Submission Files
            asm_files_path = os.path.join(root, '*.asm')
            m.addFilesByWildcard(asm_files_path)

            url = m.send() # Submission Report URL
            print ("Report Url: " + url)

            # create folder where the results will be saved
            date = str(datetime.now()).split('.')[0].replace(' ', '_').replace(':', '-')
            print(date)
            report_path = os.path.join( args.target_dir,
                                        root.replace('/', '_') + '_' + date)
            try:
                os.makedirs(report_path, exist_ok=True)
            except OSError:
                print("Dir {} already exists")

            # Save html
            m.saveWebPage(url, os.path.join(report_path,
                                            "report.html"))

            # Download whole report locally including code diff links
            mosspy.download_report( url, os.path.join(report_path, "report/"), 
                                    connections=8, log_level=logging.INFO)

if __name__ == "__main__":
    main()