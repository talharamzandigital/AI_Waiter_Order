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
# Ye Python ki built-in library import karta hai jo file aur folder
# ke paths ko handle karti hai.Windows, Linux, Mac sab pe kaam karta hai automatically.
# from decouple import config(Configuration = Settings ya setup)

# decouple ek middleman hai jo secret values ko .env file se uthata hai aur settings.py ko deta hai — 
# taake koi secret GitHub pe na jaye!


# config — .env file se secret values padhne ke liye (API keys, passwords directly
#  code mein nahi likhte)

# Bina pathlib ke — Purana Tarika ❌
# python# Manually likhna parta tha — Windows pe kaam karta tha
# path = "E:\\django_ai_waiter\\example_project\\settings.py"

# # Linux pe yahi code tod jata tha!
# path = "E:/FoodHub/foodhub/settings.py"

# Problem ye thi ke Windows mein \\ hota hai aur Linux/Mac mein / — 
# dono mein alag likhna parta tha
# pathlib ke saath — Naya Tarika ✅
# pythonfrom pathlib import Path

# path = Path("E:/FoodHub/foodhub/settings.py")

# BASE_DIR = Path(__file__).resolve().parent.parent
# Poore project ka root folder define karta hai. Matlab jahan manage.py 
# hai woh location. Baaki sari paths isi se calculate hoti hain.
# __file__          = settings.py ki location
# .parent           = example_project/ folder
# .parent.parent    = root folder (jahan manage.py hai)
# django_ai_waiter/ (Container)
# │
# │   # Ye sirf pada rehta hai — koi kaam nahi karta
# │
# └── example_project/ (App Config)
#     │
#     ├── settings.py
#     │     DATABASES = {...}      ← PostgreSQL connect karo
#     │     INSTALLED_APPS = [...]  ← Konsi apps load karo
#     │     MEDIA_ROOT = ...        ← Images kahan rakho
#     │
#     ├── urls.py
#     │     /login  → auth app
#     │     /menu   → menu app
#     │     /order  → order app
#     │
#     └── wsgi.py
#           Browser → Django → Response
# settings.py file mein ye likha hai
# __file__ = "settings.py"  # Django ko sirf itna pata hai

# # .resolve() lagaya
# Path(__file__).resolve()
# # → E:\FoodHub\foodhub\settings.py  ✅ Full path mil gayi



# SECRET_KEY = config('SECRET_KEY')
# Django ka security password hai — sessions, cookies, CSRF tokens sab 
# SECRET_KEY = config('SECRET_KEY') matlab — ".env file mein jao, SECRET_KEY dhundo,
#  uski value uthao aur yahan set karo" — taake ye secret value
#  GitHub pe kabhi na jaye! 🔐

#                           CSRF = Django ka security guard 🛡️
# CSRF = Cross Site Request Forgery
# CSRF ek attack hai jisme hacker teri taraf se fake request bhejta hai 
# — Django secret token se ye attack
# rokta hai, kyunke sirf asli form ke paas token hota hai! 

# FoodHub ka form khola
#         ↓
# Django ne ek UNIQUE secret token banaya
#         ↓
# Form ke saath bheja
#         ↓
# Tu ne submit kiya — token bhi gaya saath
#         ↓
# Django ne check kiya — "Token sahi hai?" ✅
#         ↓
# Request accept ki


                              # Token Kahan Save Hota Hai
# Django ne token banaya
#         ↓
# Browser ki Cookie mein save kiya
#         ↓
# Har form submit pe cookie se token uthaya
#         ↓
# Server pe bheja — verify kiya

# Yeh check karta hai:

# # "Kya yeh POST request waqai meri website ke form se aayi hai,
#  ya kisi hacker website se?


# Session Kya Hai? 📋
# Session = Server pe temporarily 
#           save ki gayi information

# Jab tu login karta hai:
# Server ne ek locker banaya 🔒
# Locker mein tera data rakha
# Locker ki chabi (ID) tujhe de di

# Cookie Vs Session — Asli Faraq 🔍
# Cookie — Sab Browser Mein:
# Browser mein save:
# user_id    = 42
# name       = talha
# balance    = 50000   ← Sensitive! Sab dikhra hai 😱
# password   = 1234    ← Dangerous! ❌
# Session — Server Pe Safe:
# Browser mein sirf:
# session_id = xK9mN2   ← Sirf ye chabi hai

# Server pe:
# xK9mN2 = {
#     user_id  : 42,
#     name     : talha,
#     balance  : 50000,  ← Safe! Server pe hai ✅
#     password : 1234    ← Safe! Koi nahi dekh sakta ✅
# }


                                 # .gitignore Kya Hai?
# .gitignore ek simple text file hai
# Jisme tu likhta hai:
# "In files ko GitHub pe mat bhejna"

# Git ye file padhta hai
# Aur listed files ko 
# IGNORE kar deta hai — upload nahi karta

#              DEBUG = config('DEBUG', default=True, cast=bool)

# Django ko kehti hai: "Sab se pehle .env file kholo aur dekho kya "
# "usmein DEBUG naam ki koi setting likhi hui hai. Agar likhi hui hai "
# "to uski value le lo. Agar DEBUG mil hi nahi raha, to pareshan mat ho "
# "aur khud se True use kar lo. Lekin .env file mein jo value milegi, wo text"
# " ki shakal mein hogi, jaise 'True' ya 'False'. Django ko text nahi balki"
# " asli boolean values True ya False chahiye hoti hain, isliye cast=bool us "
# "text ko boolean mein badal deta hai."


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