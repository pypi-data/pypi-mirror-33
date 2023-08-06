# -*- coding:utf-8 -*-
DEBUG = False

ALLOWED_HOSTS = [
    'craiglists.ru',
]

ADMINS = (
    ('Admin', 'inoks@mail.ru'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dcf_db',
        'USER': 'dcf_user',
        'PASSWORD': 'dcf_pass',
        'HOST': 'localhost',
        'PORT': '',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

SECRET_KEY = 'sfdfsdfksd;f;sdkf;lskdf;ksd;lfk;sdkf;lksd;lfksd;lfk;lsdkfl;skdf;lksdl;kfl;wekrwer'

TIME_ZONE = 'Europe/Kaliningrad'

LANGUAGE_CODE = 'ru'

SOCIAL_AUTH_FACEBOOK_KEY = '969556519755162'
SOCIAL_AUTH_FACEBOOK_SECRET = 'f6db07da59e8adf61f6cf9e221f5cfb6'

DCF_SITE_NAME = u'Доска объявлений'
DCF_SITE_DESCRIPTION = u'Бесплатные объявления о продаже, покупке, предложении услуг и работы'
DCF_DISPLAY_CREDITS = False

GOOGLE_ANALYTICS_PROPERTY_ID = 'UA-568125-13'
GOOGLE_SITE_VERIFICATION_ID = 'lXKVmyI_Mbr2sEGtgxVJozISRwUWDj4yIAZ98Hi1-UQ'

EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_HOST_USER = SERVER_EMAIL = 'contact@craiglists.ru'
EMAIL_HOST_PASSWORD = 'tysatf1212A'
EMAIL_PORT = '587'
EMAIL_USE_TLS = True
