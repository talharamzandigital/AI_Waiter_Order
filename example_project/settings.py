from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_ai_waiter',
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

ROOT_URLCONF = 'example_project.urls'

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

WSGI_APPLICATION = 'example_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

GROQ_API_KEY = config('GROQ_API_KEY')





# from pathlib import Path
# from decouple import config

# Path — file system paths handle karne ke liye (Windows/Linux dono par kaam kare)
# config — .env file se secret values padhne ke liye (API keys, passwords directly code mein nahi likhte)


# BASE_DIR = Path(__file__).resolve().parent.parent
# Poore project ka root folder define karta hai. Matlab jahan manage.py hai woh location. Baaki sari paths isi se calculate hoti hain.
# __file__          = settings.py ki location
# .parent           = example_project/ folder
# .parent.parent    = root folder (jahan manage.py hai)



# SECRET_KEY = config('SECRET_KEY')
# Django ka security password hai — sessions, cookies, CSRF tokens sab isko use karte hain. .env file se read ho raha hai taake GitHub par accidentally upload na ho.

# CSRF = Django ka security guard 🛡️

# Yeh check karta hai:

# # "Kya yeh POST request waqai meri website ke form se aayi hai, ya kisi hacker website se?
# # DEBUG = config('DEBUG', default=True, cast=bool)
# # ".env file se DEBUG ki value lao. Agar value na mile to True maan lo. 
# # Aur jo value mile usko text se asli boolean (True ya False) mein convert kar do.
# INSTALLED_APPS = [
#     'django.contrib.admin',       # Admin panel (/admin/)
#     'django.contrib.auth',        # Login/logout/users system
#     'django.contrib.contenttypes',# Models ke types track karna
#     'django.contrib.sessions',    # User session handle karna
#     'django.contrib.messages',    # Flash messages (success/error)
#     'django.contrib.staticfiles', # CSS/JS/images serve karna
#     'rest_framework',             # REST API banane ke liye
#     'django_ai_waiter',           # TERA APNA APP ✓
# ]
# MIDDLEWARE = [
#     'SecurityMiddleware',    # HTTPS, security headers
#     'SessionMiddleware',     # Har request mein session attach karna
#     'CommonMiddleware',      # URL trailing slash, etc.
#     'CsrfViewMiddleware',    # Form attacks se bachao (CSRF protection)
#     'AuthenticationMiddleware', # Request mein logged-in user attach karna
#     'MessageMiddleware',     # Flash messages support
#     'XFrameOptionsMiddleware',  # Clickjacking se bachao
# ]
# AI Waiter Example

# User browser mein likhta hai:

# http://127.0.0.1:8000/chat/

# Request Django ko mili.

# Middleware 1: Security Check

# Django dekhta hai:

# Kya user login hai?

# Agar nahi:

# Login page par bhej do.

# Agar hai:

# Agay jane do.
# Middleware 2: CSRF Check

# Django dekhta hai:

# Kya POST request mein csrf token hai?

# Agar nahi:

# 403 Forbidden

# Agar hai:

# Request allow
# . ROOT_URLCONF
# pythonROOT_URLCONF = 'example_project.urls'
# Django ko batata hai URLs pehle kahan se padhni hain — example_project/urls.py main entry point hai.

# 9. TEMPLATES
# python'APP_DIRS': True,
# Django automatically har app ke templates/ folder mein HTML files dhundega. Teri chat.html isi setting ki wajah se milti hai.

# 10. DATABASES ⭐
# pythonDATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',  # PostgreSQL use karo
#         'NAME': config('DB_NAME'),      # Database ka naam (.env se)
#         'USER': config('DB_USER'),      # DB username (.env se)
#         'PASSWORD': config('DB_PASSWORD'), # DB password (.env se)
#         'HOST': config('DB_HOST', default='localhost'), # DB server
#         'PORT': config('DB_PORT', default='5432'),      # PostgreSQL ka default port
#     }
# }
# Yeh PostgreSQL database use ho raha hai (SQLite nahi). Saari credentials .env file se aa rahi hain — secure tarika.

# 11. AUTH_PASSWORD_VALIDATORS
# pythonAUTH_PASSWORD_VALIDATORS = [...]
# Jab koi user password set kare toh yeh rules check hoti hain:

# Username jaisa password nahi hona chahiye
# Minimum length honi chahiye
# Common password (123456) nahi hona chahiye
# Sirf numbers ka password nahi hona chahiye


# 12. Language & Time Settings
# pythonLANGUAGE_CODE = 'en-us'  # English
# TIME_ZONE = 'UTC'        # Time zone
# USE_I18N = True          # Internationalization on
# USE_TZ = True            # Timezone-aware dates use karo

# 13. STATIC_URL
# pythonSTATIC_URL = 'static/'
# CSS, JS, images ka URL path — browser yoursite.com/static/style.css se files access karega.

# 14. GROQ_API_KEY ⭐
# pythonGROQ_API_KEY = config('GROQ_API_KEY')
# Tera AI ka engine key — Groq API se LLM (llama3) call karne ke liye. .env mein rakha hai taake GitHub par leak na ho. llm_client.py is key ko yahan se read karta hai.