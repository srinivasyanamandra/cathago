from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .forms import UserRegistrationForm, LoginForm, CreditRequestForm
from .models import User, Scan, CreditRequest

def home(request):
    return render(request, 'core/home.html')

def register(request):
    """Handles user registration."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Account created for {user.username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'core/auth/register.html', {'form': form})


def login(request):
    """Handles user authentication and login."""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                auth_login(request, user)
                user.reset_credits_if_needed()
                return redirect('admin_dashboard' if user.role == 'admin' else 'user_profile')
            messages.error(request, 'Invalid username or password.')
    
    else:
        form = LoginForm()
    
    return render(request, 'core/auth/login.html', {'form': form})


@login_required
def logout(request):
    """Logs out the user."""
    auth_logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def user_profile(request):
    """Displays the user profile and handles credit requests."""
    if request.user.role != 'user':
        return redirect('admin_dashboard')

    request.user.reset_credits_if_needed()
    
    scans = Scan.objects.filter(user=request.user)
    credit_requests = CreditRequest.objects.filter(user=request.user)
    credit_form = CreditRequestForm(request.POST or None, user=request.user)

    if credit_form.is_valid():
        credit_request = credit_form.save(commit=False)
        credit_request.user = request.user
        credit_request.save()
        messages.success(request, 'Credit request submitted successfully!')
        return redirect('user_profile')

    return render(request, 'core/user/profile.html', {
        'scans': scans,
        'credit_requests': credit_requests,
        'credit_form': credit_form
    })


from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

# views.py
from django.http import JsonResponse
from .utils.text_matching import text_similarity

from .utils.text_matching import (
    levenshtein_distance,
    word_frequency,
    text_similarity,
    enhanced_text_matching
)

@login_required
def perform_scan(request):
    if request.user.role != 'user':
        messages.error(request, 'Only regular users can perform scans.')
        return redirect('admin_dashboard')

    request.user.reset_credits_if_needed()

    if request.user.credits <= 0:
        messages.error(request, 'No credits left. Please request more.')
        return redirect('user_profile')

    if request.method == 'POST':
        scan_type = request.POST.get('scan_type', 'Default Scan')
        uploaded_file = request.FILES.get('document')

        if uploaded_file:
            file_content = uploaded_file.read().decode('utf-8')
            scan_result = f"Scan completed: {scan_type} at {timezone.now()}\nFile Content: {file_content[:100]}..." 

            scan = Scan.objects.create(user=request.user, scan_type=scan_type, result=scan_result, document_content=file_content)

            stored_documents = Scan.objects.exclude(id=scan.id)  

            matches = []
            for doc in stored_documents:
                if scan_type == 'Default Scan':
                    similarity, distance = text_similarity(file_content, doc.document_content)
                    if similarity > 0.5:
                        matches.append({
                            'id': doc.id,
                            'user': doc.user.username,
                            'scan_type': doc.scan_type,
                            'scan_date': doc.scan_date,
                            'similarity': similarity,
                            'distance': distance,
                            'download_url': f"/download-document/{doc.id}/"
                        })
                elif scan_type == 'Advanced Scan':
                    all_documents = [d.document_content for d in stored_documents]
                    similarity = enhanced_text_matching(file_content, doc.document_content, all_documents)
                    if similarity > 0.5: 
                        matches.append({
                            'id': doc.id,
                            'user': doc.user.username,
                            'scan_type': doc.scan_type,
                            'scan_date': doc.scan_date,
                            'similarity': similarity,
                            'download_url': f"/download-document/{doc.id}/"
                        })

            request.user.credits -= 1
            request.user.save()

            messages.success(request, 'Scan completed successfully! 1 credit used.')
            return render(request, 'core/user/matches.html', {'matches': matches})

    return render(request, 'core/user/scanUpload.html')


# views.py
from django.http import HttpResponse

# views.py
@login_required
def export_scan_history(request):
    scans = Scan.objects.filter(user=request.user).order_by('-scan_date')
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="scan_history.txt"'

    for scan in scans:
        response.write(f"Scan Type: {scan.scan_type}\n")
        response.write(f"Scan Date: {scan.scan_date}\n")
        response.write(f"Result: {scan.result}\n")
        response.write(f"Document Content: {scan.document_content[:100]}...\n")
        response.write("\n" + "=" * 50 + "\n")

    return response


from django.db.models import Count, Sum
from django.db import models
@login_required
def admin_dashboard(request):
    
    """Admin dashboard showing pending credit requests, user details, and analytics."""
    if request.user.role != 'admin':
        return redirect('user_profile')

    scans_per_user = User.objects.annotate(total_scans=Count('scans')).order_by('-total_scans')
    top_users_by_credits = User.objects.order_by('-credits')
    
    approved_credits_per_user = User.objects.annotate(
        total_approved_credits=Sum('credit_requests__requested_credits', filter=models.Q(credit_requests__status='approved'))
    ).values('username', 'total_approved_credits')

    credit_usage_stats = CreditRequest.objects.filter(status='approved').aggregate(total_credits=Sum('requested_credits'))

    return render(request, 'core/admin/dashboard.html', {
        'pending_requests': CreditRequest.objects.filter(status='pending'),
        'users': User.objects.filter(role='user'),
        'scans_per_user': scans_per_user,
        'top_users_by_credits': top_users_by_credits,
        'credit_usage_stats': credit_usage_stats,
        'approved_credits_per_user': approved_credits_per_user,
    })


@login_required
def review_credit_request(request, request_id):
    """Allows admin to approve or deny credit requests."""
    if request.user.role != 'admin':
        return redirect('user_profile')

    credit_request = get_object_or_404(CreditRequest, id=request_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            new_credits = credit_request.user.credits + credit_request.requested_credits
            if new_credits > 20:
                credit_request.user.credits = 20
            else:
                credit_request.user.credits = new_credits
            credit_request.user.save()
            credit_request.status = 'approved'
            messages.success(request, f'Credit request approved for {credit_request.user.username}.')
        else:
            credit_request.status = 'denied'
            messages.success(request, f'Credit request denied for {credit_request.user.username}.')

        credit_request.review_date = timezone.now()
        credit_request.reviewed_by = request.user
        credit_request.save()
        return redirect('admin_dashboard')

    return render(request, 'core/admin/review_request.html', {'credit_request': credit_request})



@login_required
def upload_document(request):
    """Allows admins to upload and store text files."""
    if request.user.role != 'admin':
        messages.error(request, 'Only admins can upload documents.')
        return redirect('user_profile')

    if request.method == 'POST':
        name = request.POST.get('name')
        uploaded_file = request.FILES.get('document')

        if uploaded_file:
            content = uploaded_file.read().decode('utf-8')
            Document.objects.create(name=name, content=content)
            messages.success(request, 'Document uploaded successfully!')
            return redirect('admin_dashboard')

    return render(request, 'core/admin/upload_document.html')

# views.py
@login_required
def download_document(request, doc_id):
    document = get_object_or_404(Scan, id=doc_id, user=request.user)
    response = HttpResponse(document.document_content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="document_{doc_id}.txt"'
    return response

@login_required
def get_matching_documents(request, doc_id):
    document = get_object_or_404(Scan, id=doc_id, user=request.user)
    stored_documents = Scan.objects.filter(user=request.user).exclude(id=doc_id)

    matches = []
    for doc in stored_documents:
        similarity, distance = text_similarity(document.document_content, doc.document_content)
        if similarity > 0.5: 
            matches.append({
                'id': doc.id,
                'scan_type': doc.scan_type,
                'scan_date': doc.scan_date,
                'similarity': similarity,
                'distance': distance,
                'download_url': f"/download-document/{doc.id}/"  
            })

    return JsonResponse({'matches': matches})
