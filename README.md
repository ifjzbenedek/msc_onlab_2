# MSc Önlab 2

Dokumentumfeldolgozás nagy nyelvi modellekkel: ágensalapú RAG kérdés-válasz rendszer.

## Telepítés

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
cd web
npm install
```

A `.env`-ben meg kell adni a kiértékelő adathalmaz helyét és a nyelvi modell hívásának beállításait.
A kiértékelő adathalmaz nem része a tárolónak.

## Futtatás

```
uvicorn src.api.main:app --reload
```

Fejlesztés közben a felület külön fut, egy másik terminálban:

```
cd web
npm run dev
```

Ez a http://localhost:5173 címen érhető el. A demóhoz az `npm run build` lefordítja a felületet a `web/dist`
mappába, és utána a backend szolgálja ki a http://localhost:8000 címen.
