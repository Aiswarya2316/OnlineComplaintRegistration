from django.urls import path
from . import views
urlpatterns = [
path('',views.login),
path('logout/',views.logout),

#### user

path('user_reg',views.user_reg),
path('userhome/',views.userhome),
path('search/', views.police_search, name='police_search'),
path('submit_complaint/', views.submit_complaint, name='submit_complaint'),
path('userprofile/',views.userprofile),
path('updateuserprofile/',views.updateuserprofile),
path('userhistory/',views.userhistory, name='userhistory'),
path('chat/<int:id>', views.chat, name='chat'),
path('contactus/',views.contactus),
path('about/', views.aboutus, name='about'),
path('message/', views.message, name='message'),
# path('policesearch/', views.policesearch, name='policesearch'),
path('viewpolices/',views.viewpolices),







#### police 

path('police_reg/',views.police_reg),
path('policehome/',views.policehome),
path('view_complaints/', views.view_complaints, name='view_complaints'),
path('viewuser/',views.viewuser,name='viewuser'),
path("complainthistory/", views.registered_complaints, name="complainthistory"),
path('delete/<int:id>',views.delete),
path('chats/<int:id>', views.chats, name='chats'),
path('messagee/', views.messagee, name='messagee'),
path('usersearch/', views.usersearch, name='usersearch'),




#### Admin

path('adminhome/',views.adminhome),
path('viewpolice/',views.viewpolice,name='viewpolice'),
path('viewusers/',views.viewusers,name='viewusers'),
path('viewcomplaint/',views.viewcomplaint,name='viewcomplaint'),
path('addstation/',views.addstation),




    
]