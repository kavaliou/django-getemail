import imaplib

from django_getemail.email_client.exceptions import EmailClientException, ReadOnlyEmailClientException, ServiceError


class BaseEmailClient(object):

    HOST = ''
    PORT = imaplib.IMAP4_SSL_PORT

    def __init__(self, login, password):
        self._login = login
        self._password = password
        self._mail = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._mail.close()

    def connect(self):
        if not self._mail:
            self._mail = imaplib.IMAP4_SSL(self.HOST, self.PORT)
            try:
                self._mail.login(self._login, self._password)
            except imaplib.IMAP4.error as exc:
                raise EmailClientException(msg=str(exc))
            except Exception as exc:
                raise exc

    def select_folder(self, mailbox):
        try:
            self._mail.select(mailbox)
        except imaplib.IMAP4.readonly:
            raise ReadOnlyEmailClientException()
        except imaplib.IMAP4.abort:
            self._mail = None
            self.connect()
            self._mail.select(mailbox)

    def _find_emails_uids(self, search_query, *args, **kwargs):
        raise NotImplementedError

    def search_email_uids(self, search_query, *args, **kwargs):
        try:
            result, uids = self._find_emails_uids(search_query, *args, **kwargs)
        except imaplib.IMAP4_SSL.error as exc:
            raise EmailClientException(msg=str(exc))
        except imaplib.IMAP4_SSL.abort as exc:
            self._mail = None  # need refactoring
            self.connect()
            result, uids = self._find_emails_uids(search_query, *args, **kwargs)
        return uids[0].decode().split()

    def _fetch_email_by_uid(self, uid):
        raise NotImplementedError

    def get_raw_email_by_uid(self, uid):
        try:
            result, data = self._fetch_email_by_uid(uid)
        except imaplib.IMAP4_SSL.error as exc:
            raise EmailClientException(msg=str(exc))
        except imaplib.IMAP4_SSL.abort as exc:
            self._mail = None
            self.connect()
            result, data = self._fetch_email_by_uid(uid)
        return data[0][1]


__all__ = ['BaseEmailClient', ]
