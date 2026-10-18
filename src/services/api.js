// The Vite development proxy forwards /analyze to FastAPI on port 8000.
export async function analyzeRepository(repositoryUrl) {
  let response;
  try {
    response = await fetch('/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ repository_url: repositoryUrl }),
    });
  } catch {
    throw new Error('Cannot reach DevLens backend. Start FastAPI on port 8000 and try again.');
  }

  const contentType = response.headers.get('content-type') || '';
  if (!contentType.includes('application/json')) {
    throw new Error('Unexpected API response. Make sure FastAPI is running on port 8000.');
  }

  const data = await response.json();
  if (!response.ok) {
    let detail = data?.detail;
    if (Array.isArray(detail)) detail = detail.map((item) => item.msg).join(', ');
    throw new Error(typeof detail === 'string' ? detail : `Analysis failed (HTTP ${response.status}).`);
  }
  if (!data?.project_name || !data?.code_analysis) {
    throw new Error('The backend returned an incomplete analysis response.');
  }
  return data;
}
