import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import recommender as r  # noqa: E402


def ornek_df():
    return pd.DataFrame({
        "Kitap Adı": ["A", "B", "C", "D"],
        "Yazar": ["a", "b", "c", "d"],
        r.SURE_SUTUNU: [3.0, 6.5, 12.0, 30.0],
    })


# --- Şehir eşleştirme (TS-01 ... TS-05) ---

@pytest.mark.parametrize("girdi, beklenen", [
    ("İstanbul", "İstanbul"),
    ("istanbul", "İstanbul"),   # küçük harf, noktalı i
    ("İSTANBUL", "İstanbul"),
    ("izmir", "İzmir"),
    ("eskisehir", "Eskişehir"),  # Türkçe karaktersiz
    ("diyarbakir", "Diyarbakır"),
    ("  KONYA  ", "Konya"),      # boşluk + büyük harf
])
def test_gecerli_sehirler_bulunur(girdi, beklenen):
    assert r.sehir_bul(girdi) == beklenen


@pytest.mark.parametrize("girdi", ["Atlantis", "", "   ", "ist"])
def test_gecersiz_sehir_none_doner(girdi):
    assert r.sehir_bul(girdi) is None


# --- Öneri mantığı (TS-06 ... TS-08) ---

def test_sigan_kitaplar_secilir_ve_hepsi_sureye_uyar():
    kitaplar, bitirilebilir = r.oner(ornek_df(), 7.0)
    assert bitirilebilir is True
    assert (kitaplar[r.SURE_SUTUNU] <= 7.0).all()


def test_uzun_yolculukta_en_uzun_sigan_kitap_once_gelir():
    kitaplar, _ = r.oner(ornek_df(), 26.0)
    assert kitaplar.iloc[0]["Kitap Adı"] == "C"  # 12 saat: 26'ya sığan en uzun


def test_hicbiri_sigmazsa_en_kisa_kitaplar_doner():
    kitaplar, bitirilebilir = r.oner(ornek_df(), 1.5)
    assert bitirilebilir is False
    assert kitaplar.iloc[0]["Kitap Adı"] == "A"  # en kısa


def test_adet_siniri_uygulanir():
    kitaplar, _ = r.oner(ornek_df(), 100.0, adet=2)
    assert len(kitaplar) == 2


# --- Yüzde hesabı (TS-09) ---

def test_yuzde_100u_gecmez():
    assert r.okunabilir_yuzde(3.0, 10.0) == 100


def test_yuzde_kismi_okuma():
    assert r.okunabilir_yuzde(10.0, 5.0) == 50


# --- Veri dosyası (TS-10, TS-11) ---

def test_gercek_veri_yuklenir_ve_sureler_sayidir():
    df = r.kitaplari_yukle()
    assert len(df) > 0
    assert pd.api.types.is_numeric_dtype(df[r.SURE_SUTUNU])
    assert {"Kitap Adı", "Yazar", "Kitap Dili"} <= set(df.columns)


def test_virgullu_ondalik_acik_hata_verir(tmp_path):
    bozuk = tmp_path / "bozuk.csv"
    bozuk.write_text(f'Kitap Adı,Yazar,"{r.SURE_SUTUNU}"\nA,a,"4,8"\n', encoding="utf-8")
    with pytest.raises(ValueError, match="ondalık"):
        r.kitaplari_yukle(bozuk)
