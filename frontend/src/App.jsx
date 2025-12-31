import { useEffect, useState } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL;


export default function App() {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [isSignup, setIsSignup] = useState(false);

  return (
    <div className="app">
      {token ? (
        <Dashboard token={token} setToken={setToken} />
      ) : (
        <Auth
          isSignup={isSignup}
          setIsSignup={setIsSignup}
          setToken={setToken}
        />
      )}
    </div>
  );
}



function Auth({ isSignup, setIsSignup, setToken }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const submit = async () => {
    const endpoint = isSignup ? "/signup" : "/login";
    const body = isSignup
      ? { name, email, password }
      : { email, password };

    try {
      const res = await fetch(`${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      const data = await res.json();

      if (!res.ok) {
        alert(data.detail || "Error");
        return;
      }

      if (isSignup) {
        alert("Signup successful. Please login.");
        setIsSignup(false);
      } else {
        localStorage.setItem("token", data.access_token);
        setToken(data.access_token);
      }
    } catch {
      alert("Backend not reachable");
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="card auth-card">
        <h2>{isSignup ? "Signup" : "Login"}</h2>

        {isSignup && (
          <input
            placeholder="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        )}

        <input
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button onClick={submit}>
          {isSignup ? "Signup" : "Login"}
        </button>

        <button
          className="secondary-btn"
          onClick={() => setIsSignup(!isSignup)}
        >
          {isSignup ? "Login" : "Signup"}
        </button>
      </div>
    </div>
  );
}



function Dashboard({ token, setToken }) {
  const [students, setStudents] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [isEdit, setIsEdit] = useState(false);
  const [searchId, setSearchId] = useState("");

  const [form, setForm] = useState({
    student_id: "",
    name: "",
    age: "",
    email: "",
    department: "",
    gender: "",
  });

  const headers = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
  };


  const loadStudents = async () => {
    try {
      const res = await fetch(`${API_URL}/students`, { headers });

      if (res.status === 403) {
        logout();
        return;
      }

      const data = await res.json();
      setStudents(data);
    } catch {
      alert("Cannot load students");
    }
  };

  useEffect(() => {
    if (token) loadStudents();
  }, [token]);

  
  const searchStudentById = async () => {
    if (!searchId.trim()) return alert("Enter Student ID");

    const res = await fetch(
      `${API_URL}/students/${searchId}`,
      { headers }
    );

    if (!res.ok) return alert("Student not found");

    const data = await res.json();
    setStudents([data]);
  };

  
  const addStudent = async () => {
    const res = await fetch(`${API_URL}/students`, {
      method: "POST",
      headers,
      body: JSON.stringify({ ...form, age: Number(form.age) }),
    });

    if (!res.ok) {
      const data = await res.json();
      return alert(data.detail || "Add failed");
    }

    setShowForm(false);
    loadStudents();
  };

 
  const updateStudent = async () => {
    const res = await fetch(
      `${API_URL}/students/${form.student_id}`,
      {
        method: "PUT",
        headers,
        body: JSON.stringify({ ...form, age: Number(form.age) }),
      }
    );

    if (!res.ok) {
      const data = await res.json();
      return alert(data.detail || "Update failed");
    }

    setShowForm(false);
    setIsEdit(false);
    loadStudents();
  };

 
  const deleteStudent = async (id) => {
    if (!window.confirm("Delete student?")) return;

    await fetch(`${API_URL}/students/${id}`, {
      method: "DELETE",
      headers,
    });

    loadStudents();
  };

  return (
    <div className="dashboard">
      <div className="header">
        <h2>Student Dashboard</h2>
        <button onClick={logout}>Logout</button>
      </div>

      <button
        onClick={() => {
          setShowForm(true);
          setIsEdit(false);
          setForm({
            student_id: "",
            name: "",
            age: "",
            email: "",
            department: "",
            gender: "",
          });
        }}
      >
        ➕ Add Student
      </button>

      <input
        placeholder="Search Student ID"
        value={searchId}
        onChange={(e) => setSearchId(e.target.value)}
      />
      <button onClick={searchStudentById}>Search</button>

      {showForm && (
        <div className="card">
          {Object.keys(form).map((k) => (
            <input
              key={k}
              placeholder={k}
              value={form[k]}
              disabled={isEdit && k === "student_id"}
              onChange={(e) =>
                setForm({ ...form, [k]: e.target.value })
              }
            />
          ))}

          <button onClick={isEdit ? updateStudent : addStudent}>
            {isEdit ? "Update" : "Save"}
          </button>
          <button onClick={() => setShowForm(false)}>Cancel</button>
        </div>
      )}

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Age</th>
            <th>Email</th>
            <th>Dept</th>
            <th>Gender</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {students.map((s) => (
            <tr key={s.student_id}>
              <td>{s.student_id}</td>
              <td>{s.name}</td>
              <td>{s.age}</td>
              <td>{s.email}</td>
              <td>{s.department}</td>
              <td>{s.gender}</td>
              <td>
                <button
                  onClick={() => {
                    setForm(s);
                    setIsEdit(true);
                    setShowForm(true);
                  }}
                >
                  Edit
                </button>
                <button onClick={() => deleteStudent(s.student_id)}>
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
