import requests


ENV_NAME = "my_environment"


def test_environment(client):
    response = client.delete(f"/api/environments/{ENV_NAME}")
    assert response.status_code == 404
    environment = dict(packages=["attrs"])
    response = client.post(f"/api/environments/{ENV_NAME}", json=environment)
    assert response.status_code == 201

    response = client.get("/api/environments")
    assert response.status_code == 200
    environments = response.json()
    assert ENV_NAME in environments


def test_server(client):
    response = client.post(f"/api/servers/{ENV_NAME}")
    assert response.status_code == 201

    response = client.get("/api/servers")
    assert response.status_code == 200
    servers = response.json()
    assert ENV_NAME in servers

    response = client.get(f"/api/servers/{ENV_NAME}")
    assert response.status_code == 200
    server = response.json()

    response = requests.get(server["url"])
    assert response.status_code == 200

    response = client.delete(f"/api/servers/{ENV_NAME}")
    assert response.status_code == 200

    response = client.get(f"/api/servers")
    assert response.status_code == 200
    servers = response.json()
    assert ENV_NAME not in servers

    response = client.delete(f"/api/environments/{ENV_NAME}")
    assert response.status_code == 200

    response = client.get(f"/api/environments")
    assert response.status_code == 200
    environments = response.json()
    assert ENV_NAME not in environments
