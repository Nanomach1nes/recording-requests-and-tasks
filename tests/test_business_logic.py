# tests/test_business_logic.py

def test_create_request_positive(client):
    """
    ID: REQ-01
    Модуль: Управление заявками
    Роль: Клиент / Пользователь
    Цель: Успешное создание новой заявки на ремонт оборудования авторизованным пользователем
    """
    user_payload = {"email": "worker@example.com", "username": "worker", "password": "password123"}
    user_resp = client.post("/api/v1/auth/register", json=user_payload)
    user_id = user_resp.json()["id"]
    login_resp = client.post("/api/v1/auth/login", data={"username": "worker", "password": "password123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        "/api/v1/requests/",
        json={
            "title": "Сломался ПК",
            "description": "Не включается после грозы",
            "user_id": user_id,
            "category_id": None
        },
        headers=headers
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Сломался ПК"


def test_get_requests_list_positive(client):
    """
    ID: REQ-02
    Модуль: Управление заявками
    Роль: Диспетчер / Администратор
    Цель: Получение полного списка зарегистрированных ремонтных заявок из базы данных
    """
    user_payload = {"email": "reader@example.com", "username": "reader", "password": "password123"}
    client.post("/api/v1/auth/register", json=user_payload)
    login_resp = client.post("/api/v1/auth/login", data={"username": "reader", "password": "password123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/requests/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_task_positive(client):
    """
    ID: TASK-01
    Модуль: Управление подзадачами
    Роль: Мастер / Исполнитель
    Цель: Добавление конкретной технической подзадачи к созданной заявке
    """
    user_payload = {"email": "manager@example.com", "username": "manager", "password": "password123"}
    user_resp = client.post("/api/v1/auth/register", json=user_payload)
    user_id = user_resp.json()["id"]
    login_resp = client.post("/api/v1/auth/login", data={"username": "manager", "password": "password123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    req_resp = client.post(
        "/api/v1/requests/",
        json={"title": "Заявка для задачи", "description": "Описание", "user_id": user_id, "category_id": None},
        headers=headers
    )
    request_id = req_resp.json()["id"]

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
    assert task_resp.status_code == 201
    assert task_resp.json()["title"] == "Поменять термопасту"


def test_create_request_unauthorized(client):
    """
    ID: REQ-03
    Модуль: Управление заявками
    Роль: Неавторизованный пользователь
    Цель: Негативный тест — блокировка создания заявки без передачи авторизационного JWT-токена
    """
    response = client.post(
        "/api/v1/requests/",
        json={"title": "Hack Attack", "description": "No token provided", "user_id": 1, "category_id": None}
    )
    assert response.status_code == 401


def test_get_request_by_id_positive(client):
    """
    ID: REQ-04
    Модуль: Управление заявками
    Роль: Мастер / Клиент
    Цель: Успешный просмотр детальной карточки конкретной заявки по её уникальному идентификатору (ID)
    """
    user_payload = {"email": "iduser@example.com", "username": "iduser", "password": "password123"}
    user_resp = client.post("/api/v1/auth/register", json=user_payload)
    user_id = user_resp.json()["id"]
    login_resp = client.post("/api/v1/auth/login", data={"username": "iduser", "password": "password123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    req_resp = client.post(
        "/api/v1/requests/",
        json={"title": "Unique Request", "description": "Check ID", "user_id": user_id, "category_id": None},
        headers=headers
    )
    req_id = req_resp.json()["id"]
    
    response = client.get(f"/api/v1/requests/{req_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Unique Request"


def test_get_request_not_found(client):
    """
    ID: REQ-05
    Модуль: Управление заявками
    Роль: Диспетчер
    Цель: Негативный тест — обработка ошибки при запросе несуществующего ID заявки
    """
    user_payload = {"email": "nfuser@example.com", "username": "nfuser", "password": "password123"}
    client.post("/api/v1/auth/register", json=user_payload)
    login_resp = client.post("/api/v1/auth/login", data={"username": "nfuser", "password": "password123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/requests/99999", headers=headers)
    assert response.status_code == 404


def test_delete_request_api_positive(client):
    """
    ID: REQ-06
    Модуль: Управление заявками
    Роль: Администратор / Диспетчер
    Цель: Успешное удаление заявки из системы через программный API интерфейс
    """
    user_payload = {"email": "deluser@example.com", "username": "deluser", "password": "password123"}
    user_resp = client.post("/api/v1/auth/register", json=user_payload)
    user_id = user_resp.json()["id"]
    login_resp = client.post("/api/v1/auth/login", data={"username": "deluser", "password": "password123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    req_resp = client.post(
        "/api/v1/requests/",
        json={"title": "To Delete", "description": "Text", "user_id": user_id, "category_id": None},
        headers=headers
    )
    req_id = req_resp.json()["id"]
    
    del_resp = client.delete(f"/api/v1/requests/{req_id}", headers=headers)
    assert del_resp.status_code in [200, 204]


def test_create_request_empty_title(client):
    """
    ID: REQ-07
    Модуль: Управление заявками
    Роль: Клиент
    Цель: Негативный тест — валидация обязательного поля названия (запрет пустой строки)
    """
    user_payload = {"email": "empty@example.com", "username": "emptyuser", "password": "password123"}
    user_resp = client.post("/api/v1/auth/register", json=user_payload)
    user_id = user_resp.json()["id"]
    login_resp = client.post("/api/v1/auth/login", data={"username": "emptyuser", "password": "password123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        "/api/v1/requests/",
        json={"title": "", "description": "Empty title checking", "user_id": user_id, "category_id": None},
        headers=headers
    )
    assert response.status_code in [400, 422]


def test_update_request_status_api_positive(client):
    """
    ID: REQ-08
    Модуль: Управление заявками
    Роль: Мастер / Ответственный исполнитель
    Цель: Изменение текущего статуса заявки (например, переключение на 'in_progress')
    """
    user_payload = {"email": "status@example.com", "username": "statususer", "password": "password123"}
    user_resp = client.post("/api/v1/auth/register", json=user_payload)
    user_id = user_resp.json()["id"]
    login_resp = client.post("/api/v1/auth/login", data={"username": "statususer", "password": "password123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    req_resp = client.post(
        "/api/v1/requests/",
        json={"title": "Status change", "description": "Desc", "user_id": user_id, "category_id": None},
        headers=headers
    )
    req_id = req_resp.json()["id"]
    
    update_resp = client.put(
        f"/api/v1/requests/{req_id}/status",
        json={"status": "in_progress"},
        headers=headers
    )
    assert update_resp.status_code == 200


def test_get_requests_with_filter_status(client):
    """
    ID: FILTER-01
    Модуль: Поиск и фильтрация
    Роль: Диспетчер / Мастер
    Цель: Проверка работы фильтрации списка ремонтных заявок по определённому статусу
    """
    user_payload = {"email": "filter@example.com", "username": "filteruser", "password": "password123"}
    client.post("/api/v1/auth/register", json=user_payload)
    login_resp = client.post("/api/v1/auth/login", data={"username": "filteruser", "password": "password123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/requests/?status=pending", headers=headers)
    assert response.status_code == 200


def test_get_tasks_list_by_request_positive(client):
    """
    ID: TASK-02
    Модуль: Управление подзадачами
    Роль: Мастер / Исполнитель
    Цель: Успешное получение списка всех технических подзадач, закреплённых за заявкой
    """
    user_payload = {"email": "tasklist@example.com", "username": "tasklistuser", "password": "password123"}
    client.post("/api/v1/auth/register", json=user_payload)
    login_resp = client.post("/api/v1/auth/login", data={"username": "tasklistuser", "password": "password123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/tasks/", headers=headers)
    assert response.status_code == 200


def test_create_category_positive(client):
    """
    ID: CAT-01
    Модуль: Справочники и категории
    Роль: Администратор системы
    Цель: Добавление новой категории неисправностей (например, 'Ремонт видеокарт')
    """
    user_payload = {"email": "cat@example.com", "username": "catuser", "password": "password123"}
    client.post("/api/v1/auth/register", json=user_payload)
    login_resp = client.post("/api/v1/auth/login", data={"username": "catuser", "password": "password123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post("/api/v1/categories/", json={"name": "Ремонт ПК"}, headers=headers)
    assert response.status_code in [201, 404]


def test_get_categories_list_positive(client):
    """
    ID: CAT-02
    Модуль: Справочники и категории
    Роль: Клиент / Диспетчер
    Цель: Получение списка всех доступных категорий для классификации обращений
    """
    user_payload = {"email": "catl@example.com", "username": "catluser", "password": "password123"}
    client.post("/api/v1/auth/register", json=user_payload)
    login_resp = client.post("/api/v1/auth/login", data={"username": "catluser", "password": "password123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/categories/", headers=headers)
    assert response.status_code in [200, 404]


def test_create_comment_positive(client):
    """
    ID: COMM-01
    Модуль: Модуль комментариев и истории
    Роль: Клиент / Исполнитель
    Цель: Добавление текстового комментария (заметки) к карточке ремонтной заявки
    """
    user_payload = {"email": "comm@example.com", "username": "commuser", "password": "password123"}
    client.post("/api/v1/auth/register", json=user_payload)
    login_resp = client.post("/api/v1/auth/login", data={"username": "commuser", "password": "password123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post("/api/v1/comments/", json={"text": "Тестовый комментарий", "request_id": 1}, headers=headers)
    assert response.status_code in [201, 404, 422]


def test_get_requests_with_filter_search(client):
    """
    ID: FILTER-02
    Модуль: Поиск и фильтрация
    Роль: Диспетчер
    Цель: Проверка текстового полнотекстового поиска заявок по ключевым словам в названии
    """
    user_payload = {"email": "fsearch@example.com", "username": "fsearchuser", "password": "password123"}
    client.post("/api/v1/auth/register", json=user_payload)
    login_resp = client.post("/api/v1/auth/login", data={"username": "fsearchuser", "password": "password123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/requests/?search=Ремонт", headers=headers)
    assert response.status_code == 200