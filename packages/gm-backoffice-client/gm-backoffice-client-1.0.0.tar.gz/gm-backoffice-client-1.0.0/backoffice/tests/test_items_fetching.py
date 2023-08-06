import pytest
import requests_mock

from ..client import BackofficeHTTPException


@pytest.mark.parametrize('api_data', (
    {
        'price_cashless': '300500.00',
        'price_cash': '200500.00',
    },
))
def test_price_url(api_data, backoffice):
    with requests_mock.mock() as m:
        m.get('http://testhost/price_lists/sell/100500/', status_code=200, json=api_data)

        assert backoffice.get_price(100500) == api_data


def test_non_200_response_to_price_get(backoffice):
    with requests_mock.mock() as m:
        m.get('http://testhost/price_lists/sell/100500/', status_code=404)

        with pytest.raises(BackofficeHTTPException):
            assert backoffice.get_price(100500)
