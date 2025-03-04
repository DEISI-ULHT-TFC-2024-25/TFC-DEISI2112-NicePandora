"""pandora URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.urls import path, include # url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.urls import include

from shared.views import (login_view, register_view)
from .views import (
    manage,
)




base_urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin-django/', admin.site.urls),
    path('admin/', include('administration.urls')),
    path('', include('user.urls')),
    path('login/', login_view, name='login'),
    # path('signup/', register_view, name='register'),
    # re_path(r'^login/$', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
	path('oauth/', include('social_django.urls', namespace='social')),
    path('celery-progress/', include('celery_progress.urls')),
	#path(
    #'logout/',
    #LogoutView.as_view(template_name=settings.LOGOUT_REDIRECT_URL),
    #name='logout'
    #),
	#path('manage/', manage, name='manage'),
    path('api/', include('api.urls')),
    path('api/', include('shared.urls')),
] + staticfiles_urlpatterns()



urlpatterns = [
    path(settings.BASE_USR_PATH, include(base_urlpatterns)),
]


if settings.DEBUG:
    # test mode
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


