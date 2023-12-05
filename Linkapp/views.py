from django.shortcuts import render, redirect
from Linkapp.models import ScrapedData1
from Linkapp.main.connection_configs import slinkrconnect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from Linkapp.forms import Registerform
from time import sleep, time
from Linkapp.models import CompanyData1
from Linkapp.models import EmployeeDetail1
import re
from django.db.models import Q
from django.contrib import messages
from Linkapp.main.user_scraping import Scraper
from Linkapp.main.company_scraping import Comp_Scraper



content = {}

'''user_page
The code checks if a user is logged in. it renders a user page with the username, 
if wrong user trys to enter, it redirects them to the login page.'''

def user_page(request):
    if request.user.username:
        uname = request.user.username
        return render(request, "Linkapp/user.html", {'uname': uname})
    else:
        return redirect('/login')

'''company_page
 the user is not logged in, the function redirects them to the "/login" URL. 
 This implies that if a user tries to access the company page without being authenticated, 
 they will be redirected to the login page.'''

def company_page(request):
    if request.user.username:
        uname=request.user.username
        return render(request,"Linkapp/company.html",{'uname':uname})  
    else:
         return redirect('/login')

'''user_details_scrape
The code fetches user details either from the database or by scraping a given URL.
The extracted data is then displayed on a user template, and a success message is shown to the user.
If any issues occur during the process, the user is redirected to the home page.'''

def user_detials_scrape(request):
    content={}
    
    if request.method == 'POST':
        url = request.POST.get('link')
        try:   # It tries to fetch data from a database table named ScrapedData1 based on the provided URL
            person_data = ScrapedData1.objects.filter(profile_url=url).first()
            exp_data=person_data.exp
            raw_exp_data=''.join(exp_data)
            exp_string = re.sub(r'[^a-zA-Z0-9\s]', '', raw_exp_data)
            content = {
                'profile_url': person_data.profile_url,
                'name': person_data.name,
                'works_at': person_data.works_at,
                'location': person_data.location,
                'exp': exp_string,
                'about': person_data.about,
                'uname': person_data.uname,
                'education': person_data.education,
            }
        except Exception:
            # If no data is found in the database, it implies that the information needs to be scraped from the web.
            driver = slinkrconnect()
            scraper = Scraper(driver)
            content=scraper.scrape_data(url, request)
            return render(request, 'Linkapp/user.html', content)
            
    else:
        messages.error(request, "Invalid request method. Please use POST.")
        return redirect('/home')  
    return render(request, 'Linkapp/user.html', content)


          
'''register
this code processes user registration requests. If the request is a form submission with valid data, 
it creates a new user, saves the information to the database, and redirects to the login page. 
If the data is invalid, an error message is shown, and the user is redirected back to the registration page'''

def register(request):
    if request.method == 'POST': # The function register checks if the incoming request method is 'POST'
        frmdata = Registerform(request.POST) # If it's a 'POST' request, it creates a Registerform object (frmdata) using the POST data from the request
        if frmdata.is_valid(): # If the form data is valid, it saves the data using frmdata.save() to create a new user record in the database.
            frmdata.save()
            return redirect('/login')
        else:
            messages.error(request,"Invaild Data")
            return redirect('/register')
    else:
        # If the request method is not 'POST', meaning it's a 'GET' request, 
        # it creates an empty Registerform object
        regform = Registerform()
        return render(request, 'Linkapp/signup.html', {'regform': regform})

'''user_login
this code handles user login requests. If it's a form submission with valid credentials, 
it authenticates the user, logs them in, and redirects to the home page. 
If the credentials are incorrect, it displays an error message on the login page. '''

def user_login(request):
    if request.method == 'POST':
        #If it's a 'POST' request, it creates an AuthenticationForm object (logform) 
        # using the POST data from the request.
        logform = AuthenticationForm(request=request, data=request.POST)

        if logform.is_valid():
            # If the form data is valid, it extracts the username and password from the cleaned data
            uname = logform.cleaned_data['username']
            passw = logform.cleaned_data['password']
            # It then attempts to authenticate the user using authenticate(username=uname, password=passw)
            u = authenticate(username=uname, password=passw)
            print('VAriable u', u)
            if u: # if u is vaild user , he should login and redirect to home page
                login(request, u)
                return redirect('/home')
            else:
                #If authentication fails, it renders the login page again with an error message indicating incorrect username or password.
                return render(request, 'Linkapp/login.html', {'logform': logform, 'msg': 'Username or password incorrect'})
        else:
            logform = AuthenticationForm()
            return render(request, 'Linkapp/login.html', {'logform': logform, 'msg': 'Username or password incorrect'})

    else:
        logform = AuthenticationForm()
        return render(request, 'Linkapp/login.html', {'logform': logform})
    

#The logout function takes the request as a parameter and clears the user's session, effectively logging them out.
def user_logout(request):
    logout(request)
    return redirect('/login')

# this code is for redirecting to company page
def company_page(request):
    return render(request, 'Linkapp/company.html')


def searchcomp(request):
    search_string = request.POST['search']# This line retrieves the search string from the POST request.
    lower_case_string=search_string.lower()# It converts the search string to lowercase for case-insensitive comparison.
    sleep(1)
    try:
        company_data = CompanyData1.objects.get(Q(comp_name__icontains=lower_case_string))
        #It attempts to retrieve company data from the database where the company name contains the provided search string
        employees = EmployeeDetail1.objects.filter(company=company_data)
        
        # Create a dictionary to hold the data
        comp_name=company_data.comp_name.lower()
        comp_size=company_data.company_size
        raw_comp_size=''.join(comp_size)

        comp_str = re.sub(r'[^a-zA-Z0-9\s-]', '', raw_comp_size)
        
        content = {
            'company_name': comp_name,
            'followers': company_data.foll,
            'website': company_data.website,
            'industry': company_data.industry,
            'company_size': comp_str,
            'headquarter': company_data.headquarter,
            'founded': company_data.founded,
            'specialties': company_data.specialties,

            'emp_info': [(employee.e_name, employee.e_head, employee.e_link) for employee in employees],
        }
        messages.success(request,"Your message has been successfully fetched from Database")
        return render(request, 'Linkapp/company.html', content)
    
    except Exception:#If the database search fails (throws an exception), it means the company data is not in the database.
        driver = slinkrconnect()
        company_scraper=Comp_Scraper(driver) # it calls class of scraping the data
        content=company_scraper.company_scrape(request,search_string) # calling class function of company scrap
        messages.success(request,"Your data has been successfully stored to Database")
        return render(request, 'Linkapp/company.html', content)

