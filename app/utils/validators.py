def validate_measurement_value(value: float, param_name: str) -> tuple:
    if value is None:
        return False, "Значение не может быть пустым"
    
    if param_name == "temperature":
        if value < 0 or value > 45:
            return False, "Температура должна быть в диапазоне 0-45°C"
    elif param_name == "ph":
        if value < 0 or value > 14:
            return False, "pH должен быть в диапазоне 0-14"
    elif param_name == "ammonia" or param_name == "nitrites":
        if value < 0:
            return False, "Значение не может быть отрицательным"
        if value > 10:
            return False, f"{param_name} не может превышать 10 мг/л"
    elif param_name == "nitrates":
        if value < 0:
            return False, "Значение не может быть отрицательным"
        if value > 200:
            return False, "Нитраты не могут превышать 200 мг/л"
    elif param_name == "gh" or param_name == "kh":
        if value < 0 or value > 30:
            return False, f"{param_name} должен быть в диапазоне 0-30"
    elif param_name == "salinity":
        if value < 1.000 or value > 1.040:
            return False, "Соленость должна быть в диапазоне 1.000-1.040"
    elif param_name == "calcium":
        if value < 0 or value > 600:
            return False, "Кальций должен быть в диапазоне 0-600 мг/л"
    
    return True, "OK"