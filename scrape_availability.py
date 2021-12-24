import sys
import asyncio
import json
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, SessionNotCreatedException, NoSuchWindowException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support.expected_conditions import *

def formatAjaxResult(response):
    timeslots = []
    
    for slot in response['ajaxresult']['slots']['listTimeSlot']:
        if slot['availability']:
            timeslots.append(slot['startTime'])
    return timeslots

async def retrieveAvailableSlots():
    results = []
    settings = json.load(open("settings.json"))
    # assign headless driver for site navigation
    options = webdriver.ChromeOptions()
    options.headless = True
    # create the driver with timeout management
    driver = webdriver.Chrome(chrome_options=options)
    wait = WebDriverWait(driver, settings['wait_timer'])

    # Attempt login with license credentials
    print('Attempting login with stored credentials in settings.json...')
    driver.get("https://www.myrta.com/wps/portal/extvp/myrta/licence/tbs/tbs-login/")
    wait.until(element_to_be_clickable((By.ID, "widget_input_familyName"))).send_keys(settings['family_name'])
    wait.until(element_to_be_clickable((By.ID,"widget_rms_noLogin-input-NSWnumbPCN"))).send_keys(settings['photo_card_number'])
    wait.until(element_to_be_clickable((By.ID,"widget_input_cardNoID"))).send_keys(settings['card_id_number'])
    wait.until(element_to_be_clickable((By.ID,"submitNoLogin"))).click()
    print('Login successful.')

    # Save time if a booking has been already made
    print('Navigating through booking options...')
    if(settings['have_booking']):
        print('Booking has already been made; directly accessing centre page...')
        driver.find_element(By.XPATH,'//*[text()="Manage booking"]').click()
        wait.until(element_to_be_clickable((By.ID, "changeLocationButton"))).click()
        wait.until(element_to_be_clickable((By.ID, "rms_batLocLoc"))).click()
    else:
        print('Selecting "car" driver\'s test...')
        wait.until(element_to_be_clickable((By.ID,"CAR"))).click()
        wait.until(element_to_be_clickable((By.ID,"c1tt3"))).click()
        await asyncio.sleep(2)
        wait.until(element_to_be_clickable((By.ID, "nextButton"))).click()
        print('Agreeing to terms & conditions...')
        wait.until(element_to_be_clickable((By.ID, 'checkTerms'))).click()
        await asyncio.sleep(2)
        wait.until(element_to_be_clickable((By.ID, "nextButton"))).click()
        wait.until(element_to_be_clickable((By.ID, "rms_batLocLocSel"))).click()
    print('Finished navigating through booking options.')

    # Determine which centers should be scanned for available timeslots
    if(settings['centres']):
        print('Centres found in settings.json!')
        options = settings['centres']
        options.insert(0,"")
    else:
        print('No centres specified in settings.json. Will assume all by default.')
        select_box_first = wait.until(element_to_be_clickable((By.ID, "rms_batLocationSelect2")))
        options = [x for x in select_box_first.find_elements(By.TAG_NAME,"option")]
        options = [x.get_attribute("value") for x in options]

    # Retrieve all available timeslots for each center
    print('Retrieving timeslots for allocated centres.')
    for option in options[1:]:
        print(f"Scraping timeslots for centre ID {option}...")
        # select centre location in dropdown
        wait.until(element_to_be_clickable((By.ID, "rms_batLocLocSel"))).click()
        select_box = wait.until(element_to_be_clickable((By.ID, "rms_batLocationSelect2")))
        Select(select_box).select_by_value(option)
        # goto booking page to find timeslots
        await asyncio.sleep(2)
        wait.until(element_to_be_clickable((By.ID, "nextButton"))).click()
        response = driver.execute_script('return timeslots')
        result = {}
        result['location'] = option
        result['timeslots'] = formatAjaxResult(response)
        results.append(result)
        # Go to next centre
        wait.until(element_to_be_clickable((By.ID, "anotherLocationLink"))).click()

    driver.quit()
    return results

async def getTimeslots():
    try:
        results = await retrieveAvailableSlots()
        return results
    except TimeoutException:
        print("ERROR: Timed out whilst accessing ServiceNSW site. Try increasing wait_time in settings.json if this continues.")
    except SessionNotCreatedException:
        print("ERROR: A new webdriver session couldn't be initialised. Try increasing refresh_time in settings.json if this continues.")
    except NoSuchWindowException:
        print("ERROR: The webdriver process was terminated whilst accessing ServiceNSW.")
    return None


