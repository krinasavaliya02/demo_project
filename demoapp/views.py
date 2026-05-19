from django.shortcuts import render, redirect
from demoapp.models import Company, Project
from django.http import JsonResponse, QueryDict
from django.db.models import Q
import json
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from demoapp.utils import name_exists, email_exists, sendResponse
User = get_user_model()

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
            if request.user.role == 'ADMIN':
                total = Company.objects.count()
            else:
                total = Company.objects.filter(user=request.user).count()
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

        if name_exists(company_name, request.user):
            errors["company"].append({"field": "company_name", "message": "Company name already exists"})
            
        if email_exists(email, request.user):
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
            user=request.user,
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
            if request.user.role == 'ADMIN':
                company = Company.objects.prefetch_related('projects').get(id=id)
            else:
                company = Company.objects.prefetch_related('projects').get(id=id, user=request.user)
        except Company.DoesNotExist:
            company = None
        return render(request, 'companies/edit.html',{'company':company})
    
    def put(self, request, id):
        company = Company.objects.prefetch_related('projects').get(id=id, user=request.user)
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
        if Company.objects.filter(name__iexact=company_name,user=request.user).exclude(id=id).exists():
            errors["company"].append({"field": "company_name", "message": "Company name already exists"})
        
        if Company.objects.filter(email__iexact=email,user=request.user).exclude(id=id).exists():
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
            selected_user = request.GET.get('user')

            if request.user.role == 'ADMIN':
                companies = Company.objects.prefetch_related('projects').all()
            else:
                companies = Company.objects.prefetch_related('projects').filter(user=request.user)

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

            if selected_user:
                companies = companies.filter(user_id=selected_user)
                
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

        users = User.objects.filter(role='STAFF')
            
        if request.user.role == 'ADMIN':
            projects = Project.objects.values_list('name', flat=True).distinct()
            technologies = Project.objects.values_list('technology', flat=True).distinct()    
        else:
            projects = Project.objects.filter(company__user=request.user).values_list('name', flat=True).distinct()
            technologies = Project.objects.filter(company__user=request.user).values_list('technology', flat=True).distinct()
        return render(request, 'companies/list.html', {'projects': projects, 'technologies': technologies, 'users': users})

class EditProfileView(View):
    def get(self, request):
        if request.user.is_authenticated:
            user = User.objects.get(id=request.user.id)
            return render(request, 'companies/edit_profile.html', {'user': user})

    def put(self, request):
        user = User.objects.get(id=request.user.id)
        data = QueryDict(request.body)
        username = data.get('username')
        email = data.get('email')

        errors = []

        if User.objects.filter(username__iexact=username).exclude(id=user.id).exists():
            errors.append({"field" : "username", "message" :"Username already exists"})
        
        if User.objects.filter(email__iexact=email).exclude(id=user.id).exists():
            errors.append({"field" : "email", "message" :"Email already exists"})

        if errors:
            return sendResponse(400, "Errors", errors)

        user.username = username
        user.email = email
        user.save()

        return sendResponse(200, "Profile updated successfully!!!" )

class ChangePasswordView(View):
    def get(self, request):
        return render(request, 'companies/change_password.html')

    def post(self, request):
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = User.objects.get(id=request.user.id)

        errors = []

        if not user.check_password(current_password):
            errors.append({"field" : "current_password", "message" :"Current password is incorrect"})
        
        if len(new_password) < 8:
            errors.append({"field" : "new_password", "message" :"Password must be at least 8 characters long"})

        if new_password != confirm_password:
            errors.append({"field" : "confirm_password", "message" :"Password do not match"})

        if errors:
            return sendResponse(400, "Errors", errors)

        user.set_password(new_password)
        user.save()

        return sendResponse(200, "Password changed successfully!!!" )
