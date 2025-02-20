from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import csv

# Set up Selenium WebDriver
def setup_driver():
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    driver_service = Service(r"C:/Windows/chromedriver.exe")  # Update with your ChromeDriver path
    return webdriver.Chrome(service=driver_service, options=options)

# Scrape a single page using BeautifulSoup
def scrape_page(soup):
    data = []
    product_cards = soup.find_all("div", {"data-component-type": "s-search-result"})

    for card in product_cards:
        try:
            # Extract Title
            title_element = card.find("span")
            title = title_element.text.strip() if title_element else "N/A"

            # Extract Link
            link_element = card.find("a", class_="a-link-normal s-no-outline")
            link = "https://www.amazon.in" + link_element["href"] if link_element else "N/A"

            # Extract Price
            price_element = card.find("span", class_="a-price-whole")
            price = price_element.text.strip() if price_element else "N/A"

            # Extract Rating
            rating_element = card.find("span", class_="a-icon-alt")
            rating_text = rating_element.text.strip() if rating_element else "N/A"
            # Extract numerical value from rating string
            rating = rating_text.split()[0] if "out of" in rating_text else "N/A"

            # Extract Reviews
            reviews_element = card.find("span", {"class": "a-size-base s-underline-text"})
            reviews = reviews_element.text.strip() if reviews_element else "N/A"

            # Add the product's data
            data.append({
                "Title": title,
                "Link": link,
                "Price": price,
                "Rating": rating,
                "Reviews": reviews,
            })

        except Exception as e:
            print(f"Error scraping product card: {e}")

    return data

# Main function to scrape multiple pages
def scrape_amazon(keyword, pages_to_scrape):
    driver = setup_driver()
    driver.get(f"https://www.amazon.in/s?k={keyword}")
    time.sleep(3)  # Wait for the page to load

    all_data = []

    for page in range(1, pages_to_scrape + 1):
        print(f"Scraping page {page}...")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        page_data = scrape_page(soup)
        all_data.extend(page_data)

        # Click 'Next' button
        try:
            next_button = driver.find_element(By.XPATH, "//a[contains(@class, 's-pagination-next')]")
            next_button.click()
            time.sleep(3)  # Wait for the next page to load
        except Exception as e:
            print(f"Could not navigate to next page: {e}")
            break

    driver.quit()
    return all_data

# Save data to a CSV file
def save_to_csv(data, filename="amazon_products.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Title", "Link", "Price", "Rating", "Reviews"])
        writer.writeheader()
        writer.writerows(data)

# Run the script
if __name__ == "__main__":
    search_keyword = input("Enter the product keyword to search on Amazon: ")
    num_pages = int(input("Enter the number of pages to scrape: "))

    scraped_data = scrape_amazon(search_keyword, num_pages)
    save_to_csv(scraped_data)
    print(f"Scraped data has been saved to 'amazon_products.csv'")