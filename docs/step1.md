## 🚀 Шаг 1: Создаём структуру проекта

### Создаём папку проекта и переходим в неё:
```bash
# Создаём папку для проекта
mkdir permafrost-temp-app
cd permafrost-temp-app

# Создаём структуру папок и файлов
mkdir -p data models utils
touch app.py model.py database.py requirements.txt README.md
touch utils/__init__.py models/__init__.py
```

### Структура проекта после создания:
```
permafrost-temp-app/
├── app.py              # Основное приложение Streamlit
├── model.py            # Логика моделей прогнозирования
├── database.py         # Работа с базой данных
├── requirements.txt    # Зависимости проекта
├── README.md           # Описание проекта
├── data/               # Для хранения данных
├── models/             # Для сохранения ML моделей
└── utils/              # Вспомогательные функции
```

### Объяснение структуры:
- **app.py** - главный файл, который запускает веб-интерфейс
- **model.py** - здесь будут математические модели для прогноза температур
- **database.py** - работа с базой данных для хранения замеров
- **requirements.txt** - список библиотек, которые нужно установить
- **data/** - здесь будет SQLite база данных
- **models/** - здесь будем сохранять обученные ML модели
- **utils/** - вспомогательные скрипты

## 🚀 Шаг 2: Настраиваем виртуальное окружение

```bash
# Создаем виртуальное окружение Python
python -m venv venv

# Активируем виртуальное окружение
source venv/bin/activate

# Теперь в терминале должно появиться (venv) в начале строки
```

## 🚀 Шаг 3: Устанавливаем базовые зависимости

Сначала откроем файл `requirements.txt` и добавим:
```txt
streamlit==1.28.0
pandas==2.0.3
numpy==1.24.3
plotly==5.15.0
scikit-learn==1.3.0
```

Устанавливаем зависимости:
```bash
pip install -r requirements.txt
```

## 🚀 Шаг 4: Создаём минимальную версию приложения

### Файл `model.py` - начнём с простой физической модели:
```python
import numpy as np

class PermafrostModel:
    def __init__(self):
        # Базовые параметры грунтов (теплопроводность, глубина затухания)
        self.ground_params = {
            "торф": {"conductivity": 0.35, "damping_depth": 2.5},
            "суглинок": {"conductivity": 1.25, "damping_depth": 4.0},
            "супесь": {"conductivity": 1.5, "damping_depth": 5.0},
            "песок": {"conductivity": 2.0, "damping_depth": 6.0}
        }
    
    def predict_temperature(self, depth, lithology, surface_temp, season="лето"):
        """
        Простая физическая модель температуры на глубине
        """
        params = self.ground_params[lithology]
        
        # Сезонные поправки (упрощённо)
        season_correction = {
            "зима": -8,
            "весна": -2, 
            "лето": 0,
            "осень": -4
        }
        
        correction = season_correction.get(season, 0)
        
        # Упрощённая формула затухания температурной амплитуды с глубиной
        temp_at_depth = surface_temp + correction * np.exp(-depth / params["damping_depth"])
        
        return round(temp_at_depth, 1)
```

### Файл `app.py` - минимальный интерфейс:
```python
import streamlit as st
import pandas as pd
from model import PermafrostModel

# Настройка страницы
st.set_page_config(
    page_title="Термометрия мерзлых грунтов",
    page_icon="🧊",
    layout="wide"
)

# Заголовок приложения
st.title("🧊 Прогноз температур в мерзлых грунтах")
st.write("Приложение для прогнозирования и валидации температурных замеров")

# Инициализация модели
if 'model' not in st.session_state:
    st.session_state.model = PermafrostModel()

# Боковая панель с параметрами
with st.sidebar:
    st.header("Параметры грунта")
    
    lithology = st.selectbox(
        "Тип грунта",
        ["торф", "суглинок", "супесь", "песок"]
    )
    
    surface_temp = st.slider(
        "Температура поверхности (°C)",
        -30.0, 20.0, -5.0, 0.5
    )
    
    season = st.selectbox(
        "Время года",
        ["зима", "весна", "лето", "осень"]
    )

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
```

## 🚀 Шаг 5: Запускаем и тестируем

```bash
# Убедитесь, что виртуальное окружение активировано (видно (venv))
# Запускаем приложение:
streamlit run app.py
```

Если всё работает, в терминале вы увидите:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

Откройте браузер и перейдите по указанному адресу.

## 🚀 Шаг 6: Инициализируем Git репозиторий

```bash
# Инициализируем Git
git init

# Создаём .gitignore чтобы не отслеживать ненужные файлы
cat > .gitignore << EOF
venv/
__pycache__/
*.pyc
*.db
*.sqlite3
.DS_Store
EOF

# Добавляем файлы в Git
git add .
git commit -m "Initial commit: basic streamlit app with physical model"
```

## ✅ Что мы получили на этом шаге:

1. **Рабочую структуру проекта**
2. **Минимальное приложение** с физической моделью
3. **Веб-интерфейс** для ввода параметров
4. **Таблицу прогнозов** для стандартных глубин
5. **Простой график** температурного профиля

## 🎯 Тестовое задание:

Попробуйте изменить параметры в интерфейсе и посмотрите:
- Как меняется температурный профиль для разных грунтов?
- Как влияет сезон на распределение температур?
- Насколько реалистичны прогнозы для вашего опыта?

Когда протестируете и всё будет работать, дайте знать - перейдём к следующему шагу: добавлению базы данных и системы валидации реальных замеров!