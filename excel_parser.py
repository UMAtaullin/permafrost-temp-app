# Создаём файл excel_parser.py
import pandas as pd
import streamlit as st


class BoreholeDataParser:
    def __init__(self):
        self.expected_columns = [
            "Скважина",
            "Глубина от, м",
            "Глубина до, м",
            "Мощность, м",
            "Интервалы керна",
            "Литология",
            "Описание",
            "Дата создания",
        ]

    def parse_excel_data(self, uploaded_file):
        """
        Парсим данные из Excel файла бурового журнала
        """
        try:
            df = pd.read_excel(uploaded_file)

            # Проверяем наличие нужных колонок
            missing_cols = [
                col for col in self.expected_columns if col not in df.columns
            ]
            if missing_cols:
                st.error(f"В файле отсутствуют колонки: {missing_cols}")
                return None

            return df
        except Exception as e:
            st.error(f"Ошибка чтения файла: {e}")
            return None

    def get_boreholes_list(self, df):
        """Получаем список скважин из данных"""
        return df["Скважина"].unique().tolist()

    def get_layers_for_borehole(self, df, borehole_id):
        """Получаем слои для конкретной скважины"""
        borehole_data = df[df["Скважина"] == borehole_id].copy()
        borehole_data = borehole_data.sort_values("Глубина от, м")

        layers = []
        for _, row in borehole_data.iterrows():
            layers.append(
                {
                    "depth_from": row["Глубина от, м"],
                    "depth_to": row["Глубина до, м"],
                    "thickness": row["Мощность, м"],
                    "lithology": self.map_lithology(row["Литология"]),
                    "description": row["Описание"],
                    "core_intervals": row["Интервалы керна"],
                }
            )

        return layers

    def map_lithology(self, lithology_name):
        """
        Приводим названия грунтов к стандартным типам
        """
        lithology_map = {
            "торф": "торф",
            "суглинок": "суглинок",
            "супесь": "супесь",
            "песок": "песок",
            "прп": "торф",  # предположение
            "прс": "торф",  # предположение
        }

        lithology_lower = lithology_name.lower().strip()
        for key, value in lithology_map.items():
            if key in lithology_lower:
                return value

        return "суглинок"  # значение по умолчанию
