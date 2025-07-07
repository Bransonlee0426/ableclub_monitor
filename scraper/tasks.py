# scraper/tasks.py (Refactored to use Playwright)

import asyncio
from playwright.async_api import async_playwright, Page, Error
from typing import List
import time
import os

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
async def scrape_corporate_events(page: Page) -> List[str]:
    """
    Filters for '報名中活動' (Events Open for Registration) and scrapes their titles across all pages
    by handling pagination. Assumes the page is already on the '公司活動' page.

    Args:
        page: The Playwright Page object on the corporate events page.

    Returns:
        A list of all event titles found across all pages.
    """
    print("篩選「報名中活動」並爬取所有頁面的標題...")

    # Click the filter dropdown
    await page.locator("#ableclub-filter-menu").click()

    # Click the "報名中活動" option to ensure there are multiple pages
    await page.locator("a.dropdown-item").get_by_text("報名中活動", exact=True).click()

    all_event_titles = []
    page_number = 1

    while True:
        # 1. Wait for the current page's content to be fully loaded.
        await page.wait_for_selector('.ableclub-cardgroup')
        print(f"正在爬取第 {page_number} 頁...")

        # 2. Scrape data from the current page.
        card_group_container = page.locator(".ableclub-cardgroup")
        title_elements = card_group_container.locator("h3.card-title")
        current_page_titles = await title_elements.all_text_contents()
        all_event_titles.extend(current_page_titles)
        print(f"本頁找到 {len(current_page_titles)} 個活動標題。")

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
            
    # 5. Return the final list of all titles.
    return all_event_titles

# --- Function 3: Main Orchestrator ---
async def run_ableclub_scraper():
    """
    Orchestrates the entire scraping process from start to finish using Playwright.
    """
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