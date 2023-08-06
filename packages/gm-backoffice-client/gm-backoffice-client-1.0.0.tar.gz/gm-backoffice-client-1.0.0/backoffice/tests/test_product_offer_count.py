import pytest
import requests_mock

from ..client import BackofficeHTTPException


@pytest.mark.parametrize('api_data', (
    [
        {
            'id': 100,
            'site_id': 128,
            'name': 'Камаз с пирожками',
            'offers_count': 450,
        },
        {
            'id': 234,
            'site_id': 256,
            'name': 'Ведро с тестами',
            'offers_count': 4,
        },
    ],
))
def test_product_offers_stat_url(api_data, backoffice):
    with requests_mock.mock() as m:
        m.get('http://testhost/products/offers_stat/?site_ids=128,256', status_code=200, json=api_data)

        assert backoffice.get_products_offers_stat([128, 256]) == api_data


def test_non_200_response_to_product_offers_stat_get(backoffice):
    with requests_mock.mock() as m:
        m.get('http://testhost/products/offers_stat/?site_ids=128,256', status_code=404)

        with pytest.raises(BackofficeHTTPException):
            assert backoffice.get_products_offers_stat([128, 256])
