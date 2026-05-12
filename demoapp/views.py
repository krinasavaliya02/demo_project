from django.shortcuts import render, redirect
from demoapp.models import Company, Project
from django.http import JsonResponse, QueryDict
from django.db.models import Q
import json
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.core.paginator import Paginator
from demoapp.utils import name_exists, email_exists, sendResponse

class RegisterView(View):

    def get(self, request):
        return render(request, 'auth/register.html')
    
    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confirmpassword')

        errors = []

        if User.objects.filter(username__icontains=username).exists():
            errors.append({"field": "username", "message" : "Username already exists"})
        
        if User.objects.filter(email__icontains=email).exists():
            errors.append({"field": "email", "message" : "Email already exists"})

        if password != confirmpassword:
            errors.append({"field": "confirmpassword", "message" : "Password do not match"})

        if errors:
            return sendResponse(400, "Errors", errors)

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        return sendResponse(200, "Registered successfully!!!" )
    
class LoginView(View):
    
    def get(self,request):
        if request.user.is_authenticated:
            return redirect('/dashboard/')
        return render(request, 'auth/login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_val = User.objects.filter(Q(username__iexact=username) | Q(email__iexact=username)).first()
        
        errors = []

        if not user_val:
            errors.append({"field": "username", "message": "Username or Email not found.Please register."})
        else:       
            user = authenticate(request, username=user_val.username, password=password)
            if user is None:
                errors.append({"field": "password", "message": "Incorrect password."})
               
        if errors:
            return sendResponse(400, "Errors", errors)
        
        login(request, user)       
        next_url = request.POST.get('next')

        return sendResponse(200, "Login successfully!!!", {
            "redirect_url": next_url
        })

def logout_view(request):
    logout(request)
    return redirect('/login/')

class DashboardView(LoginRequiredMixin,View):
    login_url = '/login/'
    def get(self, request):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            total = Company.objects.count()
            return sendResponse(200,"success", {'total': total})
        return render(request, 'companies/dashboard.html')

class AddView(LoginRequiredMixin,View):
    login_url = '/login/'
    def get(self, request):
        return render(request, 'companies/add.html')
    
    def post(self, request):
        company_name=request.POST.get('name')   
        email=request.POST.get('email')
        phone=request.POST.get('phone')
        address=request.POST.get('address')
        is_active = request.POST.get('is_active') == 'true'

        projects = json.loads(request.POST.get('projects'))
        errors = {
            "company":[],
            "project":[]
        }

        if name_exists(company_name):
            errors["company"].append({"field": "company_name", "message": "Company name already exists"})
            
        if email_exists(email):
            errors["company"].append({"field": "email", "message": "Company email already exists"})

        project_name = []
        for i,p in enumerate(projects):
            project_errors = []
            name = p.get('project_name')
            technology = p.get('technology')
            status = p.get('status')
            
            if not name:
                project_errors.append({"field": "project_name", "message": "Please enter project name"})
            if not technology:
                project_errors.append({"field": "technology", "message": "Please enter technology"})
            if not status:
                project_errors.append({"field": "status", "message": "Please select status"})
            if name: 
                value = name.strip().lower()
                if value in project_name:
                    project_errors.append({"field": "project_name", "message": "Project name already exists"})
                project_name.append(value)

            if project_errors:
                errors["project"].append({str(i):project_errors})

        if errors["company"] or errors["project"]:
            return sendResponse(400, "Errors", errors)
            
        company = Company.objects.create(
            name = company_name,
            email= email,
            phone = phone,
            address = address,
            is_active = is_active,
        )
        for p in projects:
            Project.objects.create(
                company=company,
                name=p.get('project_name'),
                technology=p.get('technology'),
                status=p.get('status')
            )
        return sendResponse(200, "Company added successfully!!!")

class EditView(LoginRequiredMixin, View):
    login_url = '/login/'
    def get(self, request, id):
        try:
            company = Company.objects.prefetch_related('projects').get(id=id)
        except Company.DoesNotExist:
            company = None
        return render(request, 'companies/edit.html',{'company':company})
    
    def put(self, request, id):
        company = Company.objects.prefetch_related('projects').get(id=id)
        data = QueryDict(request.body)
        company_name=data.get('name')   
        email=data.get('email')
        phone=data.get('phone')
        address=data.get('address')
        is_active = data.get('is_active') == 'true'

        projects = json.loads(data.get('projects'))

        errors = {
            "company":[],
            "project":[]
        }
        if Company.objects.filter(name__iexact=company_name).exclude(id=id).exists():
            errors["company"].append({"field": "company_name", "message": "Company name already exists"})
        
        if Company.objects.filter(email__iexact=email).exclude(id=id).exists():
            errors["company"].append({"field": "email", "message": "Company email already exists"})

        project_name = []
        for i,p in enumerate(projects):
            project_errors = []
            name = p.get('project_name')
            technology = p.get('technology')
            status = p.get('status')

            if not name:
                project_errors.append({"field": "project_name", "message": "Please enter project name"})
            if not technology:
                project_errors.append({"field": "technology", "message": "Please enter technology"})
            if not status:
                project_errors.append({"field": "status", "message": "Please select status"})
            if name: 
                value = name.strip().lower()
                if value in project_name:
                    project_errors.append({"field": "project_name", "message": "Project name already exists"})
                project_name.append(value)

            if project_errors:
                obj = {str(i):project_errors}
                errors["project"].append(obj)
                print(obj)
                
        if errors["company"] or errors["project"]:
            return sendResponse(400, "Errors", errors)
    
        company.name = company_name
        company.email = email
        company.phone = phone
        company.address = address
        company.is_active = is_active
        company.save()

        for p in projects:
            name = p.get('project_name')
            technology = p.get('technology')
            status = p.get('status')
            Project.objects.update_or_create(
                company=company,
                name=name,
                defaults={
                    'technology':technology,
                    'status': status
                }
            )
        return sendResponse(200, "Company updated successfully!!!" )
    
class CompanyListView(LoginRequiredMixin, View):
    login_url = '/login/'
    def get(self, request):
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        if is_ajax:
            draw = int(request.GET.get('draw',1))
            start = int(request.GET.get('start',0))
            length = int(request.GET.get('length',10))      

            order_column_index = request.GET.get('order[0][column]')
            order_dir = request.GET.get('order[0][dir]')  

            column_field = {
                'name':'name',
                'email': 'email',
                'phone': 'phone',
                'address': 'address',
                'is_active': 'is_active',
                'projects': 'projects__name'
            }

            column_name = request.GET.get(f'columns[{order_column_index}][data]')

            order_field = column_field.get(column_name)

            if order_field and order_dir == 'desc':
                    order_field = f'-{order_field}'

            search = request.GET.get('search')
            status = request.GET.get('status')
            project = request.GET.get('project')
            technology = request.GET.get('technology')

            companies = Company.objects.prefetch_related('projects').all()

            if order_field:
                companies = companies.order_by(order_field)
            else:
                companies = companies.order_by('name')
                                    
            if search:
                companies = companies.filter(
                    Q(name__icontains=search) | Q(email__icontains=search) | Q(phone__icontains=search)
                )

            if status:
                status = (status == 'active')
                companies = companies.filter(is_active=status)

            if project:
                companies = companies.filter(projects__name__icontains=project)

            if technology:
                companies = companies.filter(projects__technology__icontains=technology)
                
            total = companies.count()
            companies = companies[start:start+length]
            data = []
            for company in companies:
                data.append({
                    'name': company.name,
                    'email': company.email,
                    'phone': company.phone,
                    'address': company.address,
                    'is_active': "Active" if company.is_active else "Inactive",
                    'projects': [
                        {
                        'name' : project.name,
                        'technology' : project.technology
                    }
                    for project in company.projects.all()
                    ],
                    'action': f'<a href="/companies/{company.id}/edit/" class="btn btn-warning btn-sm">Edit</a>'
                })
            response = {
                "draw": draw,
                "recordsTotal": total,
                "recordsFiltered": total,
                "data" : data
            }
            return JsonResponse(response)
        projects = Project.objects.values_list('name', flat=True).distinct()
        technologies = Project.objects.values_list('technology', flat=True).distinct()
        return render(request, 'companies/list.html', {'projects': projects, 'technologies': technologies})