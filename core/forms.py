from django import forms
from django.contrib.auth.models import User
from .models import Attendance, Marks, Notice, Assignment, Profile, Classroom, Subject, TeacherAssignment
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
    ROLE_CHOICES = (
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES)
    classroom = forms.ModelChoiceField(queryset=Classroom.objects.all(), required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role', 'classroom']

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'classroom', 'subject', 'date', 'present']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and hasattr(user, 'profile') and user.profile.role == 'teacher':
            assignments = TeacherAssignment.objects.filter(teacher=user)
            self.fields['classroom'].queryset = Classroom.objects.filter(id__in=assignments.values('classroom'))
            self.fields['subject'].queryset = Subject.objects.filter(id__in=assignments.values('subject'))
            self.fields['student'].queryset = User.objects.filter(profile__classroom__in=assignments.values('classroom'), profile__role='student')
        else:
            self.fields['classroom'].queryset = Classroom.objects.all()
            self.fields['subject'].queryset = Subject.objects.all()
            self.fields['student'].queryset = User.objects.filter(profile__role='student')

class MarksForm(forms.ModelForm):
    class Meta:
        model = Marks
        fields = ['student', 'classroom', 'subject', 'exam_type', 'marks_obtained', 'max_marks']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and hasattr(user, 'profile') and user.profile.role == 'teacher':
            assignments = TeacherAssignment.objects.filter(teacher=user)
            self.fields['classroom'].queryset = Classroom.objects.filter(id__in=assignments.values('classroom'))
            self.fields['subject'].queryset = Subject.objects.filter(id__in=assignments.values('subject'))
            self.fields['student'].queryset = User.objects.filter(profile__classroom__in=assignments.values('classroom'), profile__role='student')
        else:
            self.fields['classroom'].queryset = Classroom.objects.all()
            self.fields['subject'].queryset = Subject.objects.all()
            self.fields['student'].queryset = User.objects.filter(profile__role='student')

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'content', 'classroom']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and hasattr(user, 'profile') and user.profile.role == 'teacher':
            assignments = TeacherAssignment.objects.filter(teacher=user)
            self.fields['classroom'].queryset = Classroom.objects.filter(id__in=assignments.values('classroom'))
        else:
            self.fields['classroom'].queryset = Classroom.objects.all()

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'classroom', 'subject', 'file']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and hasattr(user, 'profile') and user.profile.role == 'teacher':
            assignments = TeacherAssignment.objects.filter(teacher=user)
            self.fields['classroom'].queryset = Classroom.objects.filter(id__in=assignments.values('classroom'))
            self.fields['subject'].queryset = Subject.objects.filter(id__in=assignments.values('subject'))
        else:
            self.fields['classroom'].queryset = Classroom.objects.all()
            self.fields['subject'].queryset = Subject.objects.all() 