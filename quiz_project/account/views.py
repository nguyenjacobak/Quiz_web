from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, auth
from .models import Profile
from django.views.decorators.cache import never_cache
from django.templatetags.static import static
from quiz.models import Quiz, Category, Question, Option, QuizResult, StudentAnswer
from django.contrib.auth.decorators import user_passes_test
import random
import string
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_POST
import pandas as pd
import threading
import uuid
from django.core.cache import cache
import io
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseForbidden
from django.contrib import auth
from django.contrib.auth import update_session_auth_hash
# import password change form
from django.contrib.auth.forms import PasswordChangeForm
# import auth views
from django.contrib.auth import views as auth_views

def generate_captcha():
    digits = string.digits
    captcha = ''.join(random.choice(digits) for i in range(6))
    return captcha

def is_admin(user):
    return user.is_superuser
def is_staff(user):
    return user.is_staff
@never_cache
def register(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        gender = request.POST['gender']
        studen_id = request.POST['studen_id']
        user_class = request.POST['user_class']
        

        if password == password2:
            # check if email is not same
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email Already Used. Try to Login.")
                return redirect('register')
            # check if username is not same
            elif User.objects.filter(username=username).exists():
                messages.info(request, "Username Already Taken.")
                return redirect('register')
            else:
                user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
                user.save()

                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                user_model = User.objects.get(username=username)
                
                # Sử dụng update_or_create để tạo hoặc cập nhật hồ sơ người dùng
                profile, created = Profile.objects.update_or_create(
                    user=user_model,
                    defaults={
                        'email': email,
                        'gender': gender,
                        'studen_id': studen_id,
                        'user_class': user_class
                    }
                )
                
                return redirect('registerOk')
        else:
            messages.info(request, 'Passwords do not match')
            return redirect('register')

    context = {}
    return render(request, "register1.html", context)

@login_required(login_url='login')
@never_cache
def profile(request, username):
    if request.user.username != username:
        return HttpResponseForbidden("You are not allowed to view this profile.")

    user_object=User.objects.get(username=username)
    user_profile = Profile.objects.get(user=user_object)
    default_img_url = static('')
    # profile user
    context={
        "user_profile":user_profile,
        'default_img_url': default_img_url,
    }
    return render(request, "profile.html",context)
@never_cache
def login(request):
    # if request.user.is_authenticated:
    #     return redirect('profile', request.user.username)

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('profile', username)
        else:
            messages.info(request, 'Credentials Invalid!')
            return redirect('login')

    return render(request, "login.html")


@login_required(login_url='login')
def editProfile(request):

    user_object = request.user
    user_profile = request.user.profile

    if request.method == "POST":
        # Image
        if request.FILES.get('profile_img') != None:
            user_profile.profile_img = request.FILES.get('profile_img')
            user_profile.save()

        # Email
        if request.POST.get('email') != None:
            u = get_object_or_404(User, email=request.POST.get('email'))

            if u == None:
                user_object.email = request.POST.get('email')
                user_object.save()
            else:
                if u != user_object:
                    messages.info(request, "Email Already Used, Choose a different one!")
                    return redirect('edit_profile')

        # Username
        if request.POST.get('username') != None:
            u = get_object_or_404(User, username=request.POST.get('username'))

            if u == None:
                user_object.username = request.POST.get('username')
                user_object.save()
            else:
                if u != user_object:
                    messages.info(request, "Username Already Taken, Choose an unique one!")
                    return redirect('edit_profile')

        # firstname lastname
        user_object.first_name = request.POST.get('firstname')
        user_object.last_name = request.POST.get('lastname')
        user_object.save()

        # gender, studen_id, user_class
        user_profile.gender = request.POST.get('gender')
        user_profile.studen_id = request.POST.get('studen_id')
        user_profile.user_class = request.POST.get('user_class')
        user_profile.save()

        return redirect('profile', user_object.username)


    context = {"user_profile": user_profile}
    return render(request, 'profile-edit.html', context)

@login_required(login_url='login')
@never_cache
def logout(request):
    auth.logout(request)
    return redirect('home')

def custom_404(request, exception):
    return render(request, '404.html', status=404)
def registerOk(request):
    return render(request, 'registerOk.html')
@user_passes_test(is_admin or is_staff)
@login_required(login_url='login')
def manage(request):
    query = request.GET.get('query', '')
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(profile__studen_id__icontains=query) |
            Q(profile__user_class__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    else:
        users = User.objects.all()

    # Generate and store captcha in session
    captcha = generate_captcha()
    request.session['captcha'] = captcha
    print(f"Generated captcha: {captcha}")  # Debug statement

    context = {
        'users': users,
        'captcha': captcha
    }
    return render(request, 'AccountManagement.html', context)
@user_passes_test(is_admin or is_staff)
@login_required(login_url='login')
def delete_user(request, user_id):
    if request.method == 'POST':
        captcha = request.POST.get('captcha')
        session_captcha = request.session.get('captcha')
        print(f"Submitted captcha: {captcha}, Session captcha: {session_captcha}")  # Debug statement

        if captcha == session_captcha:
            user = get_object_or_404(User, id=user_id)
            if user.is_staff or user.is_superuser:
                messages.error(request, 'Cannot delete staff or admin accounts.')
            else:
                user.delete()
                messages.success(request, 'User deleted successfully.')
        else:
            messages.error(request, 'Invalid captcha.')
    return redirect('account_management')
@require_POST
@login_required(login_url='login')
@user_passes_test(is_admin or is_staff)
def upload_excel(request):
    excel_file = request.FILES.get('excel_file')
    if not excel_file:
        return JsonResponse({'error': 'No file uploaded.'})

    try:
        # Read the Excel file into a DataFrame
        df = pd.read_excel(excel_file, header=None)

        # Find the header row containing "Mã SV" (case-insensitive)
        header_row_index = None
        for idx, row in df.iterrows():
            if row.str.contains('Mã SV', case=False, na=False).any():
                header_row_index = idx
                break

        if header_row_index is None:
            return JsonResponse({'error': 'Header row with "Mã SV" not found.'})

        # Set the header
        df.columns = df.iloc[header_row_index]
        df = df.iloc[header_row_index + 1:]

        # Reset the index
        df = df.reset_index(drop=True)

        # Rename columns to remove leading/trailing spaces
        df.rename(columns=lambda x: str(x).strip(), inplace=True)

        required_columns = ['Mã SV', 'Họ lót', 'Tên', 'Mã lớp', 'Email']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return JsonResponse({'error': f'Missing columns: {", ".join(missing_columns)}'})

        users_data = []
        for idx, row in df.iterrows():
            # password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            username = str(row['Mã SV']).strip()
            password = f"{username}@PTIT"
            user_info = {
                'stt': idx + 1,
                'username': str(row['Mã SV']).strip(),
                'first_name': str(row['Họ lót']).strip(),
                'last_name': str(row['Tên']).strip(),
                'student_id': str(row['Mã SV']).strip(),
                'user_class': str(row['Mã lớp']).strip(),
                'email': str(row['Email']).strip(),
                'password': password
            }
            users_data.append(user_info)

        # Store users_data in session for later use
        request.session['users_data'] = users_data

        return JsonResponse({'users_data': users_data})
    except Exception as e:
        return JsonResponse({'error': str(e)})

@require_POST
@login_required(login_url='login')
@user_passes_test(is_admin or is_staff)
def create_accounts(request):
    users_data = request.session.get('users_data')
    if not users_data:
        messages.error(request, 'No user data found. Please upload the Excel file again.')
        return JsonResponse({'error': 'No user data found.'}, status=400)

    # Generate a unique task ID
    task_id = str(uuid.uuid4())

    # Store initial progress data in cache
    total_accounts = len(users_data)
    cache_key = f'account_creation_progress_{task_id}'
    cache.set(cache_key, {'current': 0, 'total': total_accounts, 'completed': False}, timeout=3600)  # Expires in 1 hour

    # Start account creation in a separate thread
    threading.Thread(target=create_accounts_task, args=(users_data, cache_key)).start()

    # Return the task ID to the client
    return JsonResponse({'task_id': task_id})
def create_accounts_task(users_data, cache_key):
    existing_usernames = []
    created_usernames = []
    progress_data = cache.get(cache_key)

    for user_info in users_data:
        username = user_info['username']
        if User.objects.filter(username=username).exists():
            # Username already exists, skip creating this account
            existing_usernames.append(username)
        else:
            # Create the user account
            user = User.objects.create_user(
                username=username,
                password=user_info['password'],
                first_name=user_info['first_name'],
                last_name=user_info['last_name'],
                email=user_info['email']
            )
            profile = user.profile
            profile.studen_id = user_info['student_id']
            profile.user_class = user_info['user_class']
            profile.save()
            created_usernames.append(username)

        # Update progress
        progress_data['current'] += 1
        cache.set(cache_key, progress_data, timeout=3600)

    # Mark as completed
    progress_data['completed'] = True
    cache.set(cache_key, progress_data, timeout=3600)

    # Optionally, store the result messages in cache for later retrieval
    result_key = f'account_creation_result_{cache_key}'
    cache.set(result_key, {
        'created': created_usernames,
        'existing': existing_usernames
    }, timeout=3600)

# New view to check the progress
@login_required(login_url='login')
def check_account_creation_progress(request):
    task_id = request.GET.get('task_id')
    if not task_id:
        return JsonResponse({'error': 'No task ID provided.'}, status=400)

    cache_key = f'account_creation_progress_{task_id}'
    progress_data = cache.get(cache_key)

    if not progress_data:
        return JsonResponse({'error': 'Invalid or expired task ID.'}, status=404)

    return JsonResponse(progress_data)

def change_password(request):
    if request.method=='POST':
        fm=PasswordChangeForm(user=request.user,data=request.POST)
        if fm.is_valid():
            fm.save()
            update_session_auth_hash(request,fm.user)
            messages.success(request,'Password Changed Successfully')
            return redirect('profile',request.user.username)
    else:
        fm=PasswordChangeForm(user=request.user)
    return render(request, 'change_password.html',{'fm':fm})