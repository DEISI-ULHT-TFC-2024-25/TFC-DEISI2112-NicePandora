import base64
import os
import zipfile

from django import forms
from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import transaction

from shared.utils import print_variables_debug
from .models import Attempt, Team, Contest, Test, Profile, Group, C_Specification, TeamContestDateException, \
    Java_Specification, Python_Specification
from .routines import extract, unzip


class DateInputWidget(forms.DateTimeInput):
    input_type = 'datetime-local'


class TeamDateExceptionForm(forms.ModelForm):
    class Meta:
        model=TeamContestDateException
        fields = ['valid_until']

    def submit(self, team):
        if not team:
            return
        # If a null valid_until value is being saved to an existing
        # date exception, delete it.
        if self.instance.id and not self.data.get('valid_until'):
            self.instance.delete()
            return
        if self.is_valid():
            tdef = self.save(commit=False)
            tdef.team = team
            tdef.save()


class AttemptModelForm(forms.ModelForm):
    comment = forms.CharField(required=False)
    class Meta:
        model = Attempt
        fields = ['file', 'comment']

    def submit(self, user, can_submit, contest, team):
        if can_submit and self.is_valid():
            MAX_UPLOAD_SIZE = 10 * 1024 * 1024
            file = self.cleaned_data['file']
            content_type = file.content_type.split('/')[0]
            if file.size > MAX_UPLOAD_SIZE:
                self.add_error('file', 'File size must be under 10mb.')
                return False, None
            obj = self.save(commit=False)
            obj.user = user
            obj.contest = contest
            obj.team = team
            obj.save()
            extract(obj.file)
            print_variables_debug([
                "Object: " + str(obj),
                "Object file: " + str(obj.file),
                "Object file path: " + str(obj.file.path),
                "Contest object: " + str(contest)
            ])
            return True, obj
        return False, None


class CreateMassTestsForm(forms.Form):
    file = forms.FileField()

    def submit(self, contest, file):
        zip_file = file
        processed_files = []
        valid_extensions = ['in', 'out']
        with zipfile.ZipFile(zip_file, 'r') as z:
            nfiles=0
            for file in z.namelist():
                if file.split('.')[-1] == "in":
                    nfiles +=1

            for f in z.namelist():
                for f2 in z.namelist():
                    fname, fextension = f.split('.')[0], f.split('.')[-1]
                    f2name, f2extension = f2.split('.')[0], f2.split('.')[-1]
                    if fname == f2name:
                        if fname not in processed_files:
                            if fextension != f2extension:
                                if fextension in valid_extensions and f2extension in valid_extensions:
                                    test = Test()
                                    test.contest = contest
                                    test.name = fname
                                    test.weight_pct = round(100/nfiles, 2)
                                    # TODO: MAKE THIS ATOMIC
                                    test.save()
                                    if fextension == 'in':
                                        input_file = ContentFile(z.read(f).decode())
                                        output_file = ContentFile(z.read(f2).decode())
                                    else:
                                        input_file = ContentFile(z.read(f2).decode())
                                        output_file = ContentFile(z.read(f).decode())
                                    test.input_file.save('test.in', input_file)
                                    test.output_file.save('test.out', output_file)
                                    processed_files.append(fname)



class TestModelForm(forms.ModelForm):
    override_default_specifications = forms.BooleanField(required=False, initial=False,
                                                         label='Override contest programming language specifications?')

    class Meta:
        model = Test
        exclude = ['contest']

    def submit(self, contest):
        """
            returns (formSaved, overrideSpecs, test)
            If override specs is true redirect to the specs creation page
        """
        if self.is_valid():
            override_specs = False
            if 'override_default_specifications' in self.data:
                override_specs = True
            test = self.save(commit=False)
            test.contest = contest
            test.save()
            return True, override_specs, test
        return False, False, None


class C_SpecificationModelForm(forms.ModelForm):
    class Meta:
        model = C_Specification
        exclude = ['contest', 'test']

    # fields = "__all__"

    def submit(self, obj):

        if not self.is_valid() or not obj:
            return False

        spec = self.save(commit=False)
        # spec.contest = None
        # spec.test = None
        if type(obj) == Contest:
            spec.contest = obj
        elif type(obj) == Test:
            spec.test = obj
        else:
            return False
        spec.save()
        return True

class Java_SpecificationModelForm(forms.ModelForm):
    class Meta:
        model = Java_Specification
        exclude = ['contest', 'test']

    # fields = "__all__"

    def submit(self, obj):

        if not self.is_valid() or not obj:
            return False

        spec = self.save(commit=False)
        if type(obj) == Contest:
            spec.contest = obj
        elif type(obj) == Test:
            spec.test = obj
        else:
            return False
        spec.save()
        return True


class Python_SpecificationModelForm(forms.ModelForm):
    class Meta:
        model = Python_Specification
        exclude = ['contest', 'test']

    # fields = "__all__"

    def submit(self, obj):

        if not self.is_valid() or not obj:
            return False

        spec = self.save(commit=False)
        if type(obj) == Contest:
            spec.contest = obj
        elif type(obj) == Test:
            spec.test = obj
        else:
            return False
        spec.save()
        return True



class ContestModelForm(forms.ModelForm):
    start_date = forms.CharField(required=True)
    end_date = forms.CharField(required=True)

    class Meta:
        model = Contest
        # widgets = {'start_date': DateInputWidget(), 'end_date': DateInputWidget()}
        fields = "__all__"

    def submit(self, contest_id=0):
        if self.is_valid():
            # Saves the contest and creates a new default
            # specification for the contest.
            # TODO: Maybe make this atomic
            contest = self.save(commit=False)
            contest.save()
            print(contest_id)
            if contest_id == 0:
                print('creating specs')
                spec_type = contest.getSpecificationType()
                specs = spec_type()
                specs.contest = contest
                specs.save()
            return True
        return False


class UserModelForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name'] # Adicionar campo Gemini Key aqui


class ProfileModelForm(forms.ModelForm):
    number = forms.IntegerField(required=True, label='Student Number')
    gprd = forms.BooleanField(required=True, initial=False,
                              label='Agree to share my information (name, email, number, username, grade) with the authors and other users of this application')
    gemini_key = forms.CharField(required=False, label='Gemini API Key', 
                               help_text='Optional: Enter your Gemini API key if you want to use AI features')

    class Meta:
        model = Profile
        fields = ['number', 'gprd', 'gemini_key']


class AdminUserModelForm(forms.ModelForm):
    is_active = forms.BooleanField(required=False, label="Is Active")
    is_staff = forms.BooleanField(required=False, label="Is Staff")
    is_superuser = forms.BooleanField(required=False, label="Is Super User")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser']

    def submit(self):
        if not self.is_valid():
            return False

        user = self.save(commit=False)
        user.save()
        return True, user


class AdminUserProfileModelForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['number', 'gprd', 'valid', 'gemini_key']

    def submit(self):
        if not self.is_valid():
            return False

        self.save(commit=False)
        self.save()
        return True


class TeamMemberApprovalForm(forms.Form):
    member_id = forms.CharField(required=False)
    member_id_remove = forms.CharField(required=False)
    team_remove = forms.CharField(required=False)


class TeamJoinForm(forms.Form):
    join_code = forms.SlugField(required=True, label='Code')

    def submit(self, user, contest):
        if not self.is_valid():
            return False
        team = Team.objects.filter(join_code=self.data['join_code'], contest=contest).first()
        if not team:
            self.add_error('join_code', 'There is no team with this join_code in this contest.')
            return False
        if team.hasUser(user):
            self.add_error('join_code', 'You already belong to this team.')
            return False
        if team.isFull():
            self.add_error('join_code', 'This team is full.')
        team.users.add(user)
        team.save()
        return True


class TeamModelForm(forms.ModelForm):
    name = forms.CharField(required=True, label='Team Name')
    join_code = forms.SlugField(required=True, label='Join code')

    class Meta:
        model = Team
        fields = ['name', 'join_code']

    def submit(self, user, contest):
        if not self.is_valid():
            return False

        # Check if the team name is already in use
        team = Team.objects.filter(name=self.data['name'], contest=contest).exists()
        if team:
            self.add_error('name', 'The name you entered is already in use by other team')
            return False
        # Check if the team join code is already in use
        team = Team.objects.filter(join_code=self.data['join_code'], contest=contest).exists()
        if team:
            self.add_error('join_code', 'The code you entered is already in use by other team.')
            return False
        
        team = Team.objects.create(name = self.data['name'], join_code=self.data['join_code'], contest = contest, created_by = user)
        team.contest = contest
        team.save()
        team.users.add(user)
        return True


class AdminTeamCreateForm(forms.ModelForm):
    name = forms.CharField(required=True, label='Team Name')
    join_code = forms.SlugField(required=True, label='Join code')
    include_user = forms.BooleanField(required=False, label='Include me on team')

    class Meta:
        model = Team
        fields = ['name', 'join_code']

    def submit(self, user, contest):
        if not self.is_valid():
            return False

        # Check if the team name is already in use
        team = Team.objects.filter(name=self.data['name'], contest=contest).exists()
        if team:
            self.add_error('name', 'The name you entered is already in use by other team')
            return False
        # Check if the team join code is already in use
        team = Team.objects.filter(join_code=self.data['join_code'], contest=contest).exists()
        if team:
            self.add_error('join_code', 'The code you entered is already in use by other team.')
            return False
        team = self.save(commit=False)
        team.contest = contest
        team.save()
        if self.data.get("include_user"):
            team.users.add(user)
        return True


class TestForm(forms.Form):
    pass


class TestListEditForm(forms.Form):

    def submit(self, request, contest_tests):
        with transaction.atomic():
            mandatory_ids = request.POST.getlist('mandatory')
            contest_tests.filter(pk__in=mandatory_ids).update(mandatory=True)
            contest_tests.exclude(pk__in=mandatory_ids).update(mandatory=False)
            view_error_ids = request.POST.getlist('view_error')
            contest_tests.filter(pk__in=view_error_ids).update(view_error=True)
            contest_tests.exclude(pk__in=view_error_ids).update(view_error=False)
            view_args_ids = request.POST.getlist('view_args')
            contest_tests.filter(pk__in=view_args_ids).update(view_args=True)
            contest_tests.exclude(pk__in=view_args_ids).update(view_args=False)
            view_input_ids = request.POST.getlist('view_input')
            contest_tests.filter(pk__in=view_input_ids).update(view_input=True)
            contest_tests.exclude(pk__in=view_input_ids).update(view_input=False)
            view_diff_ids = request.POST.getlist('view_diff')
            contest_tests.filter(pk__in=view_diff_ids).update(view_diff=True)
            contest_tests.exclude(pk__in=view_diff_ids).update(view_diff=False)

            weight_pct_list = request.POST.getlist('weight_pct')
            name_list = request.POST.getlist('name')
            run_args_list = request.POST.getlist('run_arguments')
            idx = 0
            for t in contest_tests:
                if idx < len(weight_pct_list):
                    t.weight_pct = weight_pct_list[idx]
                    t.name = name_list[idx]
                    t.run_arguments = run_args_list[idx]
                idx = idx + 1
                t.save()


class GroupModelForm(forms.ModelForm):
    name = forms.CharField(required=True, label='Group Name')
    join_code = forms.SlugField(required=True, label='Join code')
    registration_open = forms.BooleanField(required=False, label='Open registration?')

    # TODO: Find a way to make these checkbox selects scrollable
    # contests = forms.ModelMultipleChoiceField(required=False, label='Contests', queryset=Contest.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Group
        fields = ['name', 'join_code', 'registration_open']


class GroupJoinForm(forms.Form):
    join_code = forms.SlugField(required=True, label='Code')

    def submit(self, user):
        if not self.is_valid():
            return False
        group = Group.objects.filter(join_code=self.data['join_code']).first()
        if not group:
            self.add_error('join_code', 'There is no group with this join_code.')
            return False
        if not group.registration_open:
            self.add_error('join_code', 'Registration for this group is closed.')
            return False
        if group.hasUser(user):
            self.add_error('join_code', 'You already belong to this group.')
            return False
        group.users.add(user)
        group.save()
        return True


# CUSTOM FIELDS

class ContestsModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, contest):
        return contest.short_name


class UsersModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, user):
        return "" + user.first_name + " " + user.last_name


class UserRegisterForm(forms.ModelForm):
    first_name = forms.CharField(required=True, label='First name')
    last_name = forms.CharField(required=True, label='Last name')
    email = forms.EmailField(required=True, label='Email address')
    password = forms.CharField(widget=forms.PasswordInput(), required=True, label='Password')

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']

    def submit(self):
        if not self.is_valid():
            return False

        # Checks if there is no user with same username
        if User.objects.filter(username=self.data["email"]).exists():
            self.add_error('email', 'There is already a user with this email.')
            return False, None

        # Checks if there is no user with same email address
        if User.objects.filter(email=self.data["email"]).exists():
            self.add_error('email', 'There is already a user with this email.')
            return False, None

        user = self.save(commit=False)
        user.set_password(user.password)
        user.username = user.email
        user.is_active = True
        user.is_superuser = False
        user.is_staff = False
        user.save()
        new_user = User.objects.get(username=user.username)
        return True, new_user


class ProfileRegisterForm(forms.ModelForm):
    number = forms.IntegerField(required=True, label='Student Number')
    gprd = forms.BooleanField(required=True, initial=False,
                              label='Agree to share my information (name, email, number, username, grade) with the authors and other users of this application')

    class Meta:
        model = Profile
        fields = ['number', 'gprd']

    def submit(self):
        if not self.is_valid():
            return False

        profile = self.save(commit=False)
        profile.save()
        return True


class TeamMemberForm(object):
    pass


class GroupAddUserForm(forms.Form):
    def submit(self, group):
        action = self.data.get("action")
        if action:
            for user_id in self.data.getlist("user_id"):
                user = User.objects.get(id=user_id)
                if action == "adduser":
                    group.users.add(user)
                if action == "removeuser":
                    group.users.remove(user)


class GroupAddContestForm(forms.Form):
    def submit(self, group):
        action = self.data.get("action")
        if action:
            for contest_id in self.data.getlist("contest_id"):
                contest = Contest.objects.get(id=contest_id)
                if action == "addcontest":
                    group.contests.add(contest)
                if action == "removecontest":
                    group.contests.remove(contest)


class UserListForm(forms.Form):
    def submit(self):
        action = self.data.get("action")
        if action:
            for user_id in self.data.getlist("user_id"):
                user = User.objects.get(id=user_id)
                if action == "validate":
                    user.profile.setValid(True)
                if action == "invalidate":
                    user.profile.setValid(False)
                user.save()


class AdminTeamManagerForm(forms.Form):
    def submit(self, team):
        action = self.data.get("action")
        if action:
            for user_id in self.data.getlist("user_id"):
                user = User.objects.get(id=user_id)
                if action == "adduser":
                    if not team.isFull():
                        team.users.add(user)
                if action == "removeuser":
                    team.users.remove(user)


class AdminTeamEditForm(forms.ModelForm):
    name = forms.CharField(required=True, label='Team Name')
    join_code = forms.SlugField(required=True, label='Join code')

    class Meta:
        model = Team
        fields = ['name', 'join_code']

    def submit(self, user, contest):
        if not self.is_valid():
            return False

        # Check if the team name is already in use
        team = Team.objects.exclude(id=self.instance.getId()).filter(name=self.data['name'], contest=contest).exists()
        if team:
            self.add_error('name', 'The name you entered is already in use by other team')
            return False
        # Check if the team join code is already in use
        team = Team.objects.exclude(id=self.instance.getId()).filter(join_code=self.data['join_code'],
                                                                     contest=contest).exists()
        if team:
            self.add_error('join_code', 'The code you entered is already in use by other team.')
            return False
        team = self.save(commit=False)
        team.contest = contest
        team.save()
        return True
