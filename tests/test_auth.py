# tests/test_auth.py

def test_register_user_positive(client):
    """
    ID: AUTH-01
    Модуль: Авторизация и Регистрация
    Роль: Анонимный пользователь
    Цель: Успешное создание учётной записи с валидными данными
    """
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "strongpassword123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "id" in data


def test_login_user_positive(client):
    """
    ID: AUTH-02
    Модуль: Авторизация и Регистрация
    Роль: Зарегистрированный пользователь
    Цель: Успешная аутентификация в системе и получение JWT-токена
    """
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "loginuser@example.com",
            "username": "loginuser",
            "password": "mypassword"
        }
    )
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "loginuser", "password": "mypassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_user_invalid_email(client):
    """
    ID: AUTH-03
    Модуль: Авторизация и Регистрация
    Роль: Анонимный пользователь
    Цель: Негативный тест — отклонение регистрации при некорректном формате Email
    """
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email-format",
            "username": "user1",
            "password": "password"
        }
    )
    assert response.status_code == 422


def test_register_user_empty_fields(client):
    """
    ID: AUTH-04
    Модуль: Авторизация и Регистрация
    Роль: Анонимный пользователь
    Цель: Негативный тест — отклонение регистрации при пустых полях формы
    """
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "",
            "username": "",
            "password": ""
        }
    )
    assert response.status_code == 422


def test_login_nonexistent_user(client):
    """
    ID: AUTH-05
    Модуль: Авторизация и Регистрация
    Роль: Неавторизованный гость
    Цель: Негативный тест — попытка входа под несуществующим username
    """
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "ghost_user", "password": "password"}
    )
    assert response.status_code == 401


def test_login_wrong_password(client):
    """
    ID: AUTH-06
    Модуль: Авторизация и Регистрация
    Роль: Зарегистрированный пользователь
    Цель: Негативный тест — попытка входа с неверным паролем
    """
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrongpass@example.com",
            "username": "wrongpass",
            "password": "correctpassword"
        }
    )
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "wrongpass", "password": "incorrectpassword"}
    )
    assert response.status_code == 401


def test_ui_login_page_available(client):
    """
    ID: AUTH-07
    Модуль: Интерфейс (UI)
    Роль: Любой пользователь
    Цель: Проверка доступности визуальной формы авторизации в браузере
    """
    response = client.get("/ui/login")
    assert response.status_code == 200