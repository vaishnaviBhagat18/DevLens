import { useNavigate } from "react-router-dom";

function SignUp() {
  const navigate = useNavigate();

  const handleSignUp = (e) => {
    e.preventDefault();
    // Redirect to Dashboard or Login after registering
    navigate("/dashboard");
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="logo">DevLens</div>
        <h1>Create Account</h1>
        <p className="subtitle">Join DevLens to analyze your projects.</p>

        <form onSubmit={handleSignUp}>
          <div className="input-group">
            <label>Full Name</label>
            <input type="text" placeholder="Enter your full name" required />
          </div>

          <div className="input-group">
            <label>Email</label>
            <input type="email" placeholder="Enter your email" required />
          </div>

          <div className="input-group">
            <label>Password</label>
            <input type="password" placeholder="Create a password" required />
          </div>

          <button type="submit" className="login-btn">Sign Up</button>

          <p className="signup-text" style={{ marginTop: "1rem" }}>
            Already have an account?{" "}
            <span 
              style={{ cursor: "pointer", color: "#61dafb" }} 
              onClick={() => navigate("/")}
            >
              Log In
            </span>
          </p>
        </form>
      </div>
    </div>
  );
}

export default SignUp;