from django.urls import path
from . import views



urlpatterns = [
    path('', views.loginpage, name='login'),
    path('main/',views.main, name='main'), 
    path('help/', views.help, name='help'),
    path('logout/',views.logoutuser, name='logout'),
    path('UA10NA/', views.ua10na,name='ua10na'),
    path('UA10NA/<str:pk>', views.ua10naedit,name='ua10naedit'),
    path('UA10NAPos/<str:pk>', views.ua10na_pos,name='ua10na_pos'),
    path('UA11AA', views.ua11aa, name='ua11aa'),
    path('UA12AS', views.ua12as, name="ua12as"),
    path('Position/<str:pk>',views.position,name='position'),
    path('UA20NR', views.ua20nr,name='ua20nr'),
    path('UA21RA', views.ua21ra,name='ua21ra'),
    path('Invoice/<str:pk>', views.invoice, name='invoice'),
    path('POD/<str:pk>', views.pod, name='pod'),
]