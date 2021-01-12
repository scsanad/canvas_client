import subprocess
import os
import glob
import json
import re
import requests
import shutil
import sys
import pandas as pd
import numpy as np
import ntpath
import unicodedata

import canvas_client.util as util
from canvas_client.submission import Submission, SubmissionAttempt
from canvas_client.canvas_api import CanvasAPI


class Client:
    #TODO add destination dir and aclab_dir to the constructor
    def __init__(self, lab):

        config = util.load_json('config.json')
        access_token = config["access_token"]

        self.lab = lab
        self.lab_config = config["labs"][lab]

        self.server_url = config['url'].lower()
        if not self.server_url.startswith("https://"):
            self.server_url = "https://" + self.server_url
        self.course_id = config['course_id']
        self.assignment_id = self.lab_config['assignment_id']

        self.canvasAPI = CanvasAPI( server_url=self.server_url,
                                    course_id=self.course_id,
                                    assignment_id=self.assignment_id,
                                    access_token=access_token)

        root_dir = './'
        try:
            self.assignments_dir = os.path.join(root_dir, 'assignments')
            os.mkdir(self.assignments_dir)

        except OSError:
            pass

        try:
            self.assignment_name = self.lab.upper()
            self.assignments_dir = os.path.join(self.assignments_dir, self.assignment_name)
            os.mkdir(self.assignments_dir)
        except OSError:
            pass

        self.grades_file_name = '{}_grades.json'.format(self.assignment_name)




    def download_submissions(self, workflow_state):
            # get the list of submissions from canvas
            # TODO add workflow state as argument
            submissions = self.canvasAPI.get_list_of_submissions(workflow_state)

            # dowload student sections (student groupds like info, info+, etc)
            submissions = self._download_sections(submissions)

            # download submissions (files)
            submissions = self._download_submissions(submissions)

            # unzipp attachments
            submissions = self._unzip_subsmissions(submissions)

            # util.save_json(submissions, self.grades_file_name)

            util.json2excel(submissions, self.lab)


    def _download_sections(self, submissions):
        course_sections = self.canvasAPI.get_sections()
        students = {}
        for section in course_sections:
            for student in section.students:
                students[student] = section.name

        for submission in submissions:
            submission.user_section = students[submission.user_name]
        return submissions


    def _download_submissions(self, submissions):
        for submission in submissions:
            user_name_eng = submission.user_name.replace(" ", "_")
            user_name_eng = util.strip_accents(user_name_eng)
            user_dir = os.path.join(self.assignments_dir, user_name_eng)

            print("Processing: ", submission.user_name)
            try:
                os.mkdir(user_dir)
            except OSError:
                pass

            #download all attempts
            for attempt in submission.attempts:
                attempt.dir = os.path.join(user_dir, 'attempt_' + str(attempt.nr))

                try:
                    os.mkdir(attempt.dir)

                    for attachment in attempt.attachments:
                        attachment_path = os.path.join(attempt.dir, attachment.attachment_name)
                        attachment.attachment_path = attachment_path
                        #if the file is not already downloaded
                        if not os.path.isfile(attachment_path):
                            raw_attachment = self.canvasAPI.download_submission_attachment(attachment.attachment_url)
                            util.save_raw_file(attachment_path, raw_attachment)
                except OSError:
                    pass

        return submissions


    def _unzip_subsmissions(self, submissions):
        for step, submission in enumerate(submissions):
            print("{}/{}: {} ".format(step+1, len(submissions), submission.user_name))

            for attempt in submission.attempts:
                comment = self._unzip_attempt(attempt.dir, submission.user_section)
                if attempt.late:
                    seconds_late = attempt.seconds_late
                    delay_time = util.delay_to_string(seconds_late)
                    comment = '{} \n\n Késés: {}'.format(comment, delay_time)
                    attempt.delay_time = delay_time # TODO this can be removed from the model
                attempt.comment = comment
        return submissions


    def _unzip_attempt(self, dir_path, user_section):
        # unzip the file
        files = os.listdir(dir_path)
        zip_files = list(filter(lambda x: x.lower().endswith('.zip') or x.lower().endswith('.rar'), files))

        if len(zip_files) == 1:
            attachment_path = os.path.join(dir_path, zip_files[0])
            err = util.unpack_file(attachment_path, dir_path)
            if err:
                comment = err
                return comment
        else:
            print("Warning: {} dir contains {} files.".format(dir_path, len(zip_files)))

        return ""


    def upload_grades_from_excel(self):
        grades_df = pd.read_excel("{}.xls".format(self.lab.upper()))
        grades_df = grades_df.replace(np.nan, "", regex=True)
        graded_submissions = []
        for _, row in grades_df.iterrows():
            graded_attempt = SubmissionAttempt( None, None, None, None, None,
                                                None, comment=row['current comment'],
                                                grade=row['current grade'])
            graded_submission = Submission( row['ID'],
                                            None,
                                            None,
                                            None,
                                            [graded_attempt])
            graded_submissions.append(graded_submission)
        self.canvasAPI.upload_grades_from_submissions(graded_submissions)


    # TODO check the number of files
    def _check_nr_files(self, dir_path, user_section, warning_comment):
        #check the number of files in the dir
        asm_files = glob.glob(os.path.join(dir_path, "*.[aA][sS][mM]"))
        if (len(asm_files) != self.lab_config['nr_files']):
            comment = "A feltöltött feladat {} asm fájlt kell tartalmazzon. Ez a feltöltés {} fájlt tartalmaz"\
                        .format(self.lab_config['nr_files'], len(asm_files))
            grade = -10
            comment = comment + warning_comment
            return grade, comment