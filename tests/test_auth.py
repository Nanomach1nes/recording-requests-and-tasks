def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "testuser@example.com",
            "username": "testuser",
            "password": "strongpassword123"
        }
    )
    assert response.status_code == 201  # HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["username"] == "testuser"
    assert "id" in data


def test_login_user(client):
    # Сначала регистрируем
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "loginuser@example.com",
            "username": "loginuser",
            "password": "mypassword"
        }
    )
    
    # Пытаемся войти (OAuth2PasswordRequestForm шлет данные как form data, а не json)
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "loginuser", "password": "mypassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"