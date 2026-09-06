import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import {
  getApplications,
  createApplication,
  updateApplication,
  deleteApplication,
  computeMatchScore,
  classifyRole,
  uploadResume,
  updateExperience,
  getSkillGap,
  getAnalytics,
} from "../api/applications";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from "recharts";

const STATUS_OPTIONS = ["applied", "oa", "interview", "offer", "rejected", "withdrawn"];

export default function Dashboard() {
  const { logout } = useAuth();
  const [applications, setApplications] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [uploadStatus, setUploadStatus] = useState("");
  const [skillGapData, setSkillGapData] = useState({});
  const [expandedJD, setExpandedJD] = useState(null);

  const [experienceYears, setExperienceYears] = useState(0);
  const [expSaved, setExpSaved] = useState(false);

  const [form, setForm] = useState({
    company_name: "",
    role_title: "",
    job_description: "",
    status: "applied",
    applied_date: "",
    source: "",
  });

  const loadApplications = async () => {
    try {
      const res = await getApplications();
      setApplications(res.data);
    } catch (err) {
      setError("Failed to load applications");
    } finally {
      setLoading(false);
    }
  };

  const loadAnalytics = async () => {
    try {
      const res = await getAnalytics();
      setAnalytics(res.data);
    } catch (err) {
      console.error("Failed to load analytics", err);
    }
  };

  useEffect(() => {
    loadApplications();
    loadAnalytics();
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const payload = {
        ...form,
        applied_date: new Date(form.applied_date).toISOString(),
      };
      await createApplication(payload);
      setForm({
        company_name: "",
        role_title: "",
        job_description: "",
        status: "applied",
        applied_date: "",
        source: "",
      });
      loadApplications();
      loadAnalytics();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create application");
    }
  };

  const handleStatusChange = async (id, newStatus) => {
    try {
      await updateApplication(id, { status: newStatus });
      loadApplications();
      loadAnalytics();
    } catch (err) {
      setError("Failed to update status");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this application?")) return;
    try {
      await deleteApplication(id);
      loadApplications();
      loadAnalytics();
    } catch (err) {
      setError("Failed to delete application");
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploadStatus("Uploading...");
    try {
      const res = await uploadResume(file);
      setUploadStatus("Uploaded! Preview: " + res.data.extracted_preview.slice(0, 100) + "...");
    } catch (err) {
      setUploadStatus(err.response?.data?.detail || "Upload failed");
    }
  };

  const handleSaveExperience = async () => {
    try {
      await updateExperience(Number(experienceYears));
      setExpSaved(true);
      setTimeout(() => setExpSaved(false), 2000);
    } catch (err) {
      setError("Failed to save experience");
    }
  };

  const handleMatchScore = async (id) => {
    try {
      await computeMatchScore(id);
      loadApplications();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to compute match score");
    }
  };

  const handleClassifyRole = async (id) => {
    try {
      await classifyRole(id);
      loadApplications();
    } catch (err) {
      setError("Failed to classify role");
    }
  };

  const handleSkillGap = async (id) => {
    try {
      const res = await getSkillGap(id);
      setSkillGapData((prev) => ({ ...prev, [id]: res.data }));
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to compute skill gap");
    }
  };

  return (
  <div className="dashboard-container">
    <div className="dashboard-header">
      <h2>My Applications</h2>
      <button onClick={logout}>Logout</button>
    </div>

    <div className="card-section">
      <h3>Your Resume (used for match scoring)</h3>
      <div className="input-group">
        <label>Upload Resume (PDF or DOCX)</label>
        <input type="file" accept=".pdf,.docx" onChange={handleFileUpload} />
        {uploadStatus && (
          <p style={{ fontSize: 13, color: "#6b7280", marginTop: 8 }}>{uploadStatus}</p>
        )}
      </div>
    </div>

    <div className="card-section">
      <h3>Your Experience</h3>
      <input
        type="number"
        min="0"
        value={experienceYears}
        onChange={(e) => setExperienceYears(e.target.value)}
        style={{ width: 80 }}
      />
      <span style={{ marginLeft: 8 }}>years</span>
      <button onClick={handleSaveExperience} style={{ marginLeft: 12 }}>Save</button>
      {expSaved && <span style={{ marginLeft: 8, color: "green" }}>Saved!</span>}
    </div>

    <form onSubmit={handleSubmit} className="card-section">
      <h3>Add New Application</h3>
      <div>
        <input
          name="company_name"
          placeholder="Company"
          value={form.company_name}
          onChange={handleChange}
          required
        />
        <input
          name="role_title"
          placeholder="Role"
          value={form.role_title}
          onChange={handleChange}
          required
        />
      </div>
      <div>
        <textarea
          name="job_description"
          placeholder="Job Description (optional)"
          value={form.job_description}
          onChange={handleChange}
          rows={3}
          style={{ width: "100%", marginTop: 8 }}
        />
      </div>
      <div style={{ marginTop: 8 }}>
        <select name="status" value={form.status} onChange={handleChange}>
          {STATUS_OPTIONS.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <input
          type="date"
          name="applied_date"
          value={form.applied_date}
          onChange={handleChange}
          required
        />
        <input
          name="source"
          placeholder="Source (e.g. LinkedIn)"
          value={form.source}
          onChange={handleChange}
        />
      </div>
      {error && <p className="auth-error" style={{ marginTop: 12 }}>{error}</p>}
      <button type="submit" style={{ marginTop: 8 }}>Add Application</button>
    </form>

    {loading ? (
      <p>Loading...</p>
    ) : applications.length === 0 ? (
      <p>No applications yet. Add one above!</p>
    ) : (
      <div className="app-table-wrapper">
        <table className="app-table">
          <thead>
            <tr>
              <th>Company / Role</th>
              <th>Status</th>
              <th>Applied</th>
              <th>Source</th>
              <th>Match Score</th>
              <th>Predicted Role</th>
              <th>Skill Gap</th>
              <th>JD</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {applications.map((app) => (
              <React.Fragment key={app.id}>
                <tr>
                  <td>
                    <div className="company-name">{app.company_name}</div>
                    <div className="role-title">{app.role_title}</div>
                  </td>
                  <td>
                    <select
                      className={`status-select status-${app.status}`}
                      value={app.status}
                      onChange={(e) => handleStatusChange(app.id, e.target.value)}
                    >
                      {STATUS_OPTIONS.map((s) => (
                        <option key={s} value={s}>{s}</option>
                      ))}
                    </select>
                  </td>
                  <td>{app.applied_date?.split("T")[0]}</td>
                  <td>{app.source || "—"}</td>
                  <td>
                    {app.match_score !== null && (
                      <span className="match-score-value">
                        {(app.match_score * 100).toFixed(1)}%
                      </span>
                    )}
                    <button
                      className="btn-small btn-compute"
                      onClick={() => handleMatchScore(app.id)}
                    >
                      {app.match_score !== null ? "Recompute" : "Compute"}
                    </button>
                  </td>
                  <td>
                    {app.predicted_role_type || (
                      <button className="btn-small btn-compute" onClick={() => handleClassifyRole(app.id)}>
                        Classify
                      </button>
                    )}
                  </td>
                  <td className="skill-gap-cell">
                    {skillGapData[app.id] ? (
                      <>
                        {skillGapData[app.id].missing_skills.length > 0 ? (
                          <div className="skill-missing">
                            Missing: {skillGapData[app.id].missing_skills.join(", ")}
                          </div>
                        ) : (
                          <div className="skill-ok">No skill gaps!</div>
                        )}
                        {skillGapData[app.id].required_years_experience > 0 && (
                          <div className={skillGapData[app.id].experience_gap ? "exp-gap" : "exp-ok"}>
                            Needs {skillGapData[app.id].required_years_experience}+ yrs
                            {skillGapData[app.id].experience_gap
                              ? ` (have ${skillGapData[app.id].user_years_experience})`
                              : " ✓"}
                          </div>
                        )}
                      </>
                    ) : (
                      <button className="btn-small btn-compute" onClick={() => handleSkillGap(app.id)}>
                        Check Gaps
                      </button>
                    )}
                  </td>
                  <td>
                    <button
                      className="btn-small btn-view"
                      onClick={() => setExpandedJD(expandedJD === app.id ? null : app.id)}
                    >
                      {expandedJD === app.id ? "Hide" : "View"}
                    </button>
                  </td>
                  <td>
                    <button className="btn-small btn-delete" onClick={() => handleDelete(app.id)}>
                      Delete
                    </button>
                  </td>
                </tr>
                {expandedJD === app.id && (
                  <tr>
                    <td colSpan={9} className="jd-expanded-row">
                      <strong>Job Description:</strong> {app.job_description || "(none provided)"}
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    )}

    {analytics && (
      <div style={{ display: "flex", gap: 40, marginTop: 40, flexWrap: "wrap" }}>
        <div style={{ width: 350, height: 300 }}>
          <h3>By Status</h3>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={Object.entries(analytics.by_status).map(([status, count]) => ({
                  name: status,
                  value: count,
                }))}
                dataKey="value"
                nameKey="name"
                outerRadius={80}
                label
              >
                {Object.keys(analytics.by_status).map((_, index) => (
                  <Cell
                    key={index}
                    fill={["#8884d8", "#82ca9d", "#ffc658", "#ff8042", "#0088FE", "#00C49F"][index % 6]}
                  />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div style={{ width: 400, height: 300 }}>
          <h3>By Month</h3>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={analytics.by_month}>
              <XAxis dataKey="month" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    )}
  </div>
);
}