from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import User
from django.contrib import messages
import re
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import pytesseract
from PIL import Image
import re



# from django.contrib.auth.decorators import login_required

# from django.contrib.auth.decorators import login_required
# from django.db.models import Q






def get_user(req):
    data=User.objects.get(Email=req.session['user'])
    return data

def get_police(req):
    data=Police.objects.get(Email=req.session['police'])
    return data

def login(req):
    if 'user' in req.session:
        return redirect(userhome)
    if 'police' in req.session:
        return redirect(view_complaints)

    if req.method == 'POST':
        email = req.POST['Email']
        password = req.POST['password']
        
        # Check if it's an admin login
        admin_user = authenticate(username=email, password=password)
        if admin_user and admin_user.is_superuser:
            auth_login(req, admin_user)
            return redirect(viewcomplaint)

        # Handle normal user login
        try:
            user = User.objects.get(Email=email)
            if user.password == password:  # Ensure password matches
                req.session['user'] = user.Email
                return redirect(userhome)
            else:
                messages.warning(req, "Incorrect password")
        except User.DoesNotExist:
            try:
                police = Police.objects.get(Email=email)
                if police.password == password:
                    req.session['police'] = police.Email
                    return redirect(view_complaints)
                else:
                    messages.warning(req, "Incorrect password")
            except Police.DoesNotExist:
                messages.warning(req, "Invalid email or password")
    
    return render(req, 'login.html')


def logout(req):
    if 'user' in req.session:
        del req.session['user']
    if 'police' in req.session:
        del req.session['police']
    if req.user.is_authenticated:
        auth_logout(req)  # Logout for admin users
    return redirect(login)




#################  user  #######################

def user_reg(req):
    if req.method == 'POST':
        # Collect form data
        name = req.POST['username']
        email = req.POST['Email']
        phonenumber = req.POST['phonenumber']
        location = req.POST['location']
        password = req.POST['password']
        idproofimg = req.FILES.get('idproof')  # Get the uploaded file

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            messages.warning(req, "Invalid email format. Please enter a valid email.")
            return render(req, 'user/user_reg.html')

        # Validate phone number (assuming 10-digit numeric format)
        if not re.match(r'^\d{10}$', phonenumber):
            messages.warning(req, "Invalid phone number. Please enter a valid 10-digit phone number.")
            return render(req, 'user/user_reg.html')

        # Check if email already exists
        if User.objects.filter(Email=email).exists():
            messages.warning(req, "Email already exists. Please try another email.")
            return render(req, 'user/user_reg.html')

        # Process ID proof image using Tesseract OCR
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

        try:
            # Open the uploaded image file
            image = Image.open(idproofimg)

            # Perform OCR on the image
            text = pytesseract.image_to_string(image)

            # Use regex to find 12-digit numbers
            pattern = r'\b(?:\d\s?){12}\b'
            matches = re.findall(pattern, text)

            # Clean up matches to remove spaces
            matches = [''.join(re.findall(r'\d', match)) for match in matches]

            if matches:
                # If a 12-digit number is found, use the first one (assuming Aadhaar number)
                idproof_number = matches[0]
            else:
                messages.warning(req, "Valid Aadhaar card number not found in the uploaded ID proof.")
                return render(req, 'user/user_reg.html')

        except Exception as e:
            messages.error(req, f"Error processing ID proof image: {str(e)}")
            return render(req, 'user/user_reg.html')

        # Save user data if all validations pass
        try:
            data = User.objects.create(
                username=name,
                Email=email,
                phonenumber=phonenumber,
                location=location,
                password=password,
                idproof=idproof_number  # Save the extracted Aadhaar number
            )
            data.save()

            # # Send confirmation email
            # subject = 'Registration details'
            # message = f'Your account username is {name} and password is {password}'
            # from_email = settings.EMAIL_HOST_USER
            # recipient_list = [email]
            # send_mail(subject, message, from_email, recipient_list, fail_silently=False)

            messages.success(req, "Registration successful! You can now log in.")
            return redirect(login)  # Replace 'login' with the name of your login URL pattern

        except Exception as e:
            messages.error(req, f"An error occurred during registration: {str(e)}")

    return render(req, 'user/user_reg.html')


def userhome(req):
    if 'user' in req.session:
        # user = get_user(req)
        police_id = 123 
        complaint = Complaint.objects.filter().order_by('-created_at') 
        return render(req,'user/home.html',{'complaint':complaint,'police_id': police_id})
    else:
        return redirect(login)
    
def aboutus(req):
    return render(req,'user/about.html')

# def usersearch(req):
#     if 'user' in req.session:
#         query = req.GET.get('query') 
#         products = []
#         if query:
#             products = User.objects.filter(name__icontains=query)
            
#         return render(req, 'user/usersearch.html', {'products': products, 'query': query})
#     else:
#         return redirect(login)
    


def submit_complaint(req):
    if 'user' not in req.session:
        return redirect(login)  # Ensure the user is logged in

    user = get_user(req)
    police_officers = Police.objects.all()  # Fetch all police officers for assignment

    if req.method == 'POST':
        subject = req.POST['subject']
        description = req.POST['description']
        police_id = req.POST.get('police')

        if not subject or not description or not police_id:
            messages.warning(req, "All fields are required!")
            return redirect(submit_complaint)

        police = Police.objects.get(id=police_id)
        complaint = Complaint.objects.create(
            user=user,
            police=police,
            subject=subject,
            description=description
        )
        complaint.save()
        messages.success(req, "Complaint submitted successfully.")
        return redirect(userhome)

    return render(req, 'user/submit_complaint.html', {'police_officers': police_officers})

######### user view profile

def userprofile(req):
    if 'user' in req.session:
        return render(req,'user/user_profile.html',{'data':get_user(req)})
    else:
        return redirect(login)
    

########## user profile update

def updateuserprofile(req):
    if 'user' in req.session:
        try:
            data = User.objects.get(Email=req.session['user'])
        except User.DoesNotExist:
            return redirect(login)

        if req.method == 'POST':
            name = req.POST['username']
            phonenumber = req.POST['phonenumber']
            location = req.POST['location']
            profile_picture = req.FILES.get('profile_picture')  # Handle the file upload

            # Validate phone number
            if not re.match(r'^[789]\d{9}$', phonenumber):
                return render(req, 'user/update_user_profile.html', {
                    'data': data,
                    'error_message': 'Invalid phone number'
                })

            # Update user details
            if profile_picture:  # Update only if a new file is uploaded
                picture_path = default_storage.save(profile_picture.name, profile_picture)
                data.profile_picture = picture_path
            data.username = name
            data.phonenumber = phonenumber
            data.location = location
            data.save()
            return redirect(userprofile)

        return render(req, 'user/update_user_profile.html', {'data': data})

    else:
        return redirect(login)
    

def userhistory(req):
    if 'user' in req.session:
        user = get_user(req)  
        query = req.POST.get('query', '')  # Get the search query from the POST request
        if query:
            # Search complaints by subject or description
            complaints = Complaint.objects.filter(
                user=user
            ).filter(
                Q(subject__icontains=query) | Q(description__icontains=query)
            ).order_by('-created_at')
        else:
            # Fetch all complaints if no query is provided
            complaints = Complaint.objects.filter(user=user).order_by('-created_at')
        
        return render(req, 'user/user_history.html', {'complaints': complaints, 'query': query})
    else:
        return redirect(login)


def chat(req,id):
    if 'user' in req.session:
        complaint=Complaint.objects.get(pk=id)
        data1 = Message.objects.filter(complaint=complaint)

        if req.method=='POST':
            msg=req.POST.get('content')
            if msg:
                data=Message.objects.create(complaint=complaint,content=msg)
                data.save()
        return render(req,'user/chat.html',{'data1':data1})
    else:
        return redirect(login) 
    
def viewpolices(req):
    
        data=Police.objects.all()
        return render(req,'user/viewpolice.html', {'data':data})
    



def police_search(request):
    if request.method == 'POST':
        query = request.POST.get('query', '').strip()
        if query:
            results = Police.objects.filter(name__icontains=query) | Police.objects.filter(Email__icontains=query)
        else:
            results = Police.objects.all()  # Show all if no query
        return render(request, 'user/viewpolice.html', {'data': results})
    
def contactus(req):
    if 'user' in req.session:
        data=Police.objects.all()
        return render(req, 'user/contact_us.html',{'data':data})
    else:
        return redirect(login)


################### police  ###############

def police_reg(req):
    if req.method=='POST':
        name=req.POST['name']
        email=req.POST['Email']
        password=req.POST['password']
         # Validate email
        try:
            validate_email(email)
        except ValidationError:
            messages.warning(req, "Invalid email format, please enter a valid email.")
            return render(req, 'police/police_reg.html')

        # Validate phone number (assuming 10-digit numeric format)
        try:
            data=Police.objects.create(name=name,Email=email,password=password)
            data.save()
            return redirect(login)
        except:
            messages.warning(req, "Email Already Exits , Try Another Email.")
    return render(req,'police/police_reg.html')
    
def policehome(req):
    if 'police' in req.session:
        return render(req,'police/home.html')
    else:
        return redirect(login)

def view_complaints(req):
    if 'police' not in req.session:
        return redirect(login)  # Ensure the police officer is logged in

    police = get_police(req)  # Helper function to fetch police officer details
    complaints = Complaint.objects.filter(police=police).order_by('-created_at')

    if req.method == 'POST':
        complaint_id = req.POST.get('complaint_id')
        new_status = req.POST.get('status')

        try:
            complaint = Complaint.objects.get(id=complaint_id, police=police)
            complaint.status = new_status
            complaint.save()
            success_message = "Complaint status updated successfully."
        except Complaint.DoesNotExist:
            error_message = "Complaint not found or unauthorized action."

        return render(req, 'police/view_complaints.html', {
            'complaints': complaints,
            'success_message': success_message if 'success_message' in locals() else None,
            'error_message': error_message if 'error_message' in locals() else None,
        })

    return render(req, 'police/view_complaints.html', {'complaints': complaints})

def delete(req,id):
    data=Complaint.objects.get(pk=id)
    data.delete()
    return redirect(policehome) 

def usersearch(request):
    query = request.POST.get('query')  # Get the search term from the request
    user = []
    if query:
        user = User.objects.filter(username=query)
        
    return render(request, 'police/usersearch.html', {'user': user, 'query': query})


def viewuser(req):
    query = req.POST.get('query', '')  # Get the search query from the POST request
    if query:
        # Filter users based on the search query (case-insensitive search)
        data = User.objects.filter(
            Q(username__icontains=query) |
            Q(Email__icontains=query) |
            Q(phonenumber__icontains=query) |
            Q(location__icontains=query)
        )
    else:
        data = User.objects.all()  # Return all users if no query is provided
    return render(req, 'police/viewuser.html', {'data': data})
    


def registered_complaints(req):
    if 'police' in req.session:
        police = get_police(req)
        complaints = Complaint.objects.filter(police=police)
    elif 'user' in req.session:
        user = get_user(req)
        complaints = Complaint.objects.filter(user=user)
    else:
        return redirect(login)

    return render(req, 'police/complaint_history.html', {'complaints': complaints})   



def chats(req, id):
    complaint = Complaint.objects.get(pk=id)
    data1 = Message.objects.filter(complaint=complaint)
    
    if req.method == 'POST':
        msg = req.POST.get('content')
        if msg:
            data = Message.objects.create(complaint=complaint, content=msg)
            data.save()
    
    return render(req, 'police/chats.html', {'data1': data1})



##################  admin ###############




@login_required
def adminhome(req):
    if not req.user.is_superuser:
        return redirect(login)
    data=Complaint.objects.all()
    return render(req,'admin/viewcomplaint.html',{'data':data})



@login_required
def viewusers(req):
    if not req.user.is_superuser:
        return redirect('login')  # Update 'login' with the appropriate login URL name

    query = req.POST.get('query', '')  # Get the search query from the form
    if query:
        # Filter users by username, email, or any other relevant field
        data = User.objects.filter(
            Q(username__icontains=query) |
            Q(Email__icontains=query) 
               # Optional: filter by last name
        )
    else:
        data = User.objects.all()  # Display all users if no search query is provided

    return render(req, 'admin/viewusers.html', {'data': data, 'query': query})



def adminhome(req):
    return render(req,'admin/adminhome.html')



def viewpolice(req):
    query = req.POST.get('query', '')  
    if query:
        data = Police.objects.filter(
            Q(name__icontains=query)  )
    else:
        data = Police.objects.all()  
    return render(req, 'admin/viewpolice.html', {'data': data, 'query': query})



def viewcomplaint(req):
    query = req.POST.get('query', '')  # Retrieve the search query from the POST request
    if query:
        # Filter complaints based on the query in subject or description
        data = Complaint.objects.filter(
            Q(subject__icontains=query) | Q(description__icontains=query)
        )
    else:
        data = Complaint.objects.all()  # Return all complaints if no query is provided
    
    return render(req, 'admin/viewcomplaint.html', {'data': data, 'query': query})

def addstation(req):
    if req.method=='POST':
        name = req.POST['name']
        Email = req.POST['Email']
        password = req.POST['password']
        data=Police.objects.create(name=name,Email=Email,password=password)
        data.save()
        return redirect(viewpolice)
    return render(req,'admin/addstation.html')




###Ask Anything
def message(req):
    if 'user' in req.session:  # Check if the user is logged in
        user_email = req.session.get('user')  # Get the user's email from the session
        user = User.objects.get(Email=user_email)  # Retrieve the user object using email
        
        police_officers = Police.objects.all()  # Fetch all police officers

        # Fetch all messages where the user or police is involved
        data1 = Chat.objects.filter(user=user).order_by('id')

        if req.method == 'POST':
            msg = req.POST.get('content')  # Get the message content
            police_id = req.POST.get('police_id')  # Get the police officer's ID
            if msg and police_id:
                police = Police.objects.get(pk=police_id)  # Retrieve the police officer
                # Create a new chat message
                Chat.objects.create(user=user, police=police, content=msg)

        return render(req, 'user/message.html', {
            'data1': data1,
            'police_officers': police_officers,
        })
    else:
        return redirect('login')  # Redirect to login if the user is not logged in




def messagee(req):
    if 'police' in req.session:  # Check if the police officer is logged in
        police_email = req.session.get('police')  # Get the police officer's email from the session
        police = Police.objects.get(Email=police_email)  # Retrieve the police object
        
        # Fetch all messages where the police officer or user is involved
        data1 = Chat.objects.filter(police=police).order_by('id')

        if req.method == 'POST':
            msg = req.POST.get('content')  # Get the message content
            user_id = req.POST.get('user_id')  # Get the user's ID from the form
            if msg and user_id:
                user = User.objects.get(pk=user_id)  # Retrieve the user object
                # Create a new chat message
                Chat.objects.create(police=police, user=user, content=msg)

        return render(req, 'police/messagee.html', {
            'data1': data1,
        })
    else:
        return redirect('login')  # Redirect to login if the police officer is not logged in


