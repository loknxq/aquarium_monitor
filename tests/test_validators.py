import pytest
from app.utils.validators import validate_measurement_value

class TestValidators:
    
    def test_valid_temperature(self):
        is_valid, msg = validate_measurement_value(25.0, "temperature")
        assert is_valid is True
    
    def test_temperature_too_high(self):
        is_valid, msg = validate_measurement_value(50.0, "temperature")
        assert is_valid is False
    
    def test_temperature_negative(self):
        is_valid, msg = validate_measurement_value(-5.0, "temperature")
        assert is_valid is False
    
    def test_valid_ph(self):
        is_valid, msg = validate_measurement_value(7.0, "ph")
        assert is_valid is True
    
    def test_ph_too_high(self):
        is_valid, msg = validate_measurement_value(15.0, "ph")
        assert is_valid is False
    
    def test_ph_negative(self):
        is_valid, msg = validate_measurement_value(-1.0, "ph")
        assert is_valid is False
    
    def test_valid_ammonia(self):
        is_valid, msg = validate_measurement_value(0.25, "ammonia")
        assert is_valid is True
    
    def test_ammonia_too_high(self):
        is_valid, msg = validate_measurement_value(11.0, "ammonia")
        assert is_valid is False
    
    def test_ammonia_negative(self):
        is_valid, msg = validate_measurement_value(-0.1, "ammonia")
        assert is_valid is False
    
    def test_valid_nitrates(self):
        is_valid, msg = validate_measurement_value(40.0, "nitrates")
        assert is_valid is True
    
    def test_nitrates_negative(self):
        is_valid, msg = validate_measurement_value(-10.0, "nitrates")
        assert is_valid is False
    
    def test_valid_gh(self):
        is_valid, msg = validate_measurement_value(10.0, "gh")
        assert is_valid is True
    
    def test_gh_too_high(self):
        is_valid, msg = validate_measurement_value(35.0, "gh")
        assert is_valid is False
    
    def test_valid_salinity(self):
        is_valid, msg = validate_measurement_value(1.025, "salinity")
        assert is_valid is True
    
    def test_salinity_too_high(self):
        is_valid, msg = validate_measurement_value(1.050, "salinity")
        assert is_valid is False
    
    def test_valid_calcium(self):
        is_valid, msg = validate_measurement_value(400.0, "calcium")
        assert is_valid is True
    
    def test_calcium_too_high(self):
        is_valid, msg = validate_measurement_value(700.0, "calcium")
        assert is_valid is False