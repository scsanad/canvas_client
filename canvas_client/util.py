import unicodedata
import shutil as shutil
import sys
import os
import json
import jsonpickle
import codecs
from pyunpack import Archive
from collections import namedtuple
import pandas as pd
import textwrap
import re

jsonpickle.set_preferred_backend('json')
jsonpickle.set_encoder_options('json', ensure_ascii=False, indent=4)



def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

def strip_accents(text):
    """Converts hungarian charachters to english characters"""
    return ''.join(char for char in
                    unicodedata.normalize('NFKD', text)
                    if unicodedata.category(char) != 'Mn')


def strip_special_characters(text):
    text = text.replace(' ', '_')
    text = text.replace('/', '-')
    return text


def gather_last_attempts(submissions_file, lab, files2copy, dest_dir):
    try:
        os.mkdir(dest_dir)
    except OSError:
        print(dest_dir + " already exists!")

    try:
        submissions = load_json(submissions_file)
    except IOError as ex:
        print("{} file does not exists. Error: {}".format(submissions_file, ex))
        return

    for file_name in files2copy:
        try:
            dir_name = os.path.join(dest_dir, "{}_{}".format(lab, file_name))
            os.mkdir(dir_name)
        except OSError:
            print(dest_dir + " already exists!")

    for submission in submissions:
        attempts = submission.attempts
        attempt_dir = attempts[-1].dir

        for file_name in files2copy:
            files = list(filter(lambda x: x.lower().endswith(".asm") and file_name.lower() in x.lower(), os.listdir(attempt_dir)))
            #TODO this does not work with the assignment L3c pascal and c version. Modification required
            if len(files) != 1:
                print("Warning: {} contains {} files which contains {}".format(attempt_dir, len(files), file_name))
            for f in files:
                file_path = os.path.join(attempt_dir, f)
                shutil.copy(file_path, os.path.join(dest_dir, "{}_{}".format(lab, file_name), "{}_{}".format(strip_accents(submission.user_name.replace(" ", "_")), f)))


def save_raw_file(path, raw_file):
    with open(path, 'wb') as f:
        f.write(raw_file)


def unpack_file(file_path, destination_dir):
    _, file_ext = os.path.splitext(file_path)
    if file_ext.lower() in ['.rar', '.zip']:
        try:
            Archive(file_path).extractall(destination_dir)
        except Exception as err:
            return 'Nem lehet kicsomagolni a {} fájlt: {}'.format(file_path, err)
    else:
        return "A feltöltött állomány .zip vagy .rar kiterjesztésű kell legyen!"
    return None


def save_json(submissions, file_path):
    with codecs.open(file_path, 'w', encoding='utf-8') as f:
        f.write(jsonpickle.encode(submissions))

def load_json(file_path):
    with codecs.open(file_path, 'r', encoding='utf-8') as f:
        submissions = jsonpickle.decode(f.read())
    return submissions


def delay_to_string(seconds_late):
    weeks_late = seconds_late // (7 * 24 * 3600)
    days_late = (seconds_late % (7 * 24 * 3600)) // (24 * 3600)
    hours_late = (seconds_late % (24 * 3600)) // 3600
    minutes_late = (seconds_late % (24 * 3600)) % 3600 // 60

    delay_string = ""
    for value, unit in zip([weeks_late, days_late, hours_late, minutes_late], ["w", "d", "h", "m"]):
        if value > 0:
            delay_string += "{}{} ".format(value, unit)
    return delay_string


def json2excel(submissions, lab_type):
    columns=['ID', 'name', 'section', 'delay', 'current grade', 'current comment', 'prev_comments']
    data = []
    for submission in submissions:
        delay = ""
        prev_comments = ""
        current_grade = ""
        current_comment = ""
        #get previous comments
        if len(submission.user_comments) > 0:
            for comment in submission.user_comments:
                prev_comments += "{}:\n\t{}".format( comment.author_name,
                                                '\n\t'.join(textwrap.wrap(comment.comment, 100)))
                prev_comments += '\n' if not prev_comments.endswith('\n') else ""
            prev_comments = prev_comments[:-len('\n')]
        #get delay value of attempts
        if submission.late:
            for attempt in submission.attempts:
                if attempt.late:
                    current_delay = delay_to_string(attempt.seconds_late)
                else:
                    current_delay = "no delay"
                delay += "{} - {}\n".format(attempt.nr, current_delay)
            delay = delay[:-len('\n')]

        #get current grade and comment if the last attempt is already graded - assign "" else
        last_attempt = submission.attempts[-1]
        current_grade = last_attempt.grade if last_attempt.grade is not None else ""
        current_comment = last_attempt.comment if last_attempt.comment is not None else ""
        current_comment = re.sub(r"[(\n) ]*$", "", current_comment)         #remove newline from the end
        current_comment = re.sub(r" {2, }", " ", current_comment)       #remove multiple spaces
        current_comment = re.sub(r"[(\n) ]{2,}", "\n", current_comment) #remove unnecessary spaces
        data.append((submission.user_id,
                    submission.user_name,
                    submission.user_section,
                    delay,              #delay of attemps
                    current_grade,      #grade
                    current_comment,    #your comment
                    prev_comments))     #previous comments

    df = pd.DataFrame(data, columns=columns)
    df.to_excel(lab_type + ".xlsx")

def copy_all(src, dest, regex = "", prefix = ""):
    src_files = os.listdir(src)
    count = 0
    for file_name in src_files:
        full_file_name = os.path.join(src, file_name)
        if os.path.isfile(full_file_name) and (re.search(regex, full_file_name) is not None):
            dest_file_name = os.path.join(dest, prefix + file_name)
            if not os.path.exists(dest_file_name):
                shutil.copy(full_file_name, dest_file_name)
                count += 1
    return count

def copy_submissions(src, dest, regex):
    cwd = src
    try:
        os.mkdir(dest)
    except OSError:
        pass
    students = [ student for student in os.listdir(cwd) if os.path.isdir(os.path.join(cwd, student)) ]
    for student in students:
        swd = os.path.join(cwd, student)
        attempts = [ attempt for attempt in os.listdir(swd) if os.path.isdir(os.path.join(swd, attempt)) ]
        if len(attempts) == 0:
            print(f"Warning: No attempt found for {student}")
            continue
        attempt = attempts[-1:][0]
        awd = os.path.join(swd, attempt)
        if copy_all(awd, dest, regex, f"{student}_") == 0:
            print(f"Warning: No file(s) copied for {student}")