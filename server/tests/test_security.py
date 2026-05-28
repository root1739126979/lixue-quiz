from app.security import create_access_token, decode_access_token, hash_password, verify_password


def test_password_hash_verification():
    password_hash = hash_password("secret123")

    assert password_hash != "secret123"
    assert verify_password("secret123", password_hash)
    assert not verify_password("wrong", password_hash)


def test_access_token_contains_subject_and_role():
    token = create_access_token(subject="42", role="employee")

    assert isinstance(token, str)
    assert token.count(".") == 2
    assert decode_access_token(token)["sub"] == "42"
    assert decode_access_token(token)["role"] == "employee"
