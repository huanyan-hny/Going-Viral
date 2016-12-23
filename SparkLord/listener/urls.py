from django.conf.urls import include, url
import views

urlpatterns = [
    url(r'^submit-job$', views.submit),
]