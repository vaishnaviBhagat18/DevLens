import { useNavigate } from "react-router-dom";

function Login() {
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    navigate("/dashboard");
  };

  return (
    <div className="login-page">
      <div className="background-glow glow-one"></div>
      <div className="background-glow glow-two"></div>

      <div className="login-card">
        <div className="logo">DevLens</div>

        <h1>Welcome Back</h1>

        <p className="subtitle">
          Analyze. Understand. Build better software.
        </p>

        <form onSubmit={handleLogin}>
          <div className="input-group">
            <label>Email</label>
            <input type="email" placeholder="Enter your email" required />
          </div>

          <div className="input-group">
            <label>Password</label>
            <input type="password" placeholder="Enter your password" required />
          </div>

          <div className="options">
            <label>
              <input type="checkbox" /> Remember me
            </label>
            <span 
              className="forgot-password" 
              style={{ cursor: "pointer" }} 
              onClick={() => navigate("/forgot-password")}
            >
              Forgot password?
            </span>
          </div>

          <button type="submit" className="login-btn">Login</button>

          <p className="signup-text">
            Don't have an account?{" "}
            <span 
              className="signup-link" 
              style={{ cursor: "pointer", color: "#61dafb" }} 
              onClick={() => navigate("/signup")}
            >
              Sign Up
            </span>
          </p>
        </form>
      </div>
    </div>
  );
}

export default Login;