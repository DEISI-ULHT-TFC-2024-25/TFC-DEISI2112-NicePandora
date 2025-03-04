import io
import sys
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.utils.encoding import smart_str
from shared.routines import *
from shared.forms import AttemptModelForm
from user.context_functions import *
from shared.tasks import run_tests

# SUMISSION VIEW
from user.views.contest_views import user_has_access_to_contest, team_can_submit
from user.views.contest.team_views import join_view, user_has_team

from user.views.general import user_approval_required, user_complete_profile_required


def user_owns_submission(function):
    """
    Limit view to users that belong to the team
    that made the submission.
    """

    def _inner(request, *args, **kwargs):
        submission_id = kwargs.get('submission_id')
        submission = Attempt.getByID(submission_id)
        if submission:
            if submission.getTeam().hasUser(request.user):
                return function(request, *args, **kwargs)
        raise PermissionDenied

    return _inner


@login_required
@user_complete_profile_required
@user_approval_required
@user_has_access_to_contest
@user_has_team
@team_can_submit
def submit_view(request, contest_id):
    checkUserProfileInRequest(request)
    template_name = 'user/pages/contests/submissions/submission.html'
    context = {}
    can_submit = True

    contest = getContestByID(contest_id)

    # TODO: Make a decorator to check if user has team and get rid of this
    # Check team members when user doenst have team
    if not contest.userHasTeam(request.user):
        return redirect(join_view, contest_id)

    team = contest.getUserTeam(request.user)
    attempts = team.getAttempts()

    # this will allow specific users to submit outside the scheduled dates
    # example is a user that was sick
    #if not checkUsersDateExceptions(request, contest):
    #    return redirect(os.path.join(contest.get_absolute_url()))

    # Check attempts
    can_submit = contest.checkAttempts(request.user)

    # Check contest
    can_submit = contest.isOpen()

    # Check team
    can_submit = team.getUsers().count() > 0

    # Form Submit
    form = AttemptModelForm(request.POST or None, request.FILES or None)
    submitted, attempt = form.submit(request.user, can_submit, contest, team)
    print_variable_debug(attempt)
    if submitted and attempt:
        print("Before celery")
        download_task = run_tests.delay(attempt.id)
        # Get ID
        task_id = download_task.task_id
        print("TaskID: " + task_id)
        # Print Task ID
        print(f'Celery Task ID: {task_id}')
        # Return demo view with Task ID
        context.update(getContestDetailLayoutContext(contest))
        context.update({'task_id': task_id})
        context.update({'constest_id': contest.id})
        context.update({'attempt_id': attempt.id})

        return render(request, 'user/pages/contests/submissions/progress.html', context)

    context.update(getContestDetailLayoutContext(contest))
    context.update(getContestFormContext(contest, form))
    context.update(getTeamSubmissionHistoryContext(attempts))
    context.update(getContestSubmitFormContext(contest, attempts))
    context.update(getContestSubmitAttemptButtonContext(contest, team))
    return render(request, template_name, context)

@login_required
@user_complete_profile_required
@user_approval_required
@user_has_access_to_contest
@user_owns_submission
def detail_view(request, contest_id, submission_id):
    print("Contest ID: %i | Attempt ID: %i" % (contest_id, submission_id))
    checkUserProfileInRequest(request)
    template_name = 'user/pages/contests/submissions/details.html'
    context={}

    attempt = getAttemptByID(submission_id)
    contest = getContestByID(contest_id)

    # check if the url contest id is the same of the attempt contest id
    if not contest.id == attempt.getContest().id:
        raise Http404

    team = attempt.getTeam()

    results = attempt.getClassifications()
    n_tests, n_mandatory, n_diff = contest.getTestsCount()
    n_passed, mandatory_passed, passed_diff = attempt.getPassedTestsCount()

    # res.diff = ' '.join(map(str, res.diff))
    context.update(getContestDetailLayoutContext(contest))

    context.update(getTeamSubmissionDetailsContext(contest, request.user, attempt, n_passed, n_tests, mandatory_passed, n_mandatory, passed_diff, n_diff, results, "9"))
    context.update(getTeamSubmissionHistoryContext(team.getAttempts()))
    context.update(getContestSubmitAttemptButtonContext(contest, team))
    return render(request, template_name, context)

@login_required
@user_complete_profile_required
@user_approval_required
@user_has_access_to_contest
@user_owns_submission
def download_submission(request, contest_id, submission_id):
    contest = getContestByID(contest_id)
    attempt = Attempt.getByID(submission_id)
    file = attempt.getFile()
    fdir, fname = os.path.split(file.path)
    try:
        resp = HttpResponse(file)
        resp['Content-Disposition'] = 'attachment; filename = ' + str(fname)
        return resp
    except FileNotFoundError:
        raise Http404("File does not exist")
