import webbrowser as wb
import pandas as pd
import time
import pyautogui
import os


CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# Register Chrome in webbrowser module
wb.register("chrome", None, wb.BackgroundBrowser(CHROME_PATH))


def scroll_page(num_scrolls=20, delay=1):
    """
    Simulate scrolling down the page by sending PageDown keystrokes.
    Adjust num_scrolls and delay as needed.
    """
    for _ in range(num_scrolls):
        pyautogui.press("pagedown")
        time.sleep(delay)


def click_image(image_path, confidence=0.8, timeout=30):
    """
    Uses PyAutoGUI to locate an image on the screen and click on it.
    Returns True if successful, False otherwise.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        location = None
        try:
             location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        except pyautogui.ImageNotFoundException as e:
            pass
        if location is not None:
            pyautogui.click(location)
            print(f"Clicked on {image_path} at {location}")
            return True
        time.sleep(0.5)
    print(f"Could not find {image_path} on screen within {timeout} seconds.")
    return False


def close_tab():
    pyautogui.hotkey("ctrl", "w")
    print("Closed Tab")

# TODO: Also send location of the place so only the concerned HR are targeted, otherwise for bigger companies (TCS, Infosys), it will send mail to 1000+ people
def process_company(company_url: str):
    """
    Opens the company LinkedIn page for HR profiles in the default browser,
    scrolls through the page, then clicks on the Apollo extension UI buttons.
    """
    # Ensure URL ends with a slash
    if not company_url.endswith("/"):
        company_url += "/"

    # Construct the HR listing URL
    hr_url = company_url + "people/?facetCurrentFunction=12&facetGeoRegion=102713980"
    print(f"Opening: {hr_url}")

    # Open the HR listing page in your default browser (typically Chrome)
    wb.get("chrome").open(hr_url)
    # Wait for the page to load (adjust if needed)
    time.sleep(10)

    # Scroll down to load all HR profiles
    scroll_page(num_scrolls=20, delay=1)
    time.sleep(2)

    # Use PyAutoGUI to interact with the Apollo extension:
    if not click_image(os.path.abspath("utils/images/ApolloIcon.png")):
        return
    time.sleep(2)

    # click_image(os.path.abspath("utils/images/SelectAll.png"))
    # time.sleep(2)

    if not click_image(os.path.abspath("utils/images/AccessContactInfoOnly.png")):
        return
    time.sleep(2)

    if not click_image(os.path.abspath("utils/images/AccessContactInfo.png")):
        return
    time.sleep(8)

    print("Completed processing for this company.")
    close_tab()


def process_profile(profile_url: str):
    """
    Opens the company LinkedIn page for HR profiles in the default browser,
    scrolls through the page, then clicks on the Apollo extension UI buttons.
    """

    wb.get("chrome").open(profile_url)
    # Wait for the page to load (adjust if needed)
    time.sleep(15)

    # Use PyAutoGUI to interact with the Apollo extension:
    if not click_image(os.path.abspath("utils/images/HrAccessEmail.png")):
        return
    time.sleep(3)
    

    print(f"Completed processing for Profile: {profile_url}")
    close_tab()


def main():
    # Read CSV data (assuming a column named 'company_link' contains the company URLs)
    df = pd.read_csv("all_applied_applications_history.csv")
    company_links = df["Company Link"].tolist()

    for company_url in company_links:
        try:
            process_company(company_url)
            # Optionally, wait before processing the next company
            time.sleep(5)
        except Exception as e:
            print(f"Error processing {company_url}: {str(e)}")


if __name__ == "__main__":
    # main()
    process_profile("https://www.linkedin.com/in/shivam-rustagi-995033159/")
    process_company("https://www.linkedin.com/company/swiggy-in/")
