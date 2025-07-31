// js/auth.js
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("registerForm");
  const roleSelect = document.getElementById("role");
  const skillField = document.getElementById("skillField");

  roleSelect.addEventListener("change", () => {
    skillField.classList.toggle("hidden", roleSelect.value !== "employee");
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    const payload = {
      username: formData.get("username"),
      email: formData.get("email"),
      password: formData.get("password"),
      role: formData.get("role")
    };

    if (payload.role === "employee") {
      payload.skills = formData.get("skills").split(',').map(s => s.trim());
    }

    const res = await fetch("http://localhost:8000/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    alert(data.message || data.detail || "Error");
    if (res.ok) window.location.href = "login.html";
  });
});

// js/auth.js (append)
document.getElementById("loginForm")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);

  const res = await fetch("http://localhost:8000/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: formData.get("email"),
      password: formData.get("password")
    })
  });

  const data = await res.json();
  if (res.ok) {
    localStorage.setItem("token", data.access_token);
    window.location.href = "dashboard.html";
  } else {
    alert(data.detail || "Login failed");
  }
});
