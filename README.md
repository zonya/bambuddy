# Bambuddy — Home Assistant integracija

Nezvanična Home Assistant integracija koja čita stanje Bambu Lab štampača sa
[**Bambuddy**](https://github.com/maziggy/bambuddy) servera (self-hosted) preko
njegovog REST API-ja.

Idealno kada je štampač u **LAN-only** modu (bez Bambu Cloud-a) i nije u istoj
mreži kao Home Assistant: Bambuddy je već konektovan na štampač i izložen preko
HTTPS-a, pa HA samo povlači JSON — bez drugog MQTT klijenta na štampaču i bez
rutiranja do same mašine.

## Šta pravi

Jedan config entry = jedan Bambuddy server. Za **svaki** štampač na serveru pravi
zaseban uređaj sa entitetima:

| Entitet | Opis |
|---|---|
| `sensor` Stanje | IDLE / Štampa / Pauzirano / Završeno / Greška … |
| `sensor` Zadatak | naziv aktivnog posla |
| `sensor` Napredak | % |
| `sensor` Preostalo | minuta |
| `sensor` Sloj / Ukupno slojeva | trenutni / ukupan broj slojeva |
| `sensor` Temperatura dizne / ploče / komore | °C |
| `sensor` WiFi signal | dBm (dijagnostika) |
| `binary_sensor` Povezan | connectivity |
| `binary_sensor` Vrata | door (X1/P1S/H2…) |

## Instalacija (HACS)

1. HACS → ⋮ → **Custom repositories** → dodaj `https://github.com/zonya/bambuddy`,
   kategorija **Integration**.
2. Instaliraj **Bambuddy**, pa restartuj Home Assistant.
3. **Settings → Devices & Services → Add Integration → Bambuddy**.

## Konfiguracija

- **URL servera** — npr. `https://bambuddy.dusic.rs` ili `http://<ip>:8000`.
- **API ključ** — napravi u Bambuddy-ju (**Settings → API Keys**) sa dozvolom
  *read status*. Ključ ide u `X-API-Key` header; integracija samo čita.

## Napomena

Lista štampača se učitava pri postavljanju. Ako dodaš novi štampač na Bambuddy
server, reload-uj integraciju da se pojavi novi uređaj.
