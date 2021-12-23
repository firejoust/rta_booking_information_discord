#! /usr/local/bin/python3

import sys
import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

settings = json.load(open("settings.json"))
results_filename = "results/results_"+datetime.now().strftime("%Y%m%d%H%M%S")+".json"
driver = webdriver.Chrome()
driver.get("https://www.myrta.com/wps/myportal/extvp/myrta/")
driver.find_element(By.ID, "widget_input_familyName").send_keys(settings['family_name'])
driver.find_element(By.ID,"widget_rms_noLogin-input-NSWnumbPCN").send_keys(settings['photo_card_number'])
driver.find_element(By.ID,"widget_input_cardNoID").send_keys(settings['card_id_number'])
time.sleep(2)
driver.find_element(By.ID,"submitNoLogin").click()

if(settings['have_booking']):
    driver.find_element(By.XPATH,'//*[text()="Manage booking"]').click()
    driver.find_element(By.ID,"changeLocationButton").click()
    driver.find_element(By.ID,"rms_batLocLoc").click()
    time.sleep(2)
else:
    driver.find_element(By.XPATH,'//*[text()="Book test"]').click()
    driver.find_element(By.ID,"CAR").click()
    time.sleep(settings['wait_timer'])
    driver.find_element(By.ID,"DC").click()
    time.sleep(2)
    driver.find_element(By.ID,"nextButton").click()
    driver.find_element(By.ID,"checkTerms").click()
    time.sleep(2)
    driver.find_element(By.ID,"nextButton").click()
    driver.find_element(By.ID,"rms_batLocLocSel").click()
    time.sleep(2)

if(settings['centres']):
    options = settings['centres']
    options.insert(0,"")
else:
    select_box_first = driver.find_element(By.ID,"rms_batLocationSelect2")
    options = [x for x in select_box_first.find_elements(By.TAG_NAME,"option")]
    options = [x.get_attribute("value") for x in options]

for option in options[1:]:
    time.sleep(2)
    driver.find_element(By.ID,"rms_batLocLocSel").click()
    time.sleep(2)
    select_box = driver.find_element(By.ID,"rms_batLocationSelect2")
    Select(select_box).select_by_value(option)
    time.sleep(2)
    driver.find_element(By.ID,"nextButton").click()
    if(driver.find_element(By.ID,"getEarliestTime").size!=0):
        if(driver.find_element(By.ID,"getEarliestTime").is_displayed()):
            if(driver.find_element(By.ID,"getEarliestTime").is_enabled()):
                driver.find_element(By.ID,"getEarliestTime").click()
    result = driver.execute_script('return timeslots')
    results_file = open(results_filename,"a")
    results_file.write('{"location":"'+option+'","result":'+json.dumps(result)+'}\n')
    results_file.close()
    driver.find_element(By.ID,"anotherLocationLink").click()

driver.quit()
