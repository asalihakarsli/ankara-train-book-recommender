import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from pathlib import Path

# Ayarlar
BASE_URL = "https://katalog.ankara.bel.tr"
SEARCH_URL = "https://katalog.ankara.bel.tr/cgi-bin/koha/opac-search.pl?idx=&q=&limit=branch%3AYHT"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
KONUM_SABIT = "Ankara YHT Gar Kütüphanesi"
OKUMA_HIZI = 40 # Saatte okunan sayfa sayısı
VERI_KLASORU = Path(__file__).resolve().parent / "data"
CIKTI_DOSYASI = VERI_KLASORU / "gar_kutuphanesi_veriseti.csv"

def detay_sayfasini_tara(url):
    """Kitabın içine girerek Yazar, Dil ve Sayfa Sayısı bilgilerini çeker."""
    bilgiler = {"Yazar": None, "Dil": None, "Sayfa Sayısı": 0}
    
    try:
        req = requests.get(url, headers=HEADERS, timeout=10)
        req.raise_for_status()
        detay_soup = BeautifulSoup(req.content, "html.parser")
        
        # 1. Yazar Çekme
        yazar_etiketi = detay_soup.find("h5", class_="author")
        if not yazar_etiketi:
            yazar_etiketi = detay_soup.select_one('.results_summary.author a')
        if yazar_etiketi:
            bilgiler["Yazar"] = yazar_etiketi.text.strip()
            
        # 2. Dil Çekme
        dil_etiketi = detay_soup.find("span", class_="results_summary language")
        if dil_etiketi:
            # Get the text inside the span with class "language"
            dil_degeri_etiketi = dil_etiketi.find("span", class_="language")
            if dil_degeri_etiketi:
                bilgiler["Dil"] = dil_degeri_etiketi.text.strip()
                 
        # 3. Sayfa Sayısı Çekme
        tanim_etiketi = detay_soup.find("span", property="description")
        if tanim_etiketi:
            tanim_metni = tanim_etiketi.text.strip() 
            sayfa_bul = re.search(r'(\d+)\s*sayfa', tanim_metni, re.IGNORECASE)
            if sayfa_bul:
                bilgiler["Sayfa Sayısı"] = int(sayfa_bul.group(1))

    except Exception as e:
        print(f"  -> Veri çekilirken hata oluştu: {e}")
        
    return bilgiler

def veri_seti_olustur(hedef_kitap_sayisi=50):
    kitap_verileri = []
    gorulen_linkler = set() 
    sayfa_offset = 0 
    
    print(f"Toplam {hedef_kitap_sayisi} kitap için kütüphane taranıyor...\n")
    
    while len(kitap_verileri) < hedef_kitap_sayisi:
        guncel_sayfa_url = f"{SEARCH_URL}&offset={sayfa_offset}"
        response = requests.get(guncel_sayfa_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        kitap_linkleri = soup.select('a.title')
        
        if not kitap_linkleri:
            print("Kütüphanedeki tüm kitaplar tarandı, başka sonuç bulunamadı.")
            break
            
        for link_etiketi in kitap_linkleri:
            if len(kitap_verileri) >= hedef_kitap_sayisi:
                break
                
            detay_url = BASE_URL + link_etiketi['href']
            
            if detay_url in gorulen_linkler:
                continue
                
            gorulen_linkler.add(detay_url)
            
            # Kitap adı temizleme
            tam_baslik = link_etiketi.text.strip()
            kitap_adi = tam_baslik.split(' / ')[0].strip() if ' / ' in tam_baslik else tam_baslik

            su_anki_sayi = len(kitap_verileri) + 1
            
            print(f"[{su_anki_sayi}/{hedef_kitap_sayisi}] İnceleniyor: {kitap_adi}")
            
            detay_bilgileri = detay_sayfasini_tara(detay_url)
            
            sayfa = detay_bilgileri["Sayfa Sayısı"]
            okuma_suresi = round(sayfa / OKUMA_HIZI, 1) if isinstance(sayfa, int) and sayfa > 0 else None
            
            satir = {
                "Kitap Adı": kitap_adi,
                "Yazar": detay_bilgileri["Yazar"],
                "Kitap Dili": detay_bilgileri["Dil"],
                "Sayfa Sayısı": sayfa if sayfa > 0 else None,
                "Tahmini Okunma Süresi (Saat)": okuma_suresi,
                "Konum": KONUM_SABIT,
                "Link": detay_url
            }
            
            kitap_verileri.append(satir)
            time.sleep(1.5) 
            
        sayfa_offset += 20 
        
    df = pd.DataFrame(kitap_verileri)
    if df.empty:
        print("Hiç kitap verisi toplanamadı, dosya yazılmadı.")
        return df

    # Eksik sayfa sayısı olan satırlar yüzünden sütun ondalıklı (432.0) yazılmasın
    df["Sayfa Sayısı"] = df["Sayfa Sayısı"].astype("Int64")

    VERI_KLASORU.mkdir(parents=True, exist_ok=True)
    df.to_csv(CIKTI_DOSYASI, index=False, encoding="utf-8-sig")

    print(f"\n✅ İşlem Tamamlandı! Veriler '{CIKTI_DOSYASI}' dosyasına kaydedildi.")
    return df

if __name__ == "__main__":
    veri_tablosu = veri_seti_olustur(hedef_kitap_sayisi=50)