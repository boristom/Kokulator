# Basel Wetter

Eine kleine Tkinter-Anwendung, die die Wettervorhersage für die nächsten fünf Tage in Basel anzeigt. Die Daten kommen live von der [Open-Meteo Forecast API](https://open-meteo.com/en/docs); dafür ist kein API-Schlüssel nötig.

## Starten

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py
```

Die Schaltfläche **Aktualisieren** ruft die API erneut ab. Für einen reinen API-Test ohne Oberfläche:

```bash
.venv/bin/python app.py --check
```

## Angezeigte Werte

- Wetterlage und Temperatur-Minimum/-Maximum
- Niederschlagswahrscheinlichkeit und -menge
- Maximale Windgeschwindigkeit
