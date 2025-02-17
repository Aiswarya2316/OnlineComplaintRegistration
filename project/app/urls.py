from django.urls import path
from .import views
urlpatterns = [
    path('',views.home,name='home'),
    path('registerclient/', views.client_register, name='client_register'),
    path('registerservice/', views.service_register, name='service_register'),
    path('login/', views.user_login, name='login'),
    path('register_complaint/', views.register_complaint, name='register_complaint'),
    path('view_complaints/', views.view_complaints, name='view_complaints'),
    path('viewcomplaints/', views.viewcomplaints, name='viewcomplaints'),
    path('clienthome',views.clienthome,name='clienthome'),
    path('logout/', views.user_logout, name='user_logout'),




]
