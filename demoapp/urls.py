from django.urls import path, include
from demoapp.views import RegisterView, LoginView, DashboardView

urlpatterns = [
    path('', LoginView.as_view(), name='home'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('companies/', include('demoapp.company_urls')),
]