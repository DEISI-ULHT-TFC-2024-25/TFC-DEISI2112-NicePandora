from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from shared.models import Contest, Team, Attempt, Test, Classification, Group, Profile

class ContestAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)
        self.contest = Contest.objects.create(
            title="Test Contest",
            short_name="test",
            language="Python"
        )
        self.url = reverse('contest-detail', kwargs={'pk': self.contest.pk})

    def test_get_contest(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Test Contest")
        self.assertEqual(response.data['short_name'], "test")

    def test_update_contest(self):
        data = {
            'title': 'Updated Contest',
            'short_name': 'updated',
            'language': 'Python'
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Updated Contest")
        self.assertEqual(response.data['short_name'], "updated")

class TeamAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)
        self.contest = Contest.objects.create(
            title="Test Contest",
            short_name="test",
            language="Python"
        )
        self.team = Team.objects.create(
            name="test-team",
            contest=self.contest,
            created_by=self.user
        )
        self.url = reverse('team-detail', kwargs={'pk': self.team.pk})

    def test_get_team(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "test-team")

    def test_add_team_member(self):
        new_user = User.objects.create_user(username='newuser', password='12345')
        data = {'user_id': new_user.id}
        response = self.client.post(f"{self.url}/add_member/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.team.hasUser(new_user))

class AttemptAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)
        self.contest = Contest.objects.create(
            title="Test Contest",
            short_name="test",
            language="Python"
        )
        self.team = Team.objects.create(
            name="test-team",
            contest=self.contest,
            created_by=self.user
        )
        self.attempt = Attempt.objects.create(
            contest=self.contest,
            user=self.user,
            team=self.team,
            done=True,
            grade=100
        )
        self.url = reverse('attempt-detail', kwargs={'pk': self.attempt.pk})

    def test_get_attempt(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['grade'], 100)

    def test_get_attempt_classifications(self):
        test = Test.objects.create(
            name="Test Case 1",
            contest=self.contest
        )
        Classification.objects.create(
            attempt=self.attempt,
            test=test,
            passed=True
        )
        response = self.client.get(f"{self.url}/classifications/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class GroupAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)
        self.group = Group.objects.create(
            name="Test Group",
            registration_open=True
        )
        self.url = reverse('group-detail', kwargs={'pk': self.group.pk})

    def test_get_group(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test Group")

    def test_add_group_member(self):
        new_user = User.objects.create_user(username='newuser', password='12345')
        data = {'user_id': new_user.id}
        response = self.client.post(f"{self.url}/add_member/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.group.hasUser(new_user))

class ProfileAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)
        self.profile = Profile.objects.create(
            user=self.user,
            number=1,
            valid=True
        )
        self.url = reverse('profile-detail', kwargs={'pk': self.profile.pk})

    def test_get_profile(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['number'], 1)
        self.assertTrue(response.data['valid'])

    def test_update_profile(self):
        data = {
            'number': 2,
            'valid': False
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['number'], 2)
        self.assertFalse(response.data['valid'])
