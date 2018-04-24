import email

import re


class EmailParserException(Exception):
    default_message = "Email parsing error."

    def __init__(self, msg=None):
        self.message = msg or self.default_message


class EmailParser(object):

    def __init__(self, raw_email):
        self._raw_email = raw_email
        self.email = email.message_from_string(self._raw_email)

    def get_content(self):
        if self.email.is_multipart():
            return ''.join([part.get_payload() for part in self.email.walk()
                            if part.get_content_type() == 'text/plain'])
        return self.email.get_payload()

    def get_subject(self):
        return self.email['subject']

    def get_attachments(self):
        if self.email.get_content_maintype() != 'multipart':
            return
        raw_files = []
        for part in self.email.walk():
            if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
                continue

            raw_files.append((part.get_filename(), part.get_payload(decode=True)))

        return raw_files

    @staticmethod
    def _find_email(str):
        regexp = re.search('(<)?(\w+(?:\.\w+)*@\w+(?:\.\w+)+)(?(1)>|$)', str)
        if not regexp:
            raise EmailParserException("Can't find email.")
        return regexp.group(2)

    def get_from(self):
        return self._find_email(self.email['from'])

    def get_to(self):
        return self._find_email(self.email['Delivered-To'])
