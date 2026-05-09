import requests

# Login
login_res = requests.post('http://localhost:8000/api/v1/auth/login', json={
    "email": "test@email.com",
    "password": "Yash@1234"
})
print("Login:", login_res.status_code, login_res.text)

if login_res.status_code == 200:
    token = login_res.json()["access_token"]
    
    # Switch workspace
    switch_res = requests.post('http://localhost:8000/api/v1/auth/switch-workspace', 
        json={"workspace_id": 1},
        headers={"Authorization": f"Bearer {token}"}
    )
    print("Switch:", switch_res.status_code, switch_res.text)
