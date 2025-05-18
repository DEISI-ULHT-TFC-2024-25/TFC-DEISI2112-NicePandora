from rest_framework import serializers
from rest_framework.reverse import reverse
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import PermissionDenied


from api.serializers import UserPublicSerializer
from django.contrib.auth.models import User
from shared.models import Group, Team


from .models import Contest, Profile
from . import validators

######################## Contest Serializers ########################

class ContestInlineSerializer(serializers.Serializer):
	url = serializers.HyperlinkedIdentityField(
		view_name='contest-detail',
		lookup_field='pk',
		read_only=True
	)


class ContestSerializer(serializers.ModelSerializer):
	#    owner = UserPublicSerializer(source='user', read_only=True)
	class Meta:
		model = Contest
		fields = '__all__'



######################## User Serializers ########################


class ProfileSerializer(serializers.ModelSerializer):
	groups = serializers.SerializerMethodField()
	teams = serializers.SerializerMethodField()
	number = serializers.IntegerField(required=False, default=0)
	valid = serializers.BooleanField(required=False, default=False)
	gemini_key = serializers.CharField(required=False, allow_blank=True)

	def get_groups(self, obj):
		return GroupSerializer(obj.groups(), many=True).data

	def get_teams(self, obj):
		return TeamSerializer(obj.teams(), many=True).data

	class Meta:
		model = Profile
		fields = ['number', 'valid', 'groups', 'teams', 'gemini_key']


class UserSerializer(serializers.ModelSerializer):
	profile = ProfileSerializer(required=False, many=False)

	password = serializers.CharField(
		write_only=True,
		required=True,
		help_text='Leave empty if no change needed',
		style={'input_type': 'password', 'placeholder': 'Password'}
	)

	email = serializers.EmailField(required=True, allow_blank=False)
	first_name = serializers.CharField(required=False, default="")
	last_name = serializers.CharField(required=False, default="")
	is_superuser = serializers.BooleanField(required=False, default=False)
	is_staff = serializers.BooleanField(required=False, default=False)
	is_active = serializers.BooleanField(required=False, default=True)

	class Meta:
		model = User
		fields = ('id', 'username', 'email', 'password', 'first_name',
					'last_name', 'is_superuser', 'is_staff', 'is_active', 'last_login', 'date_joined', 'profile')

		read_only_fields = ('id', 'last_login', 'date_joined')


	def create(self, validated_data):
		"""Create and return a new user"""
		userInstance = User.objects.create(email=validated_data['email'],
											username=validated_data['username'],
											first_name=validated_data['first_name'],
											last_name=validated_data['last_name'],
											is_active=True
											)
		userInstance.set_password(validated_data['password'])
		userInstance.save()
	
		try:
			profile_data = validated_data.pop('profile')
			profile = Profile.objects.get(user=userInstance)

			if 'number' in profile_data:
				profile.number = profile_data['number']

			user = self.context.get('request').user
			if (user.is_superuser or user.is_staff):
				if 'valid' in profile_data:
					profile.valid = profile_data['valid']
			profile.save()
		except:
			pass
		return User.objects.get(id=userInstance.id)

	def update(self, instance, validated_data):
		if 'email' in validated_data:
			instance.email = validated_data['email']
		if 'first_name' in validated_data:
			instance.first_name = validated_data['first_name']
		if 'last_name' in validated_data:
			instance.last_name = validated_data['last_name']

		user = self.context.get('request').user
		if (user.is_superuser):
			if 'is_superuser' in validated_data:
				instance.is_superuser = validated_data['is_superuser']

		if (user.is_superuser or user.is_staff):
			if 'is_staff' in validated_data:
				instance.is_staff = validated_data['is_staff']
			if 'is_active' in validated_data:
				instance.is_active = validated_data['is_active']


		try:
			instance.set_password(validated_data['password'])
		except KeyError:
			pass

		try:
			profile_data = validated_data.pop('profile')
			profile = Profile.objects.get(user=instance)

			if 'number' in profile_data:
				profile.number = profile_data['number']

			if (user.is_superuser or user.is_staff) and 'valid' in profile_data:
				profile.valid = profile_data['valid']

			profile.save()
		except:
			pass		

		instance.save()
		return instance

######################## Group Serializers ########################

class GroupSerializer(serializers.ModelSerializer):
	class Meta:
		model = Group
		fields = ['id', 'name']

class GroupAdminSerializer(serializers.ModelSerializer):
	join_code = serializers.SlugField(required=False)
	registration_open = serializers.BooleanField(required=False, default=False)

	class Meta:
		model = Group
		fields = ['id', 'name', 'join_code', 'registration_open']
		read_only_fields = ['id']


class GroupAdminDetailSerializer(serializers.ModelSerializer):
	join_code = serializers.SlugField(required=False)
	registration_open = serializers.BooleanField(required=False, default=False)
	contests = serializers.SerializerMethodField()
	users = serializers.SerializerMethodField()

	def get_contests(self, obj):
		return obj.getContests().values_list('id', flat=True)

	def get_users(self, obj):
		return obj.getUsers().values_list('id', flat=True)

	class Meta:
		model = Group
		fields = ['id', 'name', 'join_code', 'registration_open', 'contests', 'users']
		read_only_fields = ['id']

	@transaction.atomic
	def update(self, instance, validated_data):
		for attr, value in validated_data.items():
			setattr(instance, attr, value)

		if "users" in self.initial_data:
			for user_id in self.initial_data["users"]:
				user_obj = get_object_or_404(User, id=user_id)
				if not instance.hasUser(user=user_obj):
					instance.users.add(user_obj)
		
		if "remove_users" in self.initial_data:
			for user_id in self.initial_data["remove_users"]:
				user_obj = get_object_or_404(User, id=user_id)
				if instance.hasUser(user=user_obj):
					instance.users.remove(user_obj)

		if "contests" in self.initial_data:
			for contest_id in self.initial_data["contests"]:
				contest_obj = get_object_or_404(Contest, id=contest_id)
				if not instance.hasContest(contest=contest_obj):
					instance.contests.add(contest_obj)
		
		if "remove_contests" in self.initial_data:
			for contest_id in self.initial_data["remove_contests"]:
				contest_obj = get_object_or_404(Contest, id=contest_id)
				if instance.hasContest(contest=contest_obj):
					instance.contests.remove(contest_obj)

		instance.save()		
		return instance	


######################## Team Serializers ########################


class TeamSerializer(serializers.ModelSerializer):
	class Meta:
		model = Team
		fields = '__all__'


class TeamJoinSerializer(serializers.ModelSerializer):
	class Meta:
		model = Team
		fields = ['id', 'join_code']
		read_only_fields = ['id', 'join_code']

class TeamUpdateSerializer(serializers.ModelSerializer):
	users = serializers.SerializerMethodField()

	def get_users(self, obj):
		return obj.getUsers().values_list('id', flat=True)

	class Meta:
		model = Team
		fields = ['id', 'name', 'join_code', 'users', 'created_by']
		read_only_fields = ['id', 'join_code', 'contest', 'created_by']



class TeamCreateSerializer(serializers.ModelSerializer):
	contest = serializers.SerializerMethodField()

	def get_contest(self, obj):
		return obj.contest.id

	class Meta:
		model = Team
		fields = ['id', 'name', 'join_code', 'contest',]
		read_only_fields = ['id', 'join_code']


	# def create(self, validated_data):
	# #	"""Create and return a new team"""
	# #	print(dir(self.request))
	# 	contest_obj = get_object_or_404(Contest, pk=validated_data['contest'])
	# 	return None
	# 	user = self.request.user

	# 	if not contest_obj.hasUser(user=user): # does not have access to group where contest is
	# 		raise PermissionDenied()

	# 	if contest_obj.getUserTeam(user=user): # already has a team
	# 		raise PermissionDenied()

	# 	teamInstance = Team.objects.create(name=validated_data['name'], contest=contest_obj)
	# 	teamInstance.users.add(user)
	# 	teamInstance.save()
	# 	return teamInstance