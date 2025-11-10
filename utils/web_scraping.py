import time
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin

# Step 1: Get listing page fully loaded
def scrape_car_listing(link):
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get(link)

        scroll_pause_time = random.uniform(2, 4)
        scroll_increment = 1000

        last_height = driver.execute_script("return window.pageYOffset + window.innerHeight")

        while True:
            driver.execute_script(f"window.scrollBy(0, {scroll_increment});")
            time.sleep(scroll_pause_time)

            new_height = driver.execute_script("return window.pageYOffset + window.innerHeight")
            total_page_height = driver.execute_script("return document.body.scrollHeight")

            if new_height >= total_page_height or new_height == last_height:
                break
            last_height = new_height

        html = driver.page_source
        driver.quit()

        return BeautifulSoup(html, 'lxml')

    except Exception as e:
        print(f"[General Error] {e}")
    finally:
        if driver:
            driver.quit()


# Step 2: Extract details from each listing + detail page
def get_car_details(soup):
    rows = []
    cards = soup.find_all("a", class_="styles_carCardWrapper__sXLIp")

    for card in cards:
        try:
            # model name
            name_el = card.find("span", class_="sc-braxZu kjFjan")
            model_name = name_el.text.strip() if name_el else None

            # specs from listing card
            km = fuel = trans = None
            spec_els = card.find_all("p", class_="sc-braxZu kvfdZL")
            for spec in spec_els:
                text = spec.text.strip()
                if "km" in text.lower():
                    km = text
                elif text.lower() in ["petrol", "diesel", "cng", "electric"]:
                    fuel = text
                elif text.lower() in ["manual", "automatic"]:
                    trans = text

            # price
            price_el = card.find("p", class_="sc-braxZu cyPhJl")
            price = price_el.text.strip() if price_el else None

            # link
            href = card.get("href")
            link = urljoin("https://www.cars24.com", href) if href else None

            # --- DETAIL PAGE EXTRACTION ---
            ownership, engine_capacity = None, None
            if link:
                headers = {"User-Agent": "Mozilla/5.0"}
                response = requests.get(link, headers=headers, timeout=random.randint(4, 8))
                detail_soup = BeautifulSoup(response.text, "lxml")

                # loop through labels (like Ownership, Engine capacity, etc.)
                labels = detail_soup.find_all("p", class_="sc-braxZu jjIUAi")
                for lbl in labels:
                    if "Ownership" in lbl.text.strip():
                        ownership = lbl.find_next_sibling("p").text.strip()
                    if "Engine capacity" in lbl.text.strip():
                        engine_capacity = lbl.find_next_sibling("p").text.strip()

            rows.append({
                "model_name": model_name,
                "km_driven": km,
                "fuel_type": fuel,
                "transmission": trans,
                "owner": ownership,          # ✅ from detail page
                "engine_capacity": engine_capacity,  # ✅ from detail page
                "price": price,
                "link": link
            })

        except Exception as e:
            print(f"[Skip one card due to error] {e}")
            continue

    return pd.DataFrame(rows)

def get_engine_capacity(urls):
    """
    Extract engine capacity values from a list of car listing page URLs.

    Parameters:
        urls (list of str): List of URLs pointing to individual car listings.

    Returns:
        list: A list containing engine capacity values (str) for each URL.
              Returns None for entries where engine capacity is not found.
    """
    engine_capacity = []
    for url in urls:
        headers = {"User-Agent":"Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=random.randint(4,8))
        soup = BeautifulSoup(response.text,"lxml")

        found = False
        for i in soup.find_all('p', attrs={"class":"sc-braxZu jjIUAi"}):
            if i.text.strip() == 'Engine capacity':
                engine_capacity.append(i.find_next_sibling().text)
                found = True
                
        if not found:
            engine_capacity.append(None)
    return engine_capacity