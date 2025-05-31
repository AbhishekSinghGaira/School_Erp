from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from .forms import UserRegisterForm, AttendanceForm, MarksForm, NoticeForm, AssignmentForm
from .models import Attendance, Marks, Notice, Assignment, Profile, TeacherAssignment, Classroom, Subject
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import date
from django.conf import settings
from django.contrib.auth.views import LogoutView
from django.contrib.auth.forms import AuthenticationForm
from collections import defaultdict
from django.http import JsonResponse

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data['role']
            Profile.objects.create(user=user, role=role)
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'core/register.html', {'form': form})

def custom_login(request, *args, **kwargs):
    from django.contrib.auth.views import LoginView
    class CustomLoginView(LoginView):
        template_name = 'core/login.html'
        authentication_form = AuthenticationForm

        def form_valid(self, form):
            user = form.get_user()
            selected_role = self.request.POST.get('login_role')
            if selected_role == 'teacher' and not user.groups.filter(name='Teachers').exists():
                messages.error(self.request, "You are not registered as a Teacher.")
                return self.form_invalid(form)
            if selected_role == 'student' and not user.groups.filter(name='Students').exists():
                messages.error(self.request, "You are not registered as a Student.")
                return self.form_invalid(form)
            auth_login(self.request, user)
            if user.is_superuser or user.groups.filter(name='Admins').exists():
                return redirect('/admin/')
            return redirect('dashboard')

        def form_invalid(self, form):
            username = form.data.get('username')
            user_qs = User.objects.filter(username=username)
            if not user_qs.exists():
                messages.error(self.request, 'Student does not exist, contact admin or teacher.')
            else:
                user = user_qs.first()
                if not (user.groups.filter(name='Teachers').exists() or user.groups.filter(name='Students').exists()):
                    messages.error(self.request, 'Student does not exist, contact admin or teacher.')
            return super().form_invalid(form)

    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.groups.filter(name='Admins').exists():
            messages.error(request, 'Admins must use the admin panel to log in.')
            return redirect('/admin/')
    return CustomLoginView.as_view()(request, *args, **kwargs)

@login_required
def dashboard(request):
    group_names = list(request.user.groups.values_list('name', flat=True))
    profile = None
    classroom = None
    subjects = []
    try:
        profile = request.user.profile
        classroom = profile.classroom
        if classroom:
            subjects = Subject.objects.filter(
                id__in=TeacherAssignment.objects.filter(classroom=classroom).values_list('subject', flat=True)
            ).distinct()
    except Exception:
        pass
    return render(request, 'core/dashboard.html', {
        'profile': profile,
        'group_names': group_names,
        'classroom': classroom,
        'subjects': subjects,
    })

@login_required
def attendance_list(request):
    profile = Profile.objects.get(user=request.user)
    if profile.role == 'teacher':
        assignments = TeacherAssignment.objects.filter(teacher=request.user)
        attendances = Attendance.objects.filter(
            classroom__in=assignments.values('classroom'),
            subject__in=assignments.values('subject')
        ).order_by('-date')
    else:
        attendances = Attendance.objects.filter(student=request.user).order_by('-date')
    return render(request, 'core/attendance_list.html', {'attendances': attendances, 'profile': profile})

@login_required
def mark_attendance(request):
    profile = Profile.objects.get(user=request.user)
    if profile.role != 'teacher':
        return redirect('attendance_list')
    if request.method == 'POST':
        form = AttendanceForm(request.POST, user=request.user)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.marked_by = request.user
            attendance.save()
            messages.success(request, 'Attendance marked!')
            return redirect('attendance_list')
    else:
        form = AttendanceForm(user=request.user)
    return render(request, 'core/mark_attendance.html', {'form': form, 'profile': profile})

@login_required
def marks_list(request):
    profile = Profile.objects.get(user=request.user)
    if profile.role == 'teacher':
        assignments = TeacherAssignment.objects.filter(teacher=request.user)
        assigned_classrooms = assignments.values('classroom')
        marks_qs = Marks.objects.filter(
            classroom__in=assigned_classrooms,
            subject__in=assignments.values('subject'),
            student__profile__classroom__in=assigned_classrooms
        ).order_by('exam_type', '-id')
    else:
        marks_qs = Marks.objects.filter(student=request.user).order_by('exam_type', '-id')

    # Group marks by exam_type
    grouped_marks = defaultdict(list)
    for m in marks_qs:
        grouped_marks[m.exam_type].append(m)

    # For class 10 and 12, show all exam types, otherwise only main ones
    exam_types = [
        ('pa1', 'PA1'),
        ('half_yearly', 'Half Yearly'),
        ('pa2', 'PA2'),
        ('finals', 'Finals'),
    ]
    if profile.classroom and (profile.classroom.name.startswith('12') or profile.classroom.name.startswith('10')):
        exam_types = [
            ('pa1', 'PA1'),
            ('half_yearly', 'Half Yearly'),
            ('pa2', 'PA2'),
            ('pre_board_1', 'Pre Board 1'),
            ('pre_board_2', 'Pre Board 2'),
        ]

    return render(request, 'core/marks_list.html', {
        'grouped_marks': grouped_marks,
        'exam_types': exam_types,
        'profile': profile,
    })

@login_required
def add_marks(request):
    profile = Profile.objects.get(user=request.user)
    if profile.role != 'teacher':
        return redirect('marks_list')
    if request.method == 'POST':
        form = MarksForm(request.POST, user=request.user)
        if form.is_valid():
            marks = form.save(commit=False)
            marks.entered_by = request.user
            marks.save()
            messages.success(request, 'Marks added!')
            return redirect('marks_list')
    else:
        form = MarksForm(user=request.user)
    return render(request, 'core/add_marks.html', {'form': form, 'profile': profile})

@login_required
def notice_list(request):
    profile = Profile.objects.get(user=request.user)
    if profile.role == 'teacher':
        assignments = TeacherAssignment.objects.filter(teacher=request.user)
        notices = Notice.objects.filter(classroom__in=assignments.values('classroom')).order_by('-created_at')
    elif profile.role == 'student' and profile.classroom:
        notices = Notice.objects.filter(classroom=profile.classroom).order_by('-created_at')
    else:
        notices = Notice.objects.all().order_by('-created_at')
    return render(request, 'core/notice_list.html', {'notices': notices, 'profile': profile})

@login_required
def add_notice(request):
    profile = Profile.objects.get(user=request.user)
    if profile.role not in ['teacher', 'admin']:
        return redirect('notice_list')
    if request.method == 'POST':
        form = NoticeForm(request.POST, user=request.user)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.posted_by = request.user
            notice.save()
            messages.success(request, 'Notice posted!')
            return redirect('notice_list')
    else:
        form = NoticeForm(user=request.user)
    return render(request, 'core/add_notice.html', {'form': form, 'profile': profile})

@login_required
def assignment_list(request):
    profile = Profile.objects.get(user=request.user)
    if profile.role == 'teacher':
        assignments = TeacherAssignment.objects.filter(teacher=request.user)
        assignments_qs = Assignment.objects.filter(
            classroom__in=assignments.values('classroom'),
            subject__in=assignments.values('subject')
        ).order_by('-created_at')
    elif profile.role == 'student' and profile.classroom:
        assignments_qs = Assignment.objects.filter(classroom=profile.classroom).order_by('-created_at')
    else:
        assignments_qs = Assignment.objects.all().order_by('-created_at')
    return render(request, 'core/assignment_list.html', {'assignments': assignments_qs, 'profile': profile})

@login_required
def add_assignment(request):
    profile = Profile.objects.get(user=request.user)
    if profile.role != 'teacher':
        return redirect('assignment_list')
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.posted_by = request.user
            assignment.save()
            messages.success(request, 'Assignment posted!')
            return redirect('assignment_list')
    else:
        form = AssignmentForm(user=request.user)
    return render(request, 'core/add_assignment.html', {'form': form, 'profile': profile})

def logout(request, *args, **kwargs):
    return LogoutView.as_view(next_page='login')(request, *args, **kwargs)

@login_required
def delete_notice(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id)
    if request.user == notice.posted_by or request.user.is_superuser:
        notice.delete()
        messages.success(request, 'Notice deleted!')
    else:
        messages.error(request, 'You do not have permission to delete this notice.')
    return redirect('notice_list')

@login_required
def get_students_by_classroom(request, classroom_id):
    user = request.user
    if hasattr(user, 'profile') and user.profile.role == 'teacher':
        assignments = TeacherAssignment.objects.filter(teacher=user)
        allowed_classrooms = assignments.values_list('classroom', flat=True)
        if int(classroom_id) not in list(allowed_classrooms):
            return JsonResponse({'students': []})
    students = User.objects.filter(profile__classroom_id=classroom_id, profile__role='student')
    data = {'students': [{'id': s.id, 'username': s.username} for s in students]}
    return JsonResponse(data)
