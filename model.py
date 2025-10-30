import numpy as np


class PermafrostModel:
    def __init__(self):
        # Базовые параметры грунтов (теплопроводность, глубина затухания)
        self.ground_params = {
            "торф": {"conductivity": 0.35, "damping_depth": 2.5},
            "суглинок": {"conductivity": 1.25, "damping_depth": 4.0},
            "супесь": {"conductivity": 1.5, "damping_depth": 5.0},
            "песок": {"conductivity": 2.0, "damping_depth": 6.0},
        }

    def predict_temperature(self, depth, lithology, surface_temp, season="лето"):
        """
        Простая физическая модель температуры на глубине
        """
        params = self.ground_params[lithology]

        # Сезонные поправки (упрощённо)
        season_correction = {"зима": -8, "весна": -2, "лето": 0, "осень": -4}

        correction = season_correction.get(season, 0)

        # Упрощённая формула затухания температурной амплитуды с глубиной
        temp_at_depth = surface_temp + correction * np.exp(
            -depth / params["damping_depth"]
        )

        return round(temp_at_depth, 1)
