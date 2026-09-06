import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../api/axios";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/register", {
        email,
        password,
        full_name: fullName,
      });
      navigate("/login");
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed");
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-visual">
        <div className="blob blob1"></div>
        <div className="blob blob2"></div>
        <div className="auth-visual-content">
          <h1>Start Tracking.</h1>
          <p>Your resume, your matches, your next offer — organized.</p>
        </div>
      </div>
      <div className="auth-form-side">
        <div className="auth-card">
          <h2>Create account</h2>
          <p className="auth-subtitle">Start tracking your applications</p>
          <form onSubmit={handleSubmit}>
            <div className="input-group">
              <label>Full Name</label>
              <input value={fullName} onChange={(e) => setFullName(e.target.value)} />
            </div>
            <div className="input-group">
              <label>Email</label>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <div className="input-group">
              <label>Password</label>
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </div>
            {error && <p className="auth-error">{error}</p>}
            <button type="submit" className="auth-submit">Register</button>
          </form>
          <p className="auth-switch">Already have an account? <Link to="/login">Login</Link></p>
        </div>
      </div>
    </div>
  );
}