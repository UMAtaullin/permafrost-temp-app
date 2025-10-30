class PermafrostModel:
    def __init__(self):
        # Базовые параметры грунтов
        self.ground_params = {
            "торф": {"conductivity": 0.35, "damping_depth": 2.5},
            "суглинок": {"conductivity": 1.25, "damping_depth": 4.0},
            "супесь": {"conductivity": 1.5, "damping_depth": 5.0},
            "песок": {"conductivity": 2.0, "damping_depth": 6.0},
        }

        # Температурные градации грунтов (твёрдомёрзлый, пластичномёрзлый, охлаждённый)
        self.temperature_grades = {
            "песок средней крупности": {
                "твёрдомёрзлый": -0.10,
                "пластичномёрзлый": (-0.11, -0.29),
            },
            "песок мелкий": {
                "твёрдомёрзлый": -0.30,
                "пластичномёрзлый": (-0.16, -0.29),
            },
            "песок пылеватый": {
                "твёрдомёрзлый": -0.15,
                "пластичномёрзлый": (-0.16, -0.29),
            },
            "супесь": {"твёрдомёрзлый": -0.60, "пластичномёрзлый": (-0.21, -0.59)},
            "суглинок": {"твёрдомёрзлый": -1.00, "пластичномёрзлый": (-0.26, -0.99)},
            "глина": {"твёрдомёрзлый": -1.50, "пластичномёрзлый": (-0.26, -1.49)},
        }

    def predict_temperature(self, depth, lithology, surface_temp, season="лето"):
        """
        Простая физическая модель температуры на глубине
        """
        params = self.ground_params[lithology]

        # Сезонные поправки
        season_correction = {"зима": -8, "весна": -2, "лето": 0, "осень": -4}

        correction = season_correction.get(season, 0)

        # Упрощённая формула затухания
        import math

        temp_at_depth = surface_temp + correction * math.exp(
            -depth / params["damping_depth"]
        )

        return round(temp_at_depth, 1)

    def get_ground_state(self, temp, ground_type):
        """
        Определяем состояние грунта по температуре
        """
        if ground_type not in self.temperature_grades:
            return "не определено"

        grades = self.temperature_grades[ground_type]

        if temp <= grades["твёрдомёрзлый"]:
            return "твёрдомёрзлый"
        elif grades["пластичномёрзлый"][0] <= temp <= grades["пластичномёрзлый"][1]:
            return "пластичномёрзлый"
        elif temp < 0:
            return "охлаждённый"
        else:
            return "талый"
