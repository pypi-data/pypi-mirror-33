
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


class LoginForm(AuthenticationForm):

    remember = forms.BooleanField(label=_("Remember Me"), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = _('Login')


class SignupForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True

    def clean_email(self):
        email = self.cleaned_data['email']

        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError(_('This email is already taken'))

        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        user.is_active = False

        if commit:
            user.save()

        return user

    class Meta(UserCreationForm.Meta):
        fields = ['username', 'email']


class UserChangeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)

        profile = getattr(self.instance, 'profile', None)

        mobile = profile.mobile if profile is not None else ''
        address = profile.address if profile is not None else ''

        self.fields['mobile'] = forms.CharField(
            label=_("Mobile"), required=False, initial=mobile)

        self.fields['address'] = forms.CharField(
            label=_("Address"), required=False, initial=address)

    def save(self, commit=True):

        user = super(UserChangeForm, self).save()

        profile = user.profile

        profile.mobile = self.cleaned_data.get('mobile', '')
        profile.address = self.cleaned_data.get('address', '')
        profile.save()

        return user

    class Meta:
        model = User
        fields = ('first_name', 'last_name', )


class ConfirmPasswordForm(forms.Form):

    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):

        super(ConfirmPasswordForm, self).__init__(*args, **kwargs)

        self.user = user

    def clean_password(self):

        password = self.cleaned_data['password']

        if not self.user.check_password(password):
            raise forms.ValidationError(
                _("The entered password is not valid!"))

        return password
