from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('aissconfig/', views.aiss_config, name='AissConfig'),
    path('suitelist/<int:page>/', views.suite_list, name='SuiteList'),
]
