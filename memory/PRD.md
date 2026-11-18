FlashPulse — PRD
Original problem statement (dal cliente)
"Crea un'app mobile: aggregatore intelligente di notizie flash, finanza, geopolitica, macro. 5-10 min al giorno. Design Linear/Bloomberg/Artifact. Progressive disclosure (Flash → Modal). Bottom nav 4 tab + ricerca universale. Home briefing con widget indici. Mercati & Previsioni. Radar Geopolitico & Storia con 'La Storia Insegna'. AI Copilot Gemini con 'Chiedi all'IA' contestuale. Fonti certificate. Impact Score 1-10, tag, Effetto Domino. Pillola Storica quotidiana. Push notifications (rimandate)."

Scelte utente: PWA installabile, Gemini 3 Flash, multi-fonte Finnhub+NewsAPI+Alpha Vantage, dark/auto, facile per tutti con approfondimenti.

Richieste iter 2:

Collega news reali ✓
Arricchimento IA ogni 15 min ✓
Watchlist ticker/paesi ✓
Esporta briefing PDF ✓
Radar 3D rotante al posto della tendina ✓
Architecture
FastAPI + MongoDB (news_live, copilot_messages, cron_runs).
Gemini 3 Flash via emergentintegrations, chat streaming SSE e arricchimento news.
Cron platform .emergent/crons.yml → */15 * * * * → /api/cron/refresh-news (Bearer WEBHOOK_CRON_SECRET) → background task fetch (Finnhub + NewsAPI) → Gemini enrichment → Mongo.
React PWA (CRA): manifest, sw.js solo build prod (service worker registration spostata in src/index.js).
Radar: react-globe.gl + three.js, texture earth-night, pulsing rings sui hotspot ad alta severità.
Watchlist: client-side localStorage, Provider React, filtro news.
Export: jspdf client-side, briefing PDF offline.
User personas
Utente privato, 5-10 min/giorno, da curioso principiante a appassionato avanzato.
Core requirements (static)
Bottom nav 4 tab + topbar sticky con search, watchlist, export, refresh, theme.
Flash card: Impact 1-10, 3 bullet, tag, Effetto Domino.
Modal L2: Analisi, Bull/Bear, "La Storia Insegna", Chiedi IA contestuale.
Widget indici live + sparkline + sentiment.
Accadde oggi nei mercati.
Radar 3D rotante con hotspot cliccabili + consigliati.
Markets: grafici recharts, Big Tech, scenari, macro.
AI Copilot Gemini 3 Flash streaming SSE.
PWA installabile, theme dark/light/auto.
What's been implemented (2026-11-15)
Backend endpoints: /api/markets, /api/news (DB-first con fallback mock), /api/news/{id}, /api/history/today, /api/radar, /api/bigtech, /api/scenarios, /api/macro, /api/chart/{id}, /api/copilot/chat (SSE), /api/copilot/history/{id}, /api/cron/refresh-news (Bearer), /api/live-news-status.
Pipeline Gemini: fetch multi-fonte → prompt JSON → persistenza news_live idempotente per run_id.
Secrets: WEBHOOK_CRON_SECRET, FINNHUB_API_KEY, NEWSAPI_API_KEY, ALPHA_VANTAGE_API_KEY configurati.
Cron: .emergent/crons.yml attivo, cadenza 15 min.
Frontend: Radar 3D con globo interattivo, pulsing rings critici, bottom sheet dettaglio.
Watchlist Provider + sheet con ticker preset, aggiunta libera, paesi, sezione dedicata in Briefing.
Export briefing PDF (A4) con indici, Accadde oggi, notizie, bullet, tag, Effetto Domino.
SW registration spostata in src/index.js (fix crash preview).
Backlog
P1: Alpha Vantage per quotazioni live (sostituire drift sintetico in /api/markets).
P1: Pull-to-refresh gesture.
P2: Push notifications (Digest 8:00 / 18:30 / Alert Impact ≥ 8).
P2: Esporta briefing via email (Resend managed).
P2: Mappa interattiva radar con rotte commerciali.
P2: Export PDF ottimizzato con caratteri unicode (per ora jsPDF font helvetica).
Next tasks
Collegare Alpha Vantage per quotazioni indici in tempo reale.
Attivare push notifications dopo la pubblicazione.
Aggiungere email digest serale (Resend).
