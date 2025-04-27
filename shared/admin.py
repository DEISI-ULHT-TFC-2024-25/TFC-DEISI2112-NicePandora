from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import (
    Profile,
    Contest,
    Test,
    Attempt,
    Classification,
    Team,
    SafeExecError,
    UserContestDateException,
    ContestTestDataFile,
    Group, C_Specification, TeamContestDateException
)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )
    list_display = ('number', 'username', 'first_name', 'last_name', 'valid', 'is_staff', 'id')

    @admin.display(
        boolean=True
    )
    def valid(self, obj):
        return obj.profile.valid == True

    def number(self, obj):
        return obj.profile.number


    def is_very_benevolent(self, obj):
        return obj.benevolence_factor > 75

    is_very_benevolent.boolean = True
    @admin.display(
        boolean=True
    )
    def is_very_benevolent(self, obj):
        return obj.benevolence_factor > 75


    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Contest)
admin.site.register(Test)
admin.site.register(Attempt)
admin.site.register(Classification)
admin.site.register(Team)
admin.site.register(SafeExecError)
admin.site.register(UserContestDateException)
admin.site.register(ContestTestDataFile)
admin.site.register(C_Specification)
admin.site.register(Group)
admin.site.register(TeamContestDateException)