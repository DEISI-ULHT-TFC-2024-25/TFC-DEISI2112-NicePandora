import datetime
import os
import shutil
import subprocess
import zipfile
import re
from shutil import copyfile
from subprocess import check_output
from django.conf import settings
from django.core.files import File
import diff_match_patch
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from shared.models import Classification, Attempt, Contest, UserContestDateException, \
	Group, Profile, Test
from shared.utils import *
import logging

logger = logging.getLogger(__name__)


# handle functions
def handle_zip_file(attempt, f, contest):
	print_variable_debug("Handling zip file...")
	src_path = os.path.abspath(f.path)
	src_base = os.path.basename(src_path)
	print_variable_debug(src_base)
	# if '.zip' in src_base:
	submission_dir = os.path.dirname(src_path)

	my_cmd = 'unzip ' + src_path
	print('extraction: ' + my_cmd)
	output, ret = check_output(my_cmd, submission_dir)
	print_variables_debug([
		"Attempt: " + str(attempt),
		"Contest: " + str(contest),
		"Src_base: " + str(src_base),
		"Output: " + str(output),
		"ret: " + str(ret)
	])

	return


# return True
# return False


# check in test files
def check_is_in_file(files):
	print_variable_debug("Checking in files")
	variable_debug = []
	for file in files:
		file_parts = file.split('.')
		variable_debug.append(file_parts[0])
		variable_debug.append(file_parts[1])
		file_type = file_parts[len(file_parts) - 1]
		if (not 'in' == file_type) \
				and (not 'inh' == file_type) \
				and (not 'inm' == file_type) \
				and (not 'inmh' == file_type):
			# print_variables_debug(variable_debug)
			print("The file: " + file + " is not an in file!")
			print("Is an " + file_parts[len(file_parts) - 1] + " file type!")
			return False
	print_variables_debug(variable_debug)
	return True


# check out test files
def check_is_out_file(files, n_files):
	if n_files < len(files):
		print("There are more out files than in files!")
		print("There are " + str(len(files)) + " out files and only " + str(n_files) + " in files!")
		return False
	elif n_files > len(files):
		print("There are more in files than out files!")
		print("There are " + str(n_files) + " out files and only " + str(len(files)) + " in files!")
		return False
	else:
		print_variable_debug("Checking out files")
		variable_debug = []
		for file in files:
			file_parts = file.split('.')
			variable_debug.append(file_parts[0])
			variable_debug.append(file_parts[1])
			file_type = file_parts[len(file_parts) - 1]
			if (not 'out' == file_type) \
					and (not 'outh' == file_type) \
					and (not 'outm' == file_type) \
					and (not 'outmh' == file_type):
				variable_debug.append("\nThe file: " + file + " is not an out file!")
				variable_debug.append("\nIs an " + file_parts[len(file_parts) - 1] + " file type!")
				print_variables_debug(variable_debug)
				return False
		print_variables_debug(variable_debug)
		return True


# check if the test files are for the contest
def check_is_for_this_contest_file(files, contest):
	print_variable_debug("Checking if the files are for the selected contest")
	variable_debug = []
	for file in files:
		file_parts = file.split('.')
		variable_debug.append(file_parts[0])
		variable_debug.append(file_parts[1])
		if contest.short_name not in file_parts[0]:
			print_variables_debug(variable_debug)
			print("The file: " + file + " is not for this contest")
			print("This contest short name is: " + str(contest.short_name))
			return False
	# print_variables_debug(variable_debug)
	return True


def deleting_previous_unzips(extract_dir):
	right_dir = False
	path_to_dir_to_remove = ""
	for c in os.walk(str(extract_dir)):
		print_variable_debug("searching " + str(c))
		for file in c[2]:
			file_path = str(c[0]) + "/" + str(file)
			if os.path.exists(file_path):
				os.remove(file_path)
		if right_dir:
			path_to_dir_to_remove = c[0]
		elif c[1] is not []:
			right_dir = True

	if os.path.exists(path_to_dir_to_remove):
		os.rmdir(path_to_dir_to_remove)


# unzip zip file
def unzip_zip_file(zip_path, f, in_out):
	extract_dir = os.path.dirname(zip_path) + '/temp' + str(in_out)
	file_name = str(os.path.basename(zip_path))

	print_variable_debug("Checking for previous unzips")
	deleting_previous_unzips(extract_dir)

	print_variable_debug("Double checking for previous unzips")
	deleting_previous_unzips(extract_dir)

	print_variable_debug("Unzipping file " + str(file_name))
	with zipfile.ZipFile(f, 'r') as in_files:
		print_variable_debug("Extracting file " + str(file_name) + " to " + str(extract_dir))
		count = 0
		in_files.extractall(extract_dir)
	print_variable_debug("File " + str(file_name) + " unzipped")

	return


# check in files
def check_in_files(f, contest):
	# set the zip path
	zip_path = os.path.abspath(f.path)
	zip_dir = os.path.dirname(zip_path)

	# unzip zip file
	unzip_zip_file(zip_path, f, '/in')

	# find the last branch level
	count = 0
	for c in os.walk(str(zip_dir) + '/temp/in'):
		print_variable_debug("searching " + str(c))
		count += 1

	# for the last branch level
	file_tree_branch = 0
	for files in os.walk(str(zip_dir) + '/temp/in'):
		file_tree_branch += 1
		if file_tree_branch == count:
			# print_variable_debug("Branch founded!")
			# check if the files are for this contest
			if check_is_for_this_contest_file(files[len(files) - 1], contest):
				print_variable_debug("Is for this contest!")
				# check if they are in files
				if check_is_in_file(files[len(files) - 1]):
					print_variable_debug("Are in files!")
					# if the files are correct return them
					return files[2]

	print_variable_debug("Leaving!")

	# if the files have some problem, return an empty list
	return []


# check out files
def check_out_files(f, contest, files_max_length):
	# set the zip path
	zip_path = os.path.abspath(f.path)
	zip_dir = os.path.dirname(zip_path)

	# unzip zip file
	unzip_zip_file(zip_path, f, '/out')

	# check last branch
	count = 0
	for c in os.walk(str(zip_dir) + '/temp/out'):
		print_variable_debug("searching " + str(c))
		count += 1

	# for the last branch
	file_tree_branch = 0
	for files in os.walk(str(zip_dir) + '/temp/out'):
		file_tree_branch += 1
		if file_tree_branch == count:
			# print_variable_debug("Branch founded!")
			# check if the files are for this contest
			if check_is_for_this_contest_file(files[len(files) - 1], contest):
				print_variable_debug("Is for this contest!")
				# check if they are out files
				if check_is_out_file(files[len(files) - 1], files_max_length):
					print_variable_debug("Are out files!")
					# if the files are correct return them
					return files[2]

	print_variable_debug("Leaving!")
	# if the files have some problem, return an empty list
	return []





def handle_uploaded_file(atempt, f, contest):
	paths = extract(f)
	atempt.time_benchmark = 0
	atempt.memory_benchmark = 0
	atempt.cpu_time = 0
	atempt.elapsed_time = 0
	atempt.grade = 0

	compile_error, error_description = compile(contest, paths)
	print("error_description: ", error_description)
	atempt.error_description = error_description
	atempt.compile_error = not compile_error
	atempt.save()

	if atempt.compile_error:
		return  # if compilation errors or warnings dont bother with running the tests

	atempt.static_analysis = static_analysis(paths)

	test_set = contest.test_set.all()
	n_tests = test_set.count()
	mandatory_failed = False
	pct = 0

	timeouts = 0

	# copy data files to the same path
	data_files = contest.contesttestdatafile_set.all()
	for dfile in data_files:
		data_file_base = os.path.basename(dfile.data_file.path)
		dfile.user_copy = os.path.join(paths['dir'], data_file_base)
		copyfile(dfile.data_file.path, dfile.user_copy)

	timeouts = 0
	i = 0
	for test in test_set:
		record = Classification()
		record.attempt = atempt
		record.test = test
		run_test(record, paths, data_files, i)
		record.passed = record.result == 0
		if not record.passed and test.mandatory:
			mandatory_failed = True

		if contest.automatic_weight:
			test.weight_pct = round(100 / n_tests, 2)
			test.save()

		if record.result == 2:  # timeout
			timeouts = timeouts + 1
			if timeouts == 2:
				record.result = 4
				record.save()
				break

		if record.passed:
			pct += test.weight_pct
			atempt.time_benchmark += record.execution_time
			atempt.memory_benchmark += record.memory_usage
			atempt.cpu_time += record.execution_time
			atempt.elapsed_time += record.execution_time

		record.save()
		i = i + 1

	atempt.grade = (round(pct / 100 * contest.max_classification, 0), 0)[mandatory_failed]
	atempt.save()

	if os.path.isfile(os.path.join(paths['dir'], paths['obj'])):
		os.remove(os.path.join(paths['dir'], paths['obj']))

	# remove data files from user directory
	for dfile in data_files:
		if os.path.isfile(dfile.user_copy):
			os.remove(dfile.user_copy)

	#cleanup_past_attempts(atempt.team, atempt)


def cleanup_past_attempts(team_obj, attempt_obj):
	attempts_qs = Attempt.objects.filter(team=team_obj).exclude(id=attempt_obj.id).order_by('-date')
	for at in attempts_qs:
		results = at.classification_set.all()
		for res in results:
			if res.output and os.path.isfile(res.output.path):
				os.remove(res.output.path)
			res.output = None

		if at.file and os.path.isfile(at.file.path):
			directory = os.path.dirname(at.file.path)
			shutil.rmtree(directory)
		at.file = None


#############################
#      HELPER FUCTIONS      #
#############################
def handle_uploaded_file(atempt, f, contest):
	paths = extract(f)
	atempt.time_benchmark = 0
	atempt.memory_benchmark = 0
	atempt.cpu_time = 0
	atempt.elapsed_time = 0
	atempt.grade = 0

	compile_error, error_description = compile(contest, paths)
	print("error_description: " + error_description)
	atempt.error_description = error_description
	atempt.compile_error = not compile_error
	atempt.save()

	if atempt.compile_error:
		return  # if compilation errors or warnings dont bother with running the tests

	atempt.static_analysis = static_analysis(paths)

	test_set = contest.test_set.all()
	n_tests = test_set.count()
	mandatory_failed = False
	pct = 0

	timeouts = 0

	# copy data files to the same path
	data_files = contest.contesttestdatafile_set.all()
	for dfile in data_files:
		data_file_base = os.path.basename(dfile.data_file.path)
		dfile.user_copy = os.path.join(paths['dir'], data_file_base)
		copyfile(dfile.data_file.path, dfile.user_copy)

	timeouts = 0
	i = 0
	for test in test_set:
		record = Classification()
		record.attempt = atempt
		record.test = test
		run_test(record, paths, data_files, i)
		record.passed = record.result == 0
		if not record.passed and test.mandatory:
			mandatory_failed = True

		if contest.automatic_weight:
			test.weight_pct = round(100 / n_tests, 2)
			test.save()

		if record.result == 2:  # timeout
			timeouts = timeouts + 1
			if timeouts == 2:
				record.result = 4
				record.save()
				break

		if record.passed:
			pct += test.weight_pct
			atempt.time_benchmark += record.execution_time
			atempt.memory_benchmark += record.memory_usage
			atempt.cpu_time += record.execution_time
			atempt.elapsed_time += record.execution_time

		record.save()
		i = i + 1

	atempt.grade = (round(pct / 100 * contest.max_classification, 0), 0)[mandatory_failed]
	atempt.save()

	if os.path.isfile(os.path.join(paths['dir'], paths['obj'])):
		os.remove(os.path.join(paths['dir'], paths['obj']))

	# remove data files from user directory
	for dfile in data_files:
		if os.path.isfile(dfile.user_copy):
			os.remove(dfile.user_copy)

	cleanup_past_attempts(atempt.team, atempt)


def checkIfUserIsSuperUser(request):
	return request.user.is_superuser


def getContestByID(id):
	return get_object_or_404(Contest, id=id)


def getAttemptByID(id):
	return get_object_or_404(Attempt, id=id)


def getContestsForUser(request):
	return Contest.objects.filter(group__users__exact=request.user).distinct()


def getContestsForAdmin(request):
	if request.user.is_superuser:
		return Contest.objects.filter(archived="False")
	else:
		return getContestsForUser(request)


def checkUserProfileInRequest(request):
	if not request.user.profile.number:
		return redirect('complete_profile')
	if not request.user.profile.valid:
		return redirect('not_active')


def checkIfUserHasAccessToContest(request, contest):
	present = timezone.now()
	# TODO: When groups are implemented, check if contest belongs to groups user is a part of
	if not checkIfUserIsSuperUser(request) and present < contest.start_date:
		return False
	else:
		return True


def getAllContestAttemptsRanking(contest):
	# TODO Make it better
	query = "SELECT att.*, maxs.attempts, maxs.team_id FROM (" \
			"select max(id) as id," \
			"count(id) as attempts," \
			"team_id from " \
			"shared_attempt" \
			" where contest_id = " + str(contest.id) + \
			"   group by team_id)" \
			"       maxs inner join shared_attempt att on att.id = maxs.id" \
			"           order by grade desc, attempts asc, time_benchmark asc, memory_benchmark asc, elapsed_time asc," \
			"                       cpu_time asc"
	# select contest_atempt.id as id, max(date), grade, count(contest_atempt.id) as number_of_atempts, time_benchmark, memory_benchmark elapsed_time, cpu_time from contest_atempt where contest_id = " + str(contest_obj.id) + " group by (team_id) order by grade desc, time_benchmark asc, memory_benchmark asc, number_of_atempts asc"
	return Attempt.objects.raw(query)


def getAllContestAttemptsSingleRanking(contest, team):
	# TODO Make it better
	query = "SELECT att.*, maxs.attempts, maxs.team_id FROM (" \
			"select max(id) as id," \
			"count(id) as attempts," \
			"team_id from " \
			"shared_attempt" \
			" where contest_id = " + str(contest.id) + \
			"   group by team_id)" \
			"       maxs inner join shared_attempt att on att.id = maxs.id" \
			"           order by grade desc, attempts asc, time_benchmark asc, memory_benchmark asc, elapsed_time asc," \
			"                       cpu_time asc"
	# select contest_atempt.id as id, max(date), grade, count(contest_atempt.id) as number_of_atempts, time_benchmark, memory_benchmark elapsed_time, cpu_time from contest_atempt where contest_id = " + str(contest_obj.id) + " group by (team_id) order by grade desc, time_benchmark asc, memory_benchmark asc, number_of_atempts asc"
	attempts = Attempt.objects.raw(query)
	rank = 1
	if team:
		for att in attempts:
			if att.team == team:
				return att, rank
			rank += 1
	return None, 0


def structureTeamsData(teams):
	for t in teams:
		t.members = t.getUsers()
		print(1)
		t.nMembers = t.members.count()
		t.attempts = t.attempt_set.all()
		if t.attempts:
			t.lastAtempt = t.attempts.latest('id')
			t.grade = t.lastAtempt.grade
			t.time = t.lastAtempt.time_benchmark
			t.memory = t.lastAtempt.memory_benchmark
			t.nAtempts = t.attempts.count()
		else:
			t.lastAtempt = None
			t.grade = 0
			t.time = 0
			t.memory = 0
			t.nAtempts = 0

		for m in t.members:
			m.nAtempts = t.attempts.filter(user=m).count()
	return teams


def checkUsersDateExceptions(request, contest):
	# this is to allow specific users to submit outside the scheduled dates
	# example is a user that was sick
	# TODO: Make this without being an exception, and being part of the normal process
	present = timezone.now()
	start_date = contest.start_date
	end_date = contest.end_date

	# Get User exceptions
	try:
		user_excep = UserContestDateException.objects.get(user=request.user, contest=contest)
	except UserContestDateException.DoesNotExist:
		user_excep = None

	# Check if user exceptions existes
	if user_excep:
		start_date = user_excep.start_date
		end_date = user_excep.end_date
	# Check if contest is opened if not superuser
	if not request.user.is_superuser:
		if present < start_date or present > end_date:
			# contest is not opened
			return False
	return True


def __get_zip_file_path(zip_file):
	zip_path = os.path.abspath(zip_file.path)
	return str(os.path.dirname(zip_path)) + "/temp"


def atoi(text):
	return int(text) if text.isdigit() else text


def natural_keys(text):
	'''
	alist.sort(key=natural_keys) sorts in human order
	http://nedbatchelder.com/blog/200712/human_sorting.html
	(See Toothy's implementation in the comments)
	'''
	return [atoi(c) for c in re.split(r'(\d+)', text)]


##########
# GROUPS #
##########

def getGroupsForUser(request):
	return Group.objects.filter(users__exact=request.user)


def getGroupsForAdmin(request):
	if request.user.is_superuser:
		return Group.objects.all()
	else:
		return getGroupsForUser(request)


def getGroupByID(id):
	return get_object_or_404(Group, id=id)


def getUserProfilesFromGroup(group):
	# TODO: Probably a better way to do this and save reading the users
	users = group.users.all()
	return Profile.objects.filter(user__in=users)


### CELERY FUNCTIONS IN USE




# compile the program
def compile(contest, paths):
	lflags = ''
	cflags = ''

	if contest.linkage_flags:
		lflags = contest.linkage_flags

	if contest.compile_flags:
		cflags = contest.compile_flags

	compile_cmd = 'gcc ' + cflags + ' ' + '*.c ' + ' -I ' + './src/*.c ' + ' -o ' + paths['obj'] + ' ' + lflags
	print('compilation: ' + compile_cmd)
	output = check_output(compile_cmd, paths['dir'])
	print(output)
	print(output[0])
	if output[0] != '':  # Output variable correction because the output is like (('', None), 0) not ('', None)
		return False, output[0]

	return True, "Compilation OK"


# build the execution command
def run_cmd(test, paths, data_files, test_idx):
	if test.override_exec_options:
		cpu, mem, space, min_uid, max_uid, core, n_proc, f_size, stack, clock = test.getDetails()
	else:
		cpu, mem, space, min_uid, max_uid, core, n_proc, f_size, stack, clock = test.getContest().getTestDetails()

	if test.run_arguments:
		run_args = str(test.run_arguments)
	else:
		run_args = ''

	if test.check_leak:
		check_leak = settings.VALGRIND_EXEC
	else:
		check_leak = ''

	for data_file in data_files:
		run_args = run_args.replace("<" + data_file.file_name + ">", data_file.user_copy)

	ascii_path = os.path.join(settings.MEDIA_ROOT, "ascii")

	exec_cmd = '/usr/bin/time --quiet -f "%U %K %p %e %M %x" -o ' + paths['test_time'][test_idx]
	exec_cmd += ' /usr/bin/timeout ' + str(clock)
	exec_cmd += " ./" + paths['obj'] + ' ' + run_args
	exec_cmd += " <" + test.input_file.path + ' | ' + ascii_path
	exec_cmd += " 1>" + paths['test_stdout'][test_idx]
	return exec_cmd


def run_test(record, paths, data_files, i):
	test = record.test
	paths['test_time'].append(os.path.join(paths['dir'], 'test' + str(i) + '.time'))
	paths['test_stdout'].append(os.path.join(paths['dir'], 'test' + str(i) + '.stdout'))

	exec_cmd = run_cmd(record.test, paths, data_files, i)
	print('exec cmd is:')
	print(exec_cmd)
	time_started = datetime.datetime.now()  # Save start time.
	check_output(exec_cmd, paths['dir'])
	record.execution_time = round((datetime.datetime.now() - time_started).microseconds / 1000,
								  0)  # Get execution time.

	f = open(paths['test_stdout'][i])
	record.output.save(paths['test_stdout'][i], File(f))
	f.close()

	f = open(paths['test_time'][i], "r")
	lines = f.readlines()
	print(lines)
	f.close()
	os.remove(paths['test_time'][i])
	time_info = lines[0].split(" ")
	# format:
	# %U %K %p %e %M %x
	# K      Average total (data+stack+text) memory use of the process, in Kilobytes.
	# M      Maximum resident set size of the process during its lifetime, in Kilobytes.
	# U      Total number of CPU-seconds that the process used directly (in user mode), in seconds.
	# e      Elapsed real (wall clock) time used by the process, in seconds.
	# p      Average unshared stack size of the process, in Kilobytes.
	# x      Exit status of the command.
	# elapsed = lines[1].split(" ")
	record.memory_usage = int(time_info[4]) - 512
	record.elapsed_time = float(time_info[3])

	# uses the diff tool
	with open(paths['test_stdout'][i]) as ff:
		fromlines = ff.readlines()
	with open(test.output_file.path) as tf:
		tolines = tf.readlines()

	dmp = diff_match_patch.diff_match_patch()

	str1 = "".join(fromlines)
	str2 = "".join(tolines)
	is_same = True if re.sub("[\s*\'*\"*,*)*(*]", "", str1) == re.sub("[\s*\'*\"*,*)*(*]", "", str2) else False

	diffs = dmp.diff_main(str1, str2)
	# dmp.diff_cleanupSemantic(diffs) # make the diffs array more "human" readable
	record.diff = dmp.diff_prettyHtml(diffs)

	if int(time_info[5]) == 124:
		record.result = 2
	else:
		record.result = 0 if is_same == True else 1

	# results meaning:
	# 0 - passed
	# 1 - output is different than expected - wrong answer
	# 2 - timeout
	# 3 ...
	# 4 ...
	os.remove(paths['test_stdout'][i])
	return record.result


def static_analysis(paths):
	output = check_output(settings.STATIC_ANALYZER, paths['dir'])
	return output[0]


############################
#### DO NOT DELETE THIS ####
############################

def read_file(file):
	try:
		with open(file) as f:
			data = f.read()
		return data
	except FileNotFoundError:
		return "Error"



def read_benchmakrs(line):
	column = line.split(" ")
	# format:
	# %U %K %p %e %M %x
	# 0 K      Average total (data+stack+text) memory use of the process, in Kilobytes.
	# 1 M      Maximum resident set size of the process during its lifetime, in Kilobytes.
	# 2 U      Total number of CPU-seconds that the process used directly (in user mode), in seconds.
	# 3 e      Elapsed real (wall clock) time used by the process, in seconds.
	# 4 p      Average unshared stack size of the process, in Kilobytes.
	# 5 x      Exit status of the command.
	total_memory = column[0]
	maximum_resident_size = column[1]
	user_mode_cpu_seconds = column[2]
	print(column[3])
	elapsed_time = int(float(column[3])*1000)
	average_unshared_stack_size = int(column[4]) - 512
	exit_code = column[5]
	return str(elapsed_time), str(average_unshared_stack_size)


def read_file_lines(file):
	try:
		with open(file) as f:
			lines = f.readlines()
		return lines
	except FileNotFoundError:
		return ["Error"]


def get_diffs(fromlines, tolines):
	dmp = diff_match_patch.diff_match_patch()
	str1 = "".join(fromlines).lower()
	str2 = "".join(tolines).lower()

	regex = re.compile(r'[\s*\'*\"*,*)*(*]')
	is_same = True if regex.sub("", str1) == regex.sub("", str2) else False

#    is_same = True if re.sub("\s*", "", str1) == re.sub("\s*", "", str2) else False
	diffs = dmp.diff_main(str1, str2)
	HTMLdiff = dmp.diff_prettyHtml(
		diffs)  # dmp.diff_cleanupSemantic(diffs) # make the diffs array more "human" readable
	return is_same, diffs, HTMLdiff


def exec_command(command, cwd):
	process = subprocess.Popen(
		command,
		shell=True,
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT,
		universal_newlines=True,
		cwd=cwd
	)
	stdout, stderr = process.communicate()
	print("****** RUNING *******")
	print(cwd + "/" + command)
	print("Output: ", stdout)
	print("*********************")

	ret_code = process.poll()
	return stdout, ret_code


# DOCKER FUNCTIONS #

def get_docker_env_vars(attempt_id, test_id, contest_id, run_args, specifications):
	ignored_attributes = ['contest', 'test', 'id', 'cpu', 'mem', 'run_arguments']
	string = ' --attempt "' + str(attempt_id) + '"'
	string += ' --test "' + str(test_id) + '"'
	string += ' --contest "' + str(contest_id) + '"'
	string += ' --run_arguments "' + str(run_args) + '"'
	for field in specifications.getFields():
		if field.name not in ignored_attributes:
			if specifications.getAttribute(field.name) is None:
				string += ' --' + str(field.name) + ' ""'
			else:
				v = specifications.getAttribute(field.name)
				string += ' --' + str(field.name) + ' "' + str(v) + '"'
	string += ' '
	return string


def create_docker_container(attempt_id, specifications, image):
	"""
	Creates a Docker container for the given attempt.
	"""
	docker_command = (
		f"docker run --name attempt{attempt_id} --rm -i -d "
		f"--cpus={specifications.getAttribute('cpu')} "
		f"--memory={specifications.getAttribute('mem')}m "
		f"-v {settings.DOCKER_CDN_PATH}:/disco {image} sleep 600"
	)
	logger.info(f"Creating Docker container for Attempt {attempt_id}: {docker_command}")
	exec_command(docker_command, settings.LOCAL_STATIC_CDN_PATH)


def run_test_in_docker(test_id, attempt_id):
	"""
	Runs a test in a Docker container for the given attempt.
	"""
	logger.warning(f"Atempt {attempt_id}: Executing Test {test_id}.")
	local_data_path = settings.LOCAL_STATIC_CDN_PATH

	attempt = Attempt.getByID(attempt_id)
	contest = attempt.getContest()
	specifications = contest.getSpecifications()

	run_args = ""
	
	# If it's a specific test (test_id > 0), retrieve its specifications
	if test_id > 0:
		test = Test.getByID(test_id)
		run_args = test.getRunArgs()
		test_specifications = test.getSpecifications()
		specifications = test_specifications or specifications

	# Ensure specifications exist
	if not specifications:
		logger.warning(f"No specifications found for Attempt {attempt_id}, Test {test_id}.")
		return

	# Determine Docker configuration based on the language
	language = contest.getLanguage().lower()
	script = f"{language}_specs.sh"

	# Construct Docker exec command for running the test
	docker_command = f"docker exec -i attempt{attempt_id} {script}"
	docker_command += get_docker_env_vars(attempt_id, test_id, contest.id, run_args, specifications)

	try:
		exec_command(docker_command, local_data_path)
		logger.info(f"Test {test_id} executed successfully for Attempt {attempt_id}.")
	except Exception as e:
		logger.error(f"Error during execution of Test {test_id} for Attempt {attempt_id}: {e}")
		raise

def extract(f):
	print(f.path)
	src_path = os.path.abspath(f.path)
	src_base = os.path.basename(src_path)
	(src_name, ext) = os.path.splitext(src_base)

	paths = {
		'src': src_path,
		'base': src_base,
		'name': src_name,
		'ext': ext,
		'dir': os.path.dirname(src_path),
		'obj': src_name + '.out',
		'test_time': [],
		'test_stdout': [],
	}

	if ext == '.zip':
		print("Unziping files")
		print(paths)
		unzip(paths)

	return paths

def unzip(paths):
	output, ret = exec_command('unzip ' + paths['src'], paths['dir'])
	return ret
