from django.test import TestCase
from rest_framework.test import force_authenticate
from django.test.client import encode_multipart, RequestFactory

from rest_framework.test import force_authenticate, APITestCase, APIRequestFactory
from rest_framework.authtoken.models import Token

# Create your tests here.

from rest_framework.test import APITestCase, APIClient

from django.urls import reverse
from rest_framework import status
import requests
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Contest, Team, Attempt, Test, Classification, Group, Profile


class TestListUsers(APITestCase):
	def setUp(self):
		self.factory = APIRequestFactory()
		# If the user must be a superuser use User.objects.create_superuser instead of create_user 
		self.user = User.objects.create_user(username='user', first_name='test', last_name='test', email='user@user.com', password='1234')
		self.admin = User.objects.create_user(username='admin', first_name='admin', last_name='admin', email='admin@admin.com', password='1234', is_superuser=True)
		self.staff = User.objects.create_user(username='staff', first_name='staff', last_name='staff', email='staff@staff.com', password='1234', is_staff=True)

		response = self.client.post(reverse("api_auth"), {'username' : self.user.username, 'password' : '1234'}, format="json")
		self.userToken = response.json()['token']
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		response = self.client.post(reverse("api_auth"), {'username' : self.admin.username, 'password' : '1234'}, format="json")
		self.adminToken = response.json()['token']
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		response = self.client.post(reverse("api_auth"), {'username' : self.staff.username, 'password' : '1234'}, format="json")
		self.staffToken = response.json()['token']
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_unauthenticated_can_not_list_users(self):
		response = self.client.get(reverse("user-list"))
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 

	def test_admin_can_list_users(self):
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.adminToken}")
		response = self.client.get(reverse("user-list"))
		self.assertEqual(response.status_code, status.HTTP_200_OK) 

	def test_staff_can_list_users(self):
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.staffToken}")
		response = self.client.get(reverse("user-list"))
		self.assertEqual(response.status_code, status.HTTP_200_OK)


class ContestModelTest(TestCase):
	def setUp(self):
		self.contest = Contest.objects.create(
			title="Test Contest",
			short_name="test",
			language="Python",
			start_date=timezone.now(),
			end_date=timezone.now() + timedelta(days=1)
		)

	def test_contest_creation(self):
		self.assertEqual(self.contest.title, "Test Contest")
		self.assertEqual(self.contest.short_name, "test")
		self.assertEqual(self.contest.language, "Python")

	def test_contest_is_open(self):
		self.assertTrue(self.contest.isOpen())
		
		# Test closed contest
		self.contest.end_date = timezone.now() - timedelta(days=1)
		self.contest.save()
		self.assertFalse(self.contest.isOpen())

	def test_contest_visibility(self):
		self.assertTrue(self.contest.visible)
		self.contest.visible = False
		self.contest.save()
		self.assertFalse(self.contest.visible)


class TeamModelTest(TestCase):
	def setUp(self):
		self.contest = Contest.objects.create(
			title="Test Contest",
			short_name="test",
			language="Python"
		)
		self.user = User.objects.create_user(username='testuser', password='12345')
		self.team = Team.objects.create(
			name="test-team",
			contest=self.contest,
			created_by=self.user
		)
		self.team.users.add(self.user)

	def test_team_creation(self):
		self.assertEqual(self.team.name, "test-team")
		self.assertEqual(self.team.contest, self.contest)
		self.assertEqual(self.team.created_by, self.user)

	def test_team_membership(self):
		self.assertTrue(self.team.hasUser(self.user))
		self.assertEqual(self.team.getUsers().count(), 1)

	def test_team_size_limits(self):
		self.assertEqual(self.team.getMaxMembers(), 3)  # Default max
		self.contest.max_team_members = 2
		self.contest.save()
		self.assertEqual(self.team.getMaxMembers(), 2)


class AttemptModelTest(TestCase):
	def setUp(self):
		self.contest = Contest.objects.create(
			title="Test Contest",
			short_name="test",
			language="Python"
		)
		self.user = User.objects.create_user(username='testuser', password='12345')
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

	def test_attempt_creation(self):
		self.assertEqual(self.attempt.contest, self.contest)
		self.assertEqual(self.attempt.user, self.user)
		self.assertEqual(self.attempt.team, self.team)
		self.assertTrue(self.attempt.done)
		self.assertEqual(self.attempt.grade, 100)

	def test_attempt_grade(self):
		self.assertEqual(self.attempt.getGrade(), 100)
		self.attempt.grade = None
		self.attempt.save()
		self.assertEqual(self.attempt.getGrade(), 0)


class TestModelTest(TestCase):
	def setUp(self):
		self.contest = Contest.objects.create(
			title="Test Contest",
			short_name="test",
			language="Python"
		)
		self.test = Test.objects.create(
			name="Test Case 1",
			contest=self.contest,
			mandatory=True,
			weight_pct=10
		)

	def test_test_creation(self):
		self.assertEqual(self.test.name, "Test Case 1")
		self.assertEqual(self.test.contest, self.contest)
		self.assertTrue(self.test.mandatory)
		self.assertEqual(self.test.weight_pct, 10)

	def test_test_specifications(self):
		self.assertEqual(self.test.getSpecificationType(), "Python")
		self.assertEqual(self.test.getSpecificationFormType(), "Python_Specification")


class ClassificationModelTest(TestCase):
	def setUp(self):
		self.contest = Contest.objects.create(
			title="Test Contest",
			short_name="test",
			language="Python"
		)
		self.test = Test.objects.create(
			name="Test Case 1",
			contest=self.contest
		)
		self.user = User.objects.create_user(username='testuser', password='12345')
		self.team = Team.objects.create(
			name="test-team",
			contest=self.contest,
			created_by=self.user
		)
		self.attempt = Attempt.objects.create(
			contest=self.contest,
			user=self.user,
			team=self.team
		)
		self.classification = Classification.objects.create(
			attempt=self.attempt,
			test=self.test,
			passed=True,
			execution_time=100,
			memory_usage=50
		)

	def test_classification_creation(self):
		self.assertEqual(self.classification.attempt, self.attempt)
		self.assertEqual(self.classification.test, self.test)
		self.assertTrue(self.classification.passed)
		self.assertEqual(self.classification.execution_time, 100)
		self.assertEqual(self.classification.memory_usage, 50)

	def test_classification_output(self):
		self.assertEqual(self.classification.getOutput(), "")


class GroupModelTest(TestCase):
	def setUp(self):
		self.group = Group.objects.create(
			name="Test Group",
			registration_open=True
		)
		self.user = User.objects.create_user(username='testuser', password='12345')
		self.contest = Contest.objects.create(
			title="Test Contest",
			short_name="test",
			language="Python"
		)
		self.group.users.add(self.user)
		self.group.contests.add(self.contest)

	def test_group_creation(self):
		self.assertEqual(self.group.getName(), "Test Group")
		self.assertTrue(self.group.isRegistrationOpen())
		self.assertTrue(self.group.hasUser(self.user))
		self.assertTrue(self.group.hasContest(self.contest))

	def test_group_registration(self):
		self.group.registration_open = False
		self.group.save()
		self.assertFalse(self.group.isRegistrationOpen())


class ProfileModelTest(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='testuser', password='12345')
		self.profile = Profile.objects.create(
			user=self.user,
			number=1,
			valid=True
		)

	def test_profile_creation(self):
		self.assertEqual(self.profile.user, self.user)
		self.assertEqual(self.profile.number, 1)
		self.assertTrue(self.profile.isValid())

	def test_profile_validation(self):
		self.profile.setValid(False)
		self.profile.save()
		self.assertFalse(self.profile.isValid())

	