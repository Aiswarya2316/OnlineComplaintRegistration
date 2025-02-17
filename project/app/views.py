from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import ClientRegisterForm, ServiceProviderRegisterForm
from django.contrib.auth.forms import AuthenticationForm


def home(request):
    return render(request,'home.html')


# Client Registration
def client_register(request):
    if request.method == "POST":
        form = ClientRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')
    else:
        form = ClientRegisterForm()
    return render(request, 'complainter/clientregister.html', {'form': form})


# Service Provider Registration
def service_register(request):
    if request.method == "POST":
        form = ServiceProviderRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')
    else:
        form = ServiceProviderRegisterForm()
    return render(request, 'service/serviceregister.html', {'form': form})


# Login View (Handles Both User Types)
def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_client():
                return redirect('clienthome')
            else:
                return redirect('viewcomplaints')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


from django.contrib.auth import logout
from django.shortcuts import redirect

def user_logout(request):
    logout(request)
    return redirect('home')  # Redirect to the home page after logout


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Complaint, Department
from .forms import ComplaintForm

# Register Complaint View
@login_required
def register_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user  # Associate complaint with logged-in user
            complaint.save()
            return redirect('view_complaints')
    else:
        form = ComplaintForm()
    return render(request, 'complainter/registercomplaint.html', {'form': form})

# View User Complaints
@login_required
def view_complaints(request):
    complaints = Complaint.objects.filter(user=request.user)
    return render(request, 'complainter/viewcomplaints.html', {'complaints': complaints})

# Admin View All Complaints

@login_required
def viewcomplaints(request):
    complaints = Complaint.objects.all()
    return render(request, 'service/adminviewcomplaints.html', {'complaints': complaints})



def clienthome(request):
    return render(request,'complainter/clienthome.html')
