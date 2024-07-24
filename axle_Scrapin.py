from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
from typing import Tuple
import undetected_chromedriver as uc


def handle_driver_quit(driver: uc.Chrome, returned_values: tuple):
    driver.quit()
    return returned_values


def check_if_element_loaded(driver: uc.Chrome, element_code: str, element: str, silent: bool = True, success_message: str = "", fail_message: str = "", wait_time: int = 1):
    if success_message == "":
        success_message = f"Found {element}"
    if fail_message == "":
        wait_time_seconds: str = "seconds"
        if wait_time == 1:
            wait_time_seconds = "second"
        fail_message = f"Did not find {element}. Waiting {wait_time} {wait_time_seconds}."

    try:
        driver.find_element(element_code, element)
        if not silent:
            print(success_message)
        return True
    except:
        if not silent:
            print(fail_message)
        time.sleep(wait_time)
        return False


def wait_for_element_to_load(driver: uc.Chrome, element_code: str, element: str, silent: bool = True, success_message: str = "", fail_message: str = "", wait_time: int = 1):
    if success_message == "":
        success_message = f"Found {element}"
    if fail_message == "":
        wait_time_seconds: str = "seconds"
        if wait_time == 1:
            wait_time_seconds = "second"
        fail_message = f"Did not find {element}. Waiting {wait_time} {wait_time_seconds}."

    kill_switch_counter = 0
    element_loaded = False
    while not element_loaded:
        element_loaded = check_if_element_loaded(
            driver, element_code, element, silent, success_message, fail_message, wait_time)
        kill_switch_counter += 1
        if kill_switch_counter >= 30:
            print(
                f"Could not find element {element} after 30 tries. Kill switch initiated. Restarting on page {CURRENT_PAGE}.")
            return_values: Tuple[int, int] = handle_driver_quit(
                driver, (MAX_PAGE_NUMBER, CURRENT_PAGE))
            return return_values
    return driver.find_element(element_code, element)


def create_selenium_driver():
    PATH = "data-axl Scrape\drivers\chromedriver_win32\chromedriver.exe"

    driver_options = webdriver.ChromeOptions()
    driver_options.add_argument("--incognito")
    driver_options.add_experimental_option(
        "excludeSwitches", ['enable-automation', 'enable-logging'])
    driver_options.add_experimental_option("detach", True)

    # driver = webdriver.Chrome(options=driver_options, executable_path=PATH)
    driver = uc.Chrome()
    return driver


def login_to_library():
    driver = create_selenium_driver()
    liburl = "https://discover.omahalibrary.org/iii/cas/login?service=https%3A%2F%2Fdiscover.omahalibrary.org%3A443%2Fpatroninfo~S1%2F0%2Fredirect%3D%2Fwamvalidate%3Furl%3Dhttp%253A%252F%252F0-referenceusa.com.discover.omahalibrary.org%253A80%252FHome%252FHomeIIITICKET&scope=1"

    driver.get(liburl)
    print(driver.title)
    # sign into lib and enters axl
    username = wait_for_element_to_load(driver, "id", "code")
    # your username/lib card
    username.send_keys("******") 
    password = wait_for_element_to_load(driver, "id", "pin")
    # your password/pin for lib card
    password.send_keys("****")
    password.send_keys(Keys.RETURN)

    return driver


def wait_for_origin_loading(driver: uc.Chrome):
    origin_loading = True
    while origin_loading:
        origin_loading = check_if_element_loaded(
            driver, 'class', 'originLoading')
    time.sleep(1)


def select_companies_multiple_pages(driver: uc.Chrome):
    for x in range(6):
        current_page = wait_for_element_to_load(
            driver, 'xpath', '//*[@id="searchResults"]/div[1]/div/div[1]/div[2]/div[2]').text
        if check_if_element_loaded(driver, 'xpath', '//*[@id="captchaValidationMessage"]'):
            print(
                f"Capcha found. Waiting 1 minute, then restarting at page {current_page}.")
            time.sleep(60)
            return int(current_page)
        if int(current_page) <= MAX_PAGE_NUMBER:
            print(f"Selecting page {current_page}.")
            wait_for_origin_loading(driver)
            wait_for_element_to_load(
                driver, "xpath", '//*[@id="checkboxCol"]').click()
            time.sleep(3)
            wait_for_element_to_load(
                driver, 'xpath', '//*[@id="searchResults"]/div[1]/div/div[1]/div[2]/div[3]').click()
            wait_for_origin_loading(driver)
    current_page = wait_for_element_to_load(
        driver, 'xpath', '//*[@id="searchResults"]/div[1]/div/div[1]/div[2]/div[2]').text
    return int(current_page)


def select_companies(driver: uc.Chrome):
    current_page = wait_for_element_to_load(
        driver, 'xpath', '//*[@id="searchResults"]/div[1]/div/div[1]/div[2]/div[2]').text
    current_page = int(current_page)
    if current_page <= MAX_PAGE_NUMBER:
        print(f"Selecting page {current_page}.")
        wait_for_origin_loading(driver)
        wait_for_element_to_load(
            driver, "xpath", '//*[@id="checkboxCol"]').click()
    return current_page + 1


def wait_for_download(driver: uc.Chrome):
    if not driver.current_url.startswith("chrome://downloads"):
        driver.get("chrome://downloads/")
    return driver.execute_script("""
        var items = document.querySelector('downloads-manager')
            .shadowRoot.getElementById('downloadsList').items;
        if (items.every(e => e.state === "COMPLETE"))
            return items.map(e => e.fileUrl || e.file_url);
        """)


def download_records(driver: uc.Chrome):
    # Clicks the download button
    wait_for_element_to_load(
        driver, 'xpath', '//*[@class="action download action-download"]').click()
    # Selects the right options for the download
    wait_for_element_to_load(
        driver, 'xpath', '//*[@id="format_excel_2007"]').click()
    wait_for_element_to_load(
        driver, 'xpath', '//*[@id="detailDetail"]').click()
    # Downloads the records
    wait_for_element_to_load(
        driver, 'xpath', '//*[@id="downloadForm"]/div[3]/a[1]/span/span').click()
    time.sleep(2)
    wait_for_download(driver)


def get_to_search_results(current_page_number: int) -> Tuple[int, int]:
    driver = login_to_library()
    datAxlSearch = "http://www.referenceusa.com/UsBusiness/Search/Custom/6ff73909a0824a4193efd45fe6668e70"

    # brings to advanced search page
    driver.get(datAxlSearch)
    print(driver.title)
    time.sleep(1)
    if "LogOn" in driver.current_url:
        print(f"Page failed to load. Trying again with {current_page_number}.")
        return_values: Tuple[int, int] = handle_driver_quit(
            driver, (MAX_PAGE_NUMBER, current_page_number))
        return return_values

    # checks the keyword/sic/naics
    wait_for_element_to_load(
        driver, 'xpath', '//*[@id="cs-YellowPageHeadingOrSic"]').click()
    wait_for_element_to_load(
        driver, 'xpath', '//*[@id="naicsPrimaryOptionId"]').click()
    naisicId = wait_for_element_to_load(
        driver, 'xpath', '//*[@id="naicsLookupKeyword"]')
    # Searches the Primary NAICS Only code
    naisicId.send_keys('561720')
    # Waits for the results to load, and if they aren't loaded, waits until they are loaded
    wait_for_element_to_load(driver, 'xpath',
                             '//*[@id="naicsKeyword"]/ul/li[1]', True,
                             "Cleaning services found. Continuing selections.",
                             "Cleaning services not found. Waiting 2 seconds before trying again.",
                             1).click()
    driver.find_element('xpath', '//*[@id="naicsKeyword"]/ul/li[2]').click()
    driver.find_element('xpath', '//*[@id="naicsKeyword"]/ul/li[3]').click()
    driver.find_element('xpath', '//*[@id="naicsKeyword"]/ul/li[4]').click()
    driver.find_element('xpath', '//*[@id="naicsKeyword"]/ul/li[5]').click()
    driver.find_element('xpath', '//*[@id="naicsKeyword"]/ul/li[6]').click()
    driver.find_element('xpath', '//*[@id="naicsKeyword"]/ul/li[7]').click()
    driver.find_element(
        'xpath', '//*[@id="dbSelector"]/div/div[2]/div[1]/div[3]/div/a[1]').click()
    max_page_number = wait_for_element_to_load(
        driver, 'xpath', '//*[@id="searchResults"]/div[1]/div/div[1]/div[1]/span[2]', True, "Found max page count", "Waiting for max page count to load.").text

    # For some reason the page number element itself loads, but the correct number doesn't.
    # This while loop tries to grab the real number every second while the page number is an empty string.
    # Need the time.sleep(1) here because the element has loaded, but the value is wrong.
    while max_page_number == "":
        max_page_number = wait_for_element_to_load(
            driver, 'xpath', '//*[@id="searchResults"]/div[1]/div/div[1]/div[1]/span[2]', True, "Attempting to get correct page count.").text
        time.sleep(1)
    max_page_number = int(max_page_number.replace(',', ''))
    # Grabs the page text box
    page_box = wait_for_element_to_load(
        driver, 'xpath', '//*[@id="searchResults"]/div[1]/div/div[1]/div[2]/div[2]')
    # Puts the current page number into the text box
    ActionChains(driver).click(page_box).send_keys(
        str(current_page_number)).send_keys(Keys.RETURN).perform()
    current_page = select_companies(driver)
    download_records(driver)
    return_values: Tuple[int, int] = handle_driver_quit(
        driver, (max_page_number, current_page))
    return return_values


MAX_PAGE_NUMBER: int
CURRENT_PAGE: int = 1
page_counter: int
MAX_PAGE_NUMBER = 1551
MAX_PAGE_NUMBER, page_counter = get_to_search_results(1)
print(f"There are {MAX_PAGE_NUMBER} pages to loop through.")

returned_max_page_number: int = MAX_PAGE_NUMBER
while page_counter <= MAX_PAGE_NUMBER:
    print(f"On page {page_counter} of {MAX_PAGE_NUMBER}")
    CURRENT_PAGE = page_counter
    returned_max_page_number, page_counter = get_to_search_results(
        page_counter)
