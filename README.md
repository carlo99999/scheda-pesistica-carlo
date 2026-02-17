## Scheda pesistica - app Streamlit

Piccola app web per visualizzare la scheda contenuta in `scheda.json`.

## Avvio in locale

1. Installa le dipendenze:

```bash
pip install -e .
```

2. Avvia l'app:

```bash
streamlit run main.py
```

3. Apri il browser all'URL mostrato da Streamlit (di solito `http://localhost:8501`).

## Cosa mostra l'app

- Panoramica programma e contesto.
- Workout del giorno selezionabile in alto (nessuna sidebar).
- Regole di progressione.
- Micro-sessioni opzionali.

## Hosting facile

Opzione consigliata: **Streamlit Community Cloud**

1. Carica questo progetto su GitHub.
2. Vai su Streamlit Community Cloud e crea una nuova app.
3. Seleziona repo, branch e file principale: `main.py`.
4. Deploy.

In alternativa puoi hostarla su Render/Railway/Fly.io eseguendo:

```bash
streamlit run main.py --server.port $PORT --server.address 0.0.0.0
```
