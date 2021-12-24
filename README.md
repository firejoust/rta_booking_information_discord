This script notifies you on discord when a new timeslot is available for the NSW Car Driving Test.

## Dependencies

 1. Valid license details with RTA NSW after you have passed knowledge test, hazard test etc.
 2. [chrome driver](https://sites.google.com/chromium.org/driver/) executable in your PATH variable
 3. Python3 with Selenium, Asyncio & Discord.py installed

## Usage

Clone the repo
```
git clone https://github.com/firejoust/rta_booking_information_discord
```

Set your working directory to the repo
```
cd rta_booking_information_discord
```

Copy and modify the sample settings file
```
cp settings_sample.json settings.json
```

Firstly, acquire a discord bot token from https://discord.com/developers. Change the license details & family name. if you already have a booking, set the flag to true. If you leave the centres `null` all centres will be
searched. Wait timer is how long the script will wait for the site to load. Refresh timer is how often (after scraping timeslots) that the script should restart.

Run the script (for bash based systems e.g. mac/linux/WSL)
```
./scrape_availability.py
```

Run the script (for windows) 
```
python3 scrape_availability.py
```
After the script is running, you must send a message to your discord bot to determine the correct message channel:
```
$register
```
The process can be gracefully stopped with the following command:
```
$stop
```

This has been tested to work in my system but there are numerous edge cases 
where this might fail.
 - Your account status is different to mine
 - RTA changes website.
 - RTA IT team blocks your IP
 - The website is very slow

If the website is slow and the script fails at selecting the driving test on a new booking
try increasing the wait_timer.

## Disclaimer:

 - For personal use only. 
 - Dont break the law or cause disruption using this.
 - Using automated scripts irresponsibily can cause booking loss, disruption of services etc. be careful and know what you are doing.
 - You are responsible for your actions.
