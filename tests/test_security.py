# tests/test_security.py
import pytest
from app.core.security import hash_password, verify_password, create_access_token, decode_token
from datetime import timedelta


class TestSecurity:
    def test_hash_password(self):
        """Хеширование пароля"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        """Проверка правильного пароля"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Проверка неправильного пароля"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password("wrongpassword", hashed) is False

    def test_hash_password_different_salts(self):
        """Одинаковые пароли дают разные хеши"""
        password = "testpassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_create_access_token(self):
        """Создание access токена"""
        token = create_access_token(data={"sub": "1", "username": "test"})
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_expiry(self):
        """Создание токена с пользовательским сроком"""
        expires = timedelta(minutes=5)
        token = create_access_token(
            data={"sub": "1", "username": "test"},
            expires_delta=expires
        )
        assert token is not None

    def test_decode_token_valid(self):
        """Декодирование валидного токена"""
        token = create_access_token(data={"sub": "123", "username": "testuser"})
        payload = decode_token(token)
        
        assert payload is not None
        assert payload["sub"] == "123"
        assert payload["username"] == "testuser"
        assert "exp" in payload

    def test_decode_token_invalid(self):
        """Декодирование невалидного токена"""
        payload = decode_token("invalid.token.string")
        assert payload is None

    def test_create_refresh_token(self):
        """Создание refresh токена"""
        from app.core.security import create_refresh_token
        
        token = create_refresh_token(data={"sub": "1", "username": "test"})
        assert token is not None
        assert isinstance(token, str)
        
        payload = decode_token(token)
        assert payload is not None
        assert payload["type"] == "refresh"