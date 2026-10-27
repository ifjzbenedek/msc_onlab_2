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
.venv\Scripts\activate
uvicorn src.api.main:app --reload
```

Indításkor a szerver betölti a keresőmodelleket, ez eltarthat egy ideig; addig a felület jelzi, hogy a szerver
nem érhető el.

Fejlesztés közben a felület külön fut, egy másik terminálban:

```
cd web
npm run dev
```

Ez a http://localhost:5000 címen érhető el. A demóhoz az `npm run build` lefordítja a felületet a `web/dist`
mappába, és utána a backend szolgálja ki a http://localhost:8000 címen.

## Mérések

A szkripteket a tároló gyökeréből kell futtatni, a sorrend számít. A korpusz és a keresőindex:

```
python scripts\prepare_eval.py
python scripts\build_corpus.py
python scripts\build_dense_index.py
```

Keresés a 150 kérdéses kiértékelő részhalmazon, és a CRAG-küszöbök hangolása a 60 dev kérdésen:

```
python scripts\evaluate_retrieval.py
python scripts\tune_crag_thresholds.py
```

Válaszadás és LLM-bíró rendszerenként (`baseline`, `crag`, `full`, `llm_crag`), a végén az összesítés. A
`warm_rerank_cache.py` előre kiszámolja a keresési pontszámokat a videokártyán, utána a válaszadás
`CUDA_VISIBLE_DEVICES=-1` mellett is gyors.

```
python scripts\warm_rerank_cache.py
python scripts\answer_questions.py --system baseline
python scripts\judge_answers.py --system baseline
python scripts\summarize_answers.py
```

A bíró kézi ellenőrzése: az `export_judge_review.py` elkészíti és megnyitja a `data/eval/judge_review.html`
lapot (50 eset, a bíró ítélete nélkül). Az ítéletek a böngészőben mentődnek, a lap Exportálás gombja a
Letöltések mappába menti a `judge_review_verdicts.json` fájlt, ezt olvassa a pontozó:

```
python scripts\export_judge_review.py
python scripts\score_judge_review.py
```
