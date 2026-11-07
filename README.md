# Ankara Train Book Recommender

*Picks books from the Ankara YHT Station Library catalog that fit the length of your train journey from Ankara. Python, web scraping, pandas.*

Ankara Büyükşehir Belediyesi'nin YHT Gar Kütüphanesi kataloğundan kitap bilgilerini toplar (`scraper.py`) ve seçtiğiniz şehre olan tren yolculuğunuzun süresine göre okuyabileceğiniz kitapları önerir (`recommender.py`).

## Nasıl çalışır?

1. `scraper.py`, katalogdaki YHT Gar Kütüphanesi kitaplarının adını, yazarını, dilini ve sayfa sayısını toplar. Okunma süresi, sayfa sayısının sabit bir okuma hızına (saatte 40 sayfa) bölünmesiyle tahmin edilir.
2. `recommender.py`, veriyi okur ve seçilen şehrin yaklaşık yolculuk süresine sığan kitapları önerir. Yolculuğa en iyi sığanlar (en uzun ama bitebilecek olanlar) öne çıkar. Hiçbir kitap sığmıyorsa en kısa kitaplar önerilir ve yolculukta yüzde kaçının okunabileceği gösterilir.

## Kurulum

```bash
pip install -r requirements.txt
```

## Kullanım

```bash
python scraper.py        # veriyi yeniden toplar -> data/gar_kutuphanesi_veriseti.csv
python recommender.py    # şehri seçip öneri alın
```

Örnek çıktı (`istanbul` yazıldığında):

```
İstanbul yolculuğunuz yaklaşık 5.0 saat sürecektir.

📖 Kitap Önerileriniz:
Trende tamamen bitirebileceğiniz kitaplar:
- Acı çekirdek | Yazar: Yener, Aylin İşcan
  (Toplam 5.0 saat. Yolculukta rahatlıkla bitirebilirsiniz.)
...
```

## Proje yapısı

```
├── scraper.py                         katalogdan veri toplar
├── recommender.py                     öneri programı
├── data/gar_kutuphanesi_veriseti.csv  örnek veri (50 kitap)
├── tests/test_recommender.py          otomatik testler
└── requirements.txt
```

## Veri seti sütunları

`Kitap Adı`, `Yazar`, `Kitap Dili`, `Sayfa Sayısı`, `Tahmini Okunma Süresi (Saat)`, `Konum`, `Link`

## Test senaryoları

Otomatik testleri çalıştırmak için:

```bash
pip install pytest
pytest
```

Elle yapılan test senaryoları ve sonuçları:

| No | Girdi | Beklenen sonuç | İlk sürümde | Şimdi |
|----|-------|----------------|-------------|-------|
| TS-01 | `istanbul` (küçük harf) | İstanbul için öneriler | Hiçbir çıktı vermeden sonlandı | ✅ Geçti |
| TS-02 | `izmir` (küçük harf) | İzmir için öneriler | Hiçbir çıktı vermeden sonlandı | ✅ Geçti |
| TS-03 | `Atlantis` (listede yok) | Uyarı mesajı, tekrar sorma | Hiçbir çıktı vermeden sonlandı | ✅ Geçti |
| TS-04 | `eskisehir`, `diyarbakir` (Türkçe karaktersiz) | Şehir eşleşir | Denenmedi | ✅ Geçti |
| TS-05 | `Kars` ve `İstanbul` | Farklı yolculuk süresine uygun, farklı öneriler | İkisinde de aynı en kısa kitaplar geliyordu | ✅ Geçti |
| TS-06 | CSV'de `4,8` gibi virgüllü ondalık | Açık hata mesajı | Sessizce düzeltmeye çalışıyordu | ✅ Geçti |

## Bulunan ve düzeltilen hatalar

- **Büyük/küçük harf ve Türkçe `i`/`İ` sorunu:** Python'un `capitalize()` metodu `istanbul` yazısını `Istanbul` yaptığı için şehir listede bulunamıyordu. Türkçe kurallarına uygun küçültme ve Türkçe karakter eşleştirmesi eklendi.
- **Geçersiz girdide sessiz sonlanma:** Listede olmayan şehirde program hiçbir şey yazmadan kapanıyordu. Artık uyarı veriyor ve yeniden soruyor.
- **Hep aynı öneriler:** Yolculuk süresi ne olursa olsun en kısa kitaplar öneriliyordu. Artık yolculuğa en iyi sığan kitaplar öneriliyor.
- **`Kitap Dili` sütunu:** Veri toplama ilk sürümünde sütunun tamamı "Bilinmiyor" çıkıyordu. HTML seçicisi düzeltildi.
- **Kitap adında yazar adı:** Adlar `Başlık / Yazar` biçiminde geliyordu. Başlık yazar kısmından ayrıldı.
- **Ondalık ayracı:** Okunma süresi CSV'de virgülle (`4,8`) tutuluyordu. Artık noktayla yazılıyor ve virgüllü veri açık bir hata mesajıyla bildiriliyor.
- **Dosya yolu:** Programlar artık hangi klasörden çalıştırılırsa çalıştırılsın doğru dosyayı buluyor.

## Sınırlamalar

- Okuma hızı sabit (saatte 40 sayfa), herkes için geçerli değildir.
- Yolculuk süreleri yaklaşık değerlerdir, resmi tarifeyle doğrulanmalıdır. Kayseri ve sonrasındaki hatlar YHT değil, konvansiyonel trenlerdir.
- Örnek veri 50 kitaptan oluşur, kütüphanenin tamamını kapsamaz.

## Not

Veri toplayıcı istekler arasında 1,5 saniye bekler. Katalog sahibinin kullanım koşullarına uyun ve gereksiz yere sık çalıştırmayın.
