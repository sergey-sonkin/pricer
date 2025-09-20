from typing import Any, TypedDict

from amazon_product_search import Amazon

from tools.base import ToolDefinition

amazon = Amazon()


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


def store_amazon_search_result(
    input: AmazonInputSchema, products: list[dict[Any, Any]]
):
    pass


def search_amazon(input: AmazonInputSchema) -> str:
    products: list[AmazonSearchResult] = amazon.search(  # pyright: ignore[reportAssignmentType]
        productName=input.get("product_name"),
        productType=input.get("product_type"),
        brand=input.get("brand"),
        priceRange=f"{input.get('minimum_price')}-{input.get('maximum_price')}",
    )
    return str(products)


AMAZON_SEARCH_TOOL = ToolDefinition(
    name="search_amazon",
    description="Search Amazon for products by name, type, brand, and price range",
    input_schema={
        "type": "object",
        "properties": {
            "product_name": {
                "type": "string",
                "description": "The name of the product to search for",
            },
            "product_type": {
                "type": "string",
                "description": "The type of product (e.g., 'electronics')",
            },
            "brand": {"type": "string", "description": "The brand of the product"},
            "price_minimum": {
                "type": "string",
                "description": "The minimum price (expressed as an integer)",
            },
            "price_maximum": {
                "type": "string",
                "description": "The maximum price (expressed as an integer)",
            },
        },
        "required": ["product_name"],
    },
    function=search_amazon,  # type: ignore
)
