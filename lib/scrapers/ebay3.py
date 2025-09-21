# https://brightdata.com/blog/how-tos/how-to-scrape-ebay-in-python
import json
import re
import sys

import requests
from bs4 import BeautifulSoup

# if there are no CLI parameters
if len(sys.argv) <= 1:
    item_id = "iPhone 13 mini 128gb"
    # print('Item ID argument missing!')
    # sys.exit(2)
else:
    item_id = sys.argv[1]

# read the item ID from a CLI argument
# build the URL of the target product page
url = f"https://www.ebay.com/itm/{item_id}"
# download the target page
page = requests.get(url)
print(f"{page.text=}")
# parse the HTML document returned by the server
soup = BeautifulSoup(page.text, "html.parser")
# initialize the object that will contain
# the scraped data
item = {}
# price scraping logic
price_html_element = soup.select_one('.x-price-primary span[itemprop="price"]')
price = price_html_element["content"]
currency_html_element = soup.select_one(
    '.x-price-primary span[itemprop="priceCurrency"]'
)
currency = currency_html_element["content"]
shipping_price = None
label_html_elements = soup.select(".ux-labels-values__labels")

for label_html_element in label_html_elements:
    if "Shipping:" in label_html_element.text:
        shipping_price_html_element = label_html_element.next_sibling.select_one(
            ".ux-textspans--BOLD"
        )
        # if there is not a shipping price HTML element
        if shipping_price_html_element is not None:
            # extract the float number of the price from
            # the text content
            shipping_price = re.findall("d+[.,]d+", shipping_price_html_element.text)[0]
        break
item["price"] = price
item["shipping_price"] = shipping_price
item["currency"] = currency
# product detail scraping logic
section_title_elements = soup.select(".section-title")
for section_title_element in section_title_elements:
    if (
        "Item specifics" in section_title_element.text
        or "About this product" in section_title_element.text
    ):
        # get the parent element containing the entire section
        section_element = section_title_element.parent
        for section_col in section_element.select(".ux-layout-section-evo__col"):
            print(section_col.text)
            col_label = section_col.select_one(".ux-labels-values__labels")
            col_value = section_col.select_one(".ux-labels-values__values")
            # if both elements are present
            if col_label is not None and col_value is not None:
                item[col_label.text] = col_value.text
# export the scraped data to a JSON file
with open("product_info.json", "w") as file:
    json.dump(item, file, indent=4)
