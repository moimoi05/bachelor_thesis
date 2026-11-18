from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import yaml

ALLOWED_PHASES = {"ADNI1", "ADNIGO", "ADNI2"}
EXCLUDE_DESCRIPTION = re.compile(r"mask|localizer|calibration|\bt2\*?\b|\bpd\b", re.I)


def load_paths(config: str | Path = "paths.yaml") -> dict[str, Path]:
    config = Path(config).resolve()
    raw = yaml.safe_load(config.read_text(encoding="utf-8"))
    root = Path(raw["root"])
    result = {k: root / v for k, v in raw["inputs"].items()}
    result.update({k: root / v for k, v in raw["outputs"].items()})
    result["config"] = config
    return result


def ensure_output_dirs(paths: dict[str, Path]) -> None:
    for key in ("processed_dir", "intermediate_dir", "reports_dir", "rda_cache_dir"):
        paths[key].mkdir(parents=True, exist_ok=True)


def read_csv(path: Path, **kwargs) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False, **kwargs)


def normalize_phase(value: object) -> str:
    return str(value).upper().replace(" ", "") if pd.notna(value) else ""


def valid_mmse(df: pd.DataFrame) -> pd.Series:
    date = pd.to_datetime(df["VISDATE"], errors="coerce")
    score = pd.to_numeric(df["MMSCORE"], errors="coerce")
    done = pd.to_numeric(df.get("DONE"), errors="coerce")
    qc = pd.to_numeric(df.get("HAS_QC_ERROR"), errors="coerce")
    return date.notna() & score.between(0, 30) & (done.isna() | done.ne(0)) & (qc.isna() | qc.ne(1))


def valid_cdr(df: pd.DataFrame) -> pd.Series:
    date = pd.to_datetime(df["VISDATE"], errors="coerce")
    score = pd.to_numeric(df["CDGLOBAL"], errors="coerce")
    qc = pd.to_numeric(df.get("HAS_QC_ERROR"), errors="coerce")
    return date.notna() & score.between(0, 3) & (qc.isna() | qc.ne(1))


def select_baselines(dxsum: pd.DataFrame) -> pd.DataFrame:
    d = dxsum.copy()
    d["phase_norm"] = d["PHASE"].map(normalize_phase)
    d["EXAMDATE"] = pd.to_datetime(d["EXAMDATE"], errors="coerce")
    d["DIAGNOSIS"] = pd.to_numeric(d["DIAGNOSIS"], errors="coerce")
    mask = d["phase_norm"].isin(ALLOWED_PHASES) & d["VISCODE2"].eq("bl") & d["DIAGNOSIS"].eq(2) & d["EXAMDATE"].notna()
    result = d.loc[mask].sort_values(["RID", "EXAMDATE", "ID"]).drop_duplicates("RID")
    result = result[["RID", "PTID", "phase_norm", "EXAMDATE"]].rename(columns={"phase_norm": "baseline_phase", "EXAMDATE": "baseline_date"})
    result["landmark_date"] = result["baseline_date"] + pd.DateOffset(months=18)
    return result


def clinical_outcome_for_subject(rid: int, baseline: pd.Timestamp, landmark: pd.Timestamp,
                                 dx: pd.DataFrame, mmse: pd.DataFrame, cdr: pd.DataFrame) -> dict:
    triggers: list[tuple[pd.Timestamp, str, float]] = []
    d = dx[(dx["RID"] == rid) & dx["EXAMDATE"].notna() & (dx["EXAMDATE"] <= landmark) & dx["DIAGNOSIS"].eq(3)]
    triggers += [(r.EXAMDATE, "DXSUM.DIAGNOSIS", r.DIAGNOSIS) for r in d.itertuples()]
    m = mmse[(mmse["RID"] == rid) & mmse["valid"] & (mmse["VISDATE"] <= landmark) & mmse["MMSCORE"].lt(24)]
    triggers += [(r.VISDATE, "MMSE.MMSCORE", r.MMSCORE) for r in m.itertuples()]
    c = cdr[(cdr["RID"] == rid) & cdr["valid"] & (cdr["VISDATE"] <= landmark) & cdr["CDGLOBAL"].ge(1)]
    triggers += [(r.VISDATE, "CDR.CDGLOBAL", r.CDGLOBAL) for r in c.itertuples()]
    if triggers:
        date, variable, value = min(triggers, key=lambda x: (x[0], x[1]))
        return {"early_conversion": True, "early_conversion_date": date,
                "early_conversion_variable": variable, "early_conversion_value": value}

    post: list[tuple[pd.Timestamp, str, float, bool]] = []
    m = mmse[(mmse["RID"] == rid) & mmse["valid"] & (mmse["VISDATE"] > landmark)]
    post += [(r.VISDATE, "MMSE.MMSCORE", r.MMSCORE, r.MMSCORE < 24) for r in m.itertuples()]
    c = cdr[(cdr["RID"] == rid) & cdr["valid"] & (cdr["VISDATE"] > landmark)]
    post += [(r.VISDATE, "CDR.CDGLOBAL", r.CDGLOBAL, r.CDGLOBAL >= 1) for r in c.itertuples()]
    events = [x for x in post if x[3]]
    if events:
        date, variable, value, _ = min(events, key=lambda x: (x[0], x[1]))
        return {"early_conversion": False, "event": 1, "event_date": date,
                "event_variable": variable, "event_value": value, "censor_date": pd.NaT,
                "n_valid_post_landmark": len(post)}
    censor = max((x[0] for x in post), default=pd.NaT)
    return {"early_conversion": False, "event": 0, "event_date": pd.NaT,
            "event_variable": "", "event_value": pd.NA, "censor_date": censor,
            "n_valid_post_landmark": len(post)}


def processing_rank(description: str, phase: str) -> int:
    s = description.lower().replace(" ", "")
    n3m = "n3m" in s
    n3 = "n3" in s and not n3m
    gw = "gradwarp" in s
    scaled = "scaled" in s
    b1 = "b1" in s
    phase = normalize_phase(phase)
    if phase == "ADNI1":
        patterns = [(n3 and scaled and gw and b1), (n3 and scaled and gw),
                    (n3 and scaled), (n3 and gw and b1), (n3 and gw), n3]
    else:
        patterns = [(n3m and gw), n3m, (n3 and gw), n3]
    for rank, matched in enumerate(patterns, 1):
        if matched:
            return rank
    return 99


def add_processing_metadata(mri: pd.DataFrame) -> pd.DataFrame:
    d = mri.copy()
    d["repeat_status"] = d["Description"].str.contains(r"repeat|mpr-r", case=False, regex=True, na=False).map({True: "repeat", False: "primary"})
    d["processing_rank"] = [processing_rank(x, p) for x, p in zip(d["Description"], d["Phase"])]
    d["selection_source"] = "processing_fallback"
    return d


def group_anchor_two_months(scans: pd.DataFrame) -> pd.DataFrame:
    d = scans.sort_values(["Study Date", "Image ID"]).copy()
    groups, group_id, anchor = [], -1, None
    for date in d["Study Date"]:
        if anchor is None or date > anchor + pd.DateOffset(months=2):
            group_id += 1
            anchor = date
        groups.append(group_id)
    d["timepoint_id"] = groups
    return d


def choose_one_per_timepoint(scans: pd.DataFrame) -> pd.DataFrame:
    keys = ["timepoint_id", "repeat_order", "processing_rank", "Image ID"]
    d = scans.copy()
    d["repeat_order"] = d["repeat_status"].eq("repeat").astype(int)
    return d.sort_values(keys).drop_duplicates("timepoint_id").drop(columns="repeat_order")


def select_first_mid_last(timepoints: pd.DataFrame) -> pd.DataFrame:
    d = timepoints.sort_values(["Study Date", "Image ID"]).copy()
    if len(d) <= 3:
        return d
    first, last = d.iloc[0], d.iloc[-1]
    midpoint = first["Study Date"] + (last["Study Date"] - first["Study Date"]) / 2
    candidates = d.iloc[1:-1].copy()
    candidates["mid_distance"] = (candidates["Study Date"] - midpoint).abs()
    candidates["repeat_order"] = candidates["repeat_status"].eq("repeat").astype(int)
    mid = candidates.sort_values(["mid_distance", "repeat_order", "processing_rank", "Image ID"]).iloc[0]
    return pd.DataFrame([first, mid.drop(labels=["mid_distance", "repeat_order"]), last]).sort_values("Study Date")


def assert_no_leakage(selected: pd.DataFrame, labels: pd.DataFrame) -> None:
    merged = selected[["RID", "Study Date"]].merge(labels[["RID", "baseline_date", "landmark_date", "outcome_date", "event_date", "prediction_date"]], on="RID")
    assert (merged["Study Date"] <= merged["landmark_date"]).all()
    assert (merged["Study Date"] <= merged["prediction_date"]).all()
    event_rows = merged["event_date"].notna()
    assert (merged.loc[event_rows, "Study Date"] <= merged.loc[event_rows, "event_date"]).all()
    assert (merged["outcome_date"] >= merged["prediction_date"]).all()
