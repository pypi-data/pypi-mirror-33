
def test_authorization_headers(backoffice):
    assert backoffice.headers['Authorization'] == 'Token tsttkn', 'corrrect token is inserted within __init__'
