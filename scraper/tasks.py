# scraper/tasks.py (Refactored to use Playwright with fallback handling)

import asyncio
import subprocess
import sys
from typing import List, Dict
import time
import os
import logging

logger = logging.getLogger(__name__)

# Try to import Playwright, install if not available
try:
    from playwright.async_api import async_playwright, Page, Error
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    logger.warning("Playwright not available, will attempt installation on first use")
    PLAYWRIGHT_AVAILABLE = False
    async_playwright = None
    Page = None
    Error = None

async def ensure_playwright_installed():
    """
    Ensure Playwright is installed and browsers are available
    """
    global PLAYWRIGHT_AVAILABLE, async_playwright, Page, Error
    
    if PLAYWRIGHT_AVAILABLE:
        return True
        
    try:
        logger.info("正在安裝 Playwright...")
        # Install playwright package if not available
        subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
        
        # Install browsers
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        
        # Re-import after installation
        from playwright.async_api import async_playwright, Page, Error
        PLAYWRIGHT_AVAILABLE = True
        
        logger.info("Playwright 安裝完成")
        return True
        
    except Exception as e:
        logger.error(f"Playwright 安裝失敗: {e}")
        return False

# --- Function 1: Scrape Main Menu ---
async def scrape_main_menu(page: Page) -> List[str]:
    """
    (Playwright Version)
    Scrapes the main menu items from the AbleClub homepage.
    
    Args:
        page: An active Playwright Page object.

    Returns:
        A list of strings for each main menu item.
    """
    print("正在爬取主選單項目...")
    # Wait for the menu container to be present and visible
    await page.wait_for_selector(".mainmenu-inner", state="visible")
    menu_container = page.locator(".mainmenu-inner")
    
    # Locate all h3 elements within the container
    menu_items_locators = menu_container.locator("h3")
    main_menu_items = await menu_items_locators.all_text_contents()
    
    # Clean up whitespace from the extracted text
    main_menu_items = [item.strip() for item in main_menu_items]
    
    print(f"成功取得主選單: {main_menu_items}")
    return main_menu_items

# --- Function 2: Scrape Corporate Events ---
async def scrape_corporate_events(page: Page) -> List[Dict]:
    """
    Filters for '報名中活動' (Events Open for Registration) and scrapes their titles across all pages
    by handling pagination. Assumes the page is already on the '公司活動' page.

    Args:
        page: The Playwright Page object on the corporate events page.

    Returns:
        A list of dictionaries containing event details (title, start_date, end_date) found across all pages.
    """
    print("檢查並篩選「報名中活動」，然後爬取所有頁面的標題...")

    # Check current filter status first
    try:
        # Wait for the filter menu to be present
        await page.wait_for_selector("#ableclub-filter-menu", timeout=10000)
        
        # Get the current filter text from the dropdown button
        current_filter_element = page.locator("#ableclub-filter-menu .dropdown a")
        current_filter_text = await current_filter_element.text_content()
        print(f"目前篩選狀態: {current_filter_text}")
        
        # Only change filter if it's not already set to "報名中活動"
        if current_filter_text != "報名中活動":
            print("需要切換到「報名中活動」篩選...")
            # Click the filter dropdown
            await page.locator("#ableclub-filter-menu").click()
            
            # Wait for dropdown options to appear
            await page.wait_for_selector("a.dropdown-item", timeout=5000)
            
            # Click the "報名中活動" option
            await page.locator("a.dropdown-item").get_by_text("報名中活動", exact=True).click()
            print("已切換到「報名中活動」篩選")
        else:
            print("篩選已經是「報名中活動」，無需變更")
            
    except Exception as e:
        print(f"篩選狀態檢查失敗，嘗試直接點擊篩選: {e}")
        # Fallback to original logic if checking fails
        try:
            await page.locator("#ableclub-filter-menu").click()
            await page.locator("a.dropdown-item").get_by_text("報名中活動", exact=True).click()
        except Exception as fallback_error:
            print(f"篩選操作完全失敗: {fallback_error}")
            # Continue anyway in case the filter is already correct

    all_event_data = []
    page_number = 1

    while True:
        # 1. Wait for the event cards to be loaded dynamically by JavaScript.
        # We'll wait for the first '.card' element to appear, which indicates the AJAX call is complete.
        await page.wait_for_selector('.card', state='visible', timeout=15000)
        print(f"正在爬取第 {page_number} 頁...")

        # 2. Scrape data from the current page.
        card_group_container = page.locator(".ableclub-cardgroup")
        
        # Get all event cards on current page
        event_cards = await card_group_container.locator(".card").all()
        current_page_events = []
        
        for card in event_cards:
            try:
                # Extract title from h3.card-title
                title_element = card.locator("h3.card-title")
                title = await title_element.text_content()
                title = title.strip() if title else ""
                
                # Check if p.text-date exists and extract dates
                start_date = ""
                end_date = ""
                
                date_element = card.locator("p.text-date")
                if await date_element.count() > 0:
                    # Get all time elements within p.text-date
                    time_elements = await date_element.locator("time").all()
                    
                    if len(time_elements) >= 1:
                        start_date_text = await time_elements[0].text_content()
                        start_date = start_date_text.strip() if start_date_text else ""
                    
                    if len(time_elements) >= 2:
                        end_date_text = await time_elements[1].text_content()
                        end_date = end_date_text.strip() if end_date_text else ""
                
                event_data = {
                    "title": title,
                    "start_date": start_date,
                    "end_date": end_date
                }
                
                current_page_events.append(event_data)
                print(f"  - {title} | 開始: {start_date} | 結束: {end_date}")
                
            except Exception as e:
                print(f"爬取單一活動時發生錯誤: {e}")
                # Continue processing other events
                continue
        
        all_event_data.extend(current_page_events)
        print(f"本頁找到 {len(current_page_events)} 個活動。")

        # 3. Locate the 'Next' button and check its state.
        # The specific selector for the 'Next' page <li> element.
        next_page_li_selector = ".page-item.PagedList-skipToNext"
        next_page_li = page.locator(next_page_li_selector)

        # Check if the 'Next' button is disabled.
        is_disabled = "disabled" in (await next_page_li.get_attribute("class") or "")

        # 4. Decide whether to continue or break the loop.
        if not is_disabled:
            # If the button is not disabled, click it to go to the next page.
            print("「下一頁」按鈕可用，準備換頁...")
            await next_page_li.locator("a").click()
            # Add a small delay to be respectful to the server and ensure stability.
            await page.wait_for_timeout(1000)
            page_number += 1
        else:
            # If the button is disabled, it means we are on the last page.
            print("「下一頁」按鈕已禁用，已到達最後一頁。")
            break
            
    # 5. Return the final list of all event data.
    return all_event_data

# --- Function 3: Main Orchestrator ---
async def run_ableclub_scraper():
    """
    Orchestrates the entire scraping process from start to finish using Playwright.
    """
    # Ensure Playwright is available before proceeding
    if not await ensure_playwright_installed():
        logger.error("無法安裝 Playwright，爬蟲任務無法執行")
        return {"error": "Playwright installation failed", "total_scraped": 0, "total_saved_new": 0}
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            print("導航至 ABLE Club 首頁...")
            await page.goto("https://ableclub.advantech.com.tw/Taiwan/zh-tw", wait_until="domcontentloaded")
            
            # Step 1: Scrape the main menu to get available categories
            menu_items = await scrape_main_menu(page)
            
            # Step 2: Conditionally proceed if "公司活動" exists
            if "公司活動" in menu_items:
                print("條件滿足，準備進入「公司活動」頁面...")
                await page.get_by_text("公司活動", exact=True).click()
                await page.wait_for_url("**/Event?categoryId=**")
                print("已成功進入「公司活動」頁面。")
                
                # Step 3: Scrape the corporate event details
                event_titles = await scrape_corporate_events(page)
                
                print("\n--- 最終爬取結果 ---")
                print(event_titles)
                print("--------------------")
            else:
                print("主選單中未找到「公司活動」，任務結束。")

        except Error as e:
            print(f"執行爬取任務時發生 Playwright 錯誤: {e}")
            
            # --- Debugging Logic ---
            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)
            timestamp = int(time.time())
            screenshot_file = os.path.join(log_dir, f"debug_screenshot_{timestamp}.png")
            page_source_file = os.path.join(log_dir, f"debug_page_{timestamp}.html")

            await page.screenshot(path=screenshot_file)
            print(f"已儲存除錯截圖: {screenshot_file}")

            with open(page_source_file, "w", encoding="utf-8") as f:
                f.write(await page.content())
            print(f"已儲存除錯網頁原始碼: {page_source_file}")
            
        finally:
            await browser.close()
            print("瀏覽器已關閉。")

if __name__ == "__main__":
    asyncio.run(run_ableclub_scraper())