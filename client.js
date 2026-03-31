// src/api/client.js

const API_BASE_URL = "http://localhost:8000/api";
// For production: "https://your-railway-app.up.railway.app/api"

// Store token
export const setToken = (token) => {
  localStorage.setItem("token", token);
};

export const getToken = () => {
  return localStorage.getItem("token");
};

export const setUserId = (userId) => {
  localStorage.setItem("user_id", userId);
};

export const getUserId = () => {
  return localStorage.getItem("user_id");
};

// ============ AUTH ============

export const signup = async (name, email, password) => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password })
    });
    const data = await response.json();
    
    if (response.ok) {
      setToken(data.token);
      setUserId(data.user.id);
    }
    return { ok: response.ok, data };
  } catch (error) {
    return { ok: false, error: error.message };
  }
};

export const login = async (email, password) => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    
    if (response.ok) {
      setToken(data.token);
      setUserId(data.user.id);
    }
    return { ok: response.ok, data };
  } catch (error) {
    return { ok: false, error: error.message };
  }
};

// ============ SCHEMES ============

export const getAllSchemes = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/schemes/`);
    const data = await response.json();
    return { ok: response.ok, data: data.schemes || [] };
  } catch (error) {
    return { ok: false, error: error.message };
  }
};

export const getSchemesByCategory = async (category) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/schemes/?category=${category}`
    );
    const data = await response.json();
    return { ok: response.ok, data: data.schemes || [] };
  } catch (error) {
    return { ok: false, error: error.message };
  }
};

export const getSchemesByState = async (state) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/schemes/?state=${state}`
    );
    const data = await response.json();
    return { ok: response.ok, data: data.schemes || [] };
  } catch (error) {
    return { ok: false, error: error.message };
  }
};

// ============ CHAT ============

export const askQuestion = async (userId, question) => {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: userId,
        question: question
      })
    });
    const data = await response.json();
    return { ok: response.ok, data };
  } catch (error) {
    return { ok: false, error: error.message };
  }
};

// ============ GUIDED CHAT (ELIGIBILITY) ============

export const checkEligibility = async (
  userId,
  age,
  gender,
  occupation,
  income,
  state
) => {
  try {
    const response = await fetch(`${API_BASE_URL}/guided-chat/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: userId,
        age: parseInt(age),
        gender: gender,
        occupation: occupation,
        income: parseFloat(income),
        state: state
      })
    });
    const data = await response.json();
    return { ok: response.ok, data };
  } catch (error) {
    return { ok: false, error: error.message };
  }
};