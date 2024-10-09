import streamlit as st
import requests
import extra_streamlit_components as stx
from datetime import datetime, timedelta
from auth.jwt_handler import decode_access_token

# Основной адрес API
API_URL = "http://app:8080"

# Функция для работы с куками
@st.cache_resource(experimental_allow_widgets=True)
def get_cookie_manager():
    return stx.CookieManager()

# Инициализация cookie_manager
cookie_manager = get_cookie_manager()

def set_token(token):
    cookie_manager.set("token", token, expires_at=datetime.now() + timedelta(minutes=30))

def get_token():
    return cookie_manager.get("token")

def remove_token():
    cookie_manager.delete("token")

# Инициализация session_state
def initialize_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Главная"
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None

# Функция для выполнения запросов к API с токеном
def api_request(method, endpoint, data=None):
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    url = f"{API_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            raise ValueError("Unsupported HTTP method")
        
        response.raise_for_status()  # Вызовет исключение для статус-кодов 4xx/5xx
        return response
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            st.error("Сессия истекла. Пожалуйста, войдите снова.")
            remove_token()
            st.session_state.logged_in = False
            st.session_state.current_page = "Вход"
            st.rerun()
        else:
            st.error(f"Ошибка API: {e}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Ошибка запроса: {e}")
        return None

# Страница входа в систему
def login_page():
    st.title("Вход в систему")
    username = st.text_input("Имя пользователя", key="login_username")
    password = st.text_input("Пароль", type="password", key="login_password")
    login_button = st.button("Войти")

    if login_button:
        response = api_request("POST", "/user/login", {"username": username, "password": password})
        if response and response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_id = data.get("user_id")
            set_token(token)
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.user_id = user_id
            st.session_state.current_page = "Личный кабинет"
            st.success("Вход выполнен успешно")
            st.rerun()
        else:
            st.error("Ошибка входа")

# Страница регистрации
def register_page():
    st.title("Регистрация")
    username = st.text_input("Имя пользователя", key="register_username")
    password = st.text_input("Пароль", type="password", key="register_password")
    register_button = st.button("Зарегистрироваться")

    if register_button:
        response = api_request("POST", "/user/register", {"username": username, "password": password})
        if response and response.status_code == 200:
            st.success("Регистрация выполнена успешно")
            st.session_state.current_page = "Вход"
            st.rerun()
        else:
            st.error("Ошибка регистрации")

# Страница личного кабинета
def dashboard_page():
    st.title("Личный кабинет")
    if not st.session_state.logged_in or not st.session_state.user_id:
        st.error("Сначала войдите в систему")
        st.session_state.current_page = "Вход"
        st.rerun()
        return

    st.write(f"Добро пожаловать, {st.session_state.username}!")

    # Отображение текущего баланса
    response = api_request("GET", f"/balance/{st.session_state.user_id}")
    if response and response.status_code == 200:
        balance = response.json().get("balance")
        st.write(f"Текущий баланс: {balance} кредитов")
    else:
        st.error("Ошибка получения текущего баланса")

    # Пополнение баланса
    st.subheader("Пополнение баланса")
    amount = st.number_input("Сумма пополнения (в кредитах)", min_value=0)
    if st.button("Пополнить баланс"):
        response = api_request("POST", f"/balance/{st.session_state.user_id}/add", {"amount": amount})
        if response and response.status_code == 200:
            st.success("Баланс успешно пополнен")
            st.rerun()
        else:
            st.error("Ошибка пополнения баланса")

    # Отправка данных для предсказания
    st.subheader("Запрос предсказания зарплаты")

    # Год работы (по умолчанию текущий год)
    work_year = st.number_input("Год работы", min_value=2000, max_value=2100, value=datetime.now().year)

    # Уровень опыта
    experience_level = st.selectbox(
        "Уровень опыта",
        [
            "EN: Начальный уровень / Младший специалист (Entry-level / Junior)",
            "MI: Средний уровень / Промежуточный специалист (Mid-level / Intermediate)",
            "SE: Старший уровень / Эксперт (Senior-level / Expert)",
            "EX: Руководящий уровень / Директор (Executive-level / Director)"
        ]
    )

    # Тип трудоустройства
    employment_type = st.selectbox(
        "Тип трудоустройства",
        [
            "PT: Неполный рабочий день",
            "FT: Полный рабочий день",
            "CT: Контрактный сотрудник",
            "FL: Фрилансер"
        ]
    )

    # Категория работы
    job_category = st.selectbox(
        "Категория работы",
        [
            "Data Engineering",
            "Data Science",
            "AI Engineering",
            "Data Analysis",
            "Software Engineering",
            "Research",
            "Business Intelligence",
            "Engineering",
            "Management",
            "Data Management"
        ]
    )

    # Теги работы
    job_tags = st.text_input("Теги работы (например, python, sql, aws)")

    # Место проживания сотрудника
    employee_residence = st.text_input("Страна проживания сотрудника (код страны ISO 3166)")

    # Формат удаленной работы
    remote_ratio = st.selectbox(
        "Формат удаленной работы",
        [
            "0: Без удаленной работы (менее 20%)",
            "50: Частично удаленно/гибридный формат",
            "100: Полностью удаленно (более 80%)"
        ]
    )

    # Местоположение компании
    company_location = st.text_input("Страна расположения компании (код страны ISO 3166)")

    # Размер компании
    company_size = st.selectbox(
        "Размер компании",
        [
            "S: менее 50 сотрудников (малая)",
            "M: от 50 до 250 сотрудников (средняя)",
            "L: более 250 сотрудников (крупная)"
        ]
    )

    if st.button("Получить предсказание зарплаты"):
        # Подготовка данных для запроса
        request_data = {
            "work_year": work_year,
            "experience_level": experience_level.split(":")[0],
            "employment_type": employment_type.split(":")[0],
            "job_category": job_category,
            "job_tags": job_tags,
            "employee_residence": employee_residence,
            "remote_ratio": int(remote_ratio.split(":")[0]),
            "company_location": company_location,
            "company_size": company_size.split(":")[0]
        }

        # Отправка запроса в API через MLService
        response = api_request("POST", "/prediction/predict_salary", request_data)
        if response and response.status_code == 200:
            prediction = response.json()
            st.success(f"Предсказанная зарплата: ${prediction['predicted_salary']:.2f}")
        else:
            st.error("Ошибка получения предсказания")


    # История предсказаний
    st.subheader("История предсказаний")
    if st.button("Показать историю"):
        response = api_request("GET", f"/history/{st.session_state.user_id}")
        if response and response.status_code == 200:
            history = response.json()
            if history:
                for item in history:
                    st.write(f"Дата: {item.get('created_at', 'Нет данных')}, "
                             f"Модель: {item.get('model_id', 'Нет данных')}, "
                             f"Ввод: {item.get('input_data', 'Нет данных')}, "
                             f"Вывод: {item.get('output_data', 'Нет данных')}, "
                             f"Статус: {item.get('status', 'Нет данных')}, "
                             f"Стоимость: {item.get('cost', 'Нет данных')}")
            else:
                st.write("История предсказаний пуста")
        else:
            st.error("Ошибка получения истории")

# Главная страница
def main_page():
    st.title("Добро пожаловать в ML сервис")
    st.write("""
    Наш ML сервис предоставляет следующие возможности:
    - Регистрация и авторизация пользователей
    - Просмотр и пополнение баланса (в условных кредитах)
    - Отправка запросов к ML моделям для получения предсказаний
    - Просмотр истории загруженных данных и полученных предсказаний
    
    Начните с регистрации или входа в систему, чтобы получить доступ ко всем функциям сервиса.
    """)

# Основной поток работы приложения
def main():
    initialize_session_state()

    st.sidebar.title("Навигация")
    
    # Проверяем наличие токена и обновляем статус входа
    token = get_token()
    if token:
        try:
            decoded_token = decode_access_token(token)
            if decoded_token:
                st.session_state.logged_in = True
                st.session_state.username = decoded_token.get("sub")
                st.session_state.user_id = decoded_token.get("sub")
                st.sidebar.write(f"Привет, {st.session_state.username}!")
            else:
                raise ValueError("Invalid token")
        except Exception as e:
            st.error(f"Ошибка проверки токена: {e}")
            st.session_state.logged_in = False
            remove_token()
    else:
        st.session_state.logged_in = False

    # Настраиваем навигацию в зависимости от статуса входа
    if st.session_state.logged_in:
        pages = {
            "Главная": main_page,
            "Личный кабинет": dashboard_page,
        }
        if st.sidebar.button("Выйти", key="logout_button"):
            remove_token()
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.user_id = None
            st.session_state.current_page = "Главная"
            st.rerun()
    else:
        pages = {"Главная": main_page, "Вход": login_page, "Регистрация": register_page}

    # Обновляем навигацию в боковой панели
    page = st.sidebar.radio("Перейти к", list(pages.keys()), key="navigation")
    
    if page != st.session_state.current_page:
        st.session_state.current_page = page

    # Отображаем текущую страницу
    if st.session_state.current_page in pages:
        pages[st.session_state.current_page]()
    else:
        st.error(f"Ошибка: страница '{st.session_state.current_page}' не найдена")
        main_page()

    # Проверяем, нужно ли перезагрузить страницу
    if st.session_state.current_page != page:
        st.rerun()

if __name__ == "__main__":
    main()