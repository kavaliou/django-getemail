from datetime import datetime, timedelta

from django.conf import settings
from django.core.management import BaseCommand

from django_getemail.email_client import GmailClient
from django_getemail.email_client.exceptions import EmailClientException
from django_getemail.email_parser import EmailParser, EmailParserException
from django_getemail.models import Email
from django_getemail.settings import conf
from django_getemail.utils import Publisher


class Command(BaseCommand):
    help = 'Starts Gmail receiver'
    email_publisher = Publisher(conf.RABBITMQ_HOST, conf.EXCHANGE_NAME, conf.ROUTING_KEY)
    gmail_client = GmailClient(conf.MAIL_LOGIN, conf.MAIL_PASSWORD)

    @staticmethod
    def _get_search_query(latest_uid):
        if settings.DEBUG:
            week_ago_str = (datetime.now() - timedelta(days=conf.FETCH_FOR_DAYS)).strftime('%d-%b-%Y')
            time_filter = 'SINCE "{}"'.format(week_ago_str)
        else:
            time_filter = ''

        uid_filter = 'UID {}:*'.format(int(latest_uid) + 1) if latest_uid else ''

        search_query = '{} {}'.format(time_filter, uid_filter)

        return '({})'.format(search_query.strip()) if time_filter or uid_filter else 'ALL'

    def _run_email_client(self):
        latest_uid = None

        self.email_publisher.connect()
        self.gmail_client.connect()

        while True:
            self.gmail_client.select_folder(conf.MAIL_FOLDER)

            if not latest_uid:
                latest_uid = Email.latest_uid()

            search_query = self._get_search_query(latest_uid)

            # filter messages by label
            label_filter = 'label:{}'.format(conf.FILTERING_LABEL)

            try:
                new_email_uids = self.gmail_client.search_email_uids(search_query, label_filter=label_filter)
            except EmailClientException as exc:
                self.stdout.write(search_query)
                raise exc

            if len(new_email_uids) == 1 and new_email_uids[0] == latest_uid:  # No new emails
                continue

            for uid in new_email_uids:
                raw_email = self.gmail_client.get_raw_email_by_uid(uid).decode()
                parser = EmailParser(raw_email)

                try:
                    email_data = {
                        'uid': uid,
                        'content': parser.get_content(),
                        'subject': parser.get_subject(),
                        'sender': parser.get_from(),
                        'recipient': parser.get_to(),
                        'raw_email': raw_email
                    }
                    attachments = parser.get_attachments()

                except EmailParserException as exc:
                    self.stdout.write(exc.message)
                    self.gmail_client.set_label_by_uid(uid, conf.ERROR_EMAIL_LABEL)

                else:
                    email = Email.objects.create(**email_data)
                    email.process_attachments(attachments)
                    latest_uid = uid
                    self.gmail_client.set_label_by_uid(uid, conf.IMPORTED_EMAIL_LABEL)
                    self.email_publisher.publish(str(email.id))

    def handle(self, *args, **options):
        try:
            self._run_email_client()
        except KeyboardInterrupt:
            self.stdout.write('Keyboard Interrupt')
        finally:
            self.email_publisher.close()
