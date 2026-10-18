import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { analyzeRepository, analyzeZipFile } from '../services/api';
import '../zip-upload.css';

const MAX_ZIP_BYTES = 25 * 1024 * 1024;

function UploadRepository() {
  const navigate = useNavigate();
  const [inputMode, setInputMode] = useState('github');
  const [repositoryUrl, setRepositoryUrl] = useState('');
  const [zipFile, setZipFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleAnalyze(event) {
    event.preventDefault();
    const url = repositoryUrl.trim();

    if (inputMode === 'github') {
      if (!/^https:\/\/github\.com\/[\w.-]+\/[\w.-]+(?:\.git)?\/?$/i.test(url)) {
        setError('Enter a valid public GitHub URL, such as https://github.com/user/repo');
        return;
      }
    } else if (!zipFile || !zipFile.name.toLowerCase().endsWith('.zip')) {
      setError('Select a .zip file containing your project.');
      return;
    } else if (!zipFile.size || zipFile.size > MAX_ZIP_BYTES) {
      setError('Select a non-empty ZIP file no larger than 25 MB.');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const analysis = inputMode === 'github'
        ? await analyzeRepository(url)
        : await analyzeZipFile(zipFile);
      try {
        sessionStorage.setItem('devlens:lastAnalysis', JSON.stringify(analysis));
      } catch { /* Navigation state still works if browser storage is unavailable. */ }
      navigate('/analysis', { state: { analysis } });
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Could not analyze project.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="dl-shell">
      <header className="dl-topbar">
        <Link to="/dashboard" className="dl-brand">◈ DevLens</Link>
        <nav><Link to="/dashboard">Dashboard</Link><Link to="/">Login</Link></nav>
      </header>
      <main className="dl-page dl-upload">
        <div className="dl-eyebrow">REPOSITORY INTELLIGENCE</div>
        <h1>Understand any unfamiliar repository.</h1>
        <p className="dl-lead">DevLens combines structural code analysis, module dependencies and local AI to explain how a software project works.</p>

        <form className="dl-panel dl-upload-panel" onSubmit={handleAnalyze}>
          <div className="dl-source-tabs" role="group" aria-label="Repository source">
            <button type="button" className={`dl-source-tab ${inputMode === 'github' ? 'active' : ''}`} onClick={() => { setInputMode('github'); setError(''); }} disabled={loading}>GitHub repository</button>
            <button type="button" className={`dl-source-tab ${inputMode === 'zip' ? 'active' : ''}`} onClick={() => { setInputMode('zip'); setError(''); }} disabled={loading}>Upload local ZIP</button>
          </div>

          {inputMode === 'github' ? (
            <>
              <label htmlFor="dl-repository">Public GitHub repository URL</label>
              <div className="dl-url-row">
                <input id="dl-repository" type="url" value={repositoryUrl} onChange={(event) => setRepositoryUrl(event.target.value)} placeholder="https://github.com/username/repository" disabled={loading} required />
                <button className="dl-button" disabled={loading} type="submit">{loading ? 'Analyzing…' : 'Analyze repository →'}</button>
              </div>
              <p className="dl-hint">DevLens clones and analyzes the public repository.</p>
            </>
          ) : (
            <>
              <label htmlFor="dl-zip">ZIP file containing your project</label>
              <div className="dl-zip-row">
                <input id="dl-zip" type="file" accept=".zip,application/zip" disabled={loading} required onChange={(event) => { setZipFile(event.target.files?.[0] || null); setError(''); }} />
                <button className="dl-button" disabled={loading} type="submit">{loading ? 'Analyzing…' : 'Analyze ZIP →'}</button>
              </div>
              <p className="dl-hint">Use File Explorer to compress your project folder as ZIP. Maximum upload 25 MB, extracted size 100 MB. Avoid including secrets or unnecessary generated files.</p>
            </>
          )}
          {error && <p className="dl-error" role="alert">{error}</p>}
        </form>

        {loading && (
          <div className="dl-panel dl-progress" role="status" aria-live="polite">
            <span className="dl-spinner" />
            <div><strong>Project analysis in progress</strong><p>{inputMode === 'github' ? 'Cloning' : 'Extracting'} repository, parsing files, building the module graph and generating Ollama insights. This may take a few minutes.</p></div>
          </div>
        )}
        <div className="dl-feature-row"><span>01 · Repository structure</span><span>02 · Technology detection</span><span>03 · Dependency graph</span><span>04 · Grounded AI insights</span></div>
      </main>
    </div>
  );
}

export default UploadRepository;
