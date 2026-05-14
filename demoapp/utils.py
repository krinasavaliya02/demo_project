from django.http import JsonResponse
from demoapp.models import Company, Project

def name_exists(company_name, user):
    return Company.objects.filter(name__iexact=company_name, user=user).exists()

def email_exists(email, user):
    return Company.objects.filter(email__iexact=email, user=user).exists()

def sendResponse(code, message, data=None):
    return JsonResponse({'code': code, 'message': message, 'data': data})