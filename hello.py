from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import csv

url = "https://www.dst.dk/da/Statistik/emner/befolkning-og-valg/navne/HvorMange"
PATH = "C:\Program Files (x86)\ChromeDriver\chromedriver.exe"
driver = webdriver.Chrome(PATH)
# The browser we use is chrome and the driver is located in PATH


driver.get(url)


cookieButton = driver.find_element_by_id("cookieDst-reject")
searchInput = driver.find_element_by_id("navnesognamefornavn")
searchButton = driver.find_element_by_id("navnesognamesog")
results = driver.find_element_by_id("navnesognameresult")
clearButton = driver.find_element_by_id("navnesognameryd")
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
            )  # wait until table is available

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
                    new_data[name] = {
                        "gender": values[0].get("gender", ""),
                        "peopleTotal": str(int(values[0].get("2023", 0))),
                        "trendTotal": str(int(values[0].get("trend", 0))),
                        (
                            "malesTotal"
                            if values[0].get("gender", "") == "male"
                            else "femalesTotal"
                        ): str(int(values[0].get("2023", 0))),
                        (
                            "trendMales"
                            if values[0].get("gender", "") == "male"
                            else "trendFemales"
                        ): str(int(values[0].get("trend", 0))),
                    }
                else:
                    new_data[name] = {
                        "gender": [
                            values[0].get("gender", 0),
                            values[1].get("gender", 0),
                        ],
                        "peopleTotal": str(
                            int(values[0]["2023"]) + int(values[1]["2023"])
                        ),
                        "trendTotal": str(
                            int(values[0]["trend"]) + int(values[1]["trend"])
                        ),
                        (
                            "malesTotal"
                            if values[0].get("gender", "") == "male"
                            else "femalesTotal"
                        ): str(int(values[0].get("2023", 0))),
                        (
                            "malesTotal"
                            if values[1].get("gender", "") == "male"
                            else "femalesTotal"
                        ): str(int(values[1].get("2023", 0))),
                        (
                            "trendMales"
                            if values[0].get("gender", "") == "male"
                            else "trendFemales"
                        ): str(int(values[0].get("trend", 0))),
                        (
                            "trendMales"
                            if values[1].get("gender", "") == "male"
                            else "trendFemales"
                        ): str(int(values[1].get("trend", 0))),
                    }

            resultList.append(new_data)
            # Create and append an object with the name as key and value of zippedList

            clearButton.click()

        except Exception as e:
            print(f"Something went wrong: {e}")
print(json.dumps(resultList, indent=4, ensure_ascii=False))
