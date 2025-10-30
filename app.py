import streamlit as st
import pandas as pd
import numpy as np
from model import PermafrostModel
from excel_parser import BoreholeDataParser

# Настройка страницы
st.set_page_config(
    page_title="Термометрия мерзлых грунтов", page_icon="🧊", layout="wide"
)

st.title("🧊 Интегрированная система термометрии")
st.write("Загрузка данных из бурового журнала и прогноз температур")

# Инициализация
if "model" not in st.session_state:
    st.session_state.model = PermafrostModel()
    st.session_state.parser = BoreholeDataParser()
    st.session_state.borehole_data = None

# Боковая панель
with st.sidebar:
    st.header("📁 Загрузка данных")

    uploaded_file = st.file_uploader(
        "Загрузите Excel файл бурового журнала", type=["xlsx", "xls"]
    )

    if uploaded_file is not None:
        st.session_state.borehole_data = st.session_state.parser.parse_excel_data(
            uploaded_file
        )

        if st.session_state.borehole_data is not None:
            boreholes = st.session_state.parser.get_boreholes_list(
                st.session_state.borehole_data
            )
            selected_borehole = st.selectbox("Выберите скважину", boreholes)

            # Показываем информацию о скважине
            borehole_layers = st.session_state.parser.get_layers_for_borehole(
                st.session_state.borehole_data, selected_borehole
            )

            st.subheader("Геологический разрез скважины")
            for i, layer in enumerate(borehole_layers, 1):
                st.write(
                    f"{i}. {layer['lithology']}: {layer['depth_from']}-{layer['depth_to']}м"
                )

    st.header("🌡️ Климатические параметры")
    surface_temp = st.number_input(
        "Температура поверхности (°C)", -30.0, 20.0, -5.0, 0.5
    )
    season = st.selectbox("Время года", ["зима", "весна", "лето", "осень"])

    st.header("🤖 Настройки модели")
    use_ml = st.checkbox(
        "Использовать ML модель", value=st.session_state.model.is_ml_trained
    )

    if st.button("Обучить ML модель") and len(st.session_state.model.training_data) > 0:
        success, message = st.session_state.model.train_ml_model()
        if success:
            st.success(message)
        else:
            st.error(message)

# Основная область
if st.session_state.borehole_data is not None and "selected_borehole" in locals():
    # Получаем слои для выбранной скважины
    layers = st.session_state.parser.get_layers_for_borehole(
        st.session_state.borehole_data, selected_borehole
    )

    st.header(f"Температурный профиль для скважины {selected_borehole}")

    # Функция для определения грунта на глубине
    def get_lithology_at_depth(depth, layers):
        for layer in layers:
            if depth <= layer["depth_to"]:
                return layer["lithology"]
        return layers[-1]["lithology"]

    # Стандартные глубины для термометрии
    standard_depths = [
        0,
        0.5,
        1,
        1.5,
        2,
        2.5,
        3,
        3.5,
        4,
        4.5,
        5,
        6,
        7,
        8,
        9,
        10,
        12,
        14,
    ]

    # Создаём таблицу с прогнозами
    data = []
    for depth in standard_depths:
        if depth <= layers[-1]["depth_to"]:
            lith_at_depth = get_lithology_at_depth(depth, layers)
            predicted_temp = st.session_state.model.predict_temperature(
                depth, lith_at_depth, surface_temp, season, use_ml
            )

            ground_type_map = {
                "песок": "песок средней крупности",
                "супесь": "супесь",
                "суглинок": "суглинок",
                "торф": "суглинок",
            }

            ground_type = ground_type_map.get(lith_at_depth, "суглинок")
            ground_state = st.session_state.model.get_ground_state(
                predicted_temp, ground_type
            )

            data.append(
                {
                    "Глубина (м)": depth,
                    "Грунт": lith_at_depth,
                    "Температура (°C)": predicted_temp,
                    "Состояние": ground_state,
                }
            )

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

    # Секция для ввода реальных замеров и обучения
    st.header("📝 Ввод реальных замеров для обучения")

    col1, col2, col3 = st.columns(3)
    with col1:
        train_depth = st.number_input("Глубина замера (м)", 0.0, 20.0, 2.0, 0.5)
    with col2:
        train_lithology = st.selectbox(
            "Грунт на глубине", ["торф", "суглинок", "супесь", "песок"]
        )
    with col3:
        actual_temp = st.number_input(
            "Реальная температура (°C)", -30.0, 20.0, 0.0, 0.1
        )

    if st.button("Добавить замер для обучения"):
        st.session_state.model.add_training_data(
            train_depth, train_lithology, surface_temp, season, actual_temp
        )
        st.success(
            f"Замер на глубине {train_depth}м добавлен. Всего замеров: {len(st.session_state.model.training_data)}"
        )

    # Информация о ML модели
    st.header("Информация о модели")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Замеров для обучения", len(st.session_state.model.training_data))
    with col2:
        st.metric(
            "ML модель обучена", "Да" if st.session_state.model.is_ml_trained else "Нет"
        )

else:
    st.info("👆 Загрузите файл бурового журнала чтобы начать работу")

# Инструкция
with st.expander("Инструкция по использованию"):
    st.markdown(
        """
    1. **Загрузите Excel файл** бурового журнала в боковой панели
    2. **Выберите скважину** для анализа
    3. **Установите климатические параметры** (температура поверхности, время года)
    4. **Просмотрите температурный профиль** в основной таблице
    5. **Добавляйте реальные замеры** для улучшения модели
    6. **Обучайте ML модель** когда накопится достаточно данных
    """
    )
