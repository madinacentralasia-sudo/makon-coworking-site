# -*- coding: utf-8 -*-
"""Makon sayti: qidiruv tizimlari va AI (ChatGPT, Gemini, Alisa va b.) uchun texnik belgilar.

build.py har bir sahifa uchun apply() ni chaqiradi. Qayta ishga tushirsa bo'ladi:
eski belgilar o'chirilib, yangisi qo'yiladi.

Nima qiladi:
- har sahifaga o'z tilidagi canonical havola;
- rahmat.html sahifalarini qidiruvdan yopadi (noindex);
- bosh sahifa va Aloqa sahifasiga o'z tilidagi LocalBusiness ma'lumotlari (JSON-LD);
- bosh sahifaga WebSite ma'lumotlari;
- Fotogalereya sahifasiga bosh sahifadan farqli tavsif (description).

Faktlar (manzil, telefon, soat, narx) o'zgarsa — shu fayldagi FAKTLAR va TIL bo'limlarini,
llms.txt ni va sahifa matnlarini birga yangilang.
"""
import json
import re

DOMAIN = 'https://makoncoworking.uz/'
BIZ_ID = DOMAIN + '#makon'
SITE_ID = DOMAIN + '#website'

# ---- Hamma tilda bir xil faktlar ----
FAKTLAR = {
    'telephone': ['+998990704441', '+998957474441'],
    'geo': {'@type': 'GeoCoordinates', 'latitude': 41.320518, 'longitude': 69.29376},
    'openingHoursSpecification': [{
        '@type': 'OpeningHoursSpecification',
        'dayOfWeek': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
        'opens': '10:00',
        'closes': '19:00',
    }],
    'sameAs': [
        'https://www.instagram.com/makon_coworking/',
        'https://yandex.uz/maps/org/233840017594/',
        'https://www.worka.com/en/workplace/789b2ae9-73ab-4c14-bbdd-9d58ca59d19e',
        'https://g.page/r/CURgSQPNN5rjEBM',
        'https://www.instantoffices.com/de/uz/buroraume/tashkent/lashkarbegi-street-789b2ae9-73ab-4c14-bbdd-9d58ca59d19e',
    ],
    'hasMap': 'https://yandex.uz/maps/org/233840017594/',
    'priceRange': '$250–$350',
    'image': DOMAIN + 'assets/og-makon.png',
    'logo': DOMAIN + 'assets/logo-makon.png',
}

# ---- Tilga bog'liq matnlar (saytdagi ko'rinadigan matnlar bilan bir xil) ----
TIL = {
    'uz': {
        'description': "Toshkent markazidagi kovorking: o'z doimiy ish joyi, tinch muhit, kofe va kitoblar.",
        'street': "Lashkarbegi ko'chasi, 11, Akai City turar-joy majmuasi, 2-qavat",
        'city': 'Toshkent',
        'amenities': ['Kompyuterlar', 'Wi-Fi', 'Bepul printer', 'Bepul shaxsiy shkaf', 'Parkovka', 'Doimiy ish joyi'],
        'payment': 'QR-kod (UzQR); naqd pul qabul qilinmaydi',
        'unit': 'oy',
        'offers': [
            ('Makon rezidentlari uchun', '250',
             "Oylik a'zolik: doimiy ish joyi, kompyuterlar, Wi-Fi, bepul printer, bepul shaxsiy shkaf, kitoblar."),
            ('Turagentlar uchun', '350',
             "Oylik a'zolik: rezidentlarning barcha imkoniyatlari, faoliyat uchun litsenziya, moliyaviy, "
             "huquqiy va tashkiliy xizmatlar, tayyor buyurtmalar."),
        ],
        'galereya': ("Makon fotogalereyasi: Toshkent markazidagi kovorkingning ish zali, kofe burchagi, "
                     "kitob javoni va boshqa joylari. Lashkarbegi ko'chasi, 11."),
    },
    'ru': {
        'description': 'Коворкинг в центре Ташкента: своё постоянное рабочее место, спокойная атмосфера, кофе и книги.',
        'street': 'улица Лашкарбеги, 11, ЖК Akai City, 2 этаж',
        'city': 'Ташкент',
        'amenities': ['Компьютеры', 'Wi-Fi', 'Бесплатный принтер', 'Бесплатный личный шкафчик', 'Парковка',
                      'Постоянное рабочее место'],
        'payment': 'QR-код (UzQR); наличные не принимаются',
        'unit': 'месяц',
        'offers': [
            ('Для резидентов Makon', '250',
             'Ежемесячное членство: постоянное рабочее место, компьютеры, Wi-Fi, бесплатный принтер, '
             'бесплатный личный шкафчик, книги.'),
            ('Для турагентов', '350',
             'Ежемесячное членство: все возможности резидентов, лицензия для работы, финансовые, '
             'юридические и организационные услуги, готовые заказы.'),
        ],
        'galereya': ('Фотогалерея Makon: рабочий зал, кофейный уголок, книжная полка и другие места '
                     'коворкинга в центре Ташкента. Улица Лашкарбеги, 11.'),
    },
    'en': {
        'description': 'A coworking space in central Tashkent: your own dedicated desk, a calm atmosphere, coffee and books.',
        'street': '11 Lashkarbegi Street, Akai City residential complex, 2nd floor',
        'city': 'Tashkent',
        'amenities': ['Computers', 'Wi-Fi', 'Free printer', 'Free personal locker', 'Parking', 'Dedicated desk'],
        'payment': 'QR code (UzQR); cash is not accepted',
        'unit': 'month',
        'offers': [
            ('For Makon residents', '250',
             'Monthly membership: a dedicated desk, computers, Wi-Fi, a free printer, a free personal locker, books.'),
            ('For travel agents', '350',
             'Monthly membership: everything residents get, a licence to operate, financial, legal and '
             'organisational services, ready client requests.'),
        ],
        'galereya': ('Makon photo gallery: the work hall, coffee corner, bookshelf and other spaces of a '
                     'coworking space in central Tashkent. 11 Lashkarbegi Street.'),
    },
}


def page_url(lang, page):
    prefix = '' if lang == 'uz' else lang + '/'
    return DOMAIN + prefix + ('' if page == 'index.html' else page)


def local_business(lang):
    t = TIL[lang]
    d = {
        '@context': 'https://schema.org',
        '@type': 'LocalBusiness',
        '@id': BIZ_ID,
        'name': 'Makon Coworking',
        'alternateName': ['Makon', 'Makon kovorking', 'Коворкинг Makon'],
        'description': t['description'],
        'url': page_url(lang, 'index.html'),
        'image': FAKTLAR['image'],
        'logo': FAKTLAR['logo'],
        'telephone': FAKTLAR['telephone'],
        'address': {
            '@type': 'PostalAddress',
            'streetAddress': t['street'],
            'addressLocality': t['city'],
            'addressCountry': 'UZ',
        },
        'geo': FAKTLAR['geo'],
        'openingHoursSpecification': FAKTLAR['openingHoursSpecification'],
        'sameAs': FAKTLAR['sameAs'],
        'hasMap': FAKTLAR['hasMap'],
        'priceRange': FAKTLAR['priceRange'],
        'paymentAccepted': t['payment'],
        'amenityFeature': [{'@type': 'LocationFeatureSpecification', 'name': a, 'value': True}
                           for a in t['amenities']],
        'makesOffer': [{
            '@type': 'Offer',
            'name': name,
            'description': desc,
            'url': page_url(lang, 'azolik.html'),
            'price': price,
            'priceCurrency': 'USD',
            'priceSpecification': {
                '@type': 'UnitPriceSpecification',
                'price': price,
                'priceCurrency': 'USD',
                'unitText': t['unit'],
            },
        } for name, price, desc in t['offers']],
    }
    return d


def website(lang):
    return {
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        '@id': SITE_ID,
        'url': DOMAIN,
        'name': 'Makon Coworking',
        'alternateName': ['Makon', 'Makon kovorking'],
        'inLanguage': ['uz', 'ru', 'en'],
        'publisher': {'@id': BIZ_ID},
    }


# ---- "Makon hayotida" maqolalari (BlogPosting) ----
MAQOLALAR = {
    'maqola-syomka-19-noyabr.html': {
        'date': '2026-11-21',
        'image': DOMAIN + 'assets/maqola-syomka-zilola.jpg',
        'uz': ("Makonda syomka: «Turizm va turagentlik kursi» haqida videolar",
               "19-noyabr kuni Makonda Madina Central Asia'ning Instagram sahifasi uchun videolar suratga olindi. "
               "Videolarda Makonda o'tadigan «Turizm va turagentlik kursi» haqida ma'lumot beriladi."),
        'ru': ("Съёмка в Makon: видео о «Курсе туризма и турагентского дела»",
               "19 ноября в Makon снимали видео для Instagram-страницы Madina Central Asia. "
               "В них рассказывают о «Курсе туризма и турагентского дела», который проходит в Makon."),
        'en': ("Filming at Makon: videos about the Tourism and Travel Agency Course",
               "On 19 November, videos for Madina Central Asia's Instagram page were filmed at Makon. "
               "They give information about the Tourism and Travel Agency Course, which takes place at Makon."),
    },
}


def blog_posting(lang, page):
    m = MAQOLALAR[page]
    headline, desc = m[lang]
    return {
        '@context': 'https://schema.org',
        '@type': 'BlogPosting',
        'headline': headline,
        'description': desc,
        'datePublished': m['date'],
        'inLanguage': lang,
        'image': m['image'],
        'mainEntityOfPage': page_url(lang, page),
        'author': {'@type': 'Organization', 'name': 'Makon Coworking', 'url': DOMAIN},
        'publisher': {'@id': BIZ_ID},
        'about': {'@id': BIZ_ID},
    }


def ld_script(data, ident):
    body = json.dumps(data, ensure_ascii=False, indent=1)
    return '<script type="application/ld+json" id="%s">\n%s\n</script>\n' % (ident, body)


def apply(src, lang, page):
    # 1) eski belgilarni olib tashlash (qayta ishga tushirish uchun)
    src = re.sub(r'<link rel="canonical" href="[^"]*">\n', '', src)
    src = re.sub(r'<meta name="robots" content="[^"]*">\n', '', src)
    src = re.sub(r'<script type="application/ld\+json" id="ld-[a-z]+">.*?</script>\n', '', src, flags=re.S)
    # avvalgi id'siz LocalBusiness bloki (eski versiya)
    src = re.sub(r'<script type="application/ld\+json">(?:(?!</script>).)*"LocalBusiness"(?:(?!</script>).)*</script>\n?',
                 '', src, flags=re.S)

    # 2) canonical — har sahifa o'zining manziliga ishora qiladi
    src = src.replace('<meta name="theme-color"',
                      '<link rel="canonical" href="%s">\n<meta name="theme-color"' % page_url(lang, page), 1)

    # 3) rahmat sahifasi qidiruvda chiqmasin
    if page == 'rahmat.html':
        src = src.replace('<meta name="viewport" content="width=device-width, initial-scale=1">\n',
                          '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                          '<meta name="robots" content="noindex, follow">\n', 1)

    # 4) tuzilgan ma'lumotlar (JSON-LD)
    blocks = ''
    if page in ('index.html', 'aloqa.html'):
        blocks += ld_script(local_business(lang), 'ld-makon')
    if page == 'index.html':
        blocks += ld_script(website(lang), 'ld-sayt')
    if page in MAQOLALAR:
        blocks += ld_script(blog_posting(lang, page), 'ld-maqola')
    if blocks:
        src = src.replace('</head>', blocks + '</head>', 1)

    # 5) Fotogalereya — o'z tavsifi
    if page == 'galereya.html':
        desc = TIL[lang]['galereya'].replace('"', '&quot;')
        src = re.sub(r'<meta name="description" content="[^"]*">',
                     lambda m: '<meta name="description" content="%s">' % desc, src, count=1)
        src = re.sub(r'<meta property="og:description" content="[^"]*">',
                     lambda m: '<meta property="og:description" content="%s">' % desc, src, count=1)
    return src


SITEMAP_PAGES = ['index.html', 'makon.html', 'galereya.html', 'azolik.html',
                 'rezidentlar.html', 'hayot.html', 'aloqa.html'] + list(MAQOLALAR)  # rahmat.html — kirmaydi (noindex)


def page_images(site_dir, page):
    """Sahifadagi suratlar (assets/ ichidagi .jpg/.jpeg/.webp) — to'liq manzil bilan, takrorlarsiz.
    QR kod va logotip (.png) kirmaydi."""
    import os
    import re
    try:
        src = open(os.path.join(site_dir, page), encoding='utf-8').read()
    except OSError:
        return []
    found = []
    for m in re.finditer(r'<img\b[^>]*\bsrc="(assets/[^"]+\.(?:jpe?g|webp))"', src):
        url = DOMAIN + m.group(1)
        if url not in found:
            found.append(url)
    return found


def write_sitemap(site_dir, extra_urls=()):
    """sitemap.xml: har sahifa 3 tilda, hreflang bilan, lastmod — build ishga tushgan sana."""
    import datetime
    import os
    today = datetime.date.today().isoformat()
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
           'xmlns:xhtml="http://www.w3.org/1999/xhtml" '
           'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
    for page in SITEMAP_PAGES:
        images = page_images(site_dir, page)
        for lang in ('uz', 'ru', 'en'):
            out.append(' <url>')
            out.append('  <loc>%s</loc>' % page_url(lang, page))
            out.append('  <lastmod>%s</lastmod>' % today)
            for img in images:  # sahifadagi suratlar — rasm qidiruvi uchun
                out.append('  <image:image><image:loc>%s</image:loc></image:image>' % img)
            for alt in ('uz', 'ru', 'en'):
                out.append('  <xhtml:link rel="alternate" hreflang="%s" href="%s"/>' % (alt, page_url(alt, page)))
            out.append('  <xhtml:link rel="alternate" hreflang="x-default" href="%s"/>' % page_url('uz', page))
            out.append(' </url>')
    for url in extra_urls:  # masalan, kelajakdagi maqolalar
        out.append(' <url>\n  <loc>%s</loc>\n  <lastmod>%s</lastmod>\n </url>' % (url, today))
    out.append('</urlset>')
    open(os.path.join(site_dir, 'sitemap.xml'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
