import axios from "axios";

const BACKEND_URL = (process.env.REACT_APP_BACKEND_URL || "").replace(/\/$/, ""); // empty = same origin
export const API = `${BACKEND_URL}/api`;

export const api = axios.create({ baseURL: API, timeout: 20000 });

export const fetchMarkets = async () => (await api.get("/markets")).data;
export const fetchNews = async (params = {}) => (await api.get("/news", { params })).data;
export const fetchNewsDetail = async (id) => (await api.get(`/news/${id}`)).data;
export const fetchHistoryToday = async () => (await api.get("/history/today")).data;
export const fetchRadar = async () => (await api.get("/radar")).data;
export const fetchBigTech = async () => (await api.get("/bigtech")).data;
export const fetchScenarios = async () => (await api.get("/scenarios")).data;
export const fetchMacro = async () => (await api.get("/macro")).data;
export const fetchChart = async (id, range_days = 30) => (await api.get(`/chart/${id}`, { params: { range_days } })).data;
export const fetchHistoryCuriosities = async () => (await api.get("/history/curiosities")).data;
export const fetchBigTechDetail = async (ticker) => (await api.get(`/bigtech/${ticker}`)).data;
export const fetchForecasts = async (deviceId) => (await api.get("/forecasts", { params: { device_id: deviceId } })).data;
export const createForecast = async (body) => (await api.post("/forecasts", body)).data;
export const deleteForecast = async (ticker, deviceId) => (await api.delete(`/forecasts/${ticker}`, { params: { device_id: deviceId } })).data;
export const fetchLearnWord = async () => (await api.get("/learn/word-of-day")).data;
export const fetchLearnTerms = async () => (await api.get("/learn/terms")).data;
export const fetchLearnQuiz = async () => (await api.get("/learn/quiz")).data;
export const postLearnProgress = async (body) => (await api.post("/learn/progress", body)).data;
export const fetchLearnProgressGet = async (deviceId) => (await api.get("/learn/progress", { params: { device_id: deviceId } })).data;
export const fetchNewsTags = async () => (await api.get("/news/tags")).data;

export const streamCopilot = async ({ sessionId, message, newsContext, onDelta, onDone, onError }) => {
  try {
    const res = await fetch(`${API}/copilot/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message, news_context: newsContext || null }),
    });
    if (!res.ok || !res.body) {
      let detail = `HTTP ${res.status}`;
      try { detail = (await res.json())?.detail || detail; } catch {}
      throw new Error(detail);
    }
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split("\n\n");
      buffer = parts.pop();
      for (const p of parts) {
        const line = p.trim();
        if (!line.startsWith("data:")) continue;
        try {
          const payload = JSON.parse(line.slice(5).trim());
          if (payload.delta) onDelta?.(payload.delta);
          if (payload.error) onError?.(payload.error);
          if (payload.done) onDone?.();
        } catch {}
      }
    }
    onDone?.();
  } catch (e) {
    onError?.(e?.message || "network");
  }
};
export const fetchCopilotHistory = async (sessionId) =>
  (await api.get(`/copilot/history/${encodeURIComponent(sessionId)}`)).data;
