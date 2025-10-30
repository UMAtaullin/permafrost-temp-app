import streamlit as st
import pandas as pd
from model import PermafrostModel

# Настройка страницы
st.set_page_config(
    page_title="Термометрия мерзлых грунтов", page_icon="🧊", layout="wide"
)

# Заголовок приложения
st.title("🧊 Прогноз температур в мерзлых грунтах")
st.write("Приложение для прогнозирования и валидации температурных замеров")

# Инициализация модели
if "model" not in st.session_state:
    st.session_state.model = PermafrostModel()

# Боковая панель с параметрами
with st.sidebar:
    st.header("Параметры грунта")

    lithology = st.selectbox("Тип грунта", ["торф", "суглинок", "супесь", "песок"])

    surface_temp = st.slider("Температура поверхности (°C)", -30.0, 20.0, -5.0, 0.5)

    season = st.selectbox("Время года", ["зима", "весна", "лето", "осень"])

# Основная область
st.header("Температурный профиль")

# Стандартные глубины как в ваших журналах
standard_depths = [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 12, 14]

# Создаём таблицу с прогнозами
data = []
for depth in standard_depths:
    predicted_temp = st.session_state.model.predict_temperature(
        depth, lithology, surface_temp, season
    )
    data.append({"Глубина (м)": depth, "Прогноз температуры (°C)": predicted_temp})

df = pd.DataFrame(data)
st.dataframe(df, use_container_width=True)

# Простая визуализация
st.line_chart(df.set_index("Глубина (м)"))
