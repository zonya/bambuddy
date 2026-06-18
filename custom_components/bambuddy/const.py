"""Konstante za Bambuddy integraciju."""

DOMAIN = "bambuddy"

CONF_HOST = "host"
CONF_API_KEY = "api_key"

DEFAULT_HOST = "https://bambuddy.dusic.rs"
DEFAULT_SCAN_INTERVAL = 20  # sekundi

MANUFACTURER = "Bambu Lab"

# Mapiranje stanja štampača → ljudski/ikona (Bambuddy state stringovi)
PRINTER_STATES = {
    "IDLE": "Mirovanje",
    "RUNNING": "Štampa",
    "PAUSE": "Pauzirano",
    "FINISH": "Završeno",
    "FAILED": "Greška",
    "PREPARE": "Priprema",
    "SLICING": "Slicing",
    "OFFLINE": "Offline",
}
