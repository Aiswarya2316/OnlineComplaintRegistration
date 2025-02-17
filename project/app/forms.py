from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class ClientRegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'client'
        if commit:
            user.save()
        return user

class ServiceProviderRegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'service'
        if commit:
            user.save()
        return user


from django import forms
from .models import Complaint, Department

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['description', 'category']
        
    # Dynamically populate category dropdown with available departments
    category = forms.ModelChoiceField(queryset=Department.objects.all(), empty_label="Select Department")


