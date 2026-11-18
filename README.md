# FlashPulse

App finanza/geopolitica semplice per tutti, con approfondimenti per i curiosi.
Frontend React (CRA + craco) · Backend FastAPI + MongoDB.

## Avvio

```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env        # compila almeno MONGO_URL, DB_NAME e una chiave AI
uvicorn server:app --reload --port 8001

# Frontend
cd frontend
cp .env.example .env        # REACT_APP_BACKEND_URL=http://localhost:8001
yarn install && yarn start
```

## Fonti dati (tutte gratuite)

| Cosa | Fonte | Chiave |
|---|---|---|
| Indici, oro, petrolio, BTC + storico grafici | Yahoo Finance (BTC: CoinGecko / Alpha Vantage di riserva) | no |
| Notizie | RSS (ANSA, BBC, CNBC, Guardian) + Finnhub + NewsAPI | opzionali |
| Ricavi, crescita, P/E Big Tech | Finnhub, riserva Alpha Vantage | opzionali |
| Tassi Fed/BCE, inflazione, Treasury, BTP, disoccupazione | FRED + BCE | no |
| Fear & Greed | CNN (se non raggiungibile: stima dichiarata come tale) | no |
| Analisi AI e Copilot | Gemini (`GEMINI_API_KEY`) oppure `EMERGENT_LLM_KEY` | una delle due |

Se una fonte non risponde l'app mostra l'ultimo dato noto o "non disponibile": non inventa più numeri.
Il feed notizie si aggiorna da solo (ogni 15 min, alla prima richiesta); il webhook `/api/cron/refresh-news` è facoltativo.

## Test backend

```bash
cd backend && python -m pytest tests -q
```
