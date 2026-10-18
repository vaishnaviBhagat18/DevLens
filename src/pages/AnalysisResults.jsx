import { Link, useLocation } from 'react-router-dom';
import ModuleGraph from '../components/ModuleGraph';

function getSavedAnalysis() {
  try { return JSON.parse(sessionStorage.getItem('devlens:lastAnalysis') || 'null'); } catch { return null; }
}

function LabelList({ values, empty = 'Not detected' }) {
  if (!values?.length) return <p className="dl-muted">{empty}</p>;
  return <div className="dl-chips">{values.map((value, index) => <span className="dl-chip" key={`${value}-${index}`}>{value}</span>)}</div>;
}

function ReportCard({ title, children, className = '' }) {
  return <section className={`dl-panel ${className}`}><h2>{title}</h2>{children}</section>;
}

function AnalysisResults() {
  const location = useLocation();
  const data = location.state?.analysis ?? getSavedAnalysis();
  if (!data) return (
    <div className="dl-shell"><header className="dl-topbar"><Link to="/dashboard" className="dl-brand">◈ DevLens</Link></header><main className="dl-page"><div className="dl-panel"><h1>No analysis report found</h1><p>Analyze a repository to generate your first report.</p><Link className="dl-button dl-inline-button" to="/upload">Analyze repository →</Link></div></main></div>
  );

  const tech = data.technology ?? {};
  const insights = data.ai_insights ?? {};
  const code = data.code_analysis ?? {};
  const parsed = code.parsed_files ?? [];
  const graph = code.module_graph ?? {};
  const deps = code.dependencies ?? [];
  const external = [...new Set(deps.flatMap((item) => item.external_dependencies ?? []))];
  const apiRoutes = parsed.flatMap((file) => (file.structure?.routes ?? [])
    .filter((route) => ['app', 'router'].includes(route.object) && typeof route.path === 'string' && route.path.startsWith('/'))
    .map((route) => ({ ...route, file: file.file })));
  const uncertainties = [...new Set((insights.uncertainties ?? []).filter(Boolean))];

  function downloadReport() {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `${(data.project_name || 'devlens').replace(/[^\w.-]+/g, '-')}-analysis.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  return <div className="dl-shell">
    <header className="dl-topbar"><Link to="/dashboard" className="dl-brand">◈ DevLens</Link><nav><Link to="/dashboard">Dashboard</Link><Link to="/upload">New analysis</Link></nav></header>
    <main className="dl-page">
      <div className="dl-report-header"><div><div className="dl-eyebrow">REPOSITORY ANALYSIS · COMPLETED</div><h1>{data.project_name}</h1><p className="dl-lead">{insights.project_summary || 'Structural analysis completed. AI summary was not provided.'}</p>{data.repository_url && <a className="dl-repo-link" href={data.repository_url} target="_blank" rel="noreferrer">View analyzed repository ↗</a>}</div><button className="dl-button dl-button-light" onClick={downloadReport}>Download JSON report ↓</button></div>

      <div className="dl-stats">
        <div className="dl-stat"><span>Repository files</span><strong>{data.statistics?.total_files ?? 0}</strong></div>
        <div className="dl-stat"><span>Directories</span><strong>{data.statistics?.total_directories ?? 0}</strong></div>
        <div className="dl-stat"><span>Parsed source files</span><strong>{parsed.length}</strong></div>
        <div className="dl-stat"><span>Module relationships</span><strong>{graph.statistics?.edges ?? 0}</strong></div>
      </div>

      <div className="dl-grid">
        <ReportCard title="Technology stack"><h3>Languages</h3><LabelList values={(tech.languages ?? []).map((i) => i.name)} /><h3>Frameworks</h3><LabelList values={(tech.frameworks ?? []).map((i) => i.name)} /><h3>Databases</h3><LabelList values={(tech.databases ?? []).map((i) => i.name)} /><h3>Package managers</h3><LabelList values={(tech.package_managers ?? []).map((i) => i.name)} /></ReportCard>
        <ReportCard title="Architecture · AI interpretation"><p className="dl-copy">{insights.architecture || 'Architecture explanation unavailable.'}</p><div className="dl-divider" /><h3>External imports</h3><LabelList values={external} empty="No external imports identified" /></ReportCard>
        <ReportCard title="Main features"><ul className="dl-list">{(insights.main_features ?? []).map((feature, index) => <li key={index}>{feature}</li>)}</ul></ReportCard>
        <ReportCard title="Project flow · AI interpretation"><ol className="dl-list dl-numbered">{(insights.project_flow ?? []).map((step, index) => <li key={index}>{step}</li>)}</ol></ReportCard>
        <ReportCard title="Key modules" className="dl-wide"><div className="dl-modules">{(insights.key_modules ?? []).map((module, index) => <div className="dl-module" key={`${module.file}-${index}`}><code>{module.file}</code><p>{module.purpose}</p></div>)}</div></ReportCard>
        <ReportCard title="Module dependency graph" className="dl-wide"><ModuleGraph graph={graph} /></ReportCard>
        <ReportCard title="Detected backend API routes" className="dl-wide"><p className="dl-muted dl-small">These are statically extracted route definitions, not automatically tested endpoints.</p>{apiRoutes.length ? <div className="dl-route-list">{apiRoutes.map((route, index) => <div key={`${route.file}:${route.method}:${route.path}:${index}`} className="dl-route"><span className="dl-method">{route.method}</span><code>{route.path}</code><span className="dl-muted">{route.file}</span></div>)}</div> : <p className="dl-muted">No Express-style routes detected.</p>}</ReportCard>
        <ReportCard title="Repository files" className="dl-wide"><div className="dl-file-list">{(data.files ?? []).map((file) => <code key={file}>{file}</code>)}</div></ReportCard>
        {uncertainties.length > 0 && <ReportCard title="Uncertainties reported by AI" className="dl-wide"><p className="dl-muted dl-small">AI-generated statements may need verification against source code.</p><ul className="dl-list">{uncertainties.map((item, index) => <li key={index}>{item}</li>)}</ul></ReportCard>}
      </div>
      <div className="dl-report-footer"><Link className="dl-button dl-inline-button" to="/upload">Analyze another repository →</Link></div>
    </main>
  </div>;
}
export default AnalysisResults;
