import requests
import json
from datetime import datetime
import sys

from submission import Submission, SubmissionAttempt, SubmissionComment, SubmissionAttachment
from section import Section

class Parser:

    @staticmethod
    def submissions_to_grades_json(submissions):
        grade_data = {'grade_data': {}}
        for submission in submissions:
            last_attempt = submission.attempts[-1]
            grade_data['grade_data'][submission.user_id] = {'posted_grade': last_attempt.grade,
                                                            'text_comment': last_attempt.comment }
        return grade_data


    @staticmethod
    def submission_from_dict(submission_dict):
        submission_comments = []
        user = submission_dict['user']
        for comment_dict in submission_dict['submission_comments']:
            submission_comments.append(Parser.submission_comment_from_dict(comment_dict))

        try:
            submission_attempts = []
            for attempt in submission_dict['submission_history']:
                if attempt['workflow_state'] in ("submitted", "graded"):
                    submission_attempt = Parser.submission_attempt_from_dict(attempt)
                    submission_attempts.append(submission_attempt)

            submission = Submission(user_id=user['id'],
                                    user_name=user['name'],
                                    user_comments=submission_comments,
                                    late=submission_dict['late'],
                                    attempts=submission_attempts)
        except Exception as error:
            print("Warning. Problem during processing data of {}: {}. Cannot download the submission. Please grade this student on canvas.".format(user['name'], error))
            return None
        return submission


    @staticmethod
    def submission_comment_from_dict(comment_dict):
        submission_comment = SubmissionComment( comment_dict['comment'],
                                                comment_dict['author_name'],
                                                comment_dict['created_at'])
        return submission_comment


    @staticmethod
    def submission_attempt_from_dict(attempt_dict):
        try:
            submitted_at = datetime.strptime(   attempt_dict['submitted_at'],
                                                '%Y-%m-%dT%H:%M:%SZ')

            attachments = []

            for attachment in attempt_dict['attachments']:
                attachments.append(
                    SubmissionAttachment( attachment_name=attachment['display_name'],
                                          attachment_url=attachment['url']))

            submission_attempt = SubmissionAttempt( nr=attempt_dict['attempt'],
                                                    late=attempt_dict['late'],
                                                    submitted_at=submitted_at.strftime("%Y-%m-%d %H:%M:%S"),
                                                    seconds_late=attempt_dict['seconds_late'],
                                                    grade=attempt_dict['grade'],
                                                    attachments=attachments)
        except KeyError as error:
            raise Exception('No {} in attempts.'.format(error))
        return submission_attempt


    @staticmethod
    def section_from_dict(section_dict):
        students = []
        for s in section_dict['students']:
            students.append(s['name'])
        section = Section(section_dict['name'], students)
        return section



class CanvasAPI:
    '''Class to download from and upload to www.canvas2.cs.ubbcluj.ro'''

    def __init__(self, server_url, course_id, assignment_id, access_token):

        self.server_url = server_url
        self.course_id = course_id
        self.assignment_id = assignment_id

        self.headers = {"content-type" : "application/json"}
        self.params = {"access_token": access_token,    #access token from canvas
                        "per_page": 50}                 #nr submission per page - looks like 50 is the highest allowed value


    def upload_grades_from_submissions(self, submissions):
        """ Upload grades to server from list of submissions

                submissions: list of submissions
        """
        url = '{}/api/v1/courses/{}/assignments/{}/submissions/update_grades'\
                        .format(self.server_url,
                                self.course_id,
                                self.assignment_id)

        data = Parser.submissions_to_grades_json(submissions)

        r = requests.post(url, headers=self.headers, params=self.params, json=data)
        print("Grades uploaded. Response: {}".format(r.status_code))


    def get_assignment_info(self):
        """
        Returns the assignment specified by self.assignment_id from course self.course_id
        """
        url = self.server_url + "/api/v1/courses/" + str(self.course_id) + '/assignments/' + str(self.assignment_id)
        r = requests.get(url, headers=self.headers, params=self.params)
        assignment = json.loads(r.text)
        return assignment


    def get_list_of_submissions(self, workflow_state = ( 'submitted' )):
        """ workflow_state: { submitted, unsubmitted, graded } """
        params = self.params.copy()
        params['include[]'] = ['submission_comments', 'submission_history', 'group','user']

        #download all the pages - pagination is used with per_page=50 value
        url = "{}/api/v1/courses/{}/assignments/{}/submissions".format(self.server_url, self.course_id, self.assignment_id)
        r = requests.get(url, headers=self.headers, params=params)

        if r.status_code != 200:
            print("Cannot download submissions: {}".format(r.text))
            sys.exit(0)

        submissions = json.loads(r.text)
        while r.links.get('next'):
            url = r.links['next']['url']
            r = requests.get(url, headers=self.headers, params=params)
            submissions += json.loads(  r.text)

        #filter worflow state and parse submission
        submissions = [Parser.submission_from_dict(s) for s in submissions if s['workflow_state'] in workflow_state]
        submissions = [x for x in submissions if x is not None]
        return submissions


    def get_sections(self):

        params = self.params.copy()
        params['include[]'] = ['students']
        #download all the pages - pagination is used with per_page=50 value
        url = "{}/api/v1/courses/{}/sections".format(self.server_url, self.course_id)
        r = requests.get(url, headers=self.headers, params=params)
        sections = json.loads(r.text)

        #parse sections
        sections = [Parser.section_from_dict(s) for s in sections]
        return sections


    def download_submission_attachment(self, url):
        """Downloads a file from the given url, and saves it to dest_dir"""

        r = requests.get(url)
        return r.content
