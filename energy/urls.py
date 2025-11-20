from django.urls import path
from . import views

app_name = 'energy'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('update/', views.update_energy, name='update_energy'),
    path('buyback/', views.buyback_view, name='buyback'),
    path('loan/', views.loan_view, name='loan'),
    path('donation/', views.donation_view, name='donation'),
]
