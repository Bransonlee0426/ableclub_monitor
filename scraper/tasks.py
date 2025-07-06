from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup, Tag
import time
import os

def run_scraping_task():
    """
    Placeholder for the main web scraping logic.
    This function will be called to initiate the scraping process.
    """
    print("Executing scraping task...")
    # Business logic for scraping will be implemented here.
    pass

def scrape_main_menu():
    """
    Scrapes the main menu items from the AbleClub Taiwan website.
    """
    url = "https://ableclub.advantech.com.tw/Taiwan/zh-tw"
    driver = webdriver.Chrome()  # Assumes chromedriver is in your PATH
    driver.get(url)

    try:
        # Wait for the main menu container to be present in the DOM
        # This ensures the page is fully loaded before we try to parse it
        wait = WebDriverWait(driver, 10)
        wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "mainmenu-inner"))
        )
        
        print("Successfully located the main menu container.")

        # Get the page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find the menu container in the parsed soup
        main_menu_container = soup.find('div', class_='mainmenu-inner')
        
        if main_menu_container and isinstance(main_menu_container, Tag):
            # Find all h3 tags within the container
            menu_items = main_menu_container.find_all('h3')
            
            print("\n--- AbleClub Main Menu ---")
            for item in menu_items:
                if isinstance(item, Tag):
                    print(item.get_text(strip=True))
            print("--------------------------\n")
        else:
            print("Could not find 'mainmenu-inner' container in BeautifulSoup.")

    except TimeoutException as e:
        # This block executes when the wait times out
        print("Timeout: The element 'mainmenu-inner' was not found within 10 seconds.")
        print(f"Error details: {e}")

        # Define the logs directory
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True) # Ensure the directory exists

        # Generate a unique filename using a timestamp
        timestamp = int(time.time())
        screenshot_file = os.path.join(log_dir, f"debug_screenshot_{timestamp}.png")
        page_source_file = os.path.join(log_dir, f"debug_page_{timestamp}.html")

        # Save the screenshot of the current page
        driver.save_screenshot(screenshot_file)
        print(f"Saved screenshot for debugging: {screenshot_file}")

        # Save the HTML source of the current page
        with open(page_source_file, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"Saved page source for debugging: {page_source_file}")
    
    finally:
        # Close the browser
        driver.quit()

if __name__ == "__main__":
    scrape_main_menu()
