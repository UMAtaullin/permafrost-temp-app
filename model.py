import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
import os


class PermafrostModel:
    def __init__(self):
        # Базовые параметры грунтов
        self.ground_params = {
            "торф": {"conductivity": 0.35, "damping_depth": 2.5},
            "суглинок": {"conductivity": 1.25, "damping_depth": 4.0},
            "супесь": {"conductivity": 1.5, "damping_depth": 5.0},
            "песок": {"conductivity": 2.0, "damping_depth": 6.0},
        }

        # ML модель
        self.ml_model = None
        self.is_ml_trained = False
        self.training_data = []

        # Загружаем ML модель если она есть
        self.load_ml_model()

    def predict_temperature(
        self, depth, lithology, surface_temp, season="лето", use_ml=True
    ):
        """
        Комбинированная модель: физическая + ML
        """
        # Сначала получаем предсказание физической модели
        physical_pred = self.physical_prediction(depth, lithology, surface_temp, season)

        # Если ML модель обучена, используем её
        if use_ml and self.is_ml_trained:
            ml_pred = self.ml_prediction(depth, lithology, surface_temp, season)
            # Пока используем среднее между физической и ML моделью
            return round((physical_pred + ml_pred) / 2, 1)

        return physical_pred

    def physical_prediction(self, depth, lithology, surface_temp, season):
        """
        Физическая модель температуры на глубине
        """
        params = self.ground_params[lithology]

        # Сезонные поправки
        season_correction = {"зима": -8, "весна": -2, "лето": 0, "осень": -4}

        correction = season_correction.get(season, 0)

        # Упрощённая формула затухания
        temp_at_depth = surface_temp + correction * np.exp(
            -depth / params["damping_depth"]
        )

        return round(temp_at_depth, 1)

    def ml_prediction(self, depth, lithology, surface_temp, season):
        """
        Предсказание ML модели
        """
        if not self.is_ml_trained:
            return self.physical_prediction(depth, lithology, surface_temp, season)

        # Кодируем категориальные признаки
        season_encoded = {"зима": 0, "весна": 1, "лето": 2, "осень": 3}
        lithology_encoded = {"торф": 0, "суглинок": 1, "супесь": 2, "песок": 3}

        features = np.array(
            [
                [
                    depth,
                    lithology_encoded[lithology],
                    surface_temp,
                    season_encoded[season],
                ]
            ]
        )

        prediction = self.ml_model.predict(features)[0]
        return round(prediction, 1)

    def add_training_data(self, depth, lithology, surface_temp, season, actual_temp):
        """
        Добавляем данные для обучения ML модели
        """
        season_encoded = {"зима": 0, "весна": 1, "лето": 2, "осень": 3}
        lithology_encoded = {"торф": 0, "суглинок": 1, "супесь": 2, "песок": 3}

        self.training_data.append(
            {
                "depth": depth,
                "lithology": lithology_encoded[lithology],
                "surface_temp": surface_temp,
                "season": season_encoded[season],
                "actual_temp": actual_temp,
            }
        )

    def train_ml_model(self):
        """
        Обучаем ML модель на накопленных данных
        """
        if len(self.training_data) < 10:
            return False, "Недостаточно данных для обучения. Нужно минимум 10 замеров."

        df = pd.DataFrame(self.training_data)
        X = df[["depth", "lithology", "surface_temp", "season"]]
        y = df["actual_temp"]

        if self.ml_model is None:
            self.ml_model = RandomForestRegressor(n_estimators=100, random_state=42)

        self.ml_model.fit(X, y)
        self.is_ml_trained = True

        # Сохраняем модель
        self.save_ml_model()

        return True, f"Модель успешно обучена на {len(self.training_data)} замерах"

    def save_ml_model(self):
        """Сохраняем ML модель"""
        if self.ml_model is not None:
            os.makedirs("models", exist_ok=True)
            joblib.dump(self.ml_model, "models/temperature_model.joblib")

    def load_ml_model(self):
        """Загружаем ML модель если она есть"""
        try:
            self.ml_model = joblib.load("models/temperature_model.joblib")
            self.is_ml_trained = True
        except:
            self.ml_model = None
            self.is_ml_trained = False

    def get_ground_state(self, temp, ground_type):
        """
        Определяем состояние грунта по температуре
        """
        # (оставляем предыдущую реализацию)
        temperature_grades = {
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

        if ground_type not in temperature_grades:
            return "не определено"

        grades = temperature_grades[ground_type]

        if temp <= grades["твёрдомёрзлый"]:
            return "твёрдомёрзлый"
        elif grades["пластичномёрзлый"][0] <= temp <= grades["пластичномёрзлый"][1]:
            return "пластичномёрзлый"
        elif temp < 0:
            return "охлаждённый"
        else:
            return "талый"
