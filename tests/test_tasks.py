import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def get_auth_headers(client: AsyncClient, email: str, password: str) -> dict:
    """
    Signs up and logs in a user to get auth headers.
    """
    await client.post(
        "/auth/signup",
        json={"email": email, "password": password, "username": f"{email.split('@')[0]}"},
    )
    login_response = await client.post(
        "/auth/login", json={"email": email, "password": password}
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_create_task_success(client: AsyncClient):
    """
    Test successful creation of a task.
    """
    headers = await get_auth_headers(
        client, "taskuser@example.com", "ValidPassword1!"
    )
    response = await client.post(
        "/tasks",
        json={"title": "Test Task", "description": "This is a test task"},
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert "id" in data
    assert data["is_completed"] is False


async def test_create_task_unauthenticated(client: AsyncClient):
    """
    Test that an unauthenticated user cannot create a task.
    """
    response = await client.post(
        "/tasks",
        json={"title": "Unauthorized Task"},
    )
    assert response.status_code == 403
    assert "Not authenticated" in response.text


async def test_get_all_tasks_success(client: AsyncClient):
    """
    Test retrieving all tasks for a user.
    """
    headers = await get_auth_headers(
        client, "gettasks@example.com", "ValidPassword1!"
    )
    # Create a couple of tasks
    await client.post(
        "/tasks", json={"title": "Task 1"}, headers=headers
    )
    await client.post(
        "/tasks", json={"title": "Task 2"}, headers=headers
    )

    response = await client.get("/tasks", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Task 1"
    assert data[1]["title"] == "Task 2"


async def test_get_single_task_success(client: AsyncClient):
    """
    Test retrieving a single task by its ID.
    """
    headers = await get_auth_headers(
        client, "getsingletask@example.com", "ValidPassword1!"
    )
    # Create a task first
    create_response = await client.post(
        "/tasks", json={"title": "My Single Task"}, headers=headers
    )
    task_id = create_response.json()["id"]

    # Retrieve the task by its ID
    response = await client.get(f"/tasks/{task_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "My Single Task"


async def test_update_task_success(client: AsyncClient):
    """
    Test successfully updating a task.
    """
    headers = await get_auth_headers(
        client, "updatetask@example.com", "ValidPassword1!"
    )
    # 1. Create a task
    create_response = await client.post(
        "/tasks", json={"title": "Original Title"}, headers=headers
    )
    task_id = create_response.json()["id"]

    # 2. Update the task
    update_data = {"title": "Updated Title", "is_completed": True}
    response = await client.put(
        f"/tasks/{task_id}", json=update_data, headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["is_completed"] is True
    assert data["id"] == task_id


async def test_delete_task_success(client: AsyncClient):
    """
    Test successfully deleting a task.
    """
    headers = await get_auth_headers(
        client, "deletetask@example.com", "ValidPassword1!"
    )
    # 1. Create a task
    create_response = await client.post(
        "/tasks", json={"title": "Task to be deleted"}, headers=headers
    )
    task_id = create_response.json()["id"]

    # 2. Delete the task
    delete_response = await client.delete(f"/tasks/{task_id}", headers=headers)
    assert delete_response.status_code == 204

    # 3. Verify the task is gone
    get_response = await client.get(f"/tasks/{task_id}", headers=headers)
    assert get_response.status_code == 404


async def test_get_task_not_owned_by_user(client: AsyncClient):
    """
    Test that a user cannot retrieve a task they do not own.
    """
    # 1. Create User A and their task
    headers_a = await get_auth_headers(
        client, "usera@example.com", "PasswordA1!"
    )
    create_response = await client.post(
        "/tasks", json={"title": "User A's Task"}, headers=headers_a
    )
    task_id_a = create_response.json()["id"]

    # 2. Create User B
    headers_b = await get_auth_headers(
        client, "userb@example.com", "PasswordB1!"
    )

    # 3. User B tries to get User A's task
    response = await client.get(f"/tasks/{task_id_a}", headers=headers_b)
    assert response.status_code == 404


async def test_update_task_not_owned_by_user(client: AsyncClient):
    """
    Test that a user cannot update a task they do not own.
    """
    # 1. Create User A and their task
    headers_a = await get_auth_headers(
        client, "update_usera@example.com", "PasswordA1!"
    )
    create_response = await client.post(
        "/tasks", json={"title": "User A's Updatable Task"}, headers=headers_a
    )
    task_id_a = create_response.json()["id"]

    # 2. Create User B
    headers_b = await get_auth_headers(
        client, "update_userb@example.com", "PasswordB1!"
    )

    # 3. User B tries to update User A's task
    update_data = {"title": "User B's Malicious Update"}
    response = await client.put(
        f"/tasks/{task_id_a}", json=update_data, headers=headers_b
    )
    assert response.status_code == 404


async def test_delete_task_not_owned_by_user(client: AsyncClient):
    """
    Test that a user cannot delete a task they do not own.
    """
    # 1. Create User A and their task
    headers_a = await get_auth_headers(
        client, "delete_usera@example.com", "PasswordA1!"
    )
    create_response = await client.post(
        "/tasks", json={"title": "User A's Deletable Task"}, headers=headers_a
    )
    task_id_a = create_response.json()["id"]

    # 2. Create User B
    headers_b = await get_auth_headers(
        client, "delete_userb@example.com", "PasswordB1!"
    )

    # 3. User B tries to delete User A's task
    response = await client.delete(f"/tasks/{task_id_a}", headers=headers_b)
    assert response.status_code == 404
