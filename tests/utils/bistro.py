import re
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Union

from requests import Session, Response

from .config import test_config

BISTRO_URL = 'https://staging.benjoenergy.com'
logger = logging.getLogger(__name__)


class BistroException(Exception):
    pass


def urljoin(base, *paths):
    """Assemble a uri based on a base, any number of path segments.
    """
    paths = [base] + list(paths)
    paths = [s.strip('/') for s in paths[:-1]] + [paths[-1].lstrip('/')]
    return '/'.join(paths)


def pascal_to_upper_case(value: str) -> Union[str, None]:
    """
    Converts PascalCase values into UPPER_CASE.

    :param value: Value which will be converted.
    :return: Converted value.
    """
    if value is None:
        return value

    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', value)
    value = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).upper()
    return value


# noinspection PyMethodMayBeStatic
class BistroService:
    """
    This class will be used for communication between tranzit and bistro.
    It will be used for getting information about Chargers, TagInfo,
    Connectors, Transactions, etc.

    :param address: Address of Bistro service.
    :type address: str | None
    :type _urls: dict
    :type address: str
    :type headers: Dict[str, str]
    """
    _urls = {
        'chargers': '/v0/admin/chargers/',
        'charger_by_id': '/v0/admin/chargers/{cp_id}/',
    }

    def __init__(self, address, headers):
        self.address = address
        self.headers = headers
        self.session = Session()

    @classmethod
    def initialize(cls, headers):
        bistro_data = test_config.get('bistro', {})
        address = bistro_data.get('url', BISTRO_URL)
        cookie_header = headers['Cookie']
        session_id = cookie_header.split('; ')[1].split('=')[1]
        new_headers = {
            'Cookie': cookie_header,
            'X-Session-Id': session_id
        }
        return cls(address=address, headers=new_headers)

    def _create_url(self, url, **params):
        """
        Creates url from provided url key which will be used for getting
        endpoint path from _url dict and provided path params which will be
        used for updating found endpoint path. If url has only path part
        client address will be used.

        :param url: Url key for getting endpoint url from client _url dict.
        :type url: str
        :param params: Path params which will be used for updating found
            endpoint url.
        :return: Full endpoint url.
        :rtype: str
        """
        endpoint_url = self._urls.get(url, url).format(**params)
        if endpoint_url.startswith('http'):
            return endpoint_url
        else:
            return urljoin(self.address, endpoint_url)

    def _response_or_exception(
        self, response: Response
    ) -> Dict[str, Any]:
        """
        Check if status code is less than 400 and return json. Otherwise
        raise exception

        :param response: Provided aiohttp response.
        :return: Fetched json.
        if 400 <= self.status:
        """
        data = response.json()
        if 400 <= response.status_code:
            raise BistroException(data)

        return data

    # class ChargerStatus(models.TextChoices):
    #     AVAILABLE = 'AVAILABLE', 'Available'
    #     UNAVAILABLE = 'UNAVAILABLE', 'Unavailable'
    #     FAULTED = 'FAULTED', 'Faulted'
    #
    #
    # class ChargerState(models.TextChoices):
    #     DELETED = 'DELETED', 'Deleted'
    #     OPERATIVE = 'OPERATIVE', 'Operative'
    #     INOPERATIVE = 'INOPERATIVE', 'Inoperative'
    def add_charger(
        self,
        name,
        model,
        vendor,
        address,
        power=22.0,
        status='AVAILABLE',
        state='OPERATIVE',
        firmware_version='123'
    ) -> dict:
        """
        Creates charging point with provided cp data.

        :return: Created CP data.
        """
        cp_data = {
            'name': name,
            'model': model,
            'vendor': vendor,
            'address': address,
            'power': power,
            'status': status,
            'state': state,
            'firmware_version': firmware_version
        }
        url = self._create_url(
            'chargers'
        )
        try:
            response = self.session.post(
                url=url, verify=False, json=cp_data, headers=self.headers
            )
            cp_data = self._response_or_exception(response)
            logger.info(
                'Bistro CP created. Response: {}'.format(cp_data)
            )
        except Exception as exc:
            logger.warning(
                'Bistro CP creating failed. Reason: {}'.format(str(exc))
            )

        return cp_data

    # async def get_charge_point(self, cp_id: str) -> dict:
    #     """
    #     Gets charging point with provided cp id.
    #
    #     :param cp_id: CP identity.
    #     :return: Fetched CP data.
    #     """
    #     cp_data = None
    #     url = self._create_url(
    #         'charger_by_id', **{'cp_id': cp_id}
    #     )
    #     try:
    #         async with aiohttp.ClientSession() as session:
    #             async with session.get(
    #                     url=url, ssl=False, headers=self.headers
    #             ) as response:
    #                 cp_data = await self._response_or_exception(response)
    #                 logger.info(
    #                     'Bistro CP fetched using cp_id: {}. '
    #                     'Response: {}'.format(cp_id, cp_data)
    #                 )
    #     except Exception as exc:
    #         logger.warning(
    #             'Bistro CP updating failed. Reason: {}'.format(str(exc))
    #         )
    #
    #     return cp_data
