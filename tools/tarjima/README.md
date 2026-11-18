# Tarjima (ru/, en/)

O'zbekcha sahifalar asosiy. Rus va ingliz sahifalari ulardan yasaladi.

1. O'zbekcha sahifani o'zgartiring.
2. Yangi matnlar bo'lsa: `python3 tools/tarjima/extract.py` (strings.json yangilanadi, ishga tushirishdan oldin skriptdagi yo'llarni tekshiring) va `tr.py` ga shu tartibda tarjimasini qo'shing.
3. `python3 tools/tarjima/build.py .` — ru/ va en/ qayta yasaladi, til almashtirgich va hreflang qo'yiladi.
