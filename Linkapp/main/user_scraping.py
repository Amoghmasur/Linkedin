from django.shortcuts import render, redirect
from django.http import HttpResponse
from Linkapp.models import ScrapedData1
import random as rd
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from Linkapp.main.mods import subparts
from Linkapp.main.connection_configs import slinkrconnect
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep, time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponseRedirect

'''
this code defines a scraper class (Scraper) that uses a web driver to scrape data from a LinkedIn profile. 
It scrolls down the page, extracts various details, stores them in a dictionary, 
saves the data to the database, and provides a success message. If an exception occurs, 
it redirects to the '/home' URL.'''


class Scraper:
    def __init__(self,driver):# The class Scraper is initialized with a web driver (driver) as a parameter.
        self.driver=driver

    def scrape_data(self, profile_url, request):
        self.driver.get(profile_url)
        start = time()
        initialScroll = 0
        finalScroll = 1000
        while True: # The code uses a web driver to access the provided URL, scrolling down the page to load more content.
            self.driver.execute_script(f"window.scrollTo({initialScroll},{finalScroll})")
            initialScroll = finalScroll 
            finalScroll += 1000
            sleep(rd.randint(2, 7))
            end = time()
            if round(end - start) > rd.randint(5, 9):
                break
        src = self.driver.page_source #The HTML source code of the page is obtained after scrolling.

        # It then uses BeautifulSoup to parse the HTML and extract information such as 
        # name, workplace, location, experience, about, education, and other details.

        soup = BeautifulSoup(src, 'lxml') 
        content = {}
        # The extracted data is processed and stored in a dictionary named content
        try:
            intro = soup.find('div', {'class': 'mt2 relative'})
            name_loc = intro.find("h1")
            name = name_loc.get_text().strip()
            works_at_loc = intro.find("div", {'class': 'text-body-medium break-words'})
            works_at = works_at_loc.get_text().strip()
            loc = soup.find('span', {'class': 'text-body-small inline t-black--light break-words'})
            locat = loc.get_text().strip()
            experience = soup.find("div", {"class": "pvs-list__outer-container"}).find('ul')
            if experience: #It extracts experience information and processes it into a list (explist).
                experience = experience.find_all('div', {'class': 'display-flex flex-column full-width align-self-center'})
                exskill = []
                for i in experience:
                        exskill.append(i.find_all('span', {'class': 'visually-hidden'}))
                explist = []
                for i in exskill:
                        for j in i:
                            explist.append(j.get_text().strip())
                
            else:
                explist = ["Not Mentioned"]  # Set experiencelist to an empty list if experience is None
                
            # About data
            about = soup.find('div', {'class': 'display-flex full-width'}).find('span', {'class': 'visually-hidden'})
            about = about.get_text()
            # ALl other data xp -"//section[contains(@id, 'ember')]/div[@class='pvs-header__container' and @class='pvs-list__outer-container']/ul//span[@class='visually-hidden']
            other_info = self.driver.find_elements(By.XPATH,
                                            "//section[contains(@id, 'ember')]/div[@class='pvs-header__container' or  @class='pvs-list__outer-container' ]//span[@class='visually-hidden']")
            ind = []
            for e in other_info:
                ind.append(e.text.strip())
            education = subparts(ind, 'Education', 'person')
            certificates = subparts(ind, 'Certficates', 'person')
            projects = subparts(ind, 'Projects', 'person')
            # Extracted data is stored in a dictionary named content.
            content['profile_url']=profile_url
            content['name'] = name
            content['works_at'] = works_at
            content['location'] = locat
            content['exp'] = explist
            content['about'] = about
            content['uname'] = request.user.username
            content['edu'] = education
            content['cert'] = certificates
            content['proj'] = projects

           # The scraped data is stored in a Django model (ScrapedData1) and saved to the database
            scraped_data = ScrapedData1(
            profile_url=profile_url,
            name=name,
            works_at=works_at,
            location=locat,
            exp=explist,
            about=about,
            uname=request.user.username,
            education=education,)
            scraped_data.save()
            messages.success(request,"Your message has been successfully sent to database")
            return content
        except Exception as e:
            # If any exception occurs during the process, the code redirects to the '/home' URL
            return redirect('/home')