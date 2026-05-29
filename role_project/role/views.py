from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from .forms import AdminUserCreationForm, AssignTeamForm, LeaderMemberCreationForm, LoginForm, TeamForm
from .models import CustomUser, Team


def role_required(*allowed_roles):
    """Deny direct URL access unless the logged-in user has an allowed role."""
    def decorator(view_func):
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return dashboard_url_for(self.request.user)


def dashboard_url_for(user):
    if user.role == 'admin':
        return reverse_lazy('admin_dashboard')
    if user.role == 'leader':
        return reverse_lazy('leader_dashboard')
    return reverse_lazy('member_dashboard')


@login_required
def dashboard_redirect(request):
    return redirect(dashboard_url_for(request.user))


@role_required('admin')
def admin_dashboard(request):
    users = CustomUser.objects.select_related('team').order_by('role', 'username')
    teams = Team.objects.all().order_by('name')
    return render(request, 'admin_dashboard.html', {'users': users, 'teams': teams})


@role_required('admin')
def create_team(request):
    form = TeamForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Team created successfully.')
        return redirect('admin_dashboard')
    return render(request, 'team_form.html', {'form': form, 'title': 'Create Team'})


@role_required('admin')
def create_user(request):
    form = AdminUserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'User created successfully.')
        return redirect('admin_dashboard')
    return render(request, 'user_form.html', {'form': form, 'title': 'Create User'})


@role_required('admin')
def assign_team(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    form = AssignTeamForm(request.POST or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Team assignment updated.')
        return redirect('admin_dashboard')
    return render(request, 'user_form.html', {'form': form, 'title': f'Assign Team to {user.username}'})


@role_required('admin', 'leader')
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)

    if request.user.role == 'leader':
        can_delete = (
            request.user.team_id is not None
            and user.role == 'member'
            and user.team_id == request.user.team_id
        )
        if not can_delete:
            raise PermissionDenied

    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'{username} was deleted.')
        if request.user.is_authenticated and request.user.role == 'leader':
            return redirect('leader_dashboard')
        return redirect('admin_dashboard')

    return render(request, 'confirm_delete.html', {'target_user': user})


@role_required('leader')
def leader_dashboard(request):
    members = CustomUser.objects.none()
    if request.user.team_id:
        members = CustomUser.objects.filter(team=request.user.team, role='member').order_by('username')
    return render(request, 'leader_dashboard.html', {'members': members})


@role_required('leader')
def leader_create_member(request):
    if request.user.team_id is None:
        messages.error(request, 'You must be assigned to a team before adding members.')
        return redirect('leader_dashboard')

    form = LeaderMemberCreationForm(request.POST or None, team=request.user.team)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Team member created successfully.')
        return redirect('leader_dashboard')
    return render(request, 'user_form.html', {'form': form, 'title': 'Add Team Member'})


@role_required('member')
def member_dashboard(request):
    return render(request, 'member_dashboard.html', {'profile': request.user})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
