from django.shortcuts import render, redirect, reverse
from django.views.generic import TemplateView, RedirectView, FormView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView, \
    PasswordChangeView
from django.contrib import messages as django_messages
from django.contrib.auth import login
from django_tables2 import RequestConfig
from django.contrib.auth import get_user_model

from cosmicdb.forms import CosmicAuthenticationForm, CosmicSignupUserForm, CosmicPasswordResetForm, \
    CosmicSetPasswordForm, CosmicPasswordChangeForm, CosmicChangeEmailForm
from cosmicdb.tables import NotificationTable, MessageTable

user_model = get_user_model()

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
    form_class = CosmicAuthenticationForm

    def get_success_url(self):
        return reverse('dashboard')


class CosmicSignupView(FormView):
    form_class = CosmicSignupUserForm
    template_name = 'cosmicdb/signup.html'

    def get_success_url(self):
        return reverse('dashboard')

    def form_valid(self, form):
        new_user = user_model.objects.create_user(**form.cleaned_data)
        login(self.request, new_user)
        return super(CosmicSignupView, self).form_valid(form)


class CosmicPasswordResetView(PasswordResetView):
    form_class = CosmicPasswordResetForm


class CosmicPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CosmicSetPasswordForm


class CosmicPasswordChangeView(PasswordChangeView):
    form_class = CosmicPasswordChangeForm


class Home(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('dashboard')


class Dashboard(TemplateView):
    template_name = 'cosmicdb/dashboard.html'


def notifications(request, id = None):
    if not request.user.is_authenticated:
        return redirect(reverse('home'))
    if id is None:
        notifications = request.user.usersystemnotification_set.order_by('-created_at')
        table = NotificationTable(notifications)
        RequestConfig(request, paginate={'per_page': 10}).configure(table)
        return render(request, 'cosmicdb/notifications_all.html', {'table': table})
    else:
        notification = request.user.usersystemnotification_set.get(id=id)
        notification.read = True
        notification.save()
        return render(request, 'cosmicdb/notifications_single.html', {'notification': notification})


def messages(request, id=None):
    if not request.user.is_authenticated:
        return redirect(reverse('home'))
    if id is None:
        messages = request.user.usersystemmessage_set.order_by('-created_at')
        table = MessageTable(messages)
        RequestConfig(request, paginate={'per_page': 10}).configure(table)
        return render(request, 'cosmicdb/messages_all.html', {'table': table})
    else:
        message = request.user.usersystemmessage_set.get(id=id)
        message.read = True
        message.save()
        return render(request, 'cosmicdb/messages_single.html', {'message': message})


class CosmicChangeEmail(CosmicSaveErrorDialogsMixin, FormView):
    template_name = 'cosmicdb/change_email.html'
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
