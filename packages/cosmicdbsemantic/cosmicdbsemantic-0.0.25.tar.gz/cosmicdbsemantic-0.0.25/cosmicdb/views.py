from django.shortcuts import render, redirect, reverse
from django.views.generic.base import TemplateView
from django.views.generic import FormView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView, \
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth import login
from django.conf import settings   
from django.contrib import messages as django_messages
from django.http import JsonResponse
from django.contrib.auth import get_user_model

from django_tables2 import RequestConfig

from sitetree.sitetreeapp import register_items_hook

from cosmicdb.forms import CosmicAuthenticationForm, CosmicSignupUserForm, CosmicPasswordResetForm, \
    CosmicSetPasswordForm, CosmicChangeEmailForm, CosmicPasswordChangeForm
from cosmicdb.tables import NotificationTable

user_model = get_user_model()


def cosmicdb_items_processor(tree_items, tree_sender):
    if not settings.COSMICDB_ALLOW_SIGNUP:
        for item in tree_items:
            if item.url == 'signup':
                item.hide = True
    return tree_items

register_items_hook(cosmicdb_items_processor)


class CosmicSaveErrorDialogsMixin(object):
    success_message = 'Saved'
    error_message = 'Error'

    def forms_valid(self, form, inlines):
        response = super(CosmicSaveErrorDialogsMixin, self).forms_valid(form, inlines)
        django_messages.success(self.request, self.success_message)
        return response

    def forms_invalid(self, form, inlines):
        response = super(CosmicSaveErrorDialogsMixin, self).forms_invalid(form, inlines)
        django_messages.error(self.request, self.error_message)
        return response

    def form_valid(self, form):
        response = super(CosmicSaveErrorDialogsMixin, self).form_valid(form)
        django_messages.success(self.request, self.success_message)
        return response

    def form_invalid(self, form):
        response = super(CosmicSaveErrorDialogsMixin, self).form_invalid(form)
        django_messages.error(self.request, self.error_message)
        return response


class CosmicLoginView(LoginView):
    template_name = 'cosmicdb/login.html'
    form_class = CosmicAuthenticationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['signup_allowed'] = settings.COSMICDB_ALLOW_SIGNUP
        return context

    def get_redirect_url(self):
        return reverse('dashboard')


class CosmicLogoutView(LogoutView):
    def get_next_page(self):
        return reverse('home')


class CosmicSignupView(FormView):
    form_class = CosmicSignupUserForm
    template_name = 'cosmicdb/signup.html'

    def dispatch(self, request, *args, **kwargs):
        handler = super().dispatch(request, *args, **kwargs)
        if not settings.COSMICDB_ALLOW_SIGNUP:
            return redirect(reverse('home'))
        return handler

    def get_success_url(self):
        return reverse('dashboard')

    def form_valid(self, form):
        new_user = user_model.objects.create_user(**form.cleaned_data)
        login(self.request, new_user)
        return super().form_valid(form)


class CosmicPasswordChangeView(PasswordChangeView):
    template_name = 'cosmicdb/base_form.html'
    form_class = CosmicPasswordChangeForm


class CosmicPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'cosmicdb/password_change_done.html'


class CosmicPasswordResetView(PasswordResetView):
    template_name = 'cosmicdb/password_reset_form.html'
    email_template_name = 'cosmicdb/password_reset_email.html'
    subject_template_name = 'cosmicdb/password_reset_subject.txt'
    form_class = CosmicPasswordResetForm


class CosmicPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'cosmicdb/password_reset_done.html'


class CosmicPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'cosmicdb/password_reset_confirm.html'
    form_class = CosmicSetPasswordForm

    def dispatch(self, *args, **kwargs):
        self.uidb64 = kwargs['uidb64']
        self.token = kwargs['token']
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['uidb64'] = self.uidb64
        context['token'] = self.token
        return context


class CosmicPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'cosmicdb/password_reset_complete.html'


class CosmicChangeEmail(CosmicSaveErrorDialogsMixin, FormView):
    template_name = 'cosmicdb/base_form.html'
    form_class = CosmicChangeEmailForm

    def get_success_url(self):
        return reverse('email_change')

    def form_valid(self, form):
        response = super(CosmicChangeEmail, self).form_valid(form)
        email = form.cleaned_data["email"]
        self.request.user.email = email
        self.request.user.save()
        return response

    def get_form_kwargs(self):
        form_kwargs = super(CosmicChangeEmail, self).get_form_kwargs()
        form_kwargs['request'] = self.request
        return form_kwargs


def notifications(request, id = None):
    if not request.user.is_authenticated:
        return redirect(reverse('home'))
    if id is None:
        notifications = request.user.usersystemnotification_set.order_by('-created_at')
        table = NotificationTable(notifications)
        RequestConfig(request, paginate={'per_page': 10}).configure(table)
        return render(request, 'cosmicdb/base_table.html', {'table': table})
    else:
        notification = request.user.usersystemnotification_set.get(id=id)
        notification.read = True
        notification.save()
        return render(request, 'cosmicdb/notification.html', {'notification': notification})


class CosmicHomeView(TemplateView):
    template_name = 'cosmicdb/home.html'


class CosmicDashboardView(TemplateView):
    template_name = 'cosmicdb/dashboard.html'


class CosmicAutocomplete(TemplateView):
    def get(self, request, *args, **kwargs):
        response = {}
        results = []
        for record in self.get_queryset():
            results.append({'name': self.get_result_name(record), 'value': self.get_result_value(record)})
        response['results'] = results
        response['success'] = True
        return JsonResponse(response)

    def get_result_name(self, record):
        return str(record)

    def get_result_value(self, record):
        return record.pk

    def get_queryset(self):
        return self.get_model().objects.all()

    def get_model(self):
        return self.model

