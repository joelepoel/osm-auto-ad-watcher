import time
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import sys, os

#source venv/bin/activate to work in the virtual environment

def main():
    #Reads from config.txt
    config_path = get_path("config.txt")

    username = None
    password = None

    with open(config_path, "r") as f:
        for line in f:
            if line.startswith("username"):
                username = line.split('"')[1]
            elif line.startswith("password"):
                password = line.split('"')[1]
            elif line.startswith("dutch_osm"):
                if 'true' in line.lower():
                    dutch_osm = True
                else:
                    dutch_osm = False
            elif line.startswith("headless"):
                if 'true' in line.lower():
                    headless = True
                else:
                    headless = False

    #Sets options for the driver
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--width=1920")
    options.add_argument("--height=1080")
    options.set_preference("media.volume_scale", "0.0")

    if dutch_osm:
        url = 'https://www.onlinesoccermanager.nl/'
    else:
        url = 'https://www.onlinesoccermanager.com/'

    #Sets driver
    driver = webdriver.Firefox(options = options)
    driver.get(url)                       #Getting the given OSM url
    print('getting osm...')
    assert 'OSM' in driver.title          #Checks if you are on OSM website
    print('The bot is now on the OSM website')


    login(driver, username, password)      #Logs in the user with the credentials given in the personal.py file
    adwatcher(driver)                      #Ad watching function

    #driver.close()
    #print('succesfully closed tab')


def login(driver, username, password):   #The whole process of logging in, accepting cookies and getting past the pop ups
    if driver.find_elements(By.CSS_SELECTOR, '.btn-new.btn-orange'):            #If the terms and conditions page loads
        print('Found the accept button')
        time.sleep(sleeptime())
        button = driver.find_element(By.CSS_SELECTOR, '.btn-new.btn-orange')   #Finds the accept button
        button.click()                                                      #Clicks to accept terms and conditions
        print('Accepted terms and conditions!')
    

    if driver.find_elements(By.CLASS_NAME, 'register-title'):    #If opens register page instead of login page
        print('Currently on register page')
        time.sleep(sleeptime())
        login_button = driver.find_element(By.CLASS_NAME, 'btn-alternative')
        login_button.click()
        print('Redirected to login page')

    time.sleep(sleeptime())
    usernamefield = driver.find_element(By.ID, 'manager-name')              #Finds the username field
    print('Found username field')
    usernamefield.clear()
    usernamefield.send_keys(username)                                       #Inputs username
    time.sleep(sleeptime())
    passwordfield = driver.find_element(By.ID, 'password')                  #Finds the password field
    print('Found password field')
    passwordfield.clear()
    passwordfield.send_keys(password)                                       #Inputs password
    passwordfield.send_keys(Keys.RETURN)
    print('Succesfully logged in!')
    time.sleep(5)

def get_path(filename):
    if hasattr(sys, '_MEIPASS'):
        # Running as PyInstaller EXE → get folder of the EXE
        base_dir = os.path.dirname(sys.executable)
    else:
        # Running as normal script
        base_dir = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_dir, filename)

def adwatcher(driver):
    wallet_is_open = False
    while True:
        try:
            #All the checks
            if driver.find_elements(By.CLASS_NAME, 'fc-button-label'):   #If cookies message
                button = driver.find_element(By.CLASS_NAME, 'fc-button-label')  #Finds accept cookies
                button.click()
                print('Accepted cookies')
                time.sleep(sleeptime())

            if driver.find_elements(By.ID, 'skillRatingUpdate-modal-content'):    #In case of an XP-up/level-up screen
                print('Had an XP-screen')
                driver.execute_script("""
                    const el = document.elementFromPoint(1200, 50);
                    if (el) el.click();
                """)    #Clicks next to XP window to close it
                print('Clicked on backdrop to close XP-screen')
                time.sleep(sleeptime())
            
            if driver.find_elements(By.CSS_SELECTOR, '.btn-new.btn-primary.btn-auto-width'): #In case of an Open to-do-list screen
                print('Had a to-do-list screen')
                button = driver.find_element(By.CSS_SELECTOR, '.btn-new.btn-primary.btn-auto-width')
                button.click()
                print('Opened to-do-list')
                time.sleep(sleeptime())

            if driver.find_elements(By.ID, 'centerpopup-modal-content'):    #In case of an ingame news pop up when opening a page
                print('Had a news pop up')
                driver.execute_script("""
                    const el = document.elementFromPoint(1200, 50);
                    if (el) el.click();
                """)    #Clicks next to pop up window window to close it
                print('Clicked on backdrop to close pop up window')

            if wallet_is_open == False:
            #Opens the boss-coin wallet after all the checks
                wallet = driver.find_element(By.CSS_SELECTOR,'.wallet-amount.pull-left.center')
                wallet.click()  #Opens the Bosscoin wallet
                wallet_is_open = True
                print('Opened Boss-coin wallet')
                time.sleep(sleeptime())

            #Clicks the ad button for a free boss-coin
            ad_button = driver.find_elements(By.CSS_SELECTOR, '.product.product-small.product-free')
            if ad_button:
                ad_button[0].click()
                print('Fetched an ad')
                time.sleep(4)

                if driver.find_elements(By.CLASS_NAME, 'modal-title'):    #If OSM doesnt play an ad, because you have to wait to see more ads
                    #Clicks off the can't watch anymore ads message
                    driver.execute_script("""
                        const el = document.elementFromPoint(1200, 50);
                        if (el) el.click();
                    """)    #Clicks next to no more ads window to close it
                    print('Closed no more ads window')
                    time.sleep(sleeptime())

                    if driver.find_elements(By.CSS_SELECTOR,".product-body.claim-daily-reward:not(.disabled-product)"):    #Checks for claimable free boss coins
                        print('Bonus boss-coin claimable')
                        bonus = driver.find_element(By.CSS_SELECTOR,".product-body.claim-daily-reward")
                        bonus.click()
                        print('Claimed free daily bonus!')
                    else:
                        print('No daily free boss-coins claimable right now...')
                    
                    #Checks what time it is, so it will give a correct message on when it will try again
                    current_time = time.localtime()
                    try_hour = str(current_time.tm_hour + 1)
                    if len(try_hour) == 1:
                        try_hour = f"0{try_hour}"
                    elif try_hour == "24":
                        try_hour = "00"

                    try_minute = str(current_time.tm_min)
                    if len(try_minute) == 1:
                        try_minute = f"0{try_minute}"
                    print(f"Can't watch anymore ads, trying again at {try_hour}:{try_minute}")

                    time.sleep(3600)
                    print('Waited an hour. Trying again.')
                    driver.refresh()    #Refreshes page, so the bot can try again.
                    wallet_is_open = False
                    time.sleep(7)
                    continue

                elif driver.find_elements(By.ID, 'videoad'):  #In case OSM plays an actual ad
                    print('OSM is playing an ad.')
                    waiting = 0
                    video_stuck = False
                    while True:
                        if driver.find_elements(By.CSS_SELECTOR, '.product.product-small.product-free'):
                            print('Ad ended. Giving it some time to close...')
                            time.sleep(4)
                            break
                        print('Waiting for ad to end...')
                        waiting += 1
                        if waiting >= 30:   #If the ad takes too long or the site crashes mid ad
                            print('Bot is probably stuck, refreshing and trying again.')
                            driver.refresh()
                            wallet_is_open = False
                            time.sleep(7)
                            video_stuck = True
                            break
                        time.sleep(5)
                    if video_stuck: #If the video got stuck
                        continue    #Restarts while loop

                else:   #If OSM tries to fetch you an ad, but the ad window closes prematurely, still giving you the reward. Only happens if ad video closes within the 4 seconds of wait time given earlier.
                    print('No ad was loaded, but you did get a reward!')
                    time.sleep(sleeptime())
                    continue

            else:
                print('Ad button hasnt loaded yet, trying again in 5 seconds...')
                time.sleep(5)
            
        except Exception as e:  #In case something goes wrong
            print(f'Error: {e}')
            print('Retrying now...')
            driver.refresh()
            wallet_is_open = False
            time.sleep(sleeptime())
            continue


def sleeptime():    #Returns random float between 1 and 4.3, to slow down process a little and make it appear more human
    return random.uniform(1.0,4.3)  #Randomizes
    #return 1                       #Sets to 1 second for faster result, but higher risk of getting caught


if __name__ == '__main__':
    main()