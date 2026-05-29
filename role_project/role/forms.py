from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import CustomUser, Team


class BootstrapFormMixin:
    """Apply Bootstrap classes to Django-generated form fields."""

    def _add_bootstrap_classes(self):
        for field in self.fields.values():
            css_class = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            field.widget.attrs['class'] = css_class


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_bootstrap_classes()


class TeamForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_bootstrap_classes()


class AdminUserCreationForm(BootstrapFormMixin, UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'team', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [
            ('leader', 'Team Leader'),
            ('member', 'Team Member'),
        ]
        self._add_bootstrap_classes()

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        team = cleaned_data.get('team')

        if role in {'leader', 'member'} and team is None:
            self.add_error('team', 'A team is required for leaders and members.')

        return cleaned_data


class LeaderMemberCreationForm(BootstrapFormMixin, UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        self.team = kwargs.pop('team')
        super().__init__(*args, **kwargs)
        self._add_bootstrap_classes()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'member'
        user.team = self.team
        if commit:
            user.save()
        return user


class AssignTeamForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['team']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_bootstrap_classes()

    def clean_team(self):
        team = self.cleaned_data['team']
        if self.instance.role in {'leader', 'member'} and team is None:
            raise forms.ValidationError('Leaders and members must belong to a team.')
        return team
