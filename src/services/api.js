// The Vite development proxy forwards /analyze and /analyze/upload to FastAPI.
async function readAnalysisResponse(response) {
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
  return readAnalysisResponse(response);
}

export async function analyzeZipFile(file) {
  const body = new FormData();
  body.append('file', file);

  let response;
  try {
    response = await fetch('/analyze/upload', { method: 'POST', body });
  } catch {
    throw new Error('Cannot reach DevLens backend. Start FastAPI on port 8000 and try again.');
  }
  // Browser sets multipart boundary automatically. Do NOT set Content-Type here.
  return readAnalysisResponse(response);
}
