import pandas as pd
import numpy as np
from scipy import interpolate
from sklearn.ensemble import RandomForestRegressor
import joblib
import os


class PermafrostModel:
    def __init__(self):
        # Базовые параметры
        self.ground_params = {
            "прс": {"type": "seasonal"},
            "торф": {"type": "seasonal"},
            "суглинок": {"type": "permafrost"},
            "супесь": {"type": "permafrost"},
            "песок": {"type": "permafrost"},
        }

        # РЕАЛЬНЫЕ ДАННЫЕ ИЗ ВАШЕГО ЖУРНАЛА (средние значения)
        self.reference_profile = {
            "depth": [
                0,
                0.5,
                1.0,
                1.5,
                2.0,
                2.5,
                3.0,
                3.5,
                4.0,
                4.5,
                5.0,
                6.0,
                7.0,
                8.0,
                9.0,
                10.0,
                12.0,
                14.0,
                16.0,
                18.0,
                20.0,
                21.0,
                24.0,
                26.0,
                27.0,
                30.0,
            ],
            "temperature": [
                -3.0,
                -4.0,
                -0.92,
                -0.90,
                -0.56,
                -0.50,
                -0.46,
                -0.42,
                -0.48,
                -0.53,
                -0.74,
                -0.85,
                -0.76,
                -0.74,
                -0.81,
                -0.82,
                -0.87,
                -0.94,
                -1.01,
                -1.01,
                -1.05,
                -1.06,
                -1.09,
                -1.28,
                -1.29,
                -1.28,
            ],
        }

        # Создаем интерполяционную функцию на основе реальных данных
        self.interp_function = interpolate.interp1d(
            self.reference_profile["depth"],
            self.reference_profile["temperature"],
            kind="linear",
            fill_value="extrapolate",
        )

        # ML модель
        self.ml_model = None
        self.is_ml_trained = False
        self.training_data = []

        self.load_ml_model()

    def predict_temperature(
        self, depth, lithology, surface_temp, season="лето", use_ml=True
    ):
        """
        Модель на основе реальных данных с корректировкой по поверхности
        """
        # Базовое предсказание из эталонного профиля
        base_temp = float(self.interp_function(depth))

        # Корректируем относительно температуры поверхности
        # В эталонном профиле поверхность = -3°C, корректируем под нашу поверхность
        surface_diff = surface_temp - (-3.0)  # Разница с эталонной поверхностью
        corrected_temp = base_temp + surface_diff * self.get_surface_influence(depth)

        return round(corrected_temp, 2)

    def get_surface_influence(self, depth):
        """
        Влияние температуры поверхности с глубиной (затухание)
        """
        # На поверхности влияние 100%, на 10м - 10%, глубже - почти 0
        if depth <= 1.0:
            return 1.0
        elif depth <= 5.0:
            return 1.0 - (depth - 1.0) / 4.0  # Линейное затухание от 1 до 5м
        else:
            return max(0.1, 1.0 - depth / 10.0)  # Минимум 10% влияния

    def normalize_lithology(self, lithology_name):
        """
        Нормализуем названия грунтов к стандартным
        """
        if not isinstance(lithology_name, str):
            return "суглинок"

        lith_lower = lithology_name.lower().strip()

        lithology_map = {
            "торф": "торф",
            "суглинок": "суглинок",
            "супесь": "супесь",
            "песок": "песок",
            "прс": "прс",
            "прп": "торф",
            "растительный": "прс",
            "мох": "прс",
            "моховой": "прс",
            "растительный слой": "прс",
            "почва": "прс",
        }

        for key, value in lithology_map.items():
            if key in lith_lower:
                return value

        if "пес" in lith_lower:
            return "песок"
        elif "сугл" in lith_lower:
            return "суглинок"
        elif "супе" in lith_lower:
            return "супесь"
        elif "торф" in lith_lower:
            return "торф"

        return "суглинок"

    # Остальные методы оставляем как были
    def ml_prediction(self, depth, lithology, surface_temp, season):
        if not self.is_ml_trained:
            return self.predict_temperature(depth, lithology, surface_temp, season)

        season_encoded = {"зима": 0, "весна": 1, "лето": 2, "осень": 3}
        lithology_encoded = {
            "торф": 0,
            "суглинок": 1,
            "супесь": 2,
            "песок": 3,
            "прс": 4,
        }

        lithology_norm = self.normalize_lithology(lithology)

        features = np.array(
            [
                [
                    depth,
                    lithology_encoded.get(lithology_norm, 1),
                    surface_temp,
                    season_encoded[season],
                ]
            ]
        )

        prediction = self.ml_model.predict(features)[0]
        return round(prediction, 2)

    def add_training_data(self, depth, lithology, surface_temp, season, actual_temp):
        season_encoded = {"зима": 0, "весна": 1, "лето": 2, "осень": 3}
        lithology_encoded = {
            "торф": 0,
            "суглинок": 1,
            "супесь": 2,
            "песок": 3,
            "прс": 4,
        }

        lithology_norm = self.normalize_lithology(lithology)

        self.training_data.append(
            {
                "depth": depth,
                "lithology": lithology_encoded.get(lithology_norm, 1),
                "surface_temp": surface_temp,
                "season": season_encoded[season],
                "actual_temp": actual_temp,
            }
        )

    def train_ml_model(self):
        if len(self.training_data) < 5:
            return False, "Недостаточно данных для обучения. Нужно минимум 5 замеров."

        df = pd.DataFrame(self.training_data)
        X = df[["depth", "lithology", "surface_temp", "season"]]
        y = df["actual_temp"]

        if self.ml_model is None:
            self.ml_model = RandomForestRegressor(n_estimators=50, random_state=42)

        self.ml_model.fit(X, y)
        self.is_ml_trained = True
        self.save_ml_model()

        return True, f"Модель успешно обучена на {len(self.training_data)} замерах"

    def save_ml_model(self):
        if self.ml_model is not None:
            os.makedirs("models", exist_ok=True)
            joblib.dump(self.ml_model, "models/temperature_model.joblib")

    def load_ml_model(self):
        try:
            self.ml_model = joblib.load("models/temperature_model.joblib")
            self.is_ml_trained = True
        except:
            self.ml_model = None
            self.is_ml_trained = False

    def get_ground_state(self, temp, lithology):
        temperature_grades = {
            "песок": {"твёрдомёрзлый": -0.10, "пластичномёрзлый": (-0.11, -0.29)},
            "супесь": {"твёрдомёрзлый": -0.60, "пластичномёрзлый": (-0.21, -0.59)},
            "суглинок": {"твёрдомёрзлый": -1.00, "пластичномёрзлый": (-0.26, -0.99)},
            "торф": {"твёрдомёрзлый": -0.50, "пластичномёрзлый": (-0.21, -0.49)},
            "прс": {"твёрдомёрзлый": -0.30, "пластичномёрзлый": (-0.11, -0.29)},
        }

        lithology_norm = self.normalize_lithology(lithology)

        if lithology_norm not in temperature_grades:
            lithology_norm = "суглинок"

        grades = temperature_grades[lithology_norm]

        if temp <= grades["твёрдомёрзлый"]:
            return "твёрдомёрзлый"
        elif (
            isinstance(grades["пластичномёрзлый"], tuple)
            and grades["пластичномёрзлый"][0] <= temp <= grades["пластичномёрзлый"][1]
        ):
            return "пластичномёрзлый"
        elif temp < 0:
            return "охлаждённый"
        else:
            return "талый"
