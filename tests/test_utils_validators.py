# tests/test_utils_validators.py
import pytest
from app.utils.validators import validate_measurement_value


class TestValidators:
    def test_validate_temperature_valid(self):
        """Валидация корректной температуры"""
        is_valid, message = validate_measurement_value(25.5, "temperature")
        assert is_valid is True
        assert message == "OK"

    def test_validate_temperature_too_low(self):
        """Валидация слишком низкой температуры"""
        is_valid, message = validate_measurement_value(-5.0, "temperature")
        assert is_valid is False
        assert "0-45" in message

    def test_validate_temperature_too_high(self):
        """Валидация слишком высокой температуры"""
        is_valid, message = validate_measurement_value(50.0, "temperature")
        assert is_valid is False
        assert "0-45" in message

    def test_validate_ph_valid(self):
        """Валидация корректного pH"""
        is_valid, message = validate_measurement_value(7.2, "ph")
        assert is_valid is True

    def test_validate_ph_too_low(self):
        """Валидация слишком низкого pH"""
        is_valid, message = validate_measurement_value(-1.0, "ph")
        assert is_valid is False

    def test_validate_ph_too_high(self):
        """Валидация слишком высокого pH"""
        is_valid, message = validate_measurement_value(15.0, "ph")
        assert is_valid is False
        assert "pH должен быть" in message

    def test_validate_ammonia_valid(self):
        """Валидация корректного аммиака"""
        is_valid, message = validate_measurement_value(0.25, "ammonia")
        assert is_valid is True

    def test_validate_ammonia_too_high(self):
        """Валидация слишком высокого аммиака"""
        is_valid, message = validate_measurement_value(11.0, "ammonia")
        assert is_valid is False
        assert "10 мг/л" in message

    def test_validate_nitrates_valid(self):
        """Валидация корректных нитратов"""
        is_valid, message = validate_measurement_value(40.0, "nitrates")
        assert is_valid is True

    def test_validate_nitrates_too_high(self):
        """Валидация слишком высоких нитратов"""
        is_valid, message = validate_measurement_value(250.0, "nitrates")
        assert is_valid is False
        assert "200 мг/л" in message

    def test_validate_gh_valid(self):
        """Валидация корректной жесткости GH"""
        is_valid, message = validate_measurement_value(10.0, "gh")
        assert is_valid is True

    def test_validate_salinity_valid(self):
        """Валидация корректной солености"""
        is_valid, message = validate_measurement_value(1.025, "salinity")
        assert is_valid is True

    def test_validate_calcium_valid(self):
        """Валидация корректного кальция"""
        is_valid, message = validate_measurement_value(420.0, "calcium")
        assert is_valid is True