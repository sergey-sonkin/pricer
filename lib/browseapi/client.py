import asyncio
from base64 import b64encode
from urllib.parse import urlencode

from aiohttp import ClientSession, ClientTimeout, client_exceptions

from . import exceptions
from .containers import BrowseAPIResponse

TIMEOUT = 60


class BrowseAPI:
    """Client class for eBay Browse API"""

    # uri has been changed to ebay sandbox enpoint
    _uri = "https://api.sandbox.ebay.com/buy/browse/v1"
    _auth_uri = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
    _search_uri = _uri + "/item_summary/search?"
    _search_by_image_uri = _uri + "/item_summary/search_by_image?"
    _get_item_uri = _uri + "/item/{item_id}?"
    _get_item_by_legacy_id_uri = _uri + "/item/get_item_by_legacy_id?"
    _get_items_by_item_group_uri = _uri + "/item/get_items_by_item_group?"
    _check_compatibility_uri = _uri + "/item/{item_id}/check_compatibility"

    # Client Credential Grant Type

    _credentials_grant_type = "client_credentials"
    _scope_public_data = "https://api.ebay.com/oauth/api_scope"

    supported_methods = (
        "search",
        "search_by_image",
        "get_item",
        "get_item_by_legacy_id",
        "get_items_by_item_group",
        "check_compatibility",
    )

    marketplaces = (
        "EBAY_US",
        "EBAY_AT",
        "EBAY_AU",
        "EBAY_BE",
        "EBAY_CA",
        "EBAY_CH",
        "EBAY_DE",
        "EBAY_ES",
        "EBAY_FR",
        "EBAY_GB",
        "EBAY_HK",
        "EBAY_IE",
        "EBAY_IN",
        "EBAY_IT",
        "EBAY_MY",
        "EBAY_NL",
        "EBAY_PH",
        "EBAY_PL",
        "EBAY_SG",
        "EBAY_TH",
        "EBAY_TW",
        "EBAY_VN",
        "EBAY_MOTORS_US",
    )

    def __init__(
        self,
        app_id: str,
        cert_id: str,
        marketplace_id: str = "EBAY_US",
        partner_id: str | None = None,
        reference_id: str | None = None,
        country: str | None = None,
        zip_code: str | None = None,
    ):
        """
        Client initialization

        :param app_id: eBay developer client id
        :param cert_id: ebay developer client secret
        :param marketplace_id: eBay marketplace identifier
        :param partner_id: eBay Network Partner ID
        :param reference_id: any value to identify item or purchase order can be used only with partner_id
        :param country: country code, needed for the calculated shipping information
        :param zip_code: used only with a country for getting shipping information
        """

        if marketplace_id not in self.marketplaces:
            raise exceptions.BrowseAPIParamError("marketplace_id")

        if reference_id is not None and partner_id is None:
            raise exceptions.BrowseAPIParamError(
                "partner_id. For reference_id partner_id is required"
            )

        if (country is None and zip_code is not None) or (
            zip_code is None and country is not None
        ):
            raise exceptions.BrowseAPIParamError(
                "country or zip_code. These parameters can only both None or filled"
            )

        self._session: ClientSession | None = None
        self._oauth_session: ClientSession | None = None
        self._possible_requests: int | None = None

        self._responses = []
        self._timeout = ClientTimeout(total=TIMEOUT)

        self._oauth_headers = {
            "Authorization": "Basic {}".format(
                str(b64encode((app_id + ":" + cert_id).encode("utf8")))[2:-1]
            ),
            "Content-Type": "application/x-www-form-urlencoded",
        }

        self._headers = {
            "Accept": "application/json",
            "Accept-Charset": "utf-8",
            "Authorization": "Bearer {}",
            "X-EBAY-C-MARKETPLACE-ID": marketplace_id,
        }

        # check data and form ctx header

        ctx_header = ""

        if partner_id is not None:
            ctx_header = "affiliateCampaignId=" + partner_id

            if reference_id is not None:
                ctx_header += ",affiliateReferenceId=" + reference_id

        if country is not None:
            if len(ctx_header):
                ctx_header += ","

            ctx_header += urlencode(
                self._prepare_params(
                    {"contextualLocation": f"country={country},zip={zip_code}"}
                )
            )

        if len(ctx_header):
            self._headers["X-EBAY-C-ENDUSERCTX"] = ctx_header

    async def _create_session(self):
        """Create requests session"""

        if self._session is not None:
            await self._session.close()

        self._session = ClientSession(headers=self._headers, timeout=self._timeout)

    async def _oauth(self):
        """
        OAuth request

        :return: json response
        """
        assert self._oauth_session is not None
        return await self._request(
            self._auth_uri,
            self._oauth_session,
            request_type="POST",
            data=urlencode(
                {
                    "grant_type": self._credentials_grant_type,
                    "scope": self._scope_public_data,
                }
            ),
        )

    async def _search(
        self,
        q: str | None = None,
        gtin: str | None = None,
        charity_ids: str | None = None,
        fieldgroups: str = "MATCHING_ITEMS",
        compatibility_filter: str | None = None,
        category_ids: str | None = None,
        filter: str | None = None,
        sort: str | None = None,
        limit: int = 200,
        offset: int = 0,
        aspect_filter: str | None = None,
        epid: str | None = None,
    ) -> dict:
        """
        Browse API search method

        :param q: a string consisting of one or more keywords that are used to search for items
        :param gtin: search by the Global Trade Item Number of the item
        :param charity_ids: limits the results to only items associated with the specified charity ID
        :param fieldgroups: comma separated list of values that lets you control what is returned in the response
        :param compatibility_filter: specifies the attributes used to define a specific product
        :param category_ids: the category ID is used to limit the results
        :param filter: multiple field filters that can be used to limit/customize the result set
        :param sort: specifies the order and the field name to use to sort the items
        :param limit: the number of items, from the result set, returned in a single page
        :param offset: the number of items to skip in the result set
        :param aspect_filter: this field lets you filter by item aspects
        :param epid: eBay product identifier of a product from the eBay product catalog
        :return: json response
        """

        assert self._session is not None
        return await self._request(
            self._search_uri,
            self._session,
            params=self._prepare_params(locals(), ("self",)),
        )

    async def _search_by_image(
        self,
        image: str,
        category_ids: str | None = None,
        filter: str | None = None,
        sort: str | None = None,
        limit: int = 200,
        offset: int = 0,
        aspect_filter: str | None = None,
        epid: str | None = None,
    ) -> dict:
        """
        Browse API searchByImage method

        :param image: base64 encoded image
        :param category_ids: the category ID is used to limit the results
        :param filter: multiple field filters that can be used to limit/customize the result set
        :param sort: specifies the order and the field name to use to sort the items
        :param limit: the number of items, from the result set, returned in a single page
        :param offset: the number of items to skip in the result set
        :param aspect_filter: this field lets you filter by item aspects
        :param epid: eBay product identifier of a product from the eBay product catalog
        :return: json response
        """

        assert self._session is not None
        return await self._request(
            self._search_by_image_uri,
            self._session,
            request_type="POST",
            params=self._prepare_params(locals(), ("self", "image")),
            json_data={"image": image},
        )

    async def _get_item(self, item_id: str, fieldgroups: str | None = None) -> dict:
        """
        Browse API getItem method

        :param item_id: eBay RESTful identifier of an item
        :param fieldgroups: lets you control what is returned in the response
        :return: json response
        """

        assert self._session is not None
        return await self._request(
            self._get_item_uri.format(item_id=item_id),
            self._session,
            params=self._prepare_params(locals(), ("self", "item_id")),
        )

    async def _get_item_by_legacy_id(
        self,
        legacy_item_id: str,
        legacy_variation_id: str | None = None,
        legacy_variation_sku: str | None = None,
        fieldgroups: str | None = None,
    ) -> dict:
        """
        Browse API getItemByLegacyId method

        :param legacy_item_id: eBay legacy item ID
        :param legacy_variation_id: legacy item ID of a specific item in an item group
        :param legacy_variation_sku: legacy SKU of the item
        :param fieldgroups: lets you control what is returned in the response
        :return: json response
        """

        assert self._session is not None
        return await self._request(
            self._get_item_by_legacy_id_uri,
            self._session,
            params=self._prepare_params(locals(), ("self",)),
        )

    async def _get_items_by_item_group(self, item_group_id: str) -> dict:
        """
        Browse API getItemsByItemGroup method

        :param item_group_id: identifier of the item group to return
        :return: json response
        """

        assert self._session is not None
        return await self._request(
            self._get_items_by_item_group_uri,
            self._session,
            params=self._prepare_params(locals(), ("self",)),
        )

    async def _check_compatibility(self, item_id: str, compatibility_properties: list):
        """
        Browse API checkCompatibility method

        :param item_id: eBay RESTful identifier of an item
        :param compatibility_properties: list of attribute name/value pairs used to define a specific product, like:
            [{'name': name, 'value': value}, ]
        :return: json response
        """

        assert self._session is not None
        return await self._request(
            self._check_compatibility_uri.format(item_id=item_id),
            self._session,
            request_type="POST",
            json_data={"compatibilityProperties": compatibility_properties},
        )

    async def _send_oauth_request(self):
        """Send OAuth request for getting application token"""

        oauth_response = await self._oauth()

        try:
            app_token = oauth_response["access_token"]
            expires_in = oauth_response["expires_in"]

        except KeyError as err:
            raise exceptions.BrowseAPIOAuthError(oauth_response) from err

        self._possible_requests = expires_in // TIMEOUT
        self._headers["Authorization"] = self._headers["Authorization"].format(
            app_token
        )

    async def _send_requests(
        self, method: str, params: list, pass_errors: bool
    ) -> None:
        """
        Send async requests

        :param method: Browse API method name in lowercase
        :param params: list of params dictionaries for every request
        :param pass_errors: exceptions in the tasks are treated the same as successful results, bool
        """

        self._responses = []

        # load specified api method

        if method not in self.supported_methods:
            raise exceptions.BrowseAPIMethodError(
                f"This method is not supported: {method}"
            )

        method_name = method
        method = getattr(self, "_" + method)  # type: ignore[assignment]

        try:
            # get oauth token

            self._oauth_session = ClientSession(
                headers=self._oauth_headers, timeout=self._timeout
            )
            await self._send_oauth_request()
            await self._create_session()

            # send requests

            assert self._possible_requests is not None
            params = self._split_list(params, self._possible_requests)

            for part_number, param_part in enumerate(params):
                responses = await asyncio.gather(
                    *[method(**param) for param in param_part],  # type: ignore[misc]
                    return_exceptions=pass_errors,
                )

                self._responses += [
                    BrowseAPIResponse(response, method_name, pass_errors)
                    if isinstance(response, dict)
                    else response
                    for response in responses
                ]

                if part_number != len(params):
                    await self._send_oauth_request()
                    await self._create_session()

        finally:
            if self._oauth_session is not None:
                await self._oauth_session.close()

            if self._session is not None:
                await self._session.close()

    def execute(self, method: str, params: list, pass_errors: bool = False) -> list:
        """
        Start event loop and make requests

        :param method: Browse API method name in lowercase
        :param params: list of params dictionaries for every request
        :param pass_errors: exceptions in the tasks are treated the same as successful results, bool
        :return: list of responses
        """

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self._send_requests(method, params, pass_errors))

        finally:
            loop.close()

        return self._responses

    @staticmethod
    async def _request(
        uri: str,
        session: ClientSession,
        request_type: str = "GET",
        params: dict | None = None,
        data: str | None = None,
        json_data: dict | None = None,
    ) -> dict:
        """
        Make async request

        :param uri: request uri
        :param session: Client session instance
        :param request_type: GET or POST
        :param params: request parameters dictionary
        :param data: str with request payload
        :param json_data: dictionary with request payload
        :return: json response
        """

        try:
            if request_type == "GET":
                async with session.get(uri, params=params) as response:
                    return await response.json()

            elif request_type == "POST":
                async with session.post(
                    uri, params=params, data=data, json=json_data
                ) as response:
                    return await response.json()

            else:
                raise exceptions.BrowseAPIParamError("request_type")

        except client_exceptions.InvalidURL as err:
            raise exceptions.BrowseAPIInvalidUri("Invalid uri", uri) from err

        except client_exceptions.ServerTimeoutError as err:
            raise exceptions.BrowseAPITimeoutError("Timeout occurred", uri) from err

        except client_exceptions.ClientConnectorError as err:
            raise exceptions.BrowseAPIConnectionError("Connection error", uri) from err

        except client_exceptions.ClientOSError as err:
            raise exceptions.BrowseAPIConnectionError("Connection reset", uri) from err

        except client_exceptions.ServerDisconnectedError as err:
            raise exceptions.BrowseAPIConnectionError(
                "Server refused the request", uri
            ) from err

        except client_exceptions.ClientResponseError as err:
            raise exceptions.BrowseAPIMimeTypeError(
                "Response has unexpected mime type", uri
            ) from err

    @staticmethod
    def _prepare_params(params: dict, to_delete: tuple = ("",)) -> dict:
        """
        Prepare uri parameters

        :param params: request parameters dictionary
        :param to_delete: iterable, what params needs to be deleted
        :return: parameters dictionary or string with encoded parameters
        """

        return {
            param: str(params[param])
            for param in params
            if params[param] is not None and param not in to_delete
        }

    @staticmethod
    def _split_list(array: list, n: int):
        """Split list into parts with n elements"""

        return [array[i : i + n] for i in range(0, len(array), n)]
