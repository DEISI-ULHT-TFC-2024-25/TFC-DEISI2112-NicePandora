#############################
#      CONTEXT FUNCTIONS    #
#############################

#############################
#          LAYOUTS          #
#############################

# CONTESTS #

from shared.models import Contest, Profile, Team, Attempt, User

from datetime import datetime, timedelta


def getAdminContestNonDetailLayoutContext():
    return {}


def getAdminContestDetailLayoutContext(contest):
    context = {
        'admin_contest_detail_layout': {
            'contest': contest,
        }
    }
    context.update(getAdminContestNonDetailLayoutContext())
    return context


# TESTS #

def getAdminTestsNonDetailLayoutContext(contest):
    context = {
        'admin_test_non_detail_layout': {
            'contest': contest
        }
    }
    context.update(getAdminContestDetailLayoutContext(contest))
    return context


def getAdminTestDetailLayoutContext(contest, test):
    context = {
        'admin_test_detail_layout': {
            'test': test
        }
    }
    context.update(getAdminTestsNonDetailLayoutContext(contest))
    return context


# TEAMS #

def getAdminTeamNonDetailLayoutContext(contest):
    context = {
        'admin_team_non_detail_layout': {
            'contest': contest
        }
    }
    context.update(getAdminContestDetailLayoutContext(contest))
    return context


def getAdminTeamDetailLayoutContext(contest, team):
    context = {
        'admin_team_detail_layout': {
            'team': team
        }
    }
    context.update(getAdminTeamNonDetailLayoutContext(contest))
    return context


# SUBMISSIONS #

def getAdminSubmissionNonDetailLayoutContext(contest):
    context = {
        'admin_submission_non_detail_layout': {
            'contest': contest
        }
    }
    context.update(getAdminContestDetailLayoutContext(contest))
    return context


def getAdminSubmissionDetailLayoutContext(contest, submission):
    context = {
        'admin_submission_detail_layout': {
            'submission': submission
        }
    }
    context.update(getAdminSubmissionNonDetailLayoutContext(contest))
    return context


# GROUPS #

def getAdminGroupDetailLayoutContext(group):
    return {
        'admin_group_detail_layout': {
            'group': group
        }
    }


# USERS #

def getAdminUserDetailLayoutContext(user):
    return {
        'admin_user_detail_layout': {
            'user': user
        }
    }


#############################
#         COMPONENTS        #
#############################

# For list.html
def getAdminContestListContext(contests):
    """Context for list.html
    REQUIRED IN ALL VIEWS THAT EXTEND list.html
    Parameters
    ----------
        contests : list of Contest
    return
    ----------
        admin_contest_list
    """
    return {
        'admin_contest_list': {
            'contests': contests,
        }
    }


# For list.html
def getAdminTeamListContext(teams):
    """Context for list.html
    REQUIRED IN ALL VIEWS THAT EXTEND list.html
    Parameters
    ----------
        teams : array of Team
    return
    ----------
       team_list
    """
    return {
        'admin_team_list': {
            'teams': teams
        }
    }


# For detail.html
def getAdminContestsTeamsDetailContext(team):
    """Context for detail.html
    REQUIRED IN ALL VIEWS THAT EXTEND detail.html
    Parameters
    ----------
        team : Team
    return
    ----------
       team_list
    """
    return {
        'admin_contests_teams_detail': {
            'team': team,
        }
    }


# For form.html
def getAdminTestFormContext(contest, form):
    """Context for form.html
    REQUIRED IN ALL VIEWS THAT EXTEND form.html
    Parameters
    ----------
        contest : Contest
        form
    return
    ----------
        admin_test_form
    """
    return {
        'admin_test_form': {
            'contest': contest,
            'form': form
        }
    }


def getAdminTestListContext(tests):
    weight_sum = 0
    for t in tests:
        weight_sum += t.weight_pct
    return {
        'admin_test_list': {
            'tests': tests,
            'weight_sum': weight_sum
        }
    }


# For list.html
def getAdminGroupListContext(groups):
    """Context for list.html
       REQUIRED IN ALL VIEWS THAT INCLUDE list.html
       Parameters
       ----------
           group : list of Group
       """
    return {
        'admin_group_list': {
            'groups': groups
        }
    }


# For list.html
def getAdminGroupUserListContext(user_profiles):
    """Context for list.html
           REQUIRED IN ALL VIEWS THAT INCLUDE list.html
           Parameters
           ----------
               user_profiles : list of Profile
           """
    return {
        'admin_group_users_list': {
            'user_profiles': user_profiles
        }
    }


# For form.html
def getAdminCreateGroupFormContext(form):
    return {
        'admin_create_group_form': {
            'form': form
        }
    }


# For form.html
def getAdminCreateContestFormContext(form):
    return {
        'admin_contest_create_form': {
            'form': form
        }
    }


# For admin_test_specification_form.html
def getAdminSpecificationFormContext(form):
    return {
        'admin_test_specification_form': {
            'form': form
        }
    }


# For admin/users/list.html
def getAdminUsersListContext(users):
    return {
        'admin_users_list': {
            'users': users
        }
    }


# For admin/users/form.html
def getAdminUsersFormContext(userForm, profileForm):
    return {
        'admin_users_form': {
            'userForm': userForm,
            'profileForm': profileForm
        }
    }


# For admin/components/groups/contests_manager
def getAdminGroupsContestsManagerContext(contests, contests_in):
    return {
        'admin_group_contests_manager': {
            'contests': contests,
            'contests_in': contests_in
        }
    }


# For admin/components/groups/user_manager.html
def getAdminGroupUserManagerContext(users_not_in_group, users_in_group):
    return {
        'admin_groups_user_manager': {
            'users_not_in_group': users_not_in_group,
            'users_in_group': users_in_group
        }
    }


# For admin/components/groups/dashboard_cards.html
def getAdminGroupDashboardCardsContext(group, user_count, open_contest_count, closed_contest_count):
    return {
        'admin_groups_dashboard_cards': {
            'group': group,
            'user_count': user_count,
            'open_contest_count': open_contest_count,
            'closed_contest_count': closed_contest_count,
        }
    }


# For /contests/teams/form.html
def getAdminContestsTeamsFormContext(form):
    return {
        'admin_contests_teams_form': {
            'form': form
        }
    }


# For /contests/teams/manager.html
def getAdminContestsTeamsManagerContext(users_out, users_in, team):
    return {
        'admin_contests_teams_manager': {
            'users_out': users_out,
            'users_in': users_in,
            'team': team
        }
    }


# For admin/components/contests/dashboard_cards.html
def getAdminContestDashboardCardsContext(contest, submission_count, team_count, test_count, user_count):
    # Process AI ratings to include user names
    if contest.ai_ratings:
        for user_id, rating_data in contest.ai_ratings.items():
            try:
                user_obj = User.objects.get(id=user_id)
                rating_data['user_name'] = f"{user_obj.first_name} {user_obj.last_name}"
                # Ensure date is properly parsed from ISO format
                if isinstance(rating_data['date'], str):
                    rating_data['date'] = datetime.fromisoformat(rating_data['date'].replace('Z', '+00:00'))
            except User.DoesNotExist:
                rating_data['user_name'] = "Unknown User"

    return {
        'admin_contests_dashboard_cards': {
            'contest': contest,
            'submission_count': submission_count,
            'team_count': team_count,
            'test_count': test_count,
            'user_count': user_count,
        }
    }


# For admin/components/contests/submissions/list.html
def getAdminContestSubmissionListContext(submissions):
    return {
        'admin_contests_submissions_list': {
            'submissions': submissions,
        }
    }


# For admin/components/contests/submissions/chart.html
def getAdminContestSubmissionsOver30DaysChartContext(contest):
    dict = {}
    labels = []
    datasets = []

    thirtyDaysAgo = datetime.today() - timedelta(days=30)
    days = 1
    # Get all dates
    while days <= 30:
        date = thirtyDaysAgo + timedelta(days=days)
        labels.append(f"{date.day}/{date.month}")
        days += 1
    # Update dictionary and add all dates
    for date in labels:
        dict.update({
            date: 0
        })
    for s in contest.getSubmissionsLastThirtyDays():
        key = f"{s.date.day}/{s.date.month}"
        if key in dict:
            dict[key] += 1
        else:
            dict[key] = 0

    dataset = {
        'label': contest.title,
        'data': list(dict.values()),
        'backgroundColor': "#4e73df",
        'hoverBackgroundColor': "#2e59d9",
        'borderColor': "#4e73df",
    }
    datasets.append(dataset)

    return {
        'admin_contests_submissions_over_30_days_chart': {
            'labels': labels,
            'datasets': datasets
        }
    }


# For admin/components/contests/submissions/details.html
def getAdminContestSubmissionDetailsContext(contest, user, team, attempt, n_passed, n_tests, mandatory_passed,
                                            n_mandatory, passed_diff, n_diff, results, min_passed_grade):
    return {
        'admin_contests_submissions_details': {
            'contest': contest,
            'user': user,
            'team': team,
            'team_members': team.getUsers(),
            'attempt': attempt,
            'maxsize': 2147483647,
            'n_passed': n_passed,
            'n_total': n_tests,
            'mandatory_passed': mandatory_passed,
            'mandatory_total': n_mandatory,
            'general_passed': passed_diff,
            'n_general': n_diff,
            'results': results,
            'min_grade': min_passed_grade
        }
    }


def getAdminTestsListEditFormContext(tests):
    return {
        'admin_list_edit_form': {
            'tests': tests
        }
    }


def getAdminTestDetailsContext(test):
    return {
        'admin_test_details': {
            'test': test
        }
    }


def getAdminTestMassCreateFormContext(form):
    return {
        'admin_test_mass_create_form': {
            'form': form
        }
    }


# For rankings.html
def getAdminContestRankingsContext(attempts):
    return {
        'admin_contest_rankings': {
            'attempts': attempts
        }
    }


def getAdminDashboardSubmissionsPerContestContext():
    datasets = []
    dict = {}
    labels = []
    # https://hexcolor.co/random-colors#7497d8
    colors = ["#537fce",
              "#7497d8",

              "#70a3d7",
              "#80addb",

              "#f37344",
              "#f68f6a",

              "#6cb79a",
              "#c482e3",

              "#faf447",
              "#fcf88d",
              ]

    thirtyDaysAgo = datetime.today() - timedelta(days=30)
    days = 1
    while days <= 30:
        date = thirtyDaysAgo + timedelta(days=days)
        labels.append(f"{date.day}/{date.month}")
        days += 1
    for s in Attempt.objects.filter(date__gt=thirtyDaysAgo):
        key = f"{s.date.day}/{s.date.month}"
        if s.contest.title not in dict:
            dict.update({
                s.contest.title: {}
            })
            for date in labels:
                dict[s.contest.title].update({
                    date: 0
                })
        if key in dict[s.contest.title]:
            dict[s.contest.title][key] += 1
        else:
            dict[s.contest.title][key] = 0
    idx = 0
    for contest in dict:
        if idx >= len(colors):
            idx = 0
        bgcolor = colors[idx]
        hoverColor = colors[idx + 1]
        idx += 2
        dataset = {
            'label': contest,
            'backgroundColor': bgcolor,
            'hoverBackgroundColor': hoverColor,
            'borderColor': bgcolor,
            'data': list(dict[contest].values()),
        }
        datasets.append(dataset)

    return {
        'admin_dashboard_submissions_per_contest': {
            'labels': labels,
            'datasets': datasets
        }
    }


def getAdminDashboardActiveContestsCardContext():
    return {
        'admin_dashboard_active_contests': {
            'number': Contest.getActiveContests().count()
        }
    }


def getAdminDashboardLastWeekSubmissionsCardContext():
    oneWeek = datetime.today() - timedelta(days=7)
    return {
        'admin_dashboard_last_week_submissions': {
            'number': Attempt.objects.filter(date__gt=oneWeek).count()
        }
    }


def getAdminDashboardActiveUsersCardContext():
    return {
        'admin_dashboard_active_users': {
            'number': Profile.getActiveUsers().count()
        }
    }


def getAdminDashboardGradesAvgContext():
    labels = []
    data = []
    contests = Contest.objects.all().order_by("end_date")[:5]
    for contest in contests:
        labels.append(contest.getName())
        gradeSum = 0
        teams = contest.getTeams()
        if teams:
            for team in teams:
                sub = team.getLatestAttempt()
                if sub:
                    gradeSum += sub.getGrade()
            data.append(round(gradeSum / len(teams), 2))
        else:
            data.append(0)
    return {
        'admin_dashboard_grades_avg': {
            'labels': labels,
            'data': data
        }
    }


def getAdminTeamDateExceptionFormContext(form):
    return {
        'admin_team_date_exception_form': {
            'form': form
        }
    }
