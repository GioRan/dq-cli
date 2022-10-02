import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyvirtualdisplay import Display


class Browser:

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--user-data-dir=C:\\Users\\giora\\AppData\\Local\\Google\\Chrome\\User Data")
        chrome_options.add_argument('--profile-directory=Profile 1')
        chrome_options.add_argument("--disable-extensions") # use in headless
        chrome_options.add_argument("--disable-gpu") # use in headless
        # chrome_options.add_argument("--no-sandbox") # linux only
        # chrome_options.add_argument("--headless") # use in headless
        # chrome_options.headless = True
        # chrome_options.add_argument('--window-size=1920,1080')
        # chrome_options.add_argument('--ignore-certificate-errors')
        # chrome_options.add_argument('--allow-running-insecure-content')
        # chrome_options.add_argument('--remote-debugging-port=9222')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
        # chrome_options.add_argument("--disable-dev-shm-usage'")

        # self.display = Display(visible=False, size=(800, 600)) # run on linux
        # self.display.start() # run on linux

        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

        # project_folder = os.path.dirname(os.path.realpath(__file__))
        # self.driver = webdriver.Chrome(executable_path=f'{project_folder}{os.sep}chromedriver_windows.exe', options=chrome_options) # explicit driver path
        self.user_email = 'zgranoa@globe.com.ph'
        self.sleep_timer = 3

    def open_url(self, url: str) -> None:
        self.driver.get(url)

    def close(self):
        # self.display.stop() # run on linux
        self.driver.close()

    def navigate(self):
        time.sleep(self.sleep_timer)

        self.driver.find_element(By.XPATH, f"//div[@data-identifier='{self.user_email}']").click()

        time.sleep(self.sleep_timer)
        self.driver.find_element(By.XPATH, "//span[normalize-space()='Continue']").click()

        time.sleep(self.sleep_timer)
        checkboxes = self.driver.find_elements(By.XPATH, "(//input[contains(@type,'checkbox')])/parent::div")

        [c.click() for c in checkboxes]

        time.sleep(self.sleep_timer)
        self.driver.find_element(By.XPATH, "//span[normalize-space()='Continue']/parent::button").click()