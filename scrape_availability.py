import sys
import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

def formatAjaxResult(response):
    timeslots = []
    for slot in response['result']['ajaxresult']['slots']['listTimeSlot']:
        print(slot)
        # timeslot available
        if slot.slotNumber != 'null':
            timeslots.append(slot.startTime)
    return timeslots

async def retrieveAvailableSlots():
    results = []
    settings = json.load(open("settings.json"))
    driver = webdriver.Chrome()

    # Attempt login with license credentials
    driver.get("https://www.myrta.com/wps/myportal/extvp/myrta/")
    driver.find_element(By.ID, "widget_input_familyName").send_keys(settings['family_name'])
    driver.find_element(By.ID,"widget_rms_noLogin-input-NSWnumbPCN").send_keys(settings['photo_card_number'])
    driver.find_element(By.ID,"widget_input_cardNoID").send_keys(settings['card_id_number'])
    time.sleep(2)
    driver.find_element(By.ID,"submitNoLogin").click()

    # Save time if a booking has been already made
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

    # Determine which centers should be scanned for available timeslots
    if(settings['centres']):
        options = settings['centres']
        options.insert(0,"")
    else:
        select_box_first = driver.find_element(By.ID,"rms_batLocationSelect2")
        options = [x for x in select_box_first.find_elements(By.TAG_NAME,"option")]
        options = [x.get_attribute("value") for x in options]

    # Retrieve all available timeslots for each center
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

        response = json.dumps(driver.execute_script('return timeslots'))
        result = {}
        result['location'] = option
        result['timeslots'] = formatAjaxResult(response)
        results.push(result)

        # Go to next center
        driver.find_element(By.ID,"anotherLocationLink").click()

    driver.quit()
    return results
