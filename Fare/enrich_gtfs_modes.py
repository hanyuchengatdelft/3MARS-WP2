"""Add rail/bus route types to the GTFS fare inventory.

Reads `Fare/gtfs_fare_inventory.csv`, classifies each feed's routes against the
`RAIL_ROUTE_TYPES` and `BUS_ROUTE_TYPES` sets in `params.yml`, and writes the
`modes` column back. Run after `scan_gtfs_fares.py`, from the repository root:

    python Fare/enrich_gtfs_modes.py
"""

import io
import sys
import warnings
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config as C

warnings.filterwarnings("ignore")

CSV = Path(__file__).resolve().parent / "gtfs_fare_inventory.csv"
params = C.load_params()
RAIL, BUS = set(params.RAIL_ROUTE_TYPES), set(params.BUS_ROUTE_TYPES)

df = pd.read_csv(CSV)
modes = []
for feed in df["feed"]:
    found = set()
    try:
        with ZipFile(C.DATA / f"gtfs/feeds/{feed}.zip") as z:
            files = [f for f in z.namelist() if Path(f).stem == "routes"]
            if files:
                r = pd.read_csv(io.BytesIO(z.read(files[0])), low_memory=False)
                r.rename(columns=str.strip, inplace=True)
                if "route_type" in r.columns:
                    t = pd.to_numeric(r["route_type"], errors="coerce").dropna().astype(int)
                    if t.isin(list(RAIL)).any():
                        found.add("Rail")
                    if t.isin(list(BUS)).any():
                        found.add("Bus")
                    if len(t[~t.isin(list(RAIL)) & ~t.isin(list(BUS))]):
                        found.add("Other")
    except Exception as e:
        C.error(f"{feed}: {e}")
    modes.append("+".join(sorted(found)))

df["modes"] = modes
df.to_csv(CSV, index=False, encoding="utf-8")
C.log(f"Added modes for {len(df)} feeds")
print(df["modes"].value_counts().to_string())
print("\nFeeds with rail routes and fare data:")
print(df[df["modes"].str.contains("Rail", na=False)]
      [["feed", "icc", "agencies", "model", "n_od_pairs", "currency",
        "price_min", "price_max"]].to_string(index=False))
