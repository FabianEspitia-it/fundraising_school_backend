from src.utils.scraper import move_down

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
from selenium import webdriver

import time


def move_down_and_click(url, scroll_count):
    print(f"Opening URL: {url}")
    driver = webdriver.Chrome()

    try:
        driver.get(url)
        print(f"Successfully opened {url}")

        scroll_number = scroll_count

        for _ in range(scroll_number):
            print(f"Scrolling down... {scroll_number} times left.")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            try:
                button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[contains(@class, 'btn-xs') and contains(@class, 'sn-light-greyblue-accent-button') and contains(@class, 'sn-center') and contains(@class, 'mt3') and contains(@class, 'mb2') and contains(@class, 'btn') and contains(@class, 'btn-default')]"))
                )
                button.click()
                print("Button clicked.")
                time.sleep(3)
            except:
                print("Button not found, stopping scrolling.")
                break

        html = driver.page_source

    except Exception as e:
        print(f"An error occurred: {e}")
        html = ""

    finally:
        driver.quit()

    return BeautifulSoup(html, "html.parser")

def get_category_links():
    print("Getting category links.")
    soup = move_down_and_click("https://signal.nfx.com/investor-lists/top-latam-latin-america-investors", 1)
    
    li_items = soup.find_all("li", class_="f6 serif")
    print(f"Found {len(li_items)} category items.")
    a_items = [li.find("a") for li in li_items]
    links = [a.get("href") for a in a_items]

    print(f"Found {len(links)} category links: {links}")
    return links

def get_investors_links():
    print("Getting investor links.")
    links = get_category_links()

    investor_links = set()  

    for link in links:
        print(f"Processing category link: https://signal.nfx.com{link}")
        soup = move_down_and_click(f"https://signal.nfx.com{link}", 6)
        a_items = soup.find_all("a", class_="vc-search-card-name")
        investor_links.update([a.get("href") for a in a_items])
        print(f"Added {len(a_items)} investor links.")

    print(f"Total unique investor links found: {len(investor_links)}")
    return list(investor_links)


def get_investor_info():
    print("Getting investor information.")
    investor_links = get_investors_links()

    crm_investors = []

    print(len(investor_links))

    investor_count = 1

    for link in investor_links:
        print(f"Processing investor {investor_count}: https://signal.nfx.com{link}")
        soup = move_down(f"https://signal.nfx.com{link}", 1)

        web_sites = soup.find_all("a", class_="iconlink")            
        web_sites_final = [web_site.get("href") for web_site in web_sites]
        sector_and_stage = soup.find_all("a", class_="vc-list-chip")

        investor = {
            "name": soup.find("h1", class_="f3 f1-ns mv1").text if soup.find("h1", class_="f3 f1-ns mv1") else None,
            "location": soup.find("span", class_="ml1").text if soup.find("span", class_="ml1") else None,
            "role": soup.find("div", class_="subheader lower-subheader pb2").text if soup.find("div", class_="subheader lower-subheader pb2") else None,
            "vc_link": soup.find("a", class_="ml1 subheader lower-subheader").get("href") if soup.find("a", class_="ml1 subheader lower-subheader") else None,
            "photo": soup.find("img", style="object-fit: cover; height: auto; width: auto;")["src"] if soup.find("img", style="object-fit: cover; height: auto; width: auto;") else None,
            "investor_linkedin": next((url for url in web_sites_final if 'https://www.linkedin.com/' in url), None),
            "invest_range_final": [span.get_text() for div in soup.find_all("div", class_="col-xs-7") for span in div.find_all("span", class_="lh-solid")][1] if len([span.get_text() for div in soup.find_all("div", class_="col-xs-7") for span in div.find_all("span", class_="lh-solid")]) > 1 else None,
            "sector_and_stage": [item.text for item in sector_and_stage] if sector_and_stage else None
        }

        crm_investors.append(investor)
        print(f"Investor {investor_count} added to the list.")
        investor_count += 1

    print(f"Total investors collected: {len(crm_investors)}")
    return crm_investors
    


    
        









