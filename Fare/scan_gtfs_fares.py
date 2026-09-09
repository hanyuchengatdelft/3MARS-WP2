"""Inventory first-hand fare data embedded in the collected GTFS feeds.

For every feed in `{DATA}/gtfs/feeds` that ships any fare table, classify the
fare model it actually expresses, summarise prices, and geolocate the service
area against country and FUA boundaries.

Writes `Fare/gtfs_fare_inventory.csv`. Run from the repository root:

    python Fare/scan_gtfs_fares.py
"""

import io
import sys
import warnings
from pathlib import Path
from zipfile import ZipFile

import geopandas as gpd
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config as C

warnings.filterwarnings("ignore")

OUT = Path(__file__).resolve().parent / "gtfs_fare_inventory.csv"
FEEDS = C.DATA / "gtfs/feeds"

V1 = ["fare_attributes", "fare_rules"]
V2 = ["fare_products", "fare_leg_rules", "fare_transfer_rules",
      "fare_media", "rider_categories", "timeframes"]
GEO = ["areas", "stop_areas", "networks", "route_networks"]
ALL = V1 + V2 + GEO

countries = gpd.read_parquet(C.DATA / "countries.parquet").to_crs(C.CRS_DEG)
fuas = gpd.read_parquet(C.DATA / "fuas.parquet")
fua_pts = gpd.GeoDataFrame(
    fuas[["name", "icc", "popu"]],
    geometry=gpd.GeoSeries(fuas["centre"], crs=C.CRS_DEG),
).to_crs(C.CRS_EU)

catalog_files = sorted(C.DATA.glob("gtfs/mdb-catalog-*.csv"))
provider = {}
if catalog_files:
    cat = pd.read_csv(catalog_files[-1])
    provider = dict(zip(cat["name"], cat["provider"]))


def read(z, table):
    """Read a GTFS table from a zip regardless of nesting depth."""
    files = [f for f in z.namelist() if Path(f).stem == table]
    if not files:
        return None
    try:
        return pd.read_csv(io.BytesIO(z.read(files[0])), low_memory=False)
    except Exception:
        return None


def classify(fr, fa, present):
    """Label the fare model the feed actually expresses."""
    has_od = (fr is not None and {"origin_id", "destination_id"} <= set(fr.columns)
              and fr["origin_id"].notna().any() and fr["destination_id"].notna().any())
    if has_od:
        return "Zone-to-zone OD"
    if [t for t in V2 if t in present]:
        return "GTFS-Fares v2"
    if fr is not None and "route_id" in fr.columns and fr["route_id"].notna().any():
        return "Per-route"
    if fa is not None and len(fa):
        return "Flat"
    return "Declared only"


def price_summary(z, fa):
    """Return (n_products, currency, min, max) from v1 or v2 fare tables."""
    if fa is not None and "price" in fa.columns:
        p = pd.to_numeric(fa["price"], errors="coerce").dropna()
        cur = ""
        if "currency_type" in fa.columns and fa["currency_type"].notna().any():
            cur = str(fa["currency_type"].dropna().mode().iloc[0])
        return (len(fa), cur,
                float(p.min()) if len(p) else np.nan,
                float(p.max()) if len(p) else np.nan)
    fp = read(z, "fare_products")
    if fp is not None:
        p = pd.to_numeric(fp.get("amount"), errors="coerce").dropna() \
            if "amount" in fp.columns else pd.Series(dtype=float)
        cur = ""
        if "currency" in fp.columns and fp["currency"].notna().any():
            cur = str(fp["currency"].dropna().mode().iloc[0])
        return (len(fp), cur,
                float(p.min()) if len(p) else np.nan,
                float(p.max()) if len(p) else np.nan)
    return (0, "", np.nan, np.nan)


def locate(stops):
    """Median stop coordinate -> (icc, 'FUA (d km)', lon, lat, n_stops)."""
    if stops is None or not {"stop_lat", "stop_lon"} <= set(stops.columns):
        return "", "", np.nan, np.nan, 0
    s = stops.copy()
    for c in ("stop_lat", "stop_lon"):
        s[c] = pd.to_numeric(s[c], errors="coerce")
    s = s.dropna(subset=["stop_lat", "stop_lon"])
    s = s[s["stop_lat"].between(-90, 90) & s["stop_lon"].between(-180, 180)]
    if not len(s):
        return "", "", np.nan, np.nan, 0
    lon, lat = float(s["stop_lon"].median()), float(s["stop_lat"].median())
    pt = gpd.GeoDataFrame(geometry=gpd.points_from_xy([lon], [lat]), crs=C.CRS_DEG)
    icc = ""
    hit = gpd.sjoin(pt, countries[["icc", "geometry"]], how="left", predicate="within")
    if len(hit) and pd.notna(hit["icc"].iloc[0]):
        icc = str(hit["icc"].iloc[0])
    city = ""
    near = gpd.sjoin_nearest(pt.to_crs(C.CRS_EU), fua_pts, how="left", distance_col="d")
    if len(near) and pd.notna(near["name"].iloc[0]):
        city = f"{near['name'].iloc[0]} ({near['d'].iloc[0] / 1000:.0f} km)"
    return icc, city, lon, lat, len(s)


rows = []
for path in sorted(FEEDS.glob("*.zip")):
    try:
        with ZipFile(path) as z:
            present = {Path(f).stem for f in z.namelist()} & set(ALL)
            if not present:
                continue
            fa, fr = read(z, "fare_attributes"), read(z, "fare_rules")
            n_products, currency, pmin, pmax = price_summary(z, fa)
            n_od = 0
            if fr is not None and {"origin_id", "destination_id"} <= set(fr.columns):
                n_od = int(fr.dropna(subset=["origin_id", "destination_id"])
                           [["origin_id", "destination_id"]].drop_duplicates().shape[0])
            icc, city, lon, lat, n_stops = locate(read(z, "stops"))
            agency = read(z, "agency")
            name = ""
            if agency is not None and "agency_name" in agency.columns:
                vals = agency["agency_name"].dropna().astype(str).unique()
                name = "; ".join(vals[:2]) + (f" +{len(vals) - 2}" if len(vals) > 2 else "")
            rows.append(dict(
                feed=path.stem, provider=str(provider.get(path.stem, ""))[:80],
                agencies=name[:80], icc=icc, nearest_fua=city,
                model=classify(fr, fa, present), n_products=n_products,
                n_od_pairs=n_od, currency=currency, price_min=pmin, price_max=pmax,
                n_stops=n_stops,
                lon=round(lon, 4) if pd.notna(lon) else np.nan,
                lat=round(lat, 4) if pd.notna(lat) else np.nan,
                tables=",".join(sorted(present)),
            ))
    except Exception as e:
        C.error(f"{path.stem}: {e}")

df = pd.DataFrame(rows).sort_values(
    ["icc", "n_od_pairs", "n_products"], ascending=[True, False, False])
df.to_csv(OUT, index=False, encoding="utf-8")
C.log(f"Wrote {OUT.name}: {len(df)} feeds carrying fare data")
print(df["model"].value_counts().to_string())
