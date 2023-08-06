
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import views, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import FormView, CreateView, UpdateView
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from accounts import forms
from accounts.tokens import account_activation_token


class LoginView(views.LoginView):

    form_class = forms.LoginForm
    template_name = 'accounts/login.html'

    def form_valid(self, form):

        request = self.request

        login(request, form.get_user())

        session_age = settings.SESSION_COOKIE_AGE \
            if form.cleaned_data.get('remember') else 0

        request.session.set_expiry(session_age)

        message = _('You have successfully logged in as {}')

        messages.success(request, message.format(request.user.username))

        return redirect(self.get_success_url())


class LogoutView(views.LogoutView):

    def dispatch(self, request, *args, **kwargs):

        messages.success(self.request, _('You have successfully logged out'))

        return super().dispatch(request, *args, **kwargs)


class PasswordResetView(views.PasswordResetView):

    subject_template_name = 'accounts/password-reset-subject.txt'
    email_template_name = 'accounts/password-reset-email.html'
    html_email_template_name = 'accounts/password-reset-email.html'
    template_name = 'accounts/password-reset.html'
    success_url = reverse_lazy('home')
    success_message = _('Password reset link was sent to your email address')

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class PasswordResetConfirmView(views.PasswordResetConfirmView):

    template_name = 'accounts/password-reset-confirm.html'
    success_url = reverse_lazy('home')
    success_message = _('Your password has been changed')

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class SignupView(CreateView):

    model = get_user_model()
    form_class = forms.SignupForm
    success_url = reverse_lazy('home')
    success_message = _('Email confirmation link was sent to your email')
    template_name = 'accounts/signup.html'
    email_template_name = 'accounts/signup-email.html'
    subject_template_name = 'accounts/signup-subject.txt'

    def form_valid(self, form):

        user = form.save(commit=False)
        user.is_active = False
        user.save()

        request = self.request

        domain = get_current_site(request).domain

        subject = render_to_string(self.subject_template_name, {
            'domain': domain,
            'user': user
        })

        activate_url = reverse('accounts:activate', kwargs={
            'uidb64': (
                urlsafe_base64_encode(force_bytes(user.pk)).decode("utf-8")),
            'token': account_activation_token.make_token(user)
        })

        message = render_to_string(self.email_template_name, {
            'user': user,
            'domain': domain,
            'activate_url': request.build_absolute_uri(activate_url)
        })

        user.email_user(subject, '', html_message=message)

        messages.success(self.request, self.success_message)

        return redirect(self.success_url)


class PasswordChangeView(views.PasswordChangeView):

    template_name = 'accounts/password-change.html'
    success_url = reverse_lazy('accounts:profile')

    success_message = _('Your password has been changed')

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


@method_decorator(login_required, "dispatch")
class ProfileChangeView(UpdateView):

    form_class = forms.UserChangeForm
    success_url = reverse_lazy('accounts:profile')
    template_name = 'accounts/profile-change.html'

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _('Profile successfully changed'))
        return super(ProfileChangeView, self).form_valid(form)


@method_decorator(login_required, "dispatch")
class RemoveProfileView(FormView):

    form_class = forms.ConfirmPasswordForm
    success_url = reverse_lazy('home')
    template_name = 'accounts/profile-remove.html'

    def get_form_kwargs(self):
        kwargs = super(RemoveProfileView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        user.is_active = False
        user.save()

        logout(self.request)

        messages.success(self.request, _('Profile successfully removed'))
        return super(RemoveProfileView, self).form_valid(form)


@login_required
def profile(request):
    return render(request, 'accounts/profile.html')


def activate(request, uidb64, token):

    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid, is_active=False)
    except (TypeError, ValueError, OverflowError, ObjectDoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):

        user.is_active = True
        user.save()

        login(request, user)

        messages.success(request, _('Your account is activated'))

        return redirect('accounts:profile')

    messages.error(request, _('Activation link is invalid'))

    return redirect('home')
