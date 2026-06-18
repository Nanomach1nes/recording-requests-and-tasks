def test_create_request(client):
    # 1. Регистрируем пользователя
    user_payload = {"email": "worker@example.com", "username": "worker", "password": "password123"}
    user_resp = client.post("/api/v1/auth/register", json=user_payload)
    user_id = user_resp.json()["id"]

    # 2. Логинимся, чтобы получить JWT-токен
    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": "worker", "password": "password123"}
    )
    token = login_resp.json()["access_token"]
    
    # Формируем заголовки с токеном
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Создаем заявку, передавая авторизационный заголовок
    response = client.post(
        "/api/v1/requests/",
        json={
            "title": "Сломался ПК",
            "description": "Не включается после грозы",
            "user_id": user_id,
            "category_id": None
        },
        headers=headers  # <--- Передаем токен тут
    )
    
    # Проверяем, что заявка успешно создалась
    assert response.status_code == 201
    assert response.json()["title"] == "Сломался ПК"


def test_get_requests_list(client):
    # 1. Для чтения списка тоже регистрируемся и логинимся
    user_payload = {"email": "reader@example.com", "username": "reader", "password": "password123"}
    client.post("/api/v1/auth/register", json=user_payload)
    
    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": "reader", "password": "password123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Проверяем получение списка с токеном
    response = client.get("/api/v1/requests/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_task(client):
    # 1. Регистрируем и логиним пользователя
    user_payload = {"email": "manager@example.com", "username": "manager", "password": "password123"}
    user_resp = client.post("/api/v1/auth/register", json=user_payload)
    user_id = user_resp.json()["id"]

    login_resp = client.post("/api/v1/auth/login", data={"username": "manager", "password": "password123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Создаем заявку, к которой привяжем задачу
    req_resp = client.post(
        "/api/v1/requests/",
        json={"title": "Заявка для задачи", "description": "Описание", "user_id": user_id, "category_id": None},
        headers=headers
    )
    request_id = req_resp.json()["id"]

    # 3. Создаем саму задачу по этой заявке
    task_resp = client.post(
        "/api/v1/tasks/",
        json={
            "title": "Поменять термопасту",
            "description": "Намазать тонким слоем MX-4",
            "request_id": request_id,
            "status": "pending"
        },
        headers=headers
    )

    # Проверяем, что задача успешно создалась
    assert task_resp.status_code == 201
    assert task_resp.json()["title"] == "Поменять термопасту"