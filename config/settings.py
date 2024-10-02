from pathlib import Path
import os
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-@26m&+ov-rcayv5t8&7%@4yhf6wc4+1(bash^14xmw*%*s$rhm'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'daphne',
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 3rd party libs
    'drf_yasg',
    'rest_framework',
    'rest_framework_simplejwt',
    'tinymce',
    'channels',
    # local apps
    'accounts',
    'courses',
    'tests',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'db_edu',
        'USER': 'postgres',
        'PASSWORD': 'Asarvar-0911',
        'HOST': 'localhost',  
        'PORT': '5432',   
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.User'

JAZZMIN_SETTINGS = {
    "site_title": "Education Admin",
    "site_header": "Education Admin",
    "welcome_sign": "Education Admin Panel",
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10 
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'TOKEN_TYPE_CLAIM': 'token_type',
    'SLIDING_TOKEN_LIFETIME': timedelta(days=7),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=7),
}

# Channel layers configuration for WebSockets
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',  # For production, use Redis
    },
}

TINYMCE_DEFAULT_CONFIG = {
    "height": "320px",
    "width": "100%",
    "menubar": "file edit view insert format tools table help",
    "plugins": "advlist autolink lists link image imagetools charmap print preview anchor searchreplace visualblocks code "
               "fullscreen insertdatetime media table paste code help wordcount spellchecker",
    "toolbar": "undo redo | bold italic underline strikethrough | blockquote | image | fullscreen | fontselect fontsizeselect formatselect | alignleft "
               "aligncenter alignright alignjustify | outdent indent |  numlist bullist checklist | forecolor "
               "backcolor casechange permanentpen formatpainter removeformat | pagebreak | charmap emoticons | "
               "fullscreen  preview save print | insertfile image media pageembed template link anchor codesample | "
               "a11ycheck ltr rtl | showcomments addcomment code",
    "imagetools_toolbar": "rotateleft rotateright | flipv fliph | editimage imageoptions",
    "imagetools_cors_hosts": ['mydomain.com', 'otherdomain.com'],
    "imagetools_proxy": 'proxy.php',
    'image_advtab': True,
    "custom_undo_redo_levels": 10,
    'images_upload_url': '/api/upload_image/',  # add to plugin: image imagetools
    'relative_urls': False,
    'remove_script_host': False,
    'convert_urls': True,
    'fontsize_formats': "8px 9px 10px 11px 12px 14px 16px 18px 24px 30px 36px 48px 60px 72px 96px"
}
