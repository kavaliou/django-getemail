import email

from mailparser.utils import decode_header_part


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

    def _process_attachements(self, message_part):
        content_disposition = message_part.get("Content-Disposition", None)
        if not content_disposition:
            return
        dispositions = content_disposition.strip().split(";")
        if content_disposition and dispositions[0].lower() == "attachment":
            file_data = message_part.get_payload(decode=True)
            filename = decode_header_part(message_part.get_filename())
            return filename, file_data

    def get_attachments(self):
        raw_files = []
        for part in self.email.walk():
            attachment = self._process_attachements(message_part=part)
            if attachment:
                raw_files.append(attachment)
        return raw_files

    @staticmethod
    def _find_email(str_):
        email_addr = email.utils.parseaddr(str_)[-1]
        if '@' not in email_addr:
            raise EmailParserException("Can't find email.")
        return email_addr

    def get_from(self):
        return self._find_email(self.email['from'])

    def get_to(self):
        return self._find_email(self.email['Delivered-To'])
