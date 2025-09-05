import errno
import os
import time
import uuid

from django.contrib import messages
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from celery.utils.log import get_task_logger


import shared
from .storage import OverwriteStorage
from .validators import validate_file_extension

SUBMISSIONS_ROOT = 'submissions/'
SUBMISSION_RESULTS_ROOT = 'submission_results/'
TESTS_ROOT = 'tests/'
CONTESTS_ROOT = 'contests/'
DATAFILES_ROOT = 'datafiles/'


def get_submissions_file_path(instance, filename):
	ext = filename.split('.')[-1]
	if ext == 'java':
		filename = "Main.%s" % ext
	if ext == 'py':
		filename = "main.%s" % ext        
	else:
		filename = "src.%s" % ext
	return os.path.join(SUBMISSIONS_ROOT, str(instance.id), filename)


def get_tests_path(instance, filename):
	ext = filename.split('.')[-1]
	filename = "test.%s" % ext
	return os.path.join(TESTS_ROOT, str(instance.id), filename)


def get_contest_code_path(instance, filename):
	return os.path.join(CONTESTS_ROOT, str(instance.short_name), 'src/', filename)


def get_data_files_path(instance, filename):
	return os.path.join(DATAFILES_ROOT, str(instance.contest.id), filename)


# TODO: Mark for deletion
def get_contest_detail_path(instance, filename):
	ext = filename.split('.')[-1]
	filename = "sow.%s" % (ext)
	return os.path.join(CONTESTS_ROOT, str(instance.short_name), filename)

# TODO: Mark for deletion
def get_contest_data_path(instance, filename):
	return os.path.join(CONTESTS_ROOT, str(instance.contest.short_name), 'data/', filename)

# TODO: Mark for deletion
def get_contest_ins_files_path(instance, filename):
	return os.path.join(CONTESTS_ROOT, str(instance.short_name), 'src/temp/in', filename)

# TODO: Mark for deletion
def get_contest_outs_files_path(instance, filename):
	return os.path.join(CONTESTS_ROOT, str(instance.short_name), 'src/temp/out', filename)






 Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	number = models.IntegerField(null=True, blank=True)
	gprd = models.BooleanField(nulclassl=True, default=True, blank=True)
	valid = models.BooleanField(null=False, default=False, blank=False)
	gemini_key = models.CharField(max_length=255, null=True, blank=True)


	def __str__(self):  # __unicode__ for Python 2
		return self.user.username

	@classmethod
	def getActiveUsers(cls):
		return cls.objects.filter(valid__exact=True)

	def getUser(self):
		return self.user

	def getNumber(self):
		return self.number

	def isValid(self):
		return self.valid

	def setValid(self, value: bool):
		self.valid = value

	def groups(self):
		return self.user.group_set.all()

	def teams(self):
		return self.user.team_set.all()



@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)
	instance.profile.save()


class Specification(models.Model):
	cpu = models.PositiveIntegerField(default=1)  # <seconds>		Default: 1 second(s)
	mem = models.PositiveIntegerField(default=50, validators=[MinValueValidator(50), MaxValueValidator(
		512)])  # <Mbytes>		Default: 32768 kbyte(s)
	# TODO: Delete these run_args as they are now being placed in the Test model
	run_arguments = models.CharField(max_length=512, null=True, blank=True)
	timeout = models.PositiveIntegerField(default=10)  # <seconds>

	class Meta:
		abstract = True

	def getRunArgs(self):
		return self.run_arguments or ""

	def getCPU(self):
		return self.cpu

	def getMem(self):
		return self.mem

	def getTimeout(self):
		return self.timeout


class Contest(models.Model):
	title = models.CharField(max_length=128)
	short_name = models.CharField(max_length=16, blank=False, unique=True)
	description = models.TextField(null=True, blank=True)
	sow = models.URLField(max_length=200, blank=True)
	# TODO: Obrigar a que o reference_code seja um ZIP
	reference_code = models.FileField(upload_to=get_contest_code_path, blank=True, null=True)
	start_date = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
	end_date = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
	min_team_members = models.PositiveSmallIntegerField(default=1)
	max_team_members = models.PositiveSmallIntegerField(default=3)
	max_classification = models.IntegerField(default=20)
	visible = models.BooleanField(null=False, default=True, blank=False)
	automatic_weight = models.BooleanField(null=False, default=True, blank=False)
	max_submitions = models.PositiveIntegerField(default=0)
	language = models.CharField(max_length=512, null=False, blank=False, choices=[('C', 'C'), ('Java', 'Java'), ('Python', 'Python')])
	archived = models.BooleanField(null=False, default=False, blank=False)
	
	ai_ratings = models.JSONField(default=dict, blank=True)  # Armazena {user_id: {"rating": 1-5, "comment": "texto"}}
	ai_rated_by = models.ManyToManyField(User, related_name='rated_contests', blank=True)  # Usuários que já avaliaram
	blacklist = models.TextField(null=True, blank=True, help_text="Palavras proibidas separadas por vírgula (ex: palavra1,palavra2,palavra3)")
	gemini_responses = models.JSONField(default=dict, blank=True)  # Armazena {test_id: [{"user_input": "...", "response": "...", "timestamp": "...", "has_prohibited_words": true/false, "prohibited_words": ["palavra1", "palavra2", "palavra3"], "user": {"id": "...", "username": "...", "email": "..."}}]}

	@classmethod
	def getContestsForUser(cls, request):
		return cls.objects.filter(group__users__exact=request.user).distinct()

	@classmethod
	def getActiveContests(cls):
		from django.utils import timezone
		return cls.objects.filter(end_date__gt=timezone.now(), start_date__lt=timezone.now())


	@classmethod
	def getByID(cls, contest_id):
		return cls.objects.get(id=contest_id)

	def getUsers(self):
		return Group.objects.get(contests__exact=self).getUsers()

	def hasUser(self, user):
		if self.getUsers().filter(id=user.id).first():
			return True
		return False

	def getLanguage(self):
		return self.language

	def getSpecifications(self):
		try:
			if self.language == 'C':
				return self.c_specifications
			if self.language == 'Java':
				return self.java_specifications
			if self.language == 'Python':
				return self.python_specifications                
		# Catches RelatedObjectNotFound exception
		except Exception:
			return None

	def getSpecificationType(self):
		form_type = self.getSpecificationFormType()
		if form_type:
			return form_type.Meta.model

	def getSpecificationFormType(self):
		# Importing here avoids circular import
		from shared.forms import C_SpecificationModelForm, Java_SpecificationModelForm, Python_SpecificationModelForm
		if self.language == 'C':
			return C_SpecificationModelForm
		if self.language == 'Java':
			return Java_SpecificationModelForm
		if self.language == 'Python':
			return Python_SpecificationModelForm            
		else:
			return None

	def isOpen(self):
		"""Returns true if the contest is on going."""
		from django.utils import timezone
		if self.end_date > timezone.now() > self.start_date:
			return True
		return False

	# objects = ContestManager()
	def getUserTeam(self, user):
		return self.team_set.filter(contest=self, users__exact=user).first()

	def getTestDetails(self):
		return self.cpu, self.mem, self.space, self.minuid, self.maxuid, self.core, self.nproc, self.fsize, self.stack, self.clock

	def getTests(self):
		return self.test_set.all()

	def getTeams(self):
		return self.team_set.all()

	def checkAttempts(self, user):
		team = self.getUserTeam(user)
		if not team:
			return False
		attempts = team.getAttempts()
		if self.max_submitions > 0:
			if attempts and attempts.count() >= self.max_submitions:
				return False
		return True

	def userHasTeam(self, user):
		team = self.getUserTeam(user)
		return not not team

	def getTestsCount(self):
		n = self.getTests().count()
		mandatory = self.getTests().filter(mandatory=True).count()
		diff = n - mandatory
		return n, mandatory, diff

	def getName(self):
		return self.title

	def userHasAccess(self, user):
		return not not self.group_set.filter(users__exact=user)

	def getGroups(self):
		return self.group_set.all()

	def getSubmissions(self):
		return self.attempt_set.all()

	def getSubmissionsLastThirtyDays(self):
		"""
		Returns the submissions of the last 30 days.
		"""
		from datetime import datetime, timedelta
		thirty_days_ago = datetime.today() - timedelta(days=30)
		return self.attempt_set.filter(date__gt=thirty_days_ago)

	def getDescription(self):
		return self.description	



class Test(models.Model):
	name = models.CharField(max_length=512, null=False, blank=True)
	contest = models.ForeignKey(Contest, default=1, null=False, on_delete=models.CASCADE)
	input_file = models.FileField(max_length=512, upload_to=get_tests_path, blank=False, null=False)
	output_file = models.FileField(max_length=512, upload_to=get_tests_path, blank=False, null=False)
	mandatory = models.BooleanField(null=False, default=False)
	weight_pct = models.DecimalField(default=10, null=False, decimal_places=2, max_digits=6)
	run_arguments = models.CharField(max_length=512, null=False, default="", blank=True)

	view_diff = models.BooleanField(null=False, default=True)
	view_input = models.BooleanField(null=False, default=True)
	view_args = models.BooleanField(null=False, default=True)
	view_error = models.BooleanField(null=False, default=True)
	
	description = models.TextField(null=True, blank=True)  # Novo campo opcional
	help_ai = models.BooleanField(null=False, default=True)  # Campo para controlar se o teste tem ajuda AI
	help_difficulty = models.CharField(
		max_length=10,
		choices=[('Fácil', 'Fácil'), ('Médio', 'Médio'), ('Difícil', 'Difícil')],
		default='Médio'
	) 
	gemini_responses = models.JSONField(default=list, blank=True)  # Lista de respostas do Gemini com timestamps

	#type_of_feedback = models.PositiveIntegerField(default=1, null=False, blank=False)

	@classmethod
	def getByID(cls, id):
		return Test.objects.get(id=id)

	def getID(self):
		return self.id

	def save(self, *args, **kwargs):
		if self.id is None:
			saved_in_file = self.input_file
			saved_out_file = self.output_file
			self.input_file = None
			self.output_file = None
			super(Test, self).save(*args, **kwargs)
			self.input_file = saved_in_file
			self.output_file = saved_out_file
		else:
			try:
				this = Test.objects.get(id=self.id)
				if this.input_file != self.input_file:
					this.input_file.delete()
				if this.output_file != self.output_file:
					this.output_file.delete()
			except:
				pass
		super(Test, self).save(*args, **kwargs)

	def getOutFileContent(self):
		from shared.routines import read_file
		return read_file(self.output_file.path)

	def getInFileContent(self):
		from shared.routines import read_file
		return read_file(self.input_file.path)

	def getContestSpecifications(self):
		try:
			if self.contest.language == 'C':
				return self.contest.c_specifications
			if self.contest.language == 'Java':
				return self.contest.java_specifications
			if self.contest.language == 'Python':
				return self.contest.python_specifications                
		# Catches RelatedObjectNotFound exception
		except Exception:
			return None

	def getSpecifications(self):
		try:
			if self.contest.language == 'C':
				return self.c_specifications
			if self.contest.language == 'Java':
				return self.java_specifications
			if self.contest.language == 'Python':
				return self.python_specifications                
		# Catches RelatedObjectNotFound exception
		except Exception:
			return None

	def getExistingSpecifications(self):
		"""
		Returns the test specifications if they exist
		otherwise returns the contest specifications.
		Use with caution.
		"""
		specs = self.getSpecifications()
		if not specs:
			specs = self.getContestSpecifications()
		return specs

	def getSpecificationType(self):
		return self.contest.getSpecificationType()

	def getSpecificationFormType(self):
		return self.contest.getSpecificationFormType()

	def getContest(self):
		return self.contest


	def getRunArgs(self):
		"""
		Returns run_args for this test. Returns an empty string when null.
		"""
		if self.hasRunArgs():
			return self.run_arguments
		return ""

	def hasRunArgs(self):
		return self.run_arguments and self.run_arguments != ""

	def getDetails(self):
		# TODO: Check the minuid and maxuid
		specs = self.getSpecifications()
		return specs.cpu, specs.mem, specs.space, specs.minuid, specs.maxuid, specs.core, specs.nproc, specs.fsize, specs.stack, specs.clock


class C_Specification(Specification):
	contest = models.OneToOneField(Contest, null=True, blank=True, on_delete=models.CASCADE,
								   related_name='c_specifications')
	test = models.OneToOneField(Test, null=True, blank=True, on_delete=models.CASCADE, related_name='c_specifications')

	compile_flags = models.CharField(max_length=120, blank=True, default="-Wall")
	linkage_flags = models.CharField(max_length=120, blank=True, default="-lc")
	fsize = models.PositiveIntegerField(default=8192)  # <kbytes>		Default: 8192 kbyte(s)
	check_leak = models.BooleanField(null=False, default=False)


	class Meta:
		constraints = [
			# This constraint checks if exactly one of either contest or test
			# is filled. Rejects if both are or if none are.
			models.CheckConstraint(
				name="c_specifications_contest_test_one_only_constraint",
				check=models.Q(contest__isnull=False) & models.Q(test__isnull=True) | models.Q(
					contest__isnull=True) & models.Q(test__isnull=False)
			)
		]

	def getFields(self):
		return self._meta.get_fields()

	def getAttribute(self, name):
		return self.__getattribute__(name)


class Java_Specification(Specification):
	contest = models.OneToOneField(Contest, null=True, blank=True, on_delete=models.CASCADE,
								   related_name='java_specifications')
	test = models.OneToOneField(Test, null=True, blank=True, on_delete=models.CASCADE, related_name='java_specifications')

	fsize = models.PositiveIntegerField(default=8192)  # <kbytes>		Default: 8192 kbyte(s)


	class Meta:
		constraints = [
			# This constraint checks if exactly one of either contest or test
			# is filled. Rejects if both are or if none are.
			models.CheckConstraint(
				name="java_specifications_contest_test_one_only_constraint",
				check=models.Q(contest__isnull=False) & models.Q(test__isnull=True) | models.Q(
					contest__isnull=True) & models.Q(test__isnull=False)
			)
		]

	def getFields(self):
		return self._meta.get_fields()

	def getAttribute(self, name):
		return self.__getattribute__(name)


class Python_Specification(Specification):
	contest = models.OneToOneField(Contest, null=True, blank=True, on_delete=models.CASCADE,
								   related_name='python_specifications')
	test = models.OneToOneField(Test, null=True, blank=True, on_delete=models.CASCADE, related_name='python_specifications')

	fsize = models.PositiveIntegerField(default=8192)  # <kbytes>		Default: 8192 kbyte(s)

	class Meta:
		constraints = [
			# This constraint checks if exactly one of either contest or test
			# is filled. Rejects if both are or if none are.
			models.CheckConstraint(
				name="python_specifications_contest_test_one_only_constraint",
				check=models.Q(contest__isnull=False) & models.Q(test__isnull=True) | models.Q(
					contest__isnull=True) & models.Q(test__isnull=False)
			)
		]

	def getFields(self):
		return self._meta.get_fields()

	def getAttribute(self, name):
		return self.__getattribute__(name)



class Team(models.Model):
	name = models.SlugField(max_length=50, blank=False)
	contest = models.ForeignKey(Contest, default=1, null=False, on_delete=models.CASCADE)
	join_code = models.UUIDField(max_length=32, unique=True, default = uuid.uuid1())
	users = models.ManyToManyField(User)
	created_by = models.ForeignKey(User, default=1, null=False, on_delete=models.CASCADE, related_name='team_owner')

	# image  = models.ImageField(upload_to='images/', blank=True, null=True)

	class Meta:
		unique_together = (('contest', 'join_code'), ('contest', 'name'))

	def getId(self):
		return self.id

	def getName(self):
		return self.name

	def getContest(self):
		return self.contest

	def getUsers(self):
		return self.users.all()

	def hasUser(self, user):
		return self.users.filter(id=user.id).exists()

	def getJoinCode(self):
		return self.join_code

	def getDateException(self):
		try:
			return self.teamcontestdateexception
		except:
			return None

	def canSubmit(self):
		from django.utils import timezone
		if self.contest.max_submitions != 0 and self.attempt_set.count() > self.contest.max_submitions:
			print(1)
			return False

		date_exception = self.getDateException()
		if not self.contest.isOpen() and not date_exception:
			print(2)
			return False
		if date_exception and date_exception.valid_until < timezone.now():
			print(3)
			return False
		return True


	def getAttempts(self):
		return Attempt.objects.filter(team=self).order_by('-date')

	def getGreatestGradeAttempt(self):
		return Attempt.objects.filter(team=self).order_by('-grade').first()

	def getLatestAttempt(self):
		return Attempt.objects.filter(team=self).order_by('-id').first()

	def isFull(self):
		return self.users.count() >= self.contest.max_team_members

	def getMaxMembers(self):
		return self.contest.max_team_members

	def cleanupPastAttempts(self, current_attempt):
		import shutil
		from pandora import settings
		attempts_qs = Attempt.objects.filter(team=self).exclude(id=current_attempt.id).order_by('-date')
		print('im going to loop attempts')
		data_path = settings.LOCAL_STATIC_CDN_PATH
		for at in attempts_qs:
			print(os.path.join(data_path, SUBMISSIONS_ROOT, str(at.id)))
			try:
				shutil.rmtree(os.path.join(data_path, SUBMISSIONS_ROOT, str(at.id)))
			except FileNotFoundError:
				pass
			try:
				shutil.rmtree(os.path.join(data_path, SUBMISSION_RESULTS_ROOT, str(at.id)))
			except FileNotFoundError:
				pass
			at.file = None

	def getRanking(self):
		# TODO Make it better
		query = "SELECT att.*, maxs.attempts, maxs.team_id FROM (" \
				"select max(id) as id," \
				"count(id) as attempts," \
				"team_id from " \
				"shared_attempt" \
				" where contest_id = " + str(self.contest.id) + \
				"   group by team_id)" \
				"       maxs inner join shared_attempt att on att.id = maxs.id" \
				"           order by grade desc, attempts asc, time_benchmark asc, memory_benchmark asc, elapsed_time asc," \
				"                       cpu_time asc"
		# select contest_atempt.id as id, max(date), grade, count(contest_atempt.id) as number_of_atempts, time_benchmark, memory_benchmark elapsed_time, cpu_time from contest_atempt where contest_id = " + str(contest_obj.id) + " group by (team_id) order by grade desc, time_benchmark asc, memory_benchmark asc, number_of_atempts asc"
		attempts = Attempt.objects.raw(query)
		rank = 1
		if self:
			for att in attempts:
				if att.team == self:
					return att, rank
		return None, 0

	@classmethod
	def getById(cls, id):
		return cls.objects.get(id=id)


# TODO: Its possible to make this inside the Model?
# get the team attempts
# def getAttempts(self):
#	members_ids = self.teammember_set.values_list('user__id', flat=True).distinct()
#	if not members_ids:
#		return None
#	return Attempt.objects.filter(contest=self.contest, user__in=members_ids).order_by('-date')


class Attempt(models.Model):
	contest = models.ForeignKey(Contest, default=1, null=False, on_delete=models.CASCADE)
	user = models.ForeignKey(User, default=1, null=False, on_delete=models.CASCADE)
	team = models.ForeignKey(Team, default=1, null=True,
							 on_delete=models.SET_NULL)  # this is redundant but it's just easier...
	date = models.DateTimeField(auto_now_add=True, blank=True)
	file = models.FileField(upload_to=get_submissions_file_path, blank=False, null=False, max_length=512,
							validators=[validate_file_extension])
	auto_generated = models.BooleanField(null=False, default=False, blank=False)
	done = models.BooleanField(null=False, default=False)
	comment = models.CharField(null=True, max_length=128, blank=True)
	compile_error = models.BooleanField(null=False, default=False, blank=True)
	failed_mandatory_test = models.BooleanField(null=False, default=False, blank=True)
	error_description = models.TextField(null=True, blank=True)
	grade = models.IntegerField(blank=True, null=True, default=0)
	time_benchmark = models.IntegerField(blank=True, null=True, default=0)
	memory_benchmark = models.IntegerField(blank=True, null=True, default=0)
	elapsed_time = models.IntegerField(blank=True, null=True, default=0)
	cpu_time = models.DecimalField(blank=True, null=True, decimal_places=3, max_digits=8)
	static_analysis = models.TextField(blank=True, null=True)

	def save(self, *args, **kwargs):
		if self.id is None:
			saved_file = self.file
			self.file = None
			super(Attempt, self).save(*args, **kwargs)
			self.file = saved_file

		super(Attempt, self).save(*args, **kwargs)

	def getID(self):
		return self.id

	def getContest(self):
		return self.contest

	def getTeam(self):
		return self.team

	def getFile(self):
		return self.file

	def getClassifications(self):
		return self.classification_set.all()

	def getPassedTestsCount(self):
		n = self.getClassifications().filter(passed=True).count()
		mandatory = self.getClassifications().filter(passed=True, test__mandatory=True).count()
		diff = self.getClassifications().filter(passed=True, test__mandatory=False).count()
		return n, mandatory, diff

	def getGrade(self):
		return self.grade

	def get_absolute_url(self):
		return "/contests/%i/attempt/%i/" % (self.contest.id, self.id)

	def getTimedOutClassifications(self):
		return self.getClassifications().filter(timeout=True).all()

	@classmethod
	def getByID(cls, id):
		return cls.objects.get(id=id)

	def prepare_dirs(self):
		from pandora import settings
		from shared.routines import exec_command	
		logger = get_task_logger(__name__)

		try:
			os.makedirs(os.path.join(settings.LOCAL_STATIC_CDN_PATH, 'tmp', str(self.id)), exist_ok=True)
			logger.info(f"Temporary directory created for Attempt {self.id}.")
		except OSError as e:
			logger.error(f"Failed to create temporary directory for Attempt {self.id}: {e}")
			raise


	def cleanup(self):
		from pandora import settings
		from shared.routines import exec_command
		logger = get_task_logger(__name__)

		exec_command(f'docker kill attempt{self.id}', settings.LOCAL_STATIC_CDN_PATH)

		# Cleanup
		try:
			exec_command(f"rm -rf ./tmp/{self.id}/", settings.LOCAL_STATIC_CDN_PATH)
			logger.info(f"Temporary files cleaned up for Attempt {self.id}.")
		except Exception as e:
			logger.error(f"Failed to clean up temporary files for Attempt {self.id}: {e}")

		# Clean up past attempts
		self.team.cleanupPastAttempts(self)
		logger.info(f"Execution completed for Attempt {self.id}.")


	def run(self, progress_recorder):
		from shared.routines import run_test_in_docker, read_file, read_file_lines, get_diffs, read_benchmakrs, create_docker_container
		from pandora import settings
		if self.done:
			return False

		data_path = settings.LOCAL_STATIC_CDN_PATH
		attempt_path = os.path.join(data_path, 'submission_results', str(self.id))

		contest = self.getContest()
		tests = contest.getTests()
		total_steps = 1 + tests.count() + 1

		progress_recorder.set_progress(0, total_steps, "Initializing container")

		logger = get_task_logger(__name__)

		# Create necessary directories
		self.prepare_dirs()

		# Initialize Docker container
		create_docker_container(self.id, contest.getSpecifications(), contest.getLanguage().lower() + '_spec_test')

		# Run the first "compilation" test
		progress_recorder.set_progress(1, total_steps, "Running initial test")

		logger.info(f"Running Compilation / Test 0")
		run_test_in_docker(0, self.id)

		# Reading static analysis
		self.static_analysis = read_file(os.path.join(attempt_path, 'static.out'))
		# Checking compilation result
		compilation_output = read_file(os.path.join(attempt_path, 'compilation.result'))

		logger.info(f"Atempt {self.id}: Compilation and Static Analysis Done")
		
		mandatory_failed = False
		pct = 0
		timeouts = 0
		file_size_exceeded_count = 0

		if "Ok" not in compilation_output:  # Compilation was OK
			self.compile_error = True
			self.error_description = read_file(os.path.join(attempt_path, 'compilation.stdout'))
			self.save()

		else:
			self.compile_error = False
			self.save()
			logger.info(f"Attempt {self.id}: Compile OK")
			# Run tests
			for i, test in enumerate(tests, start=1):
				logger.info(f"Atempt {self.id}: Running test {i}.")

				if timeouts >= 2 or file_size_exceeded_count >= 2:
					logger.warning(f"Execution stopped early for Attempt {self.id} due to excessive timeouts or file size issues.")
					break

				progress_recorder.set_progress(i + 1, total_steps, f"Running test {i}")

				ref_out = test.getOutFileContent()
				input_data = test.getInFileContent()
				args = test.getRunArgs()

				classification = Classification(
					attempt=self,
					test=test,
					timeout=False,
					result=0,
					expected_output=ref_out,
					input=input_data,
					run_arguments=args,
				)

				# Run test in Docker
				run_test_in_docker(test.getID(), self.id)
				logger.info(f"Atempt {self.id}: test {i} runned correctly.")
				# Read results
				test_check_file = read_file(os.path.join(attempt_path, f"{test.getID()}.test"))
				logger.info(f"Atempt {self.id}: read test {i} results.")

				test_time_file = read_file_lines(os.path.join(attempt_path, f"{test.getID()}.time"))
				logger.info(f"Atempt {self.id}: read {i} stats.")

				try:
					classification.elapsed_time, classification.memory_usage = read_benchmakrs(
						test_time_file[1] if 'signal' in test_time_file[0] else test_time_file[0]
					)
				except Exception:
					classification.elapsed_time, classification.memory_usage = 0, 0

				self.memory_benchmark += int(classification.memory_usage)
				self.time_benchmark += float(classification.elapsed_time)

				if "Ok" in test_check_file:
					program_out = read_file(os.path.join(attempt_path, f"{test.getID()}.out"))
					are_equals, diffs, diff = get_diffs(program_out, ref_out)
					classification.passed = are_equals

					if are_equals:
						pct += test.weight_pct
					elif test.mandatory:
						mandatory_failed = True

					classification.diff = diff
					classification.output = program_out
				else:
					classification.error_description = test_check_file
					if 'Timeout' in test_check_file:
						classification.timeout = True
						timeouts += 1
					if 'Output is too big' in test_check_file:
						file_size_exceeded_count += 1

				classification.save()


		self.grade = max(0, round((pct / 100) * contest.max_classification)) if not mandatory_failed else 0
		self.done = True
		self.save()


		progress_recorder.set_progress(total_steps - 1, total_steps, "Cleaning up")
		self.cleanup()





class SafeExecError(models.Model):
	description = models.CharField(null=False, max_length=128, unique=True, blank=False)


class Classification(models.Model):
	attempt = models.ForeignKey(Attempt, default=1, null=False, on_delete=models.CASCADE)
	test = models.ForeignKey(Test, default=1, null=False, on_delete=models.CASCADE)
	passed = models.BooleanField(null=False, default=False)
	execution_time = models.IntegerField(blank=True, null=True)
	memory_usage = models.IntegerField(blank=True, null=True)
	elapsed_time = models.DecimalField(blank=True, null=True, decimal_places=3, max_digits=8)
	timeout = models.BooleanField(null=False, default=False)
	# TODO: Ver o que isto faz
	result = models.IntegerField(null=False, default=0)

	#	error = models.ForeignKey(SafeExecError, blank=True, null=True, on_delete=models.SET_NULL)
	#	exception = models.TextField(null=True, blank=True)


	error_description = models.TextField(default='')
	run_arguments = models.TextField(default='')
	input = models.TextField(default='')
	output = models.TextField(default='')
	expected_output = models.TextField(default='')
	diff = models.TextField(default='')


	def getTest(self):
		return self.test

	def getOutput(self):
		return self.test


class TeamContestDateException(models.Model):
	team = models.OneToOneField(Team, default=1, null=False, on_delete=models.CASCADE)
	valid_until = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)

class UserContestDateException(models.Model):
	contest = models.ForeignKey(Contest, default=1, null=False, on_delete=models.CASCADE)
	user = models.ForeignKey(User, default=1, null=False, on_delete=models.CASCADE)
	start_date = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
	end_date = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
	unique_together = ('contest', 'user')


class ContestTestDataFile(models.Model):
	contest = models.ForeignKey(Contest, default=1, null=False, on_delete=models.CASCADE)
	data_file = models.FileField(upload_to=get_data_files_path, blank=False, null=False, max_length=512)
	file_name = models.CharField(max_length=150, blank=False)
	unique_together = ('contest', 'file_name')


class Group(models.Model):
	name = models.CharField(max_length=50, blank=False, unique=True)
	users = models.ManyToManyField(User, blank=True)
	contests = models.ManyToManyField(Contest, blank=True)
	join_code = models.UUIDField(primary_key = False, max_length=32, unique=True, default = uuid.uuid1())
	registration_open = models.BooleanField(null=False, default=False)

	def getName(self):
		return self.name

	def getUsers(self):
		return self.users.all()

	def getContests(self):
		return self.contests.all()

	def getJoinCode(self):
		return self.join_code

	def isRegistrationOpen(self):
		return self.registration_open

	def hasUser(self, user):
		return self.users.filter(id=user.id).exists()

	def hasContest(self, contest):
		return self.contests.filter(id=contest.id).exists()

	@classmethod
	def getGroupsForUser(cls, request):
		return cls.objects.filter(users__exact=request.user)

	@classmethod
	def getByID(cls, group_id):
		return cls.objects.get(id=group_id)
