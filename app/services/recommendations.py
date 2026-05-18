from typing import Dict, List, Optional

INHABITANT_PARAMETERS = {
    "tropical_fish": {
        "temperature": {"min": 24, "max": 28, "unit": "C", "warning": "Тропическим рыбам требуется температура 24-28C"},
        "ph": {"min": 6.5, "max": 7.5, "unit": "", "warning": "pH для тропических рыб должен быть 6.5-7.5"},
        "ammonia": {"min": 0, "max": 0.25, "unit": "mg/L", "warning": "Аммиак выше 0.25 мг/л токсичен для рыб"},
        "nitrites": {"min": 0, "max": 0.5, "unit": "mg/L", "warning": "Нитриты выше 0.5 мг/л опасны"},
        "nitrates": {"min": 0, "max": 40, "unit": "mg/L", "warning": "Нитраты выше 40 мг/л вызывают стресс"}
    },
    "goldfish": {
        "temperature": {"min": 18, "max": 22, "unit": "C", "warning": "Золотым рыбкам нужна температура 18-22C"},
        "ph": {"min": 7.0, "max": 8.0, "unit": "", "warning": "pH для золотых рыбок 7.0-8.0"},
        "ammonia": {"min": 0, "max": 0.1, "unit": "mg/L", "warning": "Золотые рыбки очень чувствительны к аммиаку"},
        "nitrites": {"min": 0, "max": 0.2, "unit": "mg/L", "warning": "Нитриты выше 0.2 мг/л опасны для золотых рыбок"},
        "nitrates": {"min": 0, "max": 30, "unit": "mg/L", "warning": "Нитраты выше 30 мг/л вызывают проблемы"}
    },
    "shrimp": {
        "temperature": {"min": 22, "max": 26, "unit": "C", "warning": "Креветкам нужна температура 22-26C"},
        "ph": {"min": 6.8, "max": 7.5, "unit": "", "warning": "pH для креветок 6.8-7.5"},
        "gh": {"min": 6, "max": 8, "unit": "dGH", "warning": "Жесткость для креветок 6-8 dGH"},
        "ammonia": {"min": 0, "max": 0, "unit": "mg/L", "warning": "Креветки не выносят аммиак даже в малых дозах"},
        "nitrites": {"min": 0, "max": 0, "unit": "mg/L", "warning": "Нитриты смертельны для креветок"},
        "nitrates": {"min": 0, "max": 20, "unit": "mg/L", "warning": "Нитраты выше 20 мг/л опасны для креветок"}
    },
    "cichlids": {
        "temperature": {"min": 25, "max": 28, "unit": "C", "warning": "Цихлидам нужна температура 25-28C"},
        "ph": {"min": 7.5, "max": 8.5, "unit": "", "warning": "Цихлидам требуется pH 7.5-8.5"},
        "gh": {"min": 10, "max": 20, "unit": "dGH", "warning": "Цихлидам нужна жесткая вода 10-20 dGH"},
        "ammonia": {"min": 0, "max": 0.25, "unit": "mg/L", "warning": "Аммиак выше 0.25 мг/л токсичен"},
        "nitrites": {"min": 0, "max": 0.5, "unit": "mg/L", "warning": "Нитриты выше 0.5 мг/л опасны"},
        "nitrates": {"min": 0, "max": 50, "unit": "mg/L", "warning": "Нитраты выше 50 мг/л вызывают стресс"}
    },
    "plants": {
        "temperature": {"min": 22, "max": 26, "unit": "C", "warning": "Растениям нужна температура 22-26C"},
        "ph": {"min": 6.5, "max": 7.2, "unit": "", "warning": "pH для растений 6.5-7.2"},
        "nitrates": {"min": 10, "max": 30, "unit": "mg/L", "warning": "Растениям нужны нитраты 10-30 мг/л"},
        "co2": {"min": 20, "max": 30, "unit": "mg/L", "warning": "CO2 для растений 20-30 мг/л"},
        "kh": {"min": 3, "max": 8, "unit": "dKH", "warning": "Карбонатная жесткость для растений 3-8 dKH"}
    },
    "marine": {
        "temperature": {"min": 24, "max": 26, "unit": "C", "warning": "Морскому аквариуму нужна температура 24-26C"},
        "ph": {"min": 8.1, "max": 8.4, "unit": "", "warning": "pH для морской воды 8.1-8.4"},
        "salinity": {"min": 1.022, "max": 1.026, "unit": "SG", "warning": "Соленость морской воды 1.022-1.026"},
        "ammonia": {"min": 0, "max": 0, "unit": "mg/L", "warning": "Аммиак в морском аквариуме смертелен"},
        "nitrites": {"min": 0, "max": 0, "unit": "mg/L", "warning": "Нитриты в морском аквариуме смертельны"},
        "nitrates": {"min": 0, "max": 10, "unit": "mg/L", "warning": "Нитраты в морском аквариуме выше 10 мг/л опасны"},
        "calcium": {"min": 400, "max": 450, "unit": "mg/L", "warning": "Кальций для кораллов 400-450 мг/л"}
    }
}

def get_recommendations(inhabitants: str, measurements: Dict[str, float]) -> List[str]:
    if not inhabitants or inhabitants == "":
        inhabitants = "tropical_fish"
    
    inhabitant_params = INHABITANT_PARAMETERS.get(inhabitants, INHABITANT_PARAMETERS["tropical_fish"])
    recommendations = []
    
    for param_name, value in measurements.items():
        if param_name in inhabitant_params:
            param_range = inhabitant_params[param_name]
            min_val = param_range["min"]
            max_val = param_range["max"]
            
            if value < min_val:
                if param_name == "temperature":
                    recommendations.append(f"Температура {value}C ниже нормы ({min_val}-{max_val}C). Поднимите температуру")
                elif param_name == "ph":
                    recommendations.append(f"pH {value} ниже нормы ({min_val}-{max_val}). Используйте буферные добавки")
                elif param_name == "ammonia":
                    recommendations.append(f"Аммиак {value} мг/л. Сделайте подмену воды 30%")
                elif param_name == "nitrites":
                    recommendations.append(f"Нитриты {value} мг/л. Добавьте бактерии и сделайте подмену")
                elif param_name == "nitrates":
                    recommendations.append(f"Нитраты {value} мг/л. Сделайте подмену воды 20-30%")
                elif param_name == "gh":
                    recommendations.append(f"Жесткость {value} dGH ниже нормы. Добавьте минералы")
                elif param_name == "kh":
                    recommendations.append(f"KH {value} dKH ниже нормы. Добавьте буфер KH")
                elif param_name == "co2":
                    recommendations.append(f"CO2 {value} мг/л ниже нормы. Увеличьте подачу CO2")
                elif param_name == "salinity":
                    recommendations.append(f"Соленость {value} ниже нормы. Добавьте морскую соль")
                elif param_name == "calcium":
                    recommendations.append(f"Кальций {value} мг/л ниже нормы. Добавьте кальций")
                else:
                    recommendations.append(f"{param_name} {value}{param_range['unit']} ниже нормы ({min_val}-{max_val})")
            
            elif value > max_val:
                if param_name == "temperature":
                    recommendations.append(f"Температура {value}C выше нормы ({min_val}-{max_val}C). Охладите воду")
                elif param_name == "ph":
                    recommendations.append(f"pH {value} выше нормы ({min_val}-{max_val}). Добавьте смягчитель воды")
                elif param_name == "ammonia":
                    recommendations.append(f"Аммиак {value} мг/л критично! Сделайте подмену 50%")
                elif param_name == "nitrites":
                    recommendations.append(f"Нитриты {value} мг/л опасно! Сделайте подмену 40%")
                elif param_name == "nitrates":
                    recommendations.append(f"Нитраты {value} мг/л. Сделайте подмену воды 30-40%")
                elif param_name == "gh":
                    recommendations.append(f"Жесткость {value} dGH выше нормы. Разбавьте осмосом")
                elif param_name == "kh":
                    recommendations.append(f"KH {value} dKH выше нормы. Разбавьте осмосом")
                elif param_name == "co2":
                    recommendations.append(f"CO2 {value} мг/л выше нормы. Уменьшите подачу CO2")
                elif param_name == "salinity":
                    recommendations.append(f"Соленость {value} выше нормы. Добавьте пресную воду")
                elif param_name == "calcium":
                    recommendations.append(f"Кальций {value} мг/л выше нормы. Сделайте подмену воды")
                else:
                    recommendations.append(f"{param_name} {value}{param_range['unit']} выше нормы ({min_val}-{max_val})")
    
    return recommendations