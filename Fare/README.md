# Public fare-source audit for `agency2toc.csv`

Checked 9 September 2026. This audit maps every one of the 216 agency/mode/operator rows in `data/gtfs/agency2toc.csv` to a public tariff source, an official access route, or an explicit unresolved status. It records 124 sources and includes 15 locally verified representative source snapshots.

The main result is that public fare data are much more common than the original `Fare` folder suggests. Several systems can support NS-style exact calculation. Others publish only price ladders, bounds or rules, and commercial operators often require live offer access because the available price depends on quota and booking time.

## Deliverables

| File | Purpose |
|---|---|
| `fare_source_register.csv` | Flat, reviewable mapping for all 216 input rows |
| `fare_source_register.json` | Complete structured mapping, sources, limitations and provenance |
| `source_inventory.csv` | One row per source with access, reuse, validity and next action |
| `unresolved.md` | The 24 rows whose source or identity remains unresolved |
| `acquisition_plan.md` | Recommended implementation and data-access sequence |
| `download_plan.json` / `download_manifest.json` | Source snapshot requests, HTTP results, sizes and SHA-256 hashes |
| `documents/` | 15 validated example tariff PDFs, workbooks and CSVs |
| `build_register.py` / `validate_audit.py` | Rebuild and validation commands |
| `agents/` | Regional research notes and structured intermediate results |
| `gtfs_embedded_fares.md` / `gtfs_fare_inventory.csv` | Which collected GTFS feeds ship prices inside the archive itself, and where they apply |
| `scan_gtfs_fares.py` / `enrich_gtfs_modes.py` | Rebuild the GTFS fare inventory |

Rebuild and validate with:

```powershell
python Fare/research/2026-09-09/build_register.py
python Fare/research/2026-09-09/validate_audit.py
```

## Coverage result

| Status | CSV rows | marginal `n_ods` |
|---|---:|---:|
| Ready to acquire | 32 | 118 |
| Published partial | 113 | 1,583 |
| Access required | 38 | 2,514 |
| Retail only | 9 | 130 |
| Identity unresolved | 17 | 86 |
| Source not verified | 7 | 10 |
| **Total** | **216** | **4,441** |

`n_ods` is an order-dependent marginal count of new OD tuples contributed by each agency in `tocs.py`. It is useful for reproducing the selection logic, but it is not passenger volume, market share or the operator's complete OD count. The CSV's `country` field is also truncated to the first five sorted country codes.

`ready_to_acquire` means that a concrete public price source and its required mapping are available or close to available. It does not mean that a tested resolver exists. `published_partial` covers sources missing an OD-distance/zone join, a product subset, or live inventory. Public visibility and permission to redistribute are separate questions; the register records reuse terms independently.

## Strongest findings

| System | Public material found | What it can answer |
|---|---|---|
| Netherlands | NDOV carrier OD tariff units plus NS, Arriva, Qbuzz and other carrier price files under the NDOV publication system | Exact domestic fares after carrier/product matching; NS is already implemented |
| Austria | ÖBB route-price tables split by origin initial, including channel and advance-purchase bands | Published domestic OD fares; inventory-dependent products still need availability |
| Germany | Deutschlandtarif price list plus tariff-distance/routing corpus; several Verkehrsverbund matrices and zone tables | Exact regional fares after service/tariff authority and route matching |
| Hungary | One 2026 interurban fare table for rail and intercity bus, with supplements | Distance-band domestic base fares after tariff-distance and train category joins |
| Croatia | HŽPP Tariff 103 monetary prices and Tariff 102 tariff-distance lead | Potential exact domestic fares; the Tariff 102 version discrepancy must be resolved first |
| Italy | Trenitalia's current 212-page IC/ICN OD price list, regional Tariffa 39 tables and Trenord's current tariff | Exact listed IC/ICN and regional base fares within the table scope; high-speed quotas remain dynamic |
| Portugal | CP Alfa Pendular and Intercidades station-pair price PDFs | Exact published base fares for the listed relations and classes |
| France | SNCF machine-readable TGV/OUIGO and Intercités OD minimum/maximum prices | Official fare bounds by OD/class/profile, not the quota available on a particular train |
| Belgium | SNCB 2026 monetary tables by tariff kilometre and product | Monetary lookup after an authoritative OD tariff-kilometre source is located |
| Great Britain rail | RDG industry fares, restrictions and routeing feeds | Network-wide fares after registration/licensing; Advance availability remains separate |
| England local bus | DfT Bus Open Data Service fares in NeTEx under OGL | Published local-bus fare products after operator/service/stop mapping |
| Eurostar | Public fare grids by route, class and fare code, already represented by six PDFs in the original folder | Full published price ladders; live quota selection remains necessary |
| Galicia | Official 2026 workbook with 97,974 tariff rows | Direct fare calculation within the published regional scheme |

## Snapshot evidence

The acquisition script downloaded and validated representative records for SNCF, Trenitalia, CP, ÖBB, Deutschlandtarif, MÁV, HŽPP, Elron, Leo Express Tenders, Arriva Drielandentrein, Qbuzz, DSB and Galicia. Validation checks file signatures, PDF readability, workbook structure or CSV columns, then records file size and SHA-256 in `download_manifest.json`.

The SNCB source returned HTTP 403 because its site presented an automated-client challenge. Its official 23-page tariff document and price rows were still verified through the public source page, and the failed retrieval is retained in the manifest rather than disguised as a missing source.

## Important modelling rule

Fare data must attach to a ticket or itinerary product. Summing a nominal price on every graph edge will overprice through tickets and mishandle transfers, reservations, subscriptions and capacity-limited products. A quote should retain at least operator, itinerary legs, product, class, passenger profile, sales channel, booking time, travel time, currency, validity, source ID, `estimated`, and an availability flag.

The existing NS QA report has a reporting inconsistency: it refers to both 17 and 19 in-scope Dutch stations, while 272 ordered OD pairs equals 17 × 16. This does not invalidate the underlying NS tariff lookup, but the scope narrative should be reconciled before publication.

The regional evidence is in `agents/dach.md`, `agents/east.md`, `agents/nordic_details.md` and `agents/southwest.md`. The structured register is authoritative when these narrative files and the CSV need to be joined.
