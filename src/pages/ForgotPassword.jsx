import { useNavigate } from "react-router-dom";

function ForgotPassword() {
  const navigate = useNavigate();

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="logo">DevLens</div>
        <h1>Reset Password</h1>
        <p className="subtitle">Enter your email to receive a reset link.</p>

        <form onSubmit={(e) => { e.preventDefault(); alert("Reset link sent!"); }}>
          <div className="input-group">
            <label>Email</label>
            <input type="email" placeholder="Enter your email" required />
          </div>

          <button type="submit" className="login-btn">Send Reset Link</button>
        </form>

        <p className="signup-text" style={{ marginTop: "1rem" }}>
          Remembered your password?{" "}
          <span 
            style={{ cursor: "pointer", color: "#61dafb" }} 
            onClick={() => navigate("/")}
          >
            Back to Login
          </span>
        </p>
      </div>
    </div>
  );
}

export default ForgotPassword;