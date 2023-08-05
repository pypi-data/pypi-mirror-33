import jwt
import falcon_helpers.contrib.auth as auth


def test_generate_auth_token():
    # we don't need to hit the db for this test so don't commit it
    u1 = auth.User.testing_create(_commit=False)

    token = u1.generate_auth_token('aud', 'secret')
    result = jwt.decode(token, 'secret', algorithm='HS256', audience='aud')
    assert result['sub'] == u1.ident

    token = u1.generate_auth_token('aud', 'secret', additional_data={
        'other': 'true'
    })
    result = jwt.decode(token, 'secret', algorithm='HS256', audience='aud')
    assert result['sub'] == u1.ident
    assert result['other'] == 'true'
