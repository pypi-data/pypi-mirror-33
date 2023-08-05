from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth import password_validation
from django.utils.html import format_html

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from cosmicdb.models import CosmicUser


class CosmicFormHelper(FormHelper):
    def __init__(self, form=None, save_button=True, save_button_value='Save', save_button_name='save', save_button_extra_css=''):
        super().__init__(form)
        if save_button:
            self.add_input(Submit(save_button_name, save_button_value, css_class='ui submit button large primary'+save_button_extra_css))


class CosmicFormsetHelper(FormHelper):
    template = 'semanticui/table_inline_formset.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_tag = False


class CosmicAuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=None, *args, **kwargs)
        self.helper = CosmicFormHelper(save_button_value='Login', save_button_name='login', save_button_extra_css=' fluid ')


class CosmicSignupUserForm(forms.ModelForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if CosmicUser.objects.filter(email=email).count() > 0:
            raise forms.ValidationError('This email is in use.')
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) < 5:
            raise forms.ValidationError('Username must be 5 or more characters.')
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        self.instance.username = self.cleaned_data.get('username')
        password_validation.validate_password(password, self.instance)
        return password

    def __init__(self, *args, **kwargs):
        super(CosmicSignupUserForm, self).__init__(*args, **kwargs)
        self.fields['password'].widget = forms.PasswordInput()
        self.fields['email'].required = True
        self.helper = CosmicFormHelper(self, save_button_value='Create account', save_button_name='login', save_button_extra_css=' fluid ')

    class Meta:
        model = CosmicUser
        fields = ('username', 'email', 'password')
        help_items = [format_html('<li>{}</li>', help_text) for help_text in password_validation.password_validators_help_texts()]
        help_text_html = '<ul class="help-block">%s</ul>' % ''.join(help_items)
        help_texts = {
            'password': help_text_html,
        }


class CosmicPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = CosmicFormHelper(self, save_button_value='Reset my password', save_button_name='reset_pw', save_button_extra_css=' fluid ')


class CosmicSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = CosmicFormHelper(self, save_button_value='Reset my password', save_button_name='reset_pw', save_button_extra_css=' fluid ')


class CosmicChangeEmailForm(forms.Form):
    email = forms.EmailField(label="New email")

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CosmicChangeEmailForm, self).__init__(*args, **kwargs)
        self.fields['email'].initial = self.request.user.email
        self.helper = CosmicFormHelper(self, save_button_value='Change email')

    def clean_email(self):
        email = self.cleaned_data.get("email")
        check_email_exists_qs = CosmicUser.objects.filter(email=email)
        if email == self.request.user.email:
            raise forms.ValidationError("Email address entered is the same as your current email address.")
        if check_email_exists_qs.count() >= 1:
            raise forms.ValidationError("Email address is already in use.")
        return email


class CosmicPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(CosmicPasswordChangeForm, self).__init__(*args, **kwargs)
        self.helper = CosmicFormHelper(self, save_button_value='Change password')

