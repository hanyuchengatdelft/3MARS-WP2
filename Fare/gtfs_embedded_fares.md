# First-hand fare data embedded in the GTFS feeds

Which feeds in `{DATA}/gtfs/feeds` ship **publisher-supplied ticket prices inside the
GTFS archive itself**, where those prices apply, and what they can be used for.

Checked 9 September 2026 against the 1,259 archives collected for the 30 August 2026
snapshot (1,240 MobilityDatabase feeds plus 19 manually acquired ones).

This complements [`README.md`](README.md), the audit of *published tariff sources* for
the 216 `agency2toc.csv` rows. That audit asks which operators publish a tariff
somewhere; this one asks which operators ship prices in the feed we already hold. The
two answers differ sharply: an operator can have an excellent public tariff PDF and no
GTFS fare table, and vice versa.

Per-feed detail is in [`gtfs_fare_inventory.csv`](gtfs_fare_inventory.csv).

## Relationship to the 3MG graph

The pipeline does not consume any of this. `3m-graph.py` writes links as
`src, trg, kind, mode, operator, time, freq` — there is no price attribute — and the
repository README states fares, transfers, shapes and real-time data are unused. The
only fare script that existed, `fares-renfe.py`, was removed upstream on 2026-09-03.

If fares later become a link attribute, `operator` is already on every public-transport
link, so a per-operator fare function keyed on `(operator, distance)` attaches without
changing the graph structure. `pt-links` also carries a `dist` column upstream, which
`3m-graph.py` drops from the exported CSV.

## Headline

**171 of 1,259 feeds (13.6%) carry at least one fare table, across 18 countries.**
Almost all of it is urban or regional. For long-distance rail there is effectively
**one** usable source in the entire collection.

| Fare model | Feeds | What it gives you |
|---|---:|---|
| Zone-to-zone OD | 58 | `origin_id` → `destination_id` prices: a real OD price matrix |
| Per-route | 41 | One price per route; no OD resolution |
| Flat | 35 | Single network-wide price |
| GTFS-Fares v2 | 9 | Products, leg rules, rider categories; richest but rare |
| Declared only | 28 | Fare files present but **empty** (header row only) |

## Coverage by country

| Country | Feeds with fares | of which OD-priced | Total OD pairs |
|---|---:|---:|---:|
| France | 50 | 2 | 336 |
| Spain | 43 | 25 | 1,030 |
| Portugal | 15 | 12 | 847,923 |
| Poland | 10 | 0 | 0 |
| Italy | 9 | 2 | 555,280 |
| Latvia | 6 | 4 | 245,929 |
| Romania | 6 | 3 | 89 |
| Lithuania | 4 | 2 | 193,872 |
| Finland | 4 | 1 | 1 |
| Belgium | 3 | 1 | 2 |
| Estonia | 3 | 2 | 92 |
| Slovakia, Czechia, Bulgaria, Sweden | 2 each | 0 | 0 |
| Austria, Hungary, Slovenia | 1 each | 0–1 | 0–319 |

France leads on feed count but not on usable pricing — its 50 feeds are overwhelmingly
per-route or flat urban tariffs. Portugal, Italy, Latvia and Lithuania hold nearly all
the OD-priced records.

## The OD-priced feeds

The only ones yielding a genuine origin–destination price matrix.

| Feed | Country | Area | Operator | Modes | OD pairs | Price range |
|---|---|---|---|---|---:|---|
| `mdb-1194` | IT | Piemonte (Torino) | Bus Company S.r.l., Gunetto Autolinee +12 | Bus | 555,277 | €0.55–9.20 |
| `mdb-2838` | PT | Guimarães | GUIMABUS | Bus | 283,190 | €1.00–9.00 |
| `mdb-2837` | PT | Barcelos | TUBA | Bus | 282,208 | — |
| `mdb-2836` | PT | Aveiro region | MobiAve | Bus | 282,208 | — |
| `mdb-2337` | LV | Latvia (national) | GALSS BUSS, Daugavpils autobusu parks +23 | Bus, Rail | 236,920 | €0.70–14.10 |
| `tld-4477` / `man-Lithuania` | LT | Lithuania (national) | 74 municipal operators | Bus, Rail | ~98,000 | €0.00–2850 ⚠️ |
| **`mdb-3385` / `man-Latvia`** | **LV** | **Latvia (national rail)** | **Vivi** *(Pasažieru Vilciens)* | **Rail** | **4,504** | **€1.00–10.90** |
| `mdb-2718` | ES | Bilbao | Autobuses La Unión | Bus | 744 | €1.45–15.00 |
| `mdb-3427` | BA | Livno–Split corridor | Li-Bus | Bus | 398 | BAM 2.50–216 |
| `mdb-862` | HU | Budapest | Weekendbus | Bus | 319 | HUF 400–550 |
| `mdb-891` | IT | Venezia lagoon | Alilaguna | Ferry | 219 | €10.00–18.00 |
| `mdb-2357` | PT | Porto | Metro do Porto | Metro | 169 | €1.40–3.65 |
| `mdb-2715` | ES | Bilbao / Basque | Euskotren | Rail, Funicular | 122 | €1.95–7.90 |
| `tld-715` | PT | Lisboa south bank | Fertagus | Rail | 111 | €1.50–4.60 |
| `mdb-2143` | RO | Brașov | RATBV | Bus | 74 | RON 0–12 |
| `mdb-3368` | EE | Estonia (intercity coach) | Alukvik, Ekspressbussiliinid +3 | Bus | 67 | €1.00–5.90 |
| `mdb-2824` | ES | Álava / Vitoria-Gasteiz | Álavabus | Bus | 52 | €1.55–12.30 |
| `mdb-3046` | MD | Ungheni–Iași cross-border | Transport Public Ungheni | Bus | 30 | MDL 4.50–151.20 |

## GTFS-Fares v2 feeds

The v2 schema is the only place concession pricing and multi-leg rules are expressed.

| Feed | Country | Area | Operator | Products | Price range |
|---|---|---|---|---:|---|
| `man-Finland` | FI | national | HSL, Nysse +265 | 12 | €3.30–10.90 |
| `tdg-83024` | FR | Bordeaux | TBM | 61 | €1.00–669.60 |
| `tdg-79220` | FR | Strasbourg | CTS | 57 | €0.00–56.00 |
| `mdb-3156` | PL | Rzeszów | Rzeszowski Transport Miejski | 48 | PLN 2.10–23.00 |
| `tdg-81026` | FR | Occitanie (liO) | 14 operators | 24 | €0.00–420.00 |
| `mdb-3189` | PL | Podkarpackie | Rozkładnik.pl | 16 | PLN 2.00–7.00 |
| `mdb-2098` | RO | București | STB, Metrorex +3 | 5 | RON 3.00–5.00 |
| `tdg-81575` | FR | Bassin de Thau | Keolis | 3 | €0.00–1.60 |
| `mdb-892` | ES | Barcelona | Soler i Sauret +9 | 1 | €7.75 |

## Rail specifically

Twenty feeds contain rail routes *and* a fare table, but most are urban or suburban:

- **`man-Latvia` / `mdb-3385` — Vivi (Pasažieru Vilciens), Latvian national rail.**
  The single genuinely intercity rail fare source in the collection: 4,504 station-pair
  prices, €1.00–10.90, on a regulated distance-based tariff. A free validation set for
  a distance/tariff-unit resolver of the kind already implemented for NS.
- `tld-715` Fertagus (Lisbon south bank) and `mdb-2715` Euskotren (Basque) — suburban
  rail, zone-priced, small.
- `mdb-2091` Warszawska Kolej Dojazdowa (PLN 4.10–9.20), `mdb-767` Prague integrated
  transport (CZK 0–200), `mdb-2092` Warsaw public transport (PLN 3–26) — urban.
- `man-Finland` — HSL and regional under the v2 schema; **no VR long-distance pricing**,
  even though the feed does contain VR's services.

### Declared but empty

Three feeds ship fare files containing **only a header row**. A naive
"has `fare_attributes.txt`" filter would wrongly count them as covered.

| Feed | Operator | Evidence |
|---|---|---|
| `mdb-1170` | **Trenitalia** | `fare_attributes.txt` = 72 bytes, `fare_rules.txt` = 55 bytes |
| `mdb-2720` | Consorcio Regional de Transportes de Madrid | 75 / 58 bytes |
| `mdb-2939` | Samtrafiken / Trafikverket (Sweden) | no prices, but 2.3 MB `areas.txt` + 975 KB `stop_areas.txt` |

The Swedish case still has value: it defines national fare **zone geography** without
tariffs, ready to join to prices obtained elsewhere.

## Absent entirely

**No fare data whatsoever** from the major intercity operators: SNCF, SBB, ÖBB, DB,
Eurostar, SNCB, PKP Intercity, ČD, MÁV, Renfe, TrainOSE, UK rail — and Trenitalia
(header only).

The absence is structural, not an oversight. GTFS's fare model assumes a deterministic
price for a zone pair. European long-distance rail is yield-managed: the price depends
on booking date, specific train and remaining availability, so there is no single number
to publish. Those operators expose fares through booking APIs instead, which is why
[`README.md`](README.md) classifies so many of them as `access_required` or `retail_only`.
The feeds that *do* carry prices are precisely those with regulated flat, zonal or
distance-based tariffs: municipal bus, metro, suburban rail, and small national networks.

## Caveats before using any of this

1. **Prices mix ticket types.** v2 `fare_products` include season passes — Bordeaux's
   €669.60 and Occitanie's €420.00 are annual products, not single fares. Filter on
   `rider_categories` or product name before treating a maximum as a trip price.
2. **Lithuania's €2,850 maximum is not credible** as a single ticket and looks like a
   unit or data-entry artefact. Treat `tld-4477` / `man-Lithuania` prices as suspect
   until validated against published tariffs.
3. **`fare_rules` zone IDs are not stop IDs.** They reference `stops.zone_id`, so a join
   through `stops.txt` is needed to reach coordinates.
4. **Six currencies, two outside the study area**: CZK, PLN, HUF, RON, plus BAM
   (Bosnia, `mdb-3427`) and MDL (Moldova, `mdb-3046`). The last two lie outside the 28
   study countries and were captured through a neighbouring country's catalogue.
5. **Duplicates exist.** `mdb-3385` and `man-Latvia` are the same Vivi feed; `tld-4477`
   and `man-Lithuania` are the same Lithuanian feed. Deduplicate before aggregating.
6. **Feed vintages differ.** MobilityDatabase feeds are pinned and hash-verified against
   the dated catalogue; the manual feeds are whatever the operator served on the
   download date.

## Reproducing

From the repository root, after the feeds have been collected:

```bash
python Fare/scan_gtfs_fares.py    # classify fare model, price stats, geolocate stops
python Fare/enrich_gtfs_modes.py  # add rail/bus route types from params.yml
```

Feeds are geolocated by taking the median stop coordinate, joining it to
`countries.parquet` for the country and to the nearest FUA centre from `fuas.parquet`
for the place name. So "Braga (17 km)" means the feed's stop centroid lies 17 km from
the Braga FUA centre, not that the operator serves Braga.
