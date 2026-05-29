from django.test import TestCase
from django.urls import reverse

from .models import CustomUser, Team


class RoleAccessTests(TestCase):
    def setUp(self):
        self.alpha = Team.objects.create(name='Alpha')
        self.beta = Team.objects.create(name='Beta')
        self.admin = CustomUser.objects.create_user(
            username='admin1',
            password='pass12345',
            role='admin',
        )
        self.leader = CustomUser.objects.create_user(
            username='leader1',
            password='pass12345',
            role='leader',
            team=self.alpha,
        )
        self.alpha_member = CustomUser.objects.create_user(
            username='member1',
            password='pass12345',
            role='member',
            team=self.alpha,
        )
        self.beta_member = CustomUser.objects.create_user(
            username='member2',
            password='pass12345',
            role='member',
            team=self.beta,
        )

    def test_admin_dashboard_lists_all_users_and_teams(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse('admin_dashboard'))

        self.assertContains(response, 'Alpha')
        self.assertContains(response, 'Beta')
        self.assertContains(response, 'member1')
        self.assertContains(response, 'member2')

    def test_leader_dashboard_lists_only_own_team_members(self):
        self.client.force_login(self.leader)

        response = self.client.get(reverse('leader_dashboard'))

        self.assertContains(response, 'member1')
        self.assertNotContains(response, 'member2')

    def test_leader_cannot_delete_member_from_other_team(self):
        self.client.force_login(self.leader)

        response = self.client.post(reverse('delete_user', args=[self.beta_member.id]))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(CustomUser.objects.filter(id=self.beta_member.id).exists())

    def test_member_cannot_open_admin_or_leader_dashboards(self):
        self.client.force_login(self.alpha_member)

        admin_response = self.client.get(reverse('admin_dashboard'))
        leader_response = self.client.get(reverse('leader_dashboard'))

        self.assertEqual(admin_response.status_code, 403)
        self.assertEqual(leader_response.status_code, 403)

# Create your tests here.
