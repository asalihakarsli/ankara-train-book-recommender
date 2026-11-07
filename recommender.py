"""Ankara'dan seçilen şehre tren yolculuğu süresine göre kitap önerir.

Kitap verisi, scraper.py ile toplanan data/gar_kutuphanesi_veriseti.csv
dosyasından okunur.
"""
import sys
from pathlib import Path

import pandas as pd

VERI_YOLU = Path(__file__).resolve().parent / "data" / "gar_kutuphanesi_veriseti.csv"
SURE_SUTUNU = "Tahmini Okunma Süresi (Saat)"

# Ankara'dan yaklaşık tren yolculuğu süreleri (saat).
# Süreler yaklaşıktır, resmi tarifeyle doğrulanmalıdır.
# Kayseri ve sonrasındaki hatlar hızlı tren (YHT) değil, konvansiyonel trenlerdir.
YOLCULUK_SURELERI = {
    "Eskişehir": 1.5,
    "Konya": 1.8,
    "Sivas": 2.0,
    "Karaman": 2.7,
    "İstanbul": 5.0,
    "Kayseri": 7.0,
    "Adana": 11.0,
    "İzmir": 14.0,      # İzmir Mavi Treni
    "Erzurum": 22.0,    # Doğu Ekspresi
    "Diyarbakır": 23.0, # Güney Kurtalan Ekspresi
    "Kars": 26.0,       # Doğu Ekspresi
}

_TR_ASCII = str.maketrans("çğıöşü", "cgiosu")


def tr_kucult(metin):
    """Türkçe kurallarına uygun küçültme (İ -> i, I -> ı)."""
    return metin.replace("İ", "i").replace("I", "ı").lower()


def normallestir(metin):
    """Büyük/küçük harf ve Türkçe karakter farkını yok sayarak karşılaştırma anahtarı üretir."""
    return tr_kucult(metin.strip()).translate(_TR_ASCII)


_SEHIR_ESLEME = {normallestir(sehir): sehir for sehir in YOLCULUK_SURELERI}


def sehir_bul(girdi):
    """Kullanıcının yazdığı metni listedeki şehir adıyla eşleştirir; bulunamazsa None döner.

    'istanbul', 'İSTANBUL', 'eskisehir', 'diyarbakir' gibi yazımların hepsi kabul edilir.
    """
    return _SEHIR_ESLEME.get(normallestir(girdi))


def kitaplari_yukle(yol=VERI_YOLU):
    """CSV'yi okur; okunma süresi bilinmeyen kitapları eler."""
    df = pd.read_csv(yol)
    df[SURE_SUTUNU] = pd.to_numeric(df[SURE_SUTUNU], errors="coerce")
    df = df[df[SURE_SUTUNU] > 0]
    if df.empty:
        raise ValueError(
            f"'{SURE_SUTUNU}' sütununda geçerli sayı bulunamadı. "
            "CSV'de ondalık ayracının nokta olduğundan emin olun (4.8, 4,8 değil)."
        )
    return df


def okunabilir_yuzde(toplam_sure, yolculuk_suresi):
    """Yolculuk boyunca kitabın yüzde kaçının okunabileceği (en çok 100)."""
    return min(100, int(yolculuk_suresi / toplam_sure * 100))


def oner(df, yolculuk_suresi, adet=5):
    """Yolculuk süresine göre kitap seçer.

    Süreye sığan kitap varsa, yolculuğu en iyi dolduranları (en uzun ama
    bitebilecek olanlar) döndürür. Hiçbiri sığmıyorsa en kısa kitapları döndürür.
    Dönüş değeri: (kitaplar, hepsi_bitirilebilir)
    """
    sigan = df[df[SURE_SUTUNU] <= yolculuk_suresi]
    if not sigan.empty:
        return sigan.sort_values(SURE_SUTUNU, ascending=False).head(adet), True
    return df.sort_values(SURE_SUTUNU, ascending=True).head(adet), False


def main():
    df = kitaplari_yukle()

    print("Ankara YHT Garı'ndan nereye seyahat edeceksiniz?")
    for sehir in YOLCULUK_SURELERI:
        print(f"- {sehir}")

    while True:
        try:
            girdi = input("\nŞehir seçin (çıkmak için boş bırakın): ")
        except EOFError:
            return 1
        if not girdi.strip():
            return 0
        sehir = sehir_bul(girdi)
        if sehir:
            break
        print(f"'{girdi.strip()}' listede yok. Lütfen yukarıdaki şehirlerden birini yazın.")

    sure = YOLCULUK_SURELERI[sehir]
    print(f"\n{sehir} yolculuğunuz yaklaşık {sure} saat sürecektir.")

    kitaplar, bitirilebilir = oner(df, sure)
    print("\n📖 Kitap Önerileriniz:")
    if bitirilebilir:
        print("Trende tamamen bitirebileceğiniz kitaplar:")
    else:
        print("Bu yolculukta tamamen bitecek kadar kısa bir kitap yok. Ancak şu kitaplara başlayabilirsiniz:")

    for _, kitap in kitaplar.iterrows():
        toplam = kitap[SURE_SUTUNU]
        yuzde = okunabilir_yuzde(toplam, sure)
        print(f"- {kitap['Kitap Adı']} | Yazar: {kitap['Yazar']}")
        if yuzde == 100:
            print(f"  (Toplam {toplam} saat. Yolculukta rahatlıkla bitirebilirsiniz.)")
        else:
            print(f"  (Toplam {toplam} saat sürüyor. Yolculuk boyunca yaklaşık %{yuzde} kadarını okuyabilirsiniz.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
