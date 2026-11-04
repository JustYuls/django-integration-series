from django.urls import path

from . import views

app_name = "holiday_api"

urlpatterns = [path("<int:year>/", views.holiday_list, name="holiday_list")]
