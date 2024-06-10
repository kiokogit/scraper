from selenium import webdriver  # type: ignore
from selenium.webdriver.common.by import By  # type: ignore
from selenium.webdriver.chrome.options import Options # type: ignore
from bs4 import BeautifulSoup as bs
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.action_chains import ActionChains
import time
from .models import LinkedInUserModel, LinkedInPostModel, linkedInPostLikeDetailsModel
# from threading import Lock

# Initialize Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--log-level=3")  # Suppress console logs

# LinkedIn Credentials
email = "kiokovincent12@gmail.com"
password = "Kioko@1024"
def get_linkedin_data(user_id):
    scraped_data = []
    # Access WebDriver
    browser = webdriver.Chrome(options=chrome_options)
    page = f"https://www.linkedin.com/in/{user_id}/recent-activity/all/"

    try:
        # Open login page
        browser.get(
            "https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin"
        )

        # Enter login info
        elementID = browser.find_element(By.ID, "username")
        elementID.send_keys(email)
        elementID = browser.find_element(By.ID, "password")
        elementID.send_keys(password)
        elementID.submit()

        # Verify login was successful
        if "feed" not in browser.current_url:
            raise Exception("Login failed")

        browser.get(page)

        # Scroll the page to load all posts
        SCROLL_PAUSE_TIME = 1
        MAX_SCROLLS = 5

        SCROLL_COMMAND = "window.scrollTo(0, document.body.scrollHeight);"
        GET_SCROLL_HEIGHT_COMMAND = "return document.body.scrollHeight"

        last_height = browser.execute_script(GET_SCROLL_HEIGHT_COMMAND)
        scrolls = 0
        no_change_count = 0

        while True:
            browser.execute_script(SCROLL_COMMAND)
            time.sleep(SCROLL_PAUSE_TIME)
            new_height = browser.execute_script(GET_SCROLL_HEIGHT_COMMAND)

            no_change_count = no_change_count + 1 if new_height == last_height else 0
            if no_change_count >= 3 or (MAX_SCROLLS and scrolls >= MAX_SCROLLS):
                break

            last_height = new_height
            scrolls += 1

        # Collect page source and parse it
        company_page = browser.page_source
        linkedin_soup = bs(
            company_page.encode("utf-8"), "html.parser"
        )  # Add parser argument
        containers = linkedin_soup.find_all("div", {"class": "feed-shared-update-v2"})
        containers = [
            container
            for container in containers
            if "activity" in container.get("data-urn", "")
        ]
        if bool(len(containers)):
            posting_user = LinkedInUserModel.objects.filter(user_id=user_id).first()
            if not posting_user:
                posting_user = LinkedInUserModel.objects.create(user_id=user_id)
        # Extract required data
        for container in containers:
            post_id = container.get("data-urn")
            post = LinkedInPostModel.objects.filter(post_id=post_id).first()
            if not post:
                post = LinkedInPostModel.objects.create(post_id=post_id, posting_user=posting_user)
            else:
                """Do not scrap the same post again"""
                continue
            # scrape likers
            likers_data = []
            # if int(likes) > 0:
            likes = 0
            liker_count_element_list = container.find("ul").find_all("li")
            liker_c = [l_c for l_c in liker_count_element_list if l_c.find("span", {"class": "social-details-social-counts__reactions-count"})]
            if bool(liker_c):
                likes = int(liker_c[0].text.strip())
                # save number of likes
                post.likes_count = likes
                post.save()
                
                post_reactions_url = f"https://www.linkedin.com/analytics/post/{post_id}/?resultType=REACTIONS"
                browser.get(post_reactions_url)
                # Wait for the post to load
                time.sleep(1)
                # Parse the likers list with BeautifulSoup
                soup = bs(browser.page_source.encode("utf-8"), "html.parser")
                likers = soup.find('ul', {"aria-label": "People who reacted"}).find_all("li")
                # Extract likers' names and user IDs       
                for liker in likers:
                    try:
                        name = liker.find('span', {"dir": "ltr"}).find('span', {"aria-hidden": "true"}).text.strip()
                        user_id = liker.find('a').get('href').split('/')[-1]
                        title = liker.find('div', {"class": "artdeco-entity-lockup__subtitle ember-view"}).text.strip()
                        
                        user = LinkedInUserModel.objects.filter(user_id=user_id).first()
                        if not user:
                            user = LinkedInUserModel.objects.create(
                                user_id=user_id,
                                name=name,
                                title=title
                            )
                        linkedInPostLikeDetailsModel.objects.create(
                            post=post,
                            liker=user
                        )
                        
                        likers_data.append({'name': name, 'user_id': user_id, "title": title})
                    except Exception as e:
                        print('Attribute error found: ', e)
                        continue
                # Print the likers' data
            scraped_data.append({"post_id": post_id, "likes": likes, "likers_data": likers_data})

    except Exception as e:
        print(f"Error during scraping: {e}")
    finally:
        browser.quit()
    return {"user_id": user_id, "data": scraped_data}
