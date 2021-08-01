from . import views
from django.urls import path, include

urlpatterns = [
    path('', views.home, name='home'),
    path('procedure',views.procedure, name='procedure'),
    path('webcam_feed', views.webcam_feed, name='webcam_feed'),
    path('picam_feed', views.picam_feed, name='picam_feed'),
    path('cardno',views.cardno,name="cardno"),
    path('pin',views.pin,name="pin"),
    path('enter',views.enter,name="enter"),
    path('palm', views.palm, name="palm"),
    path('enter2',views.enter2,name="enter2"),
    path('palm_verification',views.palm_verification,name="palm_verification"),
    ]