"""data/gar_kutuphanesi_veriseti.csv dosyasını site/kitaplar.json'a çevirir.

scraper.py ile veriyi yeniledikten sonra bir kez çalıştırın:  python build_json.py
"""
import json
from pathlib import Path

import pandas as pd

KOK = Path(__file__).resolve().parent
SURE = "Tahmini Okunma Süresi (Saat)"

df = pd.read_csv(KOK / "data" / "gar_kutuphanesi_veriseti.csv")
df[SURE] = pd.to_numeric(df[SURE], errors="coerce")
df = df[df[SURE] > 0]

kitaplar = [
    {
        "ad": r["Kitap Adı"],
        "yazar": r["Yazar"] if pd.notna(r["Yazar"]) else "",
        "dil": r["Kitap Dili"] if pd.notna(r["Kitap Dili"]) else "",
        "sayfa": int(r["Sayfa Sayısı"]),
        "sure": float(r[SURE]),
        "link": r["Link"],
    }
    for _, r in df.iterrows()
]

cikti = KOK / "site" / "kitaplar.json"
cikti.write_text(json.dumps(kitaplar, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(kitaplar)} kitap yazıldı -> {cikti}")
