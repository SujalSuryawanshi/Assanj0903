from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth import views as auth_views
from core.views import CustomPasswordResetView
from Main import settings
from django.conf.urls import handler404

handler404 = 'core.views.custom_404'

urlpatterns = [
    path("", include('core.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(template_name='register/password_reset_done.html'), name="password_reset_done"),
    path("password-reset-confirm/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name='register/password_reset_confirm.html'), name="password_reset_confirm"),
    path("password-reset-complete/complete/", auth_views.PasswordResetCompleteView.as_view(template_name='register/password_reset_complete.html'), name="password_reset_complete"),
    path('password_reset/', CustomPasswordResetView.as_view(template_name='register/password_reset.html'), name='password_reset'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_URL)
urlpatterns += staticfiles_urlpatterns()


