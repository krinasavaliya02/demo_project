from django.urls import path
from demoapp.views import AddView, EditView, CompanyListView, logout_view

app_name = 'companies'
urlpatterns = [
    path('logout/',logout_view, name='logout'),
    path('', CompanyListView.as_view(), name='list_page'),
    path('new/', AddView.as_view(), name='new'),
    path('<int:id>/edit/', EditView.as_view(), name='edit_company'),
]