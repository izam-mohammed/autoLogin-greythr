import asyncio
import json
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import pytz
from datetime import datetime

class LoginManager:
    def __init__(self, login_url, cookies_file="cookies.json"):
        self.login_url = login_url
        self.cookies_file = cookies_file
        self.credentials = {
            "username": os.environ.get("username"), 
            "password": os.environ.get("password")
        }

    async def save_cookies(self, cookies):
        """Save cookies to a JSON file"""
        with open(self.cookies_file, 'w') as f:
            json.dump(cookies, f)

    async def load_cookies(self):
        """Load cookies from JSON file if it exists"""
        try:
            with open(self.cookies_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    async def is_logged_in(self, page):
        """Check if user is already logged in
        Modify this method based on your website's logged-in state indicator
        """
        try:
            await page.wait_for_selector('a[title="Logout"]', timeout=5000)
            return True
        except:
            return False

    async def perform_login(self, page):
        """Perform the login process"""
        try:
            await page.fill('input[name="username"]', self.credentials['username'])
            await asyncio.sleep(1)
            await page.fill('input[name="password"]', self.credentials['password'])
            await asyncio.sleep(1)
            await page.click('button[type="submit"]')
            
            await page.wait_for_selector('a[title="Logout"]')
            
            cookies = await page.context.cookies()
            await self.save_cookies(cookies)
            print("Manual Login successful")
            return True
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False
        
    async def check_and_click_button(self, page):
        """Check button text and click if it says 'take'"""
        try:
            button = await page.wait_for_selector('button[name="primary"][type="button"]')
            
            button_text: str = await button.inner_text()
            is_clockin = 'sign out' in button_text.lower().strip()
            print(f"Clock up status : {'already clocked' if is_clockin else 'not clocked'}")
            
            if not is_clockin:
                print("Clicking the Sign In Butoon...")
                await asyncio.sleep(1)
                await button.click()
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(0.41)
            else:
                print("Skipping the click...")
            
            return True
        except Exception as e:
            print(f"Error handling button: {str(e)}")
            return False

    async def manage_login(self):
        """Main method to handle the login process"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            cookies = await self.load_cookies()
            if cookies:
                await context.add_cookies(cookies)

            await page.goto(self.login_url)

            if not await self.is_logged_in(page):
                print("Not logged in. Attempting login...")
                login_success = await self.perform_login(page)
                if not login_success:
                    print("Login failed")
                    await browser.close()
                    return False
            else:
                print("Already logged in")

            await self.check_and_click_button(page)
            
            await page.screenshot(path='login_proof.png')
            
            await browser.close()
            return True
        
def is_workday_and_time():
    """Check if current time is between Monday-Friday, 8 AM to 1 PM"""
    # Use your local timezone - replace 'Asia/Kolkata' with your timezone
    tz = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(tz)
    
    # Check if it's Monday-Friday (weekday() returns 0-6, where 0 is Monday)
    is_weekday = current_time.weekday() < 5
    
    # Check if time is between 8 AM and 1 PM
    is_work_hours = 8 <= current_time.hour < 13
    
    current_status = {
        "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "is_weekday": is_weekday,
        "is_work_hours": is_work_hours,
        "day_of_week": current_time.strftime("%A"),
        "hour": current_time.hour
    }
    
    print("Time Check Status:")
    print(f"Current Time: {current_status['current_time']}")
    print(f"Day: {current_status['day_of_week']}")
    print(f"Is Weekday: {current_status['is_weekday']}")
    print(f"Is Work Hours: {current_status['is_work_hours']}")
    
    return is_weekday and is_work_hours

async def main():
    load_dotenv()
    
    if is_workday_and_time():
        print("\nTime check passed. Proceeding with login...")
        login_manager = LoginManager(
            login_url=os.environ.get("base_url")  # https://{company_id}.greythr.com/
        )
        await login_manager.manage_login()
    else:
        print("\nOutside of work hours or not a workday. Skipping login.")

if __name__ == "__main__":
    asyncio.run(main())