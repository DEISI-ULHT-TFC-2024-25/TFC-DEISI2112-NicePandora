from django.urls import path

from .views import contest_views, group_views, user_views
from .views.contests import team_views, test_views, submission_views
from .views.general import dashboard_view


def users_views(args):
    pass


urlpatterns = [
    # New urls / views

    # CONTESTS

    path('', dashboard_view, name='manager_home'),
    path('contests/', contest_views.dashboard_view, name='manager_contests_home'),
    path('contests/create/', contest_views.create_view, name='manager_contests_create'),
    path('contests/<int:contest_id>/', contest_views.detail_dashboard_view,
         name='manager_contests_detail_dashboard'),
    path('contests/<int:contest_id>/edit', contest_views.edit_view,
         name='manager_contest_edit'),
    path('contests/<int:contest_id>/specification', contest_views.detail_specification_view,
         name="manager_contest_detail_specification"),
    path('contests/<int:contest_id>/tests', test_views.dashboard_view,
         name='manager_contests_detail_tests'),
    path('contests/<int:contest_id>/tests/create', test_views.create_view,
         name='manager_contests_detail_tests_create'),
    path('contests/<int:contest_id>/tests/mass_create', test_views.mass_create_view,
         name='manager_contests_detail_tests_mass_create'),
    path('contests/<int:contest_id>/tests/edit', test_views.list_edit_view,
         name='manager_contests_detail_tests_list_edit'),
    path('contests/<int:contest_id>/tests/<int:test_id>', test_views.detail_view,
         name='manager_contests_detail_tests_detail'),
    path('contests/<int:contest_id>/tests/<int:test_id>/specification',
         test_views.detail_specification_view, name='manager_contest_detail_test_detail_specification'),
    path('contests/<int:contest_id>/tests/<int:test_id>/edit',
         test_views.detail_edit_view, name='manager_contest_detail_test_detail_edit'),
    path('contests/<int:contest_id>/teams/', team_views.dashboard_view,
         name='manager_contests_detail_teams'),
    path('contests/<int:contest_id>/teams/create', team_views.create_view,
         name='manager_contests_detail_teams_create'),
    path('contests/<int:contest_id>/teams/<int:team_id>', team_views.detail_view,
         name='manager_contests_detail_team_detail'),
    path('contests/<int:contest_id>/teams/<int:team_id>/edit', team_views.edit_view,
         name='manager_contests_detail_team_edit'),
    path('contests/<int:contest_id>/submissions/', submission_views.dashboard_view,
         name='manager_contests_detail_submissions'),
    path('contests/<int:contest_id>/submissions/<int:attempt_id>', submission_views.details_view,
         name='manager_contests_detail_submissions_details'),
    path('contests/<int:contest_id>/submissions/<int:attempt_id>/download', submission_views.download_submission,
         name='manager_contests_detail_submission_download'),
    path('contests/<int:contest_id>/extract_grades', contest_views.extract_grades,
         name='manager_contests_extract_grades'),
    path('contests/<int:contest_id>/extract_files', contest_views.extract_zip,
         name='manager_contests_extract_files'),
    path('contests/<int:contest_id>/export', contest_views.export_contest,
         name='manager_contests_export'),    
     path('gemini_api/', submission_views.gemini_api, name='gemini_api_admin'),
    path('submit_rating/', submission_views.submit_rating, name='submit_rating_admin'),     
    path('contests/<int:contest_id>/download-gemini-responses/', submission_views.download_gemini_responses, name='manager_contests_download_gemini_responses'),
    # GROUPS
    path('groups/', group_views.dashboard_view, name="admin_groups_home"),
    path('groups/create', group_views.create_view, name='admin_group_create'),
    path('groups/<int:group_id>/', group_views.detail_dashboard_view, name='admin_group_detail_dashboard'),
    path('groups/<int:group_id>/edit', group_views.edit_view, name='admin_group_edit'),
    path('groups/<int:group_id>/users', group_views.users_manage_view, name='admin_group_users_manager'),
    path('groups/<int:group_id>/contests', group_views.contests_manage_view, name='admin_group_contests_manager'),

    # USERS
    path('users/', user_views.dashboard_view, name="admin_users_home"),
    path('users/p/<int:pag>', user_views.dashboard_view, name="admin_users_home"),
    path('users/<int:user_id>/', user_views.user_form_view, name="admin_users_user_form"),
    path('users/create/', user_views.user_form_create_view, name="admin_users_user_form_create"),

    # Old

    # path('contests/<int:id>/admin-view/test/chooser/', admin_choose_test),
    # path('contests/<int:id>/admin-view/test/<int:t_id>/editor/', admin_test_editor),
    # path('contests/<int:c_id>/admin-view/team/<int:t_id>/status/', admin_view_teams_status),
    # path('admin-view/contest-creation/', admin_contest_creation),

]
