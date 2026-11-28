# Makon — makoncoworking.uz

Makon kovorkingining rasmiy sayti (Toshkent, Lashkarbegi ko'chasi, 11).

## Tuzilishi
| Fayl | Sahifa |
|---|---|
| `index.html` | Bosh sahifa |
| `makon.html` | Makon haqida |
| `galereya.html` | Fotogalereya |
| `azolik.html` | A'zolik va narxlar |
| `rezidentlar.html` | Rezidentlar fikrlari |
| `hayot.html` | Makon hayotida (maqolalar) |
| `aloqa.html` | Aloqa va ariza formasi |
| `rahmat.html` | Ariza yuborilgandan keyingi sahifa |
| `ru/`, `en/` | Rus va ingliz tilidagi sahifalar (o'zbekchadan yasalgan, tepada UZ · RU · EN almashtirgich) |
| `assets/` | Rasmlar, to'lov QR kodi |
| `templates/maqola-namuna.html` | Yangi maqola uchun namuna |

## Joylash
Hosting: GitHub Pages (bepul). Domen makoncoworking.uz ahost.uz'da ro'yxatdan o'tgan, DNS orqali shu repozitoriyga ulangan.
Ariza formasi Google Apps Script orqali "Makon — saytdan arizalar" jadvaliga yoziladi va Telegram'ga xabar bo'lib keladi (kod: `scripts/arizalar.gs`).

## O'zgartirish tartibi
O'zgarish taklif qilinadi → "roziman" so'zidan keyin kiritiladi → avval shu repozitoriyga, keyin saytga.

## Qidiruv tizimlari va AI (GEO)
- `tools/tarjima/seo.py` — canonical, `rahmat` sahifalarida noindex, bosh sahifa va Aloqada LocalBusiness (3 tilda), WebSite ma'lumotlari, `sitemap.xml`. `build.py` har ishga tushganda avtomatik qo'llaydi.
- Faktlar (manzil, telefon, ish vaqti, narx) o'zgarsa: sahifa matni + `seo.py` (FAKTLAR, TIL) + `llms.txt` — uchalasi birga yangilanadi.
- `llms.txt` — AI uchun Makon haqida qisqa faktlar.
- IndexNow kaliti: `cc4c4b194a14819384667ce4a5974e10.txt` (Bing, Yandex va boshqa IndexNow qidiruvlariga yangi sahifalar haqida xabar berish uchun). Faylni o'chirmang.
- IndexNow avtomatik: `.github/workflows/indexnow.yml` — `main` ga har push'dan 2 daqiqa keyin o'zgargan sahifalarni yuboradi. GitHub → Actions → IndexNow → "Run workflow" bosilsa, sitemap'dagi hamma sahifalar yuboriladi (2026-11-28 dan).
- Google Search Console va Yandex Webmaster tasdiqlash kodlari `index.html` ichida (`google-site-verification`, `yandex-verification`) — o'chirmang.

## Statistika

Yandex Metrika hisoblagichi № 114662208 (akkaunt: madinacentralasia@gmail.com) — kodi hamma sahifalarning `<head>` qismida va `templates/maqola-namuna.html` da. Vebvizor o'chirilgan.
