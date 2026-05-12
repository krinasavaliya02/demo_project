from django.http import JsonResponse
from demoapp.models import Company, Project

def name_exists(company_name):
    return Company.objects.filter(name__iexact=company_name).exists()

def email_exists(email):
    return Company.objects.filter(email__iexact=email).exists()

def sendResponse(code, message, data=None):
    return JsonResponse({'code': code, 'message': message, 'data': data})