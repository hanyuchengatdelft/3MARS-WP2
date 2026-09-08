"""Identify major transport operating companies (TOCs) from intercity 
GTFS agencies."""

#%% Imports
import pandas as pd

import config as C

#%% Load data
fuas = C.load("fuas").set_index("id").rename_axis("fua")#.view()
stns = C.load("ic-stations").set_index("stn")#.view()
lines = C.load("ic-lines").set_index("line")#.view()
seg = C.load("ic-segments")[["src", "trg", "line"]]#.view()

#%% Load the manual mapping of agencies to TOCs
agency2toc = (
    pd.read_csv(C.DATA / "gtfs/agency2toc.csv")
    .assign(rail=lambda df: df["mode"] == "Rail")
    [["agency", "rail", "operator"]]
)#.view(5)
print("Total operators:", agency2toc["operator"].nunique())

#%% Intercity lines, stations and associated data
ic_lines = (
    lines.query("intercity").reset_index()
    .merge(agency2toc, on=["agency", "rail"])
)#.view()
major_stns = ic_lines["stn"].explode().astype(int).unique()
stns2 = stns.loc[major_stns].sort_index().reset_index()#.view()
ic_jrn = (
    C.load("ic-journeys")
    .merge(ic_lines[["line"]], on="line")
)#.view()
ic_dates = (
    C.load("ic-datesets")
    .merge(ic_jrn[["dateset"]].drop_duplicates(), on="dateset")
)#.view()
ic_tt = (
    C.load("ic-timetable")
    .merge(ic_jrn[["jrn"]], on="jrn")
)#.view()

#%% Intraurban data involving major stations on intercity lines
urb_lines = (
    lines.query("~intercity")
    ["stn"].explode().astype(int).reset_index()
    .merge(stns2[["stn"]], on="stn")
    .groupby("line")
    ["stn"].agg(["count", list])
    .query("count > 1")
    ["list"].rename("stn").reset_index()
    .merge(lines.drop(columns="stn"), on="line")
    .assign(operator=".Local")
)#.view()
urb_jrn = (
    C.load("ic-journeys")
    .merge(urb_lines[["line"]], on="line")
)#.view()
urb_dates = (
    C.load("ic-datesets")
    .merge(urb_jrn[["dateset"]].drop_duplicates(), on="dateset")
)#.view()
urb_tt = (
    C.load("ic-timetable")
    .merge(urb_jrn[["jrn", "line"]], on="jrn")
    .merge(stns2[["stn"]], on="stn")
)#.view()

#%% Combine intercity and intraurban data
lines2 = (
    pd.concat([ic_lines, urb_lines])
    .drop_duplicates("line")
    .sort_values("line", ignore_index=True)
    [["line", "agency", "operator", "rail", "tz_gap", "stn", "intercity"]]
)#.view()
jrn = (
    pd.concat([ic_jrn, urb_jrn])
    .drop_duplicates("jrn")
    .sort_values("jrn", ignore_index=True)
)#.view()
dates = (
    pd.concat([ic_dates, urb_dates])
    .drop_duplicates("dateset")
    .sort_values("dateset", ignore_index=True)
)#.view()
tt = (
    pd.concat([ic_tt, urb_tt]).drop(columns="line")
    .sort_values(["jrn", "arr"], ignore_index=True)
)#.view()
seg2 = (
    seg["line"].explode().astype(int).reset_index()
    .merge(lines2[["line"]], on="line")
    .groupby("seg")["line"].agg(list).reset_index()
    .merge(C.load("ic-segments").drop(columns="line"), on="seg")
    .merge(stns2["stn"].rename("src"), on="src")
    .merge(stns2["stn"].rename("trg"), on="trg")
    .set_index("seg")
    [["src", "trg", "mode", "intercity", "line"]]
)#.view()

#%% Export updated tables
C.log("Saving intercity data tables")
for df, table in [
    (stns2, "ic-stations"),
    (lines2, "ic-lines"),
    (jrn, "ic-journeys"),
    (dates, "ic-datesets"),
    (tt, "ic-timetable"),
    (seg2, "ic-segments"),
]:
    C.log(f"Table `{table}`: {len(df):,} rows")
    C.save(df, table)
