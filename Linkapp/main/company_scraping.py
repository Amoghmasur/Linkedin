from django.shortcuts import render, redirect
import random as rd
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from Linkapp.main.mods import subparts
from Linkapp.main.connection_configs import slinkrconnect
from selenium.webdriver.common.by import By
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from selenium.webdriver.common.keys import Keys
from time import sleep, time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Linkapp.models import CompanyData1
from Linkapp.models import EmployeeDetail1
import re
from django.db.models import Q
from django.contrib import messages

'''
this class and method perform the following actions: initiate a LinkedIn search for a company,
 extract details from the company's LinkedIn page, handle cases where the LinkedIn link is not directly found,
   perform additional steps like a Google search, scroll down the page to load more content,
     extract and store company details (including employee details) in a Django database, 
     and handle exceptions by redirecting to a specific URL if necessary.'''

class Comp_Scraper:
    def __init__(self,driver):
        self.driver=driver
    def company_scrape(self,request,search_string):
        # Locates the search bar on LinkedIn, inputs the search string, and simulates pressing the 'Enter' key to perform the search.
        search = self.driver.find_element(By.XPATH, "//div[contains(@id, 'global-nav-typeahead')]/input")
        sleep(1)
        self.driver.execute_script("arguments[0].click();", search)
        sleep(1)
        # search.send_keys(s)
        self.driver.execute_script("arguments[0].value = '" + search_string + "' ", search)
        sleep(1)
        self.driver.execute_script(
            "var event = new KeyboardEvent('keydown', {'key':'Enter'}); arguments[0].dispatchEvent(event);", search)
        sleep(3)
        

        '''Tries to find and click on the company link in the LinkedIn search results.
            If unsuccessful, it performs a Google search for the company and extracts the LinkedIn link from the search results.'''
        try:
    
            lk = self.driver.find_element(By.XPATH, "//div[contains(@class, 'search-nec__hero')]//a[contains(@class, 'app-aware-link')]")
            comp_lk = lk.get_attribute('href')
            self.driver.get(comp_lk + 'about')
        except Exception as e:
            # driver.get('www.google.com')
            self.driver.execute_script("window.open('https://www.google.com');")
            self.driver.switch_to.window(self.driver.window_handles[1])
            search_bar_loc = self.driver.find_element(By.XPATH, "//textarea[contains(@type, 'search')]")
            search_bar_loc.send_keys(search_string + "linkedin link")
            search_bar_loc.send_keys(Keys.ENTER)
            search_data_loc = self.driver.find_element(By.XPATH, "//div[contains(@id, 'res')]/div[contains(@id, 'search')]//a")
            comp_google_lk = search_data_loc.get_attribute('href')
            
            if re.search('www', comp_google_lk):
                comp_lk = comp_google_lk + '/'
            else:
                comp_lk = re.sub('in', 'www', comp_google_lk, 1)+'/'
            sleep(1)
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            sleep(2)
            self.driver.get(comp_lk + 'about')
            sleep(2)
            
        sleep(3)
        # Scrolls down the company's LinkedIn page to load more content dynamically.
        start = time()
        initialScroll = 0
        finalScroll = 1000
        while True:
            self.driver.execute_script(f"window.scrollTo({initialScroll},{finalScroll})")
            initialScroll = finalScroll
            finalScroll += 1000
            sleep(rd.randint(2, 7))
            end = time()
            if round(end - start) > rd.randint(5, 9):
                break
        src = self.driver.page_source
        soup = BeautifulSoup(src, 'lxml')
        content = {}
        '''Finds and extracts various details such as company name, followers, about, website, industry, etc., from the parsed HTML.'''
        try:
            comp_name_loc = soup.find('div', {'class': 'block mt2'}).find('h1')
            comp_name = comp_name_loc.get_text().strip()
            foll_loc = soup.find('div', 'org-top-card-summary-info-list').find('div', 'inline-block')
            a = foll_loc.get_text().strip()
            b = a.replace('\n', '-').split('-')
            foll = ''
            for i in b:
                if 'followers' in i:
                    foll = i.strip()

            about_loc = self.driver.find_element(By.XPATH, "//div[@class='org-grid__content-height-enforcer']/div["
                                                    "@class='mb6']/div/div[contains(@id, 'ember')]/section")

            about = about_loc.text.split('\n')
            
            website=subparts(about, 'Website', 'company')[0]
            industry=subparts(about, 'Industry', 'company')[0]
            company_size=subparts(about, 'Company size', 'company')[0]
            headquarter=subparts(about, 'Headquarters', 'company')[0]
            founded=subparts(about, 'Founded', 'company')[0]
            specialties=subparts(about, 'Specialties', 'company')[0]
            employees=comp_emp_data(comp_lk,self.driver)

            content['company_name'] = comp_name
            content['followers'] = foll
            content['website'] = website
            content['industry'] = industry
            content['company_size'] = company_size
            content['headquarter'] = headquarter
            content['founded'] = founded
            content['specialties'] = specialties
            content['emp_info'] = employees
                
            # Creates an instance of a Django model (CompanyData1) and saves the company data to the database.
            company_data = CompanyData1(
            comp_name=comp_name,
            website=website,
            industry=industry,
            company_size=company_size,
            headquarter=headquarter,
            founded=founded,
            foll=foll,
            specialties=specialties,
            )
            company_data.save()

            #Iterates through the list of employee details and stores each employee's information in the database.
            for emp_info in employees:
                if emp_info[0]!= "LinkedIn Member" and len(emp_info)>=3 and len(emp_info[0])<=20:
                    employee_data= EmployeeDetail1(
                    # compy_name=comp_name,
                    e_name=emp_info[0],
                    e_head=emp_info[1],
                    e_link=emp_info[-1],
                    company=company_data,
                    )
                    employee_data.save()
            return content
        except Exception as e:
            redirect('/company')

def comp_emp_data(url,driver):
    #Opens the 'People' section of a LinkedIn company page by navigating to the provided URL.
    driver.get(url + 'people')
    sleep(3)
    # Initialize variables for dynamic scrolling
    #     Sets up a loop to dynamically scroll down the page, loading more content.
    # Keeps scrolling until the page height remains the same for consecutive attempts.
    prev_page_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempts = 0
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            #Waits for up to 10 seconds for a loading indicator to disappear.
            #If the indicator is not present, it continues scrolling.
            WebDriverWait(driver, 10).until_not(EC.presence_of_element_located((By.CLASS_NAME, 'loading-indicator')))
        except Exception:
            pass  # If the loading indicator doesn't appear, just continue scrolling
        sleep(2)
        curr_page_height = driver.execute_script("return document.body.scrollHeight")

        if curr_page_height == prev_page_height:
            # If the page height hasn't changed, no more content is loading
            break

        prev_page_height = curr_page_height
        scroll_attempts += 1

        '''
        Finds the list of employees on the page and iterates through each employee's information.
        Extracts relevant details and appends them to a list (lt).'''

    search_ul = driver.find_element(By.XPATH, "//div[contains(@class, 'scaffold-finite-scroll__content')]/ul")
    search_li = search_ul.find_elements(By.XPATH, './/li')
    lt = []
    for li in search_li:
        a = []
        emp_info = str(li.text).split('\n')
        #Splits the text of each employee's information into a list.
        # Discards unwanted information like connection degrees and 'Connect' buttons
        discard_info = ['3rd+ degree connection', '· 3rd', '2nd degree connection', '· 2nd', '1st degree connection', '· 1st', 'Connect']
        for i in emp_info:
            if i not in discard_info:
                a.append(i)
        ''' Attempts to find and extract the URL of the employee's LinkedIn profile.
            If not found, appends 'Not found' to the list.'''
        try:
            a_tag = li.find_element(By.XPATH, ".//a")
            href_val = a_tag.get_attribute('href')
            a.append(href_val)
        except Exception as e:
            a.append('Not found')
        lt.append(a)
    return lt # Returns the list (lt) containing information about employees on the LinkedIn company page.


'''this function goes to the 'People' section of a LinkedIn company page, dynamically scrolls to load more content, 
extracts and processes employee information, discards unwanted details, 
and returns a list of lists containing employee information, including names, roles, and profile URLs.'''