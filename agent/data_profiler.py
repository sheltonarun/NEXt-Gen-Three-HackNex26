from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "raw"


def profile_file(path: Path) -> str:
    df = pd.read_csv(path, dtype=str)  # raw text, so nothing gets hidden
    lines = [f"FILE: data/raw/{path.name} ({len(df)} rows)"]
    lines.append(f"columns: {list(df.columns)}")
    lines.append(f"exact duplicate rows: {int(df.duplicated().sum())}")
    nulls = df.isna().sum()
    nulls = nulls[nulls > 0]
    lines.append(f"missing values: {nulls.to_dict() or 'none'}")
    for col in df.columns:
        vals = df[col].dropna()
        if vals.nunique() <= 8:
            lines.append(f"  {col}: distinct values = {sorted(vals.unique())}")
        if any(k in col.lower() for k in ("date", "time", "day")):
            lines.append(f"  {col}: raw samples = {vals.head(5).tolist()}")
        if vals.str.contains(r"[$€£]", regex=True).any():
            lines.append(f"  {col}: contains currency symbols")
        if vals.str.contains(r"\d{1,3},\d{3}", regex=True).any():
            lines.append(f"  {col}: contains thousands separators")
    lines.append("first 3 rows:\n" + df.head(3).to_string(index=False))
    return "\n".join(lines)


def profile_data(data_dir=DATA_DIR) -> str:
    profiles = []
    files = sorted(Path(data_dir).glob("*.csv"))
    if not files:
        profiles.append("No CSV files found in data/raw/")
    else:
        profiles.extend(profile_file(f) for f in files)
        
    docs_dir = ROOT / "data" / "docs"
    if docs_dir.exists():
        for ext in ("*.txt", "*.md"):
            for doc in sorted(docs_dir.glob(ext)):
                try:
                    content = doc.read_text(encoding="utf-8")
                    profiles.append(f"DOCUMENT: data/docs/{doc.name}\n{content[:6000]}")
                except Exception as e:
                    profiles.append(f"DOCUMENT: data/docs/{doc.name}\n[Error reading file: {e}]")
                    
    return "\n\n".join(profiles)