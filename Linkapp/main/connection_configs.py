from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time
import random as rd



def slinkrconnect():
    chrome_options = Options() 
    '''Creates an instance of ChromeOptions to configure the behavior of the Chrome browser'''
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--disable-gpu")
    '''Initializes a Chrome WebDriver using the specified options and 
    the ChromeDriverManager to automatically download and manage the ChromeDriver executable'''
    driver = webdriver.Chrome(options=chrome_options,service=ChromeService(ChromeDriverManager().install()))
    
    '''Navigates the browser to the LinkedIn login page.'''
    driver.get('https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin')
    uname=driver.find_element(By.ID,'username')
    # uname.send_keys('riyadarkblue@gmail.com')
    # uname.send_keys('surya.exe0156@gmail.com')
    uname.send_keys('udayoffical9945@gmail.com')
    time.sleep(rd.randint(1,5))
    pwd=driver.find_element(By.ID,'password')
    # pwd.send_keys('$Momilu0156')
    pwd.send_keys('udaybca@1234')
    # pwd.send_keys('riya@2023')
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    return driver


'''
the slinkrconnect function sets up a connection to LinkedIn by configuring and launching a Chrome browser. 
It navigates to the login page, enters a username and password, and submits the login form. 
The function then returns the WebDriver for further use in web scraping or automation tasks.'''
