"""Five-day weather forecast for Basel, Switzerland."""

import json
import os
import ssl
import sys
import threading
import tkinter as tk
from datetime import date
from pathlib import Path
from tkinter import messagebox
from urllib.parse import urlencode
from urllib.request import urlopen


BASEL = {"latitude": 47.5596, "longitude": 7.5886}
API_URL = "https://api.open-meteo.com/v1/forecast"
DAILY_FIELDS = [
    "weather_code",
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "precipitation_probability_max",
    "wind_speed_10m_max",
]

WEATHER_CODES = {
    0: ("☀", "Klar"), 1: ("🌤", "Überwiegend klar"),
    2: ("⛅", "Teilweise bewölkt"), 3: ("☁", "Bedeckt"),
    45: ("🌫", "Nebel"), 48: ("🌫", "Reifnebel"),
    51: ("🌦", "Leichter Nieselregen"), 53: ("🌦", "Nieselregen"),
    55: ("🌧", "Starker Nieselregen"), 61: ("🌦", "Leichter Regen"),
    63: ("🌧", "Regen"), 65: ("🌧", "Starker Regen"),
    71: ("🌨", "Leichter Schneefall"), 73: ("🌨", "Schneefall"),
    75: ("❄", "Starker Schneefall"), 80: ("🌦", "Regenschauer"),
    81: ("🌧", "Regenschauer"), 82: ("⛈", "Starke Regenschauer"),
    95: ("⛈", "Gewitter"), 96: ("⛈", "Gewitter mit Hagel"),
    99: ("⛈", "Starkes Gewitter mit Hagel"),
}


def get_forecast():
    """Fetch five local forecast days from the Open-Meteo Forecast API."""
    import certifi

    params = {
        **BASEL,
        "daily": ",".join(DAILY_FIELDS),
        "timezone": "Europe/Zurich",
        "forecast_days": 5,
    }
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    with urlopen(f"{API_URL}?{urlencode(params)}", timeout=15, context=ssl_context) as response:
        payload = json.load(response)
    return payload["daily"]


class WeatherApp:
    BG = "#002b36"
    SURFACE = "#073642"
    TEXT = "#fdf6e3"
    MUTED = "#93a1a1"
    ACCENT = "#2aa198"
    BUTTON = "#eee8d5"
    BUTTON_TEXT = "#002b36"

    def __init__(self, root):
        self.root = root
        self.root.title("Basel Wetter · 5 Tage")
        self.root.geometry("910x490")
        self.root.minsize(760, 410)
        self.root.configure(bg=self.BG)

        header = tk.Frame(root, bg=self.BG)
        header.pack(fill=tk.X, padx=28, pady=(26, 12))
        tk.Label(header, text="Wetter in Basel", font=("Arial", 24, "bold"),
                 bg=self.BG, fg=self.TEXT).pack(side=tk.LEFT)
        self.refresh_button = tk.Button(
            header, text="Aktualisieren", font=("Arial", 10, "bold"),
            bg=self.BUTTON, fg=self.BUTTON_TEXT, activebackground="#fdf6e3",
            activeforeground=self.BUTTON_TEXT, border=0, padx=14, pady=8,
            command=self.load_forecast, cursor="hand2",
        )
        self.refresh_button.pack(side=tk.RIGHT)

        self.status = tk.StringVar(value="Vorhersage wird geladen …")
        tk.Label(root, textvariable=self.status, font=("Arial", 10),
                 bg=self.BG, fg=self.MUTED).pack(anchor="w", padx=30)

        self.cards = tk.Frame(root, bg=self.BG)
        self.cards.pack(fill=tk.BOTH, expand=True, padx=24, pady=(18, 25))
        self.load_forecast()

    def load_forecast(self):
        self.refresh_button.config(state=tk.DISABLED)
        self.status.set("Vorhersage wird geladen …")
        threading.Thread(target=self._fetch_forecast, daemon=True).start()

    def _fetch_forecast(self):
        try:
            forecast = get_forecast()
        except Exception as error:
            self.root.after(0, lambda: self._show_error(error))
        else:
            self.root.after(0, lambda: self._show_forecast(forecast))

    def _show_error(self, error):
        self.refresh_button.config(state=tk.NORMAL)
        self.status.set("Vorhersage konnte nicht geladen werden.")
        messagebox.showerror("Wetterdienst nicht erreichbar", str(error))

    def _show_forecast(self, daily):
        for widget in self.cards.winfo_children():
            widget.destroy()

        for index, date_value in enumerate(daily["time"]):
            self._create_card(index, daily, date_value)

        self.refresh_button.config(state=tk.NORMAL)
        self.status.set(f"Aktualisiert am {date.today().strftime('%d.%m.%Y')} · Quelle: Open-Meteo")

    def _create_card(self, index, daily, date_value):
        card = tk.Frame(self.cards, bg=self.SURFACE, padx=16, pady=17)
        card.grid(row=0, column=index, padx=5, sticky="nsew")
        self.cards.grid_columnconfigure(index, weight=1, uniform="day")

        parsed_date = date.fromisoformat(date_value)
        weekday = ("Mo", "Di", "Mi", "Do", "Fr", "Sa", "So")[parsed_date.weekday()]
        heading = "Heute" if index == 0 else weekday
        icon, description = WEATHER_CODES.get(daily["weather_code"][index], ("?", "Unbekannt"))

        tk.Label(card, text=heading, font=("Arial", 13, "bold"),
                 bg=self.SURFACE, fg=self.TEXT).pack()
        tk.Label(card, text=parsed_date.strftime("%d.%m."), font=("Arial", 10),
                 bg=self.SURFACE, fg=self.MUTED).pack(pady=(2, 12))
        tk.Label(card, text=icon, font=("Arial", 32), bg=self.SURFACE, fg=self.TEXT).pack()
        tk.Label(card, text=description, font=("Arial", 9), bg=self.SURFACE,
                 fg=self.MUTED, wraplength=125, height=2).pack(pady=(4, 8))

        maximum = daily["temperature_2m_max"][index]
        minimum = daily["temperature_2m_min"][index]
        tk.Label(card, text=f"{maximum:.0f}°  /  {minimum:.0f}°", font=("Arial", 14, "bold"),
                 bg=self.SURFACE, fg=self.TEXT).pack(pady=(2, 12))
        tk.Label(card, text=f"💧 {daily['precipitation_probability_max'][index]:.0f}% · "
                            f"{daily['precipitation_sum'][index]:.1f} mm",
                 font=("Arial", 9), bg=self.SURFACE, fg=self.MUTED).pack()
        tk.Label(card, text=f"Wind  {daily['wind_speed_10m_max'][index]:.0f} km/h",
                 font=("Arial", 9), bg=self.SURFACE, fg=self.MUTED).pack(pady=(5, 0))


if __name__ == "__main__":
    # Prefer the project's own environment when started with plain `python3 app.py`.
    # This keeps the HTTPS certificate dependency available without a global install.
    project_env = Path(__file__).parent / ".venv"
    project_python = project_env / "bin" / "python"
    if project_python.exists() and Path(sys.prefix).resolve() != project_env.resolve():
        os.execv(str(project_python), [str(project_python), *sys.argv])

    if "--check" in sys.argv:
        forecast = get_forecast()
        print(f"{len(forecast['time'])} forecast days loaded for Basel")
    else:
        window = tk.Tk()
        WeatherApp(window)
        window.mainloop()
