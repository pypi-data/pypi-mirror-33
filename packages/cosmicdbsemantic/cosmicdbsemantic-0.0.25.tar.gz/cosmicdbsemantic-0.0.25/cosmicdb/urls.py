from django.urls import path, re_path, include
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.contrib.auth.decorators import login_required
from django.conf import settings

from cosmicdb.views import CosmicLoginView, CosmicLogoutView, CosmicPasswordChangeView, \
    CosmicPasswordChangeDoneView, CosmicPasswordResetView, CosmicPasswordResetDoneView, CosmicPasswordResetConfirmView, \
    CosmicPasswordResetCompleteView, CosmicHomeView, CosmicSignupView, CosmicDashboardView, \
    CosmicChangeEmail, notifications

favicon_view = RedirectView.as_view(url=static('cosmicdb/favicon.ico'), permanent=True)

urlpatterns = [

    path('', CosmicHomeView.as_view(), name='home'),

    path('favicon.ico', favicon_view, name='favicon_default'),

    path('login/', CosmicLoginView.as_view(), name='login'),
    path('logout/', CosmicLogoutView.as_view(), name='logout'),

    path('password_change/', login_required(CosmicPasswordChangeView.as_view()), name='password_change'),
    path('password_change/done/', login_required(CosmicPasswordChangeDoneView.as_view()), name='password_change_done'),

    path('password_reset/', CosmicPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', CosmicPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CosmicPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', CosmicPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('email_change/', login_required(CosmicChangeEmail.as_view()), name='email_change'),

    path('signup/', CosmicSignupView.as_view(), name='signup'),

    path('notifications/', notifications, name='notifications'),
    path('notifications/<int:id>/', notifications, name='notifications'),

    path('dashboard/', login_required(CosmicDashboardView.as_view()), name='dashboard'),

]
