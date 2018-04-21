from .base import BaseEmailClient


class GmailClient(BaseEmailClient):

    HOST = 'imap.gmail.com'

    def _find_emails_uids(self, search_query, *args, **kwargs):
        label_filter = kwargs.get('label_filter')
        return self._mail.uid('search', None, search_query, 'X-GM-RAW', label_filter)

    def _fetch_email_by_uid(self, uid):
        return self._mail.uid('fetch', uid, '(X-GM-THRID RFC822)')

    def set_label_by_uid(self, uid, label):
        self._mail.uid('store', uid, '+X-GM-LABELS', label)
        self._mail.expunge()

    def remove_label_by_uid(self, uid, label):  # doesn't work properly
        self._mail.uid('store', uid, '-X-GM-LABELS', label)
        self._mail.expunge()

__all__ = ['GmailClient', ]
