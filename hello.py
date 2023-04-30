from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
import csv

PATH = "C:\Program Files (x86)\ChromeDriver\chromedriver.exe"
driver = webdriver.Chrome(PATH)
# The browser we use is chrome and the driver is located in PATH

driver.get("https://www.dst.dk/da/Statistik/emner/befolkning-og-valg/navne/HvorMange")


cookieButton = driver.find_element_by_id("cookieDst-reject")
searchInput = driver.find_element_by_id("navnesognamefornavn")
searchButton = driver.find_element_by_id("navnesognamesog")
results = driver.find_element_by_id("navnesognameresult")
clear = driver.find_element_by_id("navnesognameryd")
resultList = []

cookieButton.click()

with open("C:/codetemp/python/names.csv", "r", encoding="UTF-8") as csv_read_file:
    csv_reader = csv.reader(csv_read_file)

    for line in csv_reader:  # for every line in the csv files
        searchInput.send_keys(line)  # add line to input and search
        searchButton.click()

        try:
            main = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "table"))
            )  # wait until table is available

            data = main.find_elements_by_tag_name("td")
            for cell in data:
                resultList.append(cell.text)
                # for every cell add the text to the result list
            clear.click()

            with open(
                "data.csv", mode="a", newline="", encoding="UTF-8"
            ) as csv_write_file:
                csv_writer = csv.writer(
                    csv_write_file,
                    delimiter=",",
                    quotechar='"',
                    quoting=csv.QUOTE_MINIMAL,
                )

                # add a row of information from the result list
                csv_writer.writerow(resultList)
                resultList.clear()

        except:
            print("Something went wrong")
