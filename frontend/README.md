# UpWatch – frontend

Panoul clientului UpWatch (React + TypeScript + Vite). Consumă API-ul Django din repo-ul părinte.

## Pornire

1. Pornește API-ul Django: `python manage.py runserver` (port 8000).
2. Instalează dependențele și pornește frontendul:

   ```bash
   npm install
   npm run dev
   ```

3. Deschide http://localhost:5173 și intră cu un client din seed (ex. `ana@upwatch.test`).

Configurarea opțională: copiază `.env.example` în `.env.local`.

## Comenzi

| Comandă             | Ce face                                |
| ------------------- | -------------------------------------- |
| `npm run dev`       | server de dezvoltare cu proxy spre API |
| `npm run build`     | build de producție în `dist/`          |
| `npm run typecheck` | verificare TypeScript                  |
| `npm run lint`      | ESLint                                 |
| `npm run format`    | Prettier                               |
