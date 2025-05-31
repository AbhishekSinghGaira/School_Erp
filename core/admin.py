from django.contrib import admin
from .models import Profile, Attendance, Marks, Notice, Assignment, Classroom, Subject, TeacherAssignment

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'classroom')
    list_filter = ('role', 'classroom')
    search_fields = ['user__username', 'classroom__name']
    # autocomplete_fields = ['user', 'classroom']

@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject', 'classroom')
    list_filter = ('classroom', 'subject')
    search_fields = ['teacher__username', 'subject__name', 'classroom__name']
    # autocomplete_fields = ['teacher', 'subject', 'classroom']

admin.site.register(Classroom)
admin.site.register(Subject)
admin.site.register(Attendance)
admin.site.register(Marks)
admin.site.register(Notice)
admin.site.register(Assignment)
