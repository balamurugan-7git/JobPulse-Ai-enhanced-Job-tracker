import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../api/axios";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const res = await api.post("/login", { email, password });
      login(res.data.access_token);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed");
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-visual">
        <div className="blob blob1"></div>
        <div className="blob blob2"></div>
        <div className="auth-visual-content">
          <h1>Track Smarter.</h1>
          <p>Every application, every match score, every offer — one place.</p>
        </div>
      </div>
      <div className="auth-form-side">
        <div className="auth-card">
          <h2>Welcome back</h2>
          <p className="auth-subtitle">Log in to your job tracker</p>
          <form onSubmit={handleSubmit}>
            <div className="input-group">
              <label>Email</label>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <div className="input-group">
              <label>Password</label>
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </div>
            {error && <p className="auth-error">{error}</p>}
            <button type="submit" className="auth-submit">Login</button>
          </form>
          <p className="auth-switch">Don't have an account? <Link to="/register">Register</Link></p>
        </div>
      </div>
    </div>
  );
}