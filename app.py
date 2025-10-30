import streamlit as st
import pandas as pd
from model import PermafrostModel

# Настройка страницы
st.set_page_config(
    page_title="Термометрия мерзлых грунтов", page_icon="🧊", layout="wide"
)

st.title("🧊 Прогноз температур в мерзлых грунтов")
st.write("Расширенная версия с многослойностью и температурными градациями")

# Инициализация модели
if "model" not in st.session_state:
    st.session_state.model = PermafrostModel()

# Боковая панель - теперь для слоёв грунта
with st.sidebar:
    st.header("Геологический разрез")

    st.subheader("Слой 1")
    lithology1 = st.selectbox("Грунт слоя 1", ["торф", "суглинок", "супесь", "песок"])
    depth1 = st.number_input("Мощность слоя 1 (м)", 0.0, 20.0, 1.5, 0.5)

    st.subheader("Слой 2")
    lithology2 = st.selectbox("Грунт слоя 2", ["торф", "суглинок", "супесь", "песок"])
    depth2 = st.number_input("Мощность слоя 2 (м)", 0.0, 20.0, 3.5, 0.5)

    st.subheader("Слой 3")
    lithology3 = st.selectbox("Грунт слоя 3", ["торф", "суглинок", "супесь", "песок"])
    depth3 = st.number_input("Мощность слоя 3 (м)", 0.0, 20.0, 3.0, 0.5)

    st.header("Климатические параметры")
    surface_temp = st.number_input(
        "Температура поверхности (°C)", -30.0, 20.0, -5.0, 0.5
    )
    season = st.selectbox("Время года", ["зима", "весна", "лето", "осень"])

# Создаём описание разреза
layers = [
    {"lithology": lithology1, "depth_to": depth1},
    {"lithology": lithology2, "depth_to": depth1 + depth2},
    {"lithology": lithology3, "depth_to": depth1 + depth2 + depth3},
]

# Основная область
st.header("Температурный профиль с учётом слоистости")

# Стандартные глубины для расчёта
standard_depths = [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 12, 14]


# Функция для определения грунта на заданной глубине
def get_lithology_at_depth(depth, layers):
    for layer in layers:
        if depth <= layer["depth_to"]:
            return layer["lithology"]
    return layers[-1][
        "lithology"
    ]  # возвращаем последний грунт если глубина больше всех слоёв


# Создаём таблицу с прогнозами
data = []
for depth in standard_depths:
    if depth <= layers[-1]["depth_to"]:  # только в пределах заданных слоёв
        lith_at_depth = get_lithology_at_depth(depth, layers)
        predicted_temp = st.session_state.model.predict_temperature(
            depth, lith_at_depth, surface_temp, season
        )

        # Определяем состояние грунта (для основных типов из таблицы)
        ground_type_map = {
            "песок": "песок средней крупности",
            "супесь": "супесь",
            "суглинок": "суглинок",
            "торф": "суглинок",  # приблизительно для торфа
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

# Визуализируем разрез
st.header("Визуализация геологического разреза")
st.write(f"**Слой 1:** {lithology1} (0.0 - {depth1} м)")
st.write(f"**Слой 2:** {lithology2} ({depth1} - {depth1 + depth2} м)")
st.write(f"**Слой 3:** {lithology3} ({depth1 + depth2} - {layers[-1]['depth_to']} м)")

# Дополнительная информация по температурным градациям
st.header("Справка по температурным градациям")
st.write(
    """
- **Твёрдомёрзлый**: температура ниже границы пластичности
- **Пластичномёрзлый**: температура в интервале пластичности  
- **Охлаждённый**: отрицательная температура, но выше пластичности
- **Талый**: положительная температура
"""
)
