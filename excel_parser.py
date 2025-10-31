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


    # excel_parser.py - обновляем функцию map_lithology
    def map_lithology(self, lithology_name):
        """
        УЛУЧШЕННОЕ приведение названий грунтов к стандартным типам
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

        # Поиск по ключевым словам
        for key, value in lithology_map.items():
            if key in lith_lower:
                return value

        # Если не нашли, пытаемся определить по описанию
        if "пес" in lith_lower:
            return "песок"
        elif "сугл" in lith_lower:
            return "суглинок"
        elif "супе" in lith_lower:
            return "супесь"
        elif "торф" in lith_lower:
            return "торф"

        return "суглинок"  # значение по умолчанию
