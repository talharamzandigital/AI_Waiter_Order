"""
URL configuration for example_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
    """
# from django.contrib import admin
# from django.urls import path, include

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('api/', include('django_ai_waiter.urls')),
# ]
from django.http import HttpResponse
from django.contrib import admin
from django.urls import path, include

def home(request):
    return HttpResponse("AI Waiter Project Running Successfully")

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('api/', include('django_ai_waiter.urls')),
]


# HttpResponse browser ko simple text ya data bhejne ke liye use hota hai.



# Ye file Django project ki main URL configuration file hai jo website 
# par aane wali requests ko sahi jagah bhejne ka kaam karti hai. Sabse 
# pehle HttpResponse import kiya gaya hai jo browser ko simple text response
# bhejne ke liye use hota hai, admin Django ke built-in admin panel ko access
# karne ke liye import kiya gaya hai, aur path aur include URLs define karne aur
# dusri app ki URLs ko include karne ke liye use hote hain. home() function ek view
# hai jo user ke homepage (/) par aane par "AI Waiter Project Running Successfully"
# ka message browser me dikhata hai. urlpatterns ke andar path('', home) homepage 
# ko home() function se connect karta hai, path('admin/', admin.site.urls) admin 
# panel ko /admin/ URL par available banata hai, aur
# path('api/', include('django_ai_waiter.urls')) ka matlab hai ke /api/ 
# se shuru hone wali tamam requests django_ai_waiter/urls.py file me bhej di
# jayengi, jahan unke mutabiq views execute honge. Is tarah ye file project me
# ek traffic controller ki tarah kaam karti hai jo har request ko uski munasib
# destination tak pohanchati hai.
