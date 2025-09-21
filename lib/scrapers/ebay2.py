# https://www.youtube.com/watch?v=s6ONfBEUNDM
import time

import requests
from bs4 import BeautifulSoup


# Function to scrape details from an individual product page
def scrape_product_page(url):
    response = requests.get(url)
    product_soup = BeautifulSoup(response.text, "html.parser")

    # Extract the primary price in EUR
    primary_price_element = product_soup.find("div", class_="x-price-primary")
    primary_price = (
        primary_price_element.find("span", class_="ux-textspans").text.strip()
        if primary_price_element
        else "No primary price available"
    )

    # Extract the approximate price in USD
    approx_price_element = product_soup.find("div", class_="x-price-approx")
    approx_price = (
        approx_price_element.find("span", class_="ux-textspans--BOLD").text.strip()
        if approx_price_element
        else "No approximate price available"
    )

    # Extract the seller's username
    seller_element = product_soup.find(
        "div", class_="x-sellercard-atf__info__about-seller"
    )
    seller_username = (
        seller_element.find("span", class_="ux-textspans--BOLD").text.strip()
        if seller_element
        else "No seller information available"
    )

    # Extract the seller's feedback score
    feedback_element = (
        seller_element.find(
            "li", attrs={"data-testid": "x-sellercard-atf__about-seller"}
        )
        if seller_element
        else None
    )
    feedback_score = (
        feedback_element.find("span", class_="ux-textspans--SECONDARY").text.strip()
        if feedback_element
        else "No feedback score available"
    )

    # Extract the shipping cost and method
    shipping_element = product_soup.find(
        "div", class_="ux-labels-values__values-content"
    )
    shipping_info = (
        shipping_element.find("span", class_="ux-textspans").text.strip()
        if shipping_element
        else "No shipping information available"
    )
    shipping_method = (
        shipping_element.find_all("span", class_="ux-textspans")[3].text.strip()
        if shipping_element
        and len(shipping_element.find_all("span", class_="ux-textspans")) > 3
        else "No shipping method available"
    )

    # Extract the location
    location_element = (
        shipping_element.find_all("span", class_="ux-textspans--SECONDARY")[
            -1
        ].text.strip()
        if shipping_element
        else "No location information available"
    )

    print(f"Primary Price (EUR): {primary_price}")
    print(f"Approximate Price (USD): {approx_price}")
    print(f"Seller Username: {seller_username}")
    print(f"Seller Feedback Score: {feedback_score}")
    print(f"Shipping Cost: {shipping_info}")
    print(f"Shipping Method: {shipping_method}")
    print(f"Location: {location_element}")
    print("-" * 40)


# Function to scrape eBay search results page
def scrape_search_results(url):
    response = requests.get(url)
    print(f"{response.text=}")
    soup = BeautifulSoup(response.text, "html.parser")

    listings = soup.find_all("li", class_="s-item")
    print(f"{listings=}")
    for listing in listings:
        # Extract title
        title_element = listing.find("div", class_="s-item__title")
        title = (
            title_element.span.text.strip()
            if title_element and title_element.span
            else "No title available"
        )

        # Extract price
        price_element = listing.find("span", class_="s-item__price")
        price = price_element.text.strip() if price_element else "No price available"

        # Extract product URL
        product_url_element = listing.find("a", class_="s-item__link")
        product_url = product_url_element["href"] if product_url_element else None

        print(f"Search Result Title: {title}")
        print(f"Search Result Price: {price}")

        if product_url:
            print(f"Scraping product page: {product_url}")
            scrape_product_page(product_url)
        else:
            print("No product URL available")

        print("=" * 80)

        # To avoid overloading the server, add a small delay between requests
        time.sleep(2)


# Main execution
if __name__ == "__main__":
    search_url = "https://www.ebay.com/sch/i.html?_nkw=laptop"
    print("HELLO")
    scrape_search_results(search_url)
