from typing import TypedDict

from amazon_product_search import Amazon

from tools.base import ToolDefinition

amazon = Amazon()

VALID_CATEGORIES = [
    "alexa-skills",  # Alexa Skills
    "vehicles",  # Amazon Autos
    "amazon-device",  # Amazon Devices
    "amazonfresh",  # Amazon Fresh
    "amazon-global-store",  # Amazon Global Store
    "bazaar",  # Amazon Haul
    "amazon-one-medical",  # Amazon One Medical
    "amazon-pharmacy",  # Amazon Pharmacy
    "warehouse-deals",  # Amazon Resale
    "appliances",  # Appliances
    "mobile-apps",  # Apps & Games (<- This doesn't even include board games)
    "arts-crafts",  # Arts, Crafts & Sewing
    "audible",  # Audible Books & Originals
    "automotive",  # Automotive Parts & Accessories
    "baby-products",  # Baby
]


class AmazonInputSchema(TypedDict):
    product_name: str
    product_type: str | None
    brand: str | None
    minimum_price: str | None
    maximum_price: str | None


class AmazonSearchResult(TypedDict):
    title: str | None
    link: str | None
    review: str | None
    price: str | None
    image: str | None


def amazon_results_to_str(results: list[AmazonSearchResult]):
    ret = "title,price\n"
    for result in results:
        if (title := result.get("title")) and (price := result.get("price")):
            ret += f"{title},{price}\n"  # pyright: ignore[reportPossiblyUnboundVariable]

    return ret


def store_amazon_search_result(
    input: AmazonInputSchema, products: list[AmazonSearchResult]
):
    # TODO: Implement this!!
    pass


def search_amazon(input: AmazonInputSchema) -> str:
    products: list[AmazonSearchResult] = amazon.search(  # pyright: ignore[reportAssignmentType]
        productName=input.get("product_name"),
        productType=input.get("product_type"),
        brand=input.get("brand"),
        priceRange=f"{input.get('minimum_price')}-{input.get('maximum_price')}",
    )
    store_amazon_search_result(input, products)
    return amazon_results_to_str(products)


AMAZON_SEARCH_TOOL = ToolDefinition(
    name="search_amazon",
    description="Search Amazon for products",
    input_schema={
        "type": "object",
        "properties": {
            "product_name": {
                "type": "string",
                "description": "Search query",
            },
            # "product_type": {
            #     "type": "string",
            #     "description": "The type of product (e.g., 'electronics')",
            # },
            "brand": {"type": "string", "description": "The brand of the product"},
            "price_minimum": {
                "type": "string",
                "description": "Minimum price (integer, no commas)",
            },
            "price_maximum": {
                "type": "string",
                "description": "Maximum price (integer, no commas)",
            },
        },
        "required": ["product_name"],
    },
    function=search_amazon,  # type: ignore
)
