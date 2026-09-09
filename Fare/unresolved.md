# Unresolved agency and fare-source rows

These rows require identity resolution or further source discovery before any fare can be assigned.

| Agency | Mode | Operator | marginal n_ods | Status | Reason |
|---|---|---|---:|---|---|
| Aéroport Nantes Atlantique | Bus | Nantes Atlantique Airport transport | 28 | identity_unresolved | EUR 10 local passenger shuttle fare found, but this agency's foreign country entries are inconsistent with that scope. Verify source agency_url/routes; do not apply the shuttle fare to all credited OD entries. |
| Nahreisezug | Bus | Unresolved German bus operator | 21 | identity_unresolved | Generic feed label: recover original agency ID, URL and trip/route evidence before tariff selection. |
| DB AG | Rail | DB | 9 | identity_unresolved | Generic DB label leaves long-distance versus regional service unresolved; inspect train category and route. |
| Nachtzug | Rail | Unresolved night-train agency | 6 | identity_unresolved | Nachtzug describes service type, not a verified operator. ÖBB ranges are a lead only. |
| Bravo (Arriva) | Bus | Arriva | 5 | identity_unresolved | The agency/country combination is inconsistent; resolve its GTFS feed and concession before applying a tariff. |
| CAR_HDF_59_2 | Bus | Hauts-de-France Mobilités | 3 | not_verified | Official sector tariff portal found, direct fetch failed; indexed EUR 1/EUR 2 notices conflict. Current document and sector/route join needed. |
| MEGABUSTRANS s.r.o. | Bus | MEGABUSTRANS | 2 | not_verified | No official fare source located. Official Slovak timetable register search identifies MEGABUSTRANS on international services, but model route and tariff are unresolved; inspect GTFS route and CIS/JISCD permit. |
| Deutsche Bahn AG | Rail | DB | 2 | identity_unresolved | Generic DB label leaves long-distance versus regional service unresolved; inspect train category and route. |
| Bus6 | Bus | Unresolved German bus operator | 2 | identity_unresolved | Generic feed label: recover original agency ID, URL and trip/route evidence before tariff selection. |
| Nebenbahn Gaildorf-Untergröningen | Rail | Nebenbahn Gaildorf-Untergröningen | 2 | identity_unresolved | Resolve historical-looking agency label against original GTFS agency URL and actual trips; current passenger fare not established. |
| Bus8 | Bus | Unresolved German bus operator | 2 | identity_unresolved | Generic feed label: recover original agency ID, URL and trip/route evidence before tariff selection. |
| NVBW | Rail | NVBW | 2 | identity_unresolved | Regional authority/feed label cannot identify a carrier or one tariff; recover service and stop scope. |
| BusClassic / Weiglein | Bus | Weiglein Reisen | 1 | not_verified | Operator identity has an official BusClassic site; current route tariff and monetary table not verified. |
| Gerdes Reisen | Bus | Gerdes Reisen | 1 | not_verified | No current monetary tariff verified. Recover actual contracted route before checking VEJ/VBN/local fare authority. |
| Verkehrsgemeinschaft Müritz-Oderhaff | Bus | VMO | 1 | identity_unresolved | Current legal/tariff identity behind this agency label not established; inspect feed metadata and actual route. |
| Ebrobus SLU | Bus | Ebrobus | 1 | identity_unresolved | No official tariff tied to this exact GTFS route verified. Search produced an unrelated riverboat namesake; discard it. Check source agency URL and ALSA/concession identity before acquisition. |
| València - Alacant/Elx | Bus | Unresolved Valencian coach operator | 1 | identity_unresolved | València - Alacant/Elx is a corridor label. Resolve original GTFS agency_url, route and concession; do not assume an operator from geography. |
| FUENGIROLA | Bus | Unresolved Spanish regional bus | 1 | identity_unresolved | FUENGIROLA is a place-like label. Original feed and routes are required before choosing municipal, consortium or commercial fares. |
| CAR_HDF_59_3 | Bus | Hauts-de-France Mobilités | 1 | not_verified | Official sector tariff portal found, direct fetch failed; indexed EUR 1/EUR 2 notices conflict. Current document and sector/route join needed. |
| Arriva | Bus | Arriva | 1 | identity_unresolved | The generic label spans countries and tariff authorities; resolve the exact feed/operator/service first. |
| VD-EXPRESS | Bus | VD-EXPRESS | 1 | identity_unresolved | Candidate vdexpress.net advertises Ukraine–Italy route starting prices; exact GTFS identity and Italy-only travel eligibility unverified. No assignable tariff acquired. |
| Diamant Travel | Bus | Diamant Travel | 1 | identity_unresolved | Search found multiple namesakes and intermediary international routes. No primary fare publication securely matched to this GTFS agency. |
| LOGUDORO TOURS S.R.L. | Bus | Logudoro Tours | 1 | not_verified | Airport/ENAC material identifies logudorotours.it as operator site; site timed out. Current ordinary route price table not verified; do not replace with third-party 'from' prices. |
| PKP Intercity | Bus | PKP | 1 | not_verified | Rail-replacement or separate coach role not verified; do not assign a separate fare, free fare or rail table from agency label alone. |
