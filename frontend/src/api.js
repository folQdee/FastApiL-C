const API_URL = "http://127.0.0.1:8000";

export async function register(username, password, age) {
  const formData = new FormData();
  formData.append("username", username);
  formData.append("password", password);
  formData.append("age", age);

  const res = await fetch(`${API_URL}/register`, {
    method: "POST",
    body: formData,
  });
  return res.json();
}

export async function login(username, password) {
  const formData = new FormData();
  formData.append("username", username);
  formData.append("password", password);

  const res = await fetch(`${API_URL}/login`, {
    method: "POST",
    body: formData,
  });
  return res.json();
}

export async function getProfile(token) {
  const res = await fetch(`${API_URL}/profile`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return res.json();
}
