from django.conf import settings

CONFIG_DEFAULTS = {
    'MAIL_FOLDER': 'INBOX',
    'FETCH_FOR_DAYS': 3,
    'IMPORTED_EMAIL_LABEL': 'imported',
    'ERROR_EMAIL_LABEL': 'error',
    'SEND_GETEMAIL_EVENT': True
}

USER_CONFIG = getattr(settings, 'DJANGO_GETEMAIL_CONFIG', {})

CONFIG = CONFIG_DEFAULTS.copy()
CONFIG.update(USER_CONFIG)


class Settings(object):
    """
    Shadow Django's settings with a little logic
    """

    @property
    def MAIL_LOGIN(self):
        return CONFIG.get('MAIL_LOGIN')

    @property
    def MAIL_PASSWORD(self):
        return CONFIG.get('MAIL_PASSWORD'')

    @property
    def MAIL_FOLDER(self):
        return CONFIG.get('MAIL_FOLDER')

    @property
    def FETCH_FOR_DAYS(self):
        return CONFIG.get('FETCH_FOR_DAYS')

    @property
    def FILTERING_LABEL(self):
        return CONFIG.get('FILTERING_LABEL', '')

    @property
    def IMPORTED_EMAIL_LABEL(self):
        return CONFIG.get('IMPORTED_EMAIL_LABEL')

    @property
    def ERROR_EMAIL_LABEL(self):
        return CONFIG.get('ERROR_EMAIL_LABEL')

    @property
    def SEND_GETEMAIL_EVENT(self):
        return CONFIG.get('SEND_GETEMAIL_EVENT')

    @property
    def QUEUE_NAME(self):
        return CONFIG.get('QUEUE_NAME')

conf = Settings()
