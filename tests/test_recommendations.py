import pytest
from app.services.recommendations import get_recommendations, INHABITANT_PARAMETERS

class TestRecommendations:
    
    def test_get_recommendations_temperature_low(self):
        measurements = {"temperature": 20.0}
        recs = get_recommendations("tropical_fish", measurements)
        assert len(recs) > 0
        assert "ниже нормы" in recs[0]
    
    def test_get_recommendations_temperature_high(self):
        measurements = {"temperature": 30.0}
        recs = get_recommendations("tropical_fish", measurements)
        assert len(recs) > 0
        assert "выше нормы" in recs[0]
    
    def test_get_recommendations_ammonia_high(self):
        measurements = {"ammonia": 0.5}
        recs = get_recommendations("tropical_fish", measurements)
        assert len(recs) > 0
        assert "аммиак" in recs[0].lower()
    
    def test_get_recommendations_nitrites_high(self):
        measurements = {"nitrites": 1.0}
        recs = get_recommendations("tropical_fish", measurements)
        assert len(recs) > 0
        assert "нитриты" in recs[0].lower()
    
    def test_no_recommendations_when_ok(self):
        measurements = {"temperature": 26.0, "ph": 7.0}
        recs = get_recommendations("tropical_fish", measurements)
        assert len(recs) == 0
    
    def test_recommendations_for_goldfish(self):
        measurements = {"temperature": 15.0}
        recs = get_recommendations("goldfish", measurements)
        assert len(recs) > 0
    
    def test_recommendations_for_shrimp(self):
        measurements = {"gh": 4.0}
        recs = get_recommendations("shrimp", measurements)
        assert len(recs) > 0
    
    def test_recommendations_for_cichlids(self):
        measurements = {"ph": 7.0}
        recs = get_recommendations("cichlids", measurements)
        assert len(recs) > 0
    
    def test_recommendations_for_plants(self):
        measurements = {"co2": 10.0}
        recs = get_recommendations("plants", measurements)
        assert len(recs) > 0
    
    def test_recommendations_for_marine(self):
        measurements = {"salinity": 1.018}
        recs = get_recommendations("marine", measurements)
        assert len(recs) > 0
    
    def test_invalid_inhabitant_fallback(self):
        measurements = {"temperature": 15.0}
        recs = get_recommendations("unknown", measurements)
        assert isinstance(recs, list)
    
    def test_multiple_issues(self):
        measurements = {"temperature": 30.0, "ammonia": 0.5, "nitrites": 1.0}
        recs = get_recommendations("tropical_fish", measurements)
        assert len(recs) >= 2