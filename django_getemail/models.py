import mailparser
import tempfile

from django.core.files import File
from django.db import models

from django_getemail.signals import email_imported


def upload_to(instance, filename):
    return '{}/{}'.format(type(instance).__name__, filename)


class Email(models.Model):
    ERROR = 'error'
    NEW = 'new'
    RETRYING = 'retrying'
    SKIPPED = 'skipped'
    PROCESSED = 'processed'

    processing_statuses = (
        (ERROR, 'Error'),
        (NEW, 'New'),
        (RETRYING, 'Retrying'),
        (SKIPPED, 'Skipped'),
        (PROCESSED, 'Processed')
    )

    created_at = models.DateTimeField(auto_now_add=True)
    uid = models.CharField(max_length=20, unique=True)
    raw_email = models.TextField()
    subject = models.CharField(max_length=255, null=True, blank=True)
    sender = models.CharField(max_length=255, null=True, blank=True)
    recipient = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=processing_statuses, default=NEW)

    def __str__(self):
        return 'Email with uid: {} created at {}'.format(self.uid, self.created_at)

    def fail_processing(self):
        self.status = Email.ERROR
        self.save(update_fields=('status', ))

    def process_attachments(self, attachments):
        for attach in attachments:
            filename, payload = attach.get('filename'), attach.get('payload')
            with tempfile.TemporaryFile() as output_:
                output_.write(payload)
                EmailAttachment.objects.create(file=File(output_, filename), email=self)

    def process(self, parse_attachments=True):
        parser = mailparser.parse_from_string(self.raw_email)
        try:
            self.sender = parser.from_[0][-1]
            self.subject = parser.subject
            self.content = parser.content

            if parse_attachments:
                attachments = parser.attachments
                self.process_attachments(attachments)

            self.status = self.PROCESSED
            self.save()
        except Exception as exc:  # Add EmailParser exceptions
            print(exc)
            self.fail_processing()

    def send_imported_email_signal(self):
        email_imported.send(sender=self.__class__, email=self)


class EmailAttachment(models.Model):
    email = models.ForeignKey('Email', related_name='attachments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=upload_to)

    def __str__(self):
        return 'Attachment for email with id {}'.format(self.email_id)
