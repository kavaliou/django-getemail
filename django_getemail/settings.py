from django.conf import settings

CONFIG_DEFAULTS = {
    'MAIL_FOLDER': 'INBOX',
    'FETCH_FOR_DAYS': 3,
    'IMPORTED_EMAIL_LABEL': 'imported',
    'ERROR_EMAIL_LABEL': 'error',
    'SEND_GETEMAIL_EVENT': True,
    'RABBITMQ_HOST': 'localhost',
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
        return CONFIG.get('MAIL_PASSWORD')

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
    def ROUTING_KEY(self):
        return CONFIG.get('ROUTING_KEY')

    @property
    def RABBITMQ_HOST(self):
        return CONFIG.get('RABBITMQ_HOST')

    @property
    def EXCHANGE_NAME(self):
        return CONFIG.get('EXCHANGE_NAME')

conf = Settings()
