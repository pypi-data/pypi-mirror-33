import pytest

from ..client import BackofficeValidationError


@pytest.mark.parametrize('data', (
    {'customer': {
        'name': 'Petrovich',
    }},
    {'customer': {
        'name': 'Petrovich',
        'legal': {'name': 'Petrovich corp.', 'inn': '123456'},
    }},
    {'customer': {
        'name': 'Petrovich',
        'legal': {'name': 'Petrovich corp.', 'inn': '123456'},
    }, 'is_confirmed': True},
    {
        'customer': {
            'name': 'Petrovich',
            'legal': {'name': 'Petrovich corp.', 'inn': '123456'},
        },
        'delivery': {
            'desired_date': '2018-01-01',
            'time_from': '18:01',
            'time_till': '23:39',
        },
    },
    {
        'customer': {'name': 'Petrovich'},
        'delivery': {'floor': '1'},
    },
    {
        'customer': {'name': 'Petrovich'},
        'delivery': {'floor': 1},
    },
    {
        'customer': {'name': 'Petrovich'},
        'delivery': {'floor': '-1'},
    },
    {
        'customer': {'name': 'Petrovich'},
        'delivery': {'floor': -1},
    },
))
def test_valid_order(data, backoffice):
    assert backoffice.validate_order(data) is True


@pytest.mark.parametrize('data', (
    {},
    {'customer': {
        'name': 'Petrovich',
        'legal': {'name': 'Petrovich corp.'},
    }},
    {'customer': {
        'name': 'Petrovich',
        'legal': {'name': 'Petrovich corp.', 'inn': '123456'},
    }, 'is_confirmed': None},
    {
        'customer': {
            'name': 'Petrovich',
        },
        'delivery': {
            'desired_date': 'some awesome date',
        },
    },
    {
        'customer': {'name': 'Petrovich'},
        'delivery': {
            'time_from': 'HH:MM',
        },
    },
    {
        'customer': {'name': 'Petrovich'},
        'delivery': {
            'time_till': 'HH:MM',
        },
    },
))
def test_invalid_order(data, backoffice):
    with pytest.raises(BackofficeValidationError) as e:
        backoffice.validate_order(data)

        assert "customer" in str(e)


def test_any_utm_object_is_accepted(backoffice):
    assert backoffice.validate_order({
        'customer': {
            'name': 'Petrovich',
        },
        'utm': {
            'a': ['b', 'c', {'d': 'e'}],
            'f': 'g',
            'foo': 'bar',
        },
    }) is True


@pytest.mark.parametrize('data', [
    [{'product': {
        'name': 'kamaz of ships',
    }}],
    [{
        'product': {
            'name': 'kamaz of ships',
        },
        'price': 100500.00,
    }],
    [{
        'product': {
            'name': 'kamaz of ships',
        },
        'price': 100500.00,
        'customer_comment': 'Sudo make me a burger',
    }, {
        'product': {
            'name': 'gazel of ships',
        },
        'price': 100500.00,
    }],
])
def test_valid_item_set(data, backoffice):
    assert backoffice.validate_items(data) is True


def test_string_items_are_accepted_instead_of_numbers_because_django_deals_correctly_with_it_and_i_dont_wont_to_fucken_mess_with_this_javascript_types(backoffice):
    assert backoffice.validate_items([
        {
            'product': {
                'site_id': '100500',
            },
            'price': '1005.05',
        },
    ]) is True


def test_invalid_item_set(backoffice):
    with pytest.raises(BackofficeValidationError) as e:
        backoffice.validate_items([
            {
                'quant1ty': 100500,
            },
        ])

        assert "name" in str(e)
