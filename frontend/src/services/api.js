const API_BASE_URL = window.location.hostname === "localhost" ? "http://localhost:8000" : "";

export async function fetchAuditReport(repoUrl, signal) {
  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ repo_url: repoUrl }),
    signal
  });
  
  const resData = await response.json();
  if (!response.ok) {
    throw new Error(resData.detail || "Analysis failed");
  }
  return resData;
}
