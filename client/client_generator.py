import time
import os
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config import LocalConfig

class ClientGenerator:
    usernames = ['Alessandra', 'Matheus', 'Paulo']
    signal_files = []

    def __init__(self):
        self.__config = LocalConfig('./config.json')
        LocalConfig.SetDefault(self.__config)
        self.init_signal_files()

    def init_signal_files(self):
        path = LocalConfig.GetDefault().getSignalsFolderPath()
        try:
            files = os.listdir(path)
            self.signal_files = [os.path.join(path, file) for file in files]
    
        except FileNotFoundError:
            print(f"The directory '{path}' was not found.")

        except Exception as e:
            print(f"An error occurred: {e}")

    def init_driver(self):
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")  # Run headless for background execution
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    
    def create_client(self, driver):
        driver.get('http://localhost:5005/index.html')

        user_field = driver.find_element(By.ID, 'user')
        user_field.send_keys(random.choice(self.usernames))

        use_gain_checkbox = driver.find_element(By.ID, 'useGain')
        if random.choice([True, False]):
            use_gain_checkbox.click()

        model_select = Select(driver.find_element(By.ID, 'model'))
        # model_select.select_by_value(str(random.choice([1, 2]))) # uncomment this line to select a random model
        model_select.select_by_value(str(2)) # comment this line if you want to select a random model

        signal_file_input = driver.find_element(By.ID, 'signalFile')
        signal_file_input.send_keys(random.choice(self.signal_files))

        submit_button = driver.find_element(By.XPATH, "//button[text()='Submit']")
        submit_button.click()
    
    def download_image(self, driver):
        # TODO: define a good timeout
        timeout = 1000
        try:
            image_element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.ID, "jobImage"))
            )

            WebDriverWait(driver, timeout).until(
                lambda d: image_element.get_attribute("src") not in [None, "", "data:,"]
            )

            download_button = driver.find_element(By.ID, "downloadImage")
            download_button.click()
            time.sleep(2)

        except Exception as e:
            print(f"An error occurred while waiting for the image: {e}")

    def run(self):
        while True:
            driver = self.init_driver()
            try:
                self.create_client(driver)
                self.download_image(driver)
            finally:
                driver.quit()
            time.sleep(20)

if __name__ == "__main__":
    generator = ClientGenerator()
    generator.run()