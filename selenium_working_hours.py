import time
import datetime
import getpass
import subprocess, platform

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def pingOk(sHost):
    try:
        output = subprocess.check_output("ping -{} 1 {}.ccr.corp.intel.com".format('n' if platform.system().lower()=="windows" else 'c', sHost), shell=True)
    except Exception as e:
        return False
    return True

def driver_close(driver):
    time.sleep(2)
    driver.close()

def update_working_hours(myid, mypassword):
    user_agent = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16"
    profile = webdriver.FirefoxProfile() 
    profile.set_preference("general.useragent.override", user_agent)
    driver = webdriver.Firefox(profile)
    driver.set_window_size(360,680)
    
    #login page
    driver.get("http://180.168.210.37/app/login.xhtml")
    assert "Altran" in driver.title
    username = driver.find_element_by_name("j_username")
    username.clear()
    username.send_keys(myid)
    userpassword = driver.find_element_by_name("j_password")
    userpassword.clear()
    userpassword.send_keys(mypassword)
    userpassword.send_keys(Keys.RETURN)
    assert "No results found." not in driver.page_source
    driver.implicitly_wait(10)
    driver.switch_to_window(driver.window_handles[-1])
    
    #main page
    working_hours_button = driver.find_element_by_xpath("//a[@href='/app/timesheet/fillin.xhtml']")
    working_hours_button.click()
    driver.implicitly_wait(10)
    driver.switch_to_window(driver.window_handles[-1])
    
    #day select page
    time.sleep(1)
    try:
        button_fill = driver.find_element_by_xpath("//a[@class='button button-big button-fill button-success external']")
    except Exception as e:
        #driver_close(driver)
        return False
    button_fill.click()
    driver.switch_to_window(driver.window_handles[-1])
    
    #fill in page
    time.sleep(1)
    project = driver.find_element_by_xpath("//div[@class='item-input item-text-normal']")
    project.click()
    time.sleep(1) 
    project_sel = driver.find_element_by_xpath("//div[@class='item-title-row']")
    project_sel.click()
    
    working_hours = driver.find_element_by_name("timeEntry.hour")
    working_hours.clear()
    working_hours.send_keys("8")
    
    time.sleep(2)
    submit = driver.find_element_by_id("saveAndSubmit-btn")
    submit.click()
    #driver_close(driver)
    return True

def main():
    myid = input("please enter your APS id:")
    mypassword = getpass.getpass("please enter your APS password(password will not display here):")
    hostname = input("please enter your PC name, e.g wliu4x-MOBL:")
    h = int(input("please enter the time(hours) you would like to auto submit(0~23):"))
    m = int(input("please enter the time(min) you would like to auto submit(0~60):"))
    print("\n\nI will work on the terminal, don't close it, enjoy it~\n\n")
    while True:
        while True:
            now = datetime.datetime.now()
            if now.hour==h and now.minute==m:
                break
            time.sleep(20)

        print (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

        if pingOk(hostname): #for check on duty or not today
            if update_working_hours(myid, mypassword):
                print ("submit successful!")
            else:
                print ("I cannot submit, did you submited before or you request leave today?")
            driver_close(driver)
        else:
            print ("submit fail! your PC is not online, you are OoO today?")

        #avoid commit repeate
        time.sleep(60)

main()
