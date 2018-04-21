import pika

from datetime import datetime, timedelta

from django.conf import settings
from django.core.management import BaseCommand

from django_getemail.email_client import GmailClient
from django_getemail.email_client.exceptions import EmailClientException, ReadOnlyEmailClientException, ServiceError
from django_getemail.email_parser import EmailParser, EmailParserException
from django_getemail.models import Email
from django_getemail.settings import conf


class Command(BaseCommand):
    help = 'Starts Gmail receiver'

    @staticmethod
    def connect_to_gmail():
        try:
            gmail_client = GmailClient(conf.MAIL_LOGIN, conf.MAIL_PASSWORD)
        except (EmailClientException, ReadOnlyEmailClientException) as exc:
            raise exc
        return gmail_client

    @staticmethod
    def get_search_query(latest_uid):
        if settings.DEBUG:
            week_ago_str = (datetime.now() - timedelta(days=conf.FETCH_FOR_DAYS)).strftime('%d-%b-%Y')
            time_filter = 'SINCE "{}"'.format(week_ago_str)
        else:
            time_filter = ''

        uid_filter = ' UID {}:*'.format(int(latest_uid) + 1) if latest_uid else ''

        return '({}{})'.format(time_filter, uid_filter) if time_filter or uid_filter else 'ALL'

    def handle(self, *args, **options):
        latest_uid = None

        gmail_client = self.connect_to_gmail()

        while True:
            gmail_client.select_folder(conf.MAIL_FOLDER)

            if not latest_uid:
                latest_email = Email.objects.order_by('-uid').first()
                if latest_email:
                    latest_uid = latest_email.uid

            search_query = self.get_search_query(latest_uid)

            # filter messages by label
            label_filter = 'label:{}'.format(conf.FILTERING_LABEL)

            try:
                new_email_uids = gmail_client.search_email_uids(search_query, label_filter=label_filter)
            except ServiceError as err:
                gmail_client = self.connect_to_gmail()
                continue
            except EmailClientException as exc:
                print(exc.message)
                break

            if len(new_email_uids) == 1 and new_email_uids[0] == latest_uid:  # No new emails
                continue

            for uid in new_email_uids:
                try:
                    raw_email = gmail_client.get_raw_email_by_uid(uid).decode()
                except ServiceError:
                    gmail_client = self.connect_to_gmail()
                    break

                parser = EmailParser(raw_email)

                try:
                    email_data = {
                        'uid': uid,
                        'content': parser.get_content(),
                        'subject': parser.get_subject(),
                        'sender': parser.get_from(),
                        'raw_email': raw_email
                    }
                    email = Email.objects.create(**email_data)
                    attachments = parser.get_attachments()
                    email.process_attachments(attachments)

                except EmailParserException as exc:
                    gmail_client.set_label_by_uid(uid, conf.ERROR_EMAIL_LABEL)

                else:
                    latest_uid = uid
                    gmail_client.set_label_by_uid(uid, conf.IMPORTED_EMAIL_LABEL)
                    if conf.SEND_GETEMAIL_EVENT:
                        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
                        channel = connection.channel()
                        channel.queue_declare(queue=conf.QUEUE_NAME, durable=True)

                        channel.basic_publish(
                            exchange='',
                            routing_key=conf.QUEUE_NAME,
                            body='{}'.format(email.id),
                            properties=pika.BasicProperties(
                                delivery_mode=2,  # make message persistent
                            ))
                        connection.close()
                    else:
                        email.send_imported_email_signal()
