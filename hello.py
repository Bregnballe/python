from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import csv
import requests

url = "https://www.dst.dk/da/Statistik/emner/befolkning-og-valg/navne/HvorMange"
PATH = "C:\Program Files (x86)\ChromeDriver\chromedriver.exe"
driver = webdriver.Chrome(PATH)
# The browser we use is chrome and the driver is located in PATH
# The driver version must match the browser version


# headers = {"Content-Type": "application/json"}
# url = "http://localhost:3000/api/names/"
# API headers and url


driver.get(url)


cookieButton = driver.find_element_by_id("cookieDst-reject")
searchInput = driver.find_element_by_id("navnesognamefornavn")
searchButton = driver.find_element_by_id("navnesognamesog")
results = driver.find_element_by_id("navnesognameresult")
clearButton = driver.find_element_by_id("navnesognameryd")
# All the html-elements we need to interact with

resultList = []

cookieButton.click()

with open("C:/codetemp/python/names.csv", "r", encoding="UTF-8") as csv_read_file:
    csv_reader = csv.reader(csv_read_file)

    for name in csv_reader:  # for every line in the csv files
        searchInput.send_keys(name)  # add line to input and search
        searchButton.click()  # click the search button

        try:
            table = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "table"))
            )  # wait until html-table is available on page

            tableData = [
                [
                    "female"
                    if cell.text.startswith("Kvinder")
                    else "male"
                    if cell.text.startswith("Mænd")
                    else ""
                    if cell.text.startswith("Der")
                    else "0"
                    if cell.text == ""
                    else cell.text
                    for cell in row.find_elements_by_tag_name("td")
                ]
                for row in table.find_elements_by_tag_name("tr")
            ][1:]
            # The [1:] removes the first row (tr) which is the header row.

            tableHeader = [
                [
                    "gender"
                    if cell.text.startswith("Resultat")
                    else "trend"
                    if cell.text.startswith("Ændring")
                    else cell.text
                    for cell in row.find_elements_by_tag_name("th")
                ]
                for row in table.find_elements_by_tag_name("tr")
            ][0]
            # The [0] selects only the first row (tr) which is the header row.

            zippedList = [dict(zip(tableHeader, t)) for t in tableData]
            # zipping the two lists together and turn them into a dictionary (like an object)

            data = {name[0]: zippedList}

            print(json.dumps(data, indent=4, ensure_ascii=False))

            new_data = {}

            for name, values in data.items():
                if len(values) == 1:
                    # if there is only one row in the table ie. one gender with that name
                    new_data = {
                        "name": name,
                        "male": values[0].get("gender", "") == "male",
                        "female": values[0].get("gender", "") == "female",
                        # the second argument on the get method is the default value if the key is not found
                        "peopleCount": str(int(values[0].get("2023", 0))),
                        "trendCount": str(int(values[0].get("trend", 0))),
                        (
                            "maleCount"
                            if values[0].get("gender", "") == "male"
                            else "femaleCount"
                        ): str(int(values[0].get("2023", 0))),
                        (
                            "femaleCount"
                            if values[0].get("gender", "") == "male"
                            else "maleCount"
                        ): 0,
                        # setting the count of the gender that is not represented to 0
                        (
                            "maleTrendCount"
                            if values[0].get("gender", "") == "male"
                            else "femaleTrendCount"
                        ): str(int(values[0].get("trend", 0))),
                        (
                            "femaleTrendCount"
                            if values[0].get("gender", "") == "male"
                            else "maleTrendCount"
                        ): 0,
                        # setting the trend count of the gender that is not represented to 0
                    }
                else:
                    # if there are more rows
                    new_data = {
                        "name": name,
                        "male": True,
                        "female": True,
                        # Since there are more than one gender, we know both genders are represented
                        "totalPeople": str(
                            int(values[0]["2023"]) + int(values[1]["2023"])
                        ),
                        "trendCount": str(
                            int(values[0]["trend"]) + int(values[1]["trend"])
                        ),
                        (
                            "maleCount"
                            if values[0].get("gender", "") == "male"
                            else "femaleCount"
                        ): str(int(values[0].get("2023", 0))),
                        (
                            "maleCount"
                            if values[1].get("gender", "") == "male"
                            else "femaleCount"
                        ): str(int(values[1].get("2023", 0))),
                        (
                            "maleTrendCount"
                            if values[0].get("gender", "") == "male"
                            else "femaleTrendCount"
                        ): str(int(values[0].get("trend", 0))),
                        (
                            "maleTrendCount"
                            if values[1].get("gender", "") == "male"
                            else "femaleTrendCount"
                        ): str(int(values[1].get("trend", 0))),
                    }

            resultList.append(new_data)
            # Create and append an object with the name as key and value of zippedList

            clearButton.click()

        except Exception as e:
            print(f"Something went wrong: {e}")

print(json.dumps(resultList, indent=4, ensure_ascii=False))
