class Submission(object):
    def __init__(self, user_id, user_name, user_comments, late, attempts, user_section=None):
        self.user_id = user_id
        self.user_name = user_name
        self.user_section = user_section
        self.user_comments = user_comments
        self.late = late
        self.attempts = attempts        


class SubmissionAttempt(object):
    def __init__(   self, nr, late, submitted_at, seconds_late, attachments,
                    comment=None, grade=None, dir=None, delay_time=None):
        self.nr = nr
        self.dir = dir
        self.late = late
        self.submitted_at = submitted_at
        self.seconds_late = seconds_late
        self.delay_time = delay_time
        self.comment = comment
        self.grade = grade
        self.attachments = attachments


class SubmissionAttachment(object):
    def __init__(   self, attachment_name, attachment_url, attachment_path=None):
        self.attachment_name = attachment_name
        self.attachment_path = attachment_path
        self.attachment_url = attachment_url
        

class SubmissionComment(object):
    def __init__(self, comment, author_name, created_at):
        self.comment = comment
        self.author_name = author_name
        self.created_at = created_at
