# -*- coding: utf-8 -*-
"""Makon sayti: rus (ru/) va ingliz (en/) sahifalarini o'zbekcha asl sahifalardan yasaydi,
hamma sahifalarga til almashtirgich, hreflang va formaga "til" maydonini qo'shadi.
O'zbekcha matnlar o'zgarmaydi. Qayta ishga tushirsa bo'ladi (o'zbekcha sahifalar o'zgarishlari takrorlanmaydi)."""
import html, json, re, sys, os

SITE = sys.argv[1]
WORK = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WORK)
from tr import T

STR = json.load(open(os.path.join(WORK, 'strings.json'), encoding='utf-8'))
assert len(STR) == len(T), (len(STR), len(T))
MAP = {'ru': {}, 'en': {}}
for s, (ru, en) in zip(STR, T):
    MAP['ru'][s] = ru if ru is not None else s
    MAP['en'][s] = en if en is not None else s

PAGES = ['index.html', 'makon.html', 'galereya.html', 'azolik.html',
         'rezidentlar.html', 'hayot.html', 'aloqa.html', 'rahmat.html']
DOMAIN = 'https://makoncoworking.uz/'
LANGS = ['uz', 'ru', 'en']
LABEL = {'uz': 'Til', 'ru': 'Язык', 'en': 'Language'}
ATTRS = ['placeholder', 'alt', 'title', 'aria-label', 'content']


def page_url(lang, page):
    prefix = '' if lang == 'uz' else lang + '/'
    return DOMAIN + prefix + ('' if page == 'index.html' else page)


def rel_link(cur, target, page):
    """cur tildagi sahifadan target tildagi o'sha sahifaga nisbiy havola."""
    name = '' if page == 'index.html' else page
    if cur == 'uz':
        base = target + '/'
    elif target == 'uz':
        base = '../'
    else:
        base = '../' + target + '/'
    return (base + name) or './'


def switcher(cur, page):
    items = []
    for lg in LANGS:
        if lg == cur:
            items.append('<span aria-current="true" style="padding: 8px 10px; border-radius: 999px; background: #FFFFFF; color: #2B211B">%s</span>' % lg.upper())
        else:
            items.append('<a href="%s" hreflang="%s" lang="%s" style="padding: 8px 10px; border-radius: 999px; color: #5A4A3F; text-decoration: none">%s</a>'
                         % (rel_link(cur, lg, page), lg, lg, lg.upper()))
    return ('<div class="til" role="group" aria-label="%s" style="display: flex; align-items: center; gap: 2px; padding: 4px; border-radius: 999px; background: #F7EFE5; font-size: 13px; font-weight: 700; letter-spacing: 0.02em">%s</div>\n'
            % (LABEL[cur], ''.join(items)))


def hreflang(page):
    out = ''.join('<link rel="alternate" hreflang="%s" href="%s">\n' % (lg, page_url(lg, page)) for lg in LANGS)
    out += '<link rel="alternate" hreflang="x-default" href="%s">\n' % page_url('uz', page)
    return out


def tr_text(seg, m):
    def rep(mo):
        raw = mo.group(1)
        key = re.sub(r'\s+', ' ', html.unescape(raw)).strip()
        if not key or key not in m:
            return mo.group(0)
        lead = raw[:len(raw) - len(raw.lstrip())]
        trail = raw[len(raw.rstrip()):]
        return '>' + lead + html.escape(m[key], quote=False) + trail + '<'
    seg = re.sub(r'>([^<]+)<', rep, seg)

    def rep_attr(mo):
        name, val = mo.group(1), mo.group(2)
        key = html.unescape(val).strip()
        if key in m:
            return '%s="%s"' % (name, html.escape(m[key], quote=True).replace('&#x27;', "'"))
        return mo.group(0)
    seg = re.sub(r'\b(%s)="([^"]*)"' % '|'.join(ATTRS), rep_attr, seg)
    return seg


def translate(src, lang):
    m = MAP[lang]
    parts = re.split(r'(<script\b.*?</script>|<style\b.*?</style>)', src, flags=re.S)
    for i in range(0, len(parts), 2):
        parts[i] = tr_text(parts[i], m)
    return ''.join(parts)


def common(src, lang, page):
    # til almashtirgich (bir marta)
    src = re.sub(r'<div class="til".*?</div>\n', '', src, flags=re.S)
    src = re.sub(r'(</nav>\s*<div style="display: flex; align-items: center; gap: 8px">\n)',
                 lambda mo: mo.group(1) + switcher(lang, page), src, count=1)
    # hreflang (bir marta)
    src = re.sub(r'<link rel="alternate" hreflang="[^"]+" href="[^"]+">\n', '', src)
    src = src.replace('<meta name="theme-color"', hreflang(page) + '<meta name="theme-color"', 1)
    # formadagi til maydoni
    src = re.sub(r'<input type="hidden" name="til" value="[a-z]+">', '', src)
    src = re.sub(r'(<input type="text" name="_honey"[^>]*>)',
                 lambda mo: mo.group(1) + '<input type="hidden" name="til" value="%s">' % lang, src)
    return src


def build_lang(src, lang, page):
    if page == 'rezidentlar.html':
        if lang == 'ru':
            src = re.sub(r'Makon (<span[^>]*>)rezidentlari(</span>)', r'Резиденты \1Makon\2', src)
        else:
            src = re.sub(r'Makon (<span[^>]*>)rezidentlari(</span>)', r'Makon \1residents\2', src)
    if page == 'hayot.html':
        if lang == 'ru':
            src = re.sub(r'Makon (<span[^>]*>)hayotida(</span>)', r'Жизнь \1Makon\2', src)
        else:
            src = re.sub(r'Makon (<span[^>]*>)hayotida(</span>)', r'Life at \1Makon\2', src)
    src = translate(src, lang)
    src = src.replace('<html lang="uz">', '<html lang="%s">' % lang, 1)
    src = re.sub(r'<meta property="og:url" content="[^"]*">',
                 '<meta property="og:url" content="%s">' % page_url(lang, page), src, count=1)
    src = src.replace('src="assets/', 'src="../assets/').replace('href="assets/', 'href="../assets/')
    btn = {'ru': ("'Отправляем...'", "'Отправить ещё раз'"), 'en': ("'Sending...'", "'Send again'")}[lang]
    src = src.replace("'Yuborilmoqda...'", btn[0]).replace("'Qayta yuborish'", btn[1])
    return common(src, lang, page)


left = {}
for page in PAGES:
    path = os.path.join(SITE, page)
    uz = open(path, encoding='utf-8').read()
    uz_clean = re.sub(r'<div class="til".*?</div>\n', '', uz, flags=re.S)
    uz_clean = re.sub(r'<link rel="alternate" hreflang="[^"]+" href="[^"]+">\n', '', uz_clean)
    uz_clean = re.sub(r'<input type="hidden" name="til" value="[a-z]+">', '', uz_clean)
    open(path, 'w', encoding='utf-8').write(common(uz_clean, 'uz', page))
    for lang in ('ru', 'en'):
        out = build_lang(uz_clean, lang, page)
        os.makedirs(os.path.join(SITE, lang), exist_ok=True)
        open(os.path.join(SITE, lang, page), 'w', encoding='utf-8').write(out)
print('ok')
