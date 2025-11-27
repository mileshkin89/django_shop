from core.settings.settings import *

# Using SQLite in memory for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

DEBUG = False

# Disable unnecessary middleware to speed up testing
MIDDLEWARE = [mw for mw in MIDDLEWARE if mw not in [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]]

# Setting up e-mail
# EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'