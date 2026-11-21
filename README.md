# CDIS

Canadian Dealer Intelligence System — a local, synthetic-data personal prototype.

## Windows setup

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Open the URL shown by Streamlit, normally `http://localhost:8501`.

## Test

```powershell
python -m pytest -q
```

All application data remains in `cdis.db` beside `app.py` by default. The included dealerships are fictional synthetic demonstration records.
