import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { analyzeRepository } from '../services/api';

function UploadRepository() {
  const navigate = useNavigate();
  const [repositoryUrl, setRepositoryUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleAnalyze(event) {
    event.preventDefault();
    const url = repositoryUrl.trim();
    // Only public GitHub HTTPS URLs are supported by the current demo.
    if (!/^https:\/\/github\.com\/[\w.-]+\/[\w.-]+(?:\.git)?\/?$/i.test(url)) {
      setError('Enter a valid public GitHub repository URL, such as https://github.com/user/repo');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const analysis = await analyzeRepository(url);
      try { sessionStorage.setItem('devlens:lastAnalysis', JSON.stringify(analysis)); } catch { /* state navigation still works */ }
      navigate('/analysis', { state: { analysis } });
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Could not analyze repository.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="dl-shell">
      <header className="dl-topbar"><Link to="/dashboard" className="dl-brand">◈ DevLens</Link><nav><Link to="/dashboard">Dashboard</Link><Link to="/">Login</Link></nav></header>
      <main className="dl-page dl-upload">
        <div className="dl-eyebrow">REPOSITORY INTELLIGENCE</div>
        <h1>Understand any unfamiliar repository.</h1>
        <p className="dl-lead">DevLens combines structural code analysis, module dependencies and local AI to explain how a software project works.</p>
        <form className="dl-panel dl-upload-panel" onSubmit={handleAnalyze}>
          <label htmlFor="dl-repository">Public GitHub repository URL</label>
          <div className="dl-url-row">
            <input id="dl-repository" type="url" value={repositoryUrl} onChange={(e) => setRepositoryUrl(e.target.value)} placeholder="https://github.com/username/repository" disabled={loading} required />
            <button className="dl-button" disabled={loading} type="submit">{loading ? 'Analyzing…' : 'Analyze repository →'}</button>
          </div>
          <p className="dl-hint">Current prototype supports public GitHub URLs. ZIP upload is planned, not yet implemented.</p>
          {error && <p className="dl-error" role="alert">{error}</p>}
        </form>
        {loading && <div className="dl-panel dl-progress" role="status" aria-live="polite"><span className="dl-spinner" /><div><strong>Repository analysis in progress</strong><p>Cloning, parsing files, constructing the dependency graph and generating an explanation with Ollama. This may take a few minutes on a laptop.</p></div></div>}
        <div className="dl-feature-row"><span>01 · Repository structure</span><span>02 · Technology detection</span><span>03 · Dependency graph</span><span>04 · Grounded AI insights</span></div>
      </main>
    </div>
  );
}
export default UploadRepository;
