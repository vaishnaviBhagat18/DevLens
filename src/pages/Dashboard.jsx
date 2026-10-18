import { Link } from 'react-router-dom';

function lastProject() {
  try { return JSON.parse(sessionStorage.getItem('devlens:lastAnalysis') || 'null'); } catch { return null; }
}

function Dashboard() {
  const project = lastProject();
  return (
    <div className="dashboard">
      <nav className="navbar"><h1>DevLens</h1><div className="nav-links"><Link to="/upload">Analyze Repository</Link><Link to="/">Login</Link></div></nav>
      <main className="dashboard-content">
        <section className="hero">
          <h2>Understand unfamiliar repositories faster.</h2>
          <p>Static code intelligence and grounded AI explanations in one workspace.</p>
          <Link to="/upload"><button>Analyze Repository →</button></Link>
        </section>
        <section className="recent-projects"><h2>Recent Project (this browser session)</h2>
          {project ? (
            <div className="project-grid"><Link to="/analysis"><div className="project-card"><h3>{project.project_name}</h3><p>{project.statistics?.total_files ?? 0} files · {project.code_analysis?.module_graph?.statistics?.edges ?? 0} internal module relationships</p><span>View report →</span></div></Link></div>
          ) : <p>No repositories analyzed yet. Start with a public GitHub URL.</p>}
        </section>
      </main>
    </div>
  );
}
export default Dashboard;
