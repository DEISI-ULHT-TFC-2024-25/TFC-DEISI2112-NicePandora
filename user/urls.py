from django.urls import path

from .views import contest_views, group_views, general
from .views.contest import team_views, submission_views



urlpatterns = [

    # General
    path('', general.dashboard_view, name='user_dashboard'),
    path('profile/', general.profile_view, name='user_profile_view'),
    path('about/', general.about_view, name='about'),
    path('awaiting_approval/', general.awaiting_approval_view, name='awaiting_approval'),

    # Contests
    path('contests/', contest_views.dashboard_view, name='user_contests_home'),
    path('contests/<int:contest_id>/', contest_views.detail_dashboard_view, name='user_contests_detail_dashboard'),
    path('contests/<int:contest_id>/team/join/', team_views.join_view, name='user_contest_team_join_view'),
    path('contests/<int:contest_id>/team/<int:team_id>/', team_views.detail_dashboard_view, name="user_contest_team_detail_view"),
    path('contests/<int:contest_id>/submission/', submission_views.submit_view, name='contest_attempt_form_view'),
    path('contests/<int:contest_id>/submission/<int:submission_id>/', submission_views.detail_view, name='contest_attempt_view'),
    path('contests/<int:contest_id>/submission/<int:submission_id>/download', submission_views.download_submission, name='contest_submission_download'),
    path('gemini_api/', submission_views.gemini_api, name='gemini_api'),
    path('submit_rating/', submission_views.submit_rating, name='submit_rating'),

    # Groups
    path('groups/', group_views.dashboard_view, name='user_groups_home'),
    path('groups/join', group_views.join_view, name='user_group_join'),
    path('groups/<int:group_id>/', group_views.detail_dashboard_view, name='user_groups_detail_dashboard'),

    # Old

    # path('contests/<int:id>/team/', team_create_view),
    # path('contests/<int:id>/my_team/', team_detail_view),
    # path('contests/<int:id>/status/', attempt_list_view),
    # path('contests/<int:id>/ranking/', ranking_view),

    # path('complete_profile/', complete_profile_view, name='complete_profile'),
    # path('nonactive/', nonactive_view, name='not_active'),

]
