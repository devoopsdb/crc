#!/usr/bin/env python3
"""Generate and compile translation catalogs for CRC without GNU gettext.

Single source of truth: the TRANSLATIONS dict below maps each English msgid
to its Azerbaijani / Russian / Turkish rendering. Running this script writes
locale/<lang>/LC_MESSAGES/django.po (committed source) and django.mo (compiled,
gitignored) for each language.

Usage:  uv run python tools/make_translations.py
"""
import struct
from pathlib import Path

LOCALE = Path(__file__).resolve().parent.parent / "locale"

# msgid -> {"az": ..., "ru": ..., "tr": ...}
# English msgids are the lookup keys; en falls back to the msgid itself.
TRANSLATIONS: dict[str, dict[str, str]] = {
    # ---- Navigation / chrome ----
    "Cable Reels Calculator": {"az": "Kabel Baraban Kalkulyatoru", "ru": "Калькулятор кабельных барабанов", "tr": "Kablo Makara Hesaplayıcı"},
    "Navigation": {"az": "Naviqasiya", "ru": "Навигация", "tr": "Gezinme"},
    "Calculation": {"az": "Hesablama", "ru": "Расчёт", "tr": "Hesaplama"},
    "New calculation": {"az": "Yeni hesablama", "ru": "Новый расчёт", "tr": "Yeni hesaplama"},
    "Calculation history": {"az": "Hesablama tarixçəsi", "ru": "История расчётов", "tr": "Hesaplama geçmişi"},
    "Reference data": {"az": "Məlumat bazası", "ru": "Справочные данные", "tr": "Referans veriler"},
    "Reel list": {"az": "Baraban siyahısı", "ru": "Список барабанов", "tr": "Makara listesi"},
    "Transport list": {"az": "Nəqliyyat siyahısı", "ru": "Список транспорта", "tr": "Taşıma listesi"},
    "Language": {"az": "Dil", "ru": "Язык", "tr": "Dil"},
    "Toggle navigation": {"az": "Naviqasiyanı aç/bağla", "ru": "Переключить навигацию", "tr": "Gezinmeyi aç/kapat"},
    "Toggle light/dark theme": {"az": "Açıq/qaranlıq mövzunu dəyiş", "ru": "Переключить светлую/тёмную тему", "tr": "Açık/koyu temayı değiştir"},
    "Close": {"az": "Bağla", "ru": "Закрыть", "tr": "Kapat"},
    # ---- Common actions ----
    "Back": {"az": "Geri", "ru": "Назад", "tr": "Geri"},
    "Delete": {"az": "Sil", "ru": "Удалить", "tr": "Sil"},
    "Cancel": {"az": "Ləğv et", "ru": "Отмена", "tr": "İptal"},
    "Save": {"az": "Yadda saxla", "ru": "Сохранить", "tr": "Kaydet"},
    "Calculate": {"az": "Hesabla", "ru": "Рассчитать", "tr": "Hesapla"},
    "Add line": {"az": "Sətir əlavə et", "ru": "Добавить строку", "tr": "Satır ekle"},
    "Add reel": {"az": "Baraban əlavə et", "ru": "Добавить барабан", "tr": "Makara ekle"},
    "Add transport": {"az": "Nəqliyyat əlavə et", "ru": "Добавить транспорт", "tr": "Taşıma ekle"},
    "Remove": {"az": "Çıxar", "ru": "Удалить", "tr": "Kaldır"},
    "Remove line": {"az": "Sətiri sil", "ru": "Удалить строку", "tr": "Satırı kaldır"},
    # ---- Calculation form / inputs ----
    "Order number": {"az": "Sifarişin nömrəsi", "ru": "Номер заказа", "tr": "Sipariş numarası"},
    "Transport": {"az": "Nəqliyyat", "ru": "Транспорт", "tr": "Taşıma"},
    "Winding margin override": {"az": "Sarım kənarının dəyişimi", "ru": "Переопределение зазора намотки", "tr": "Sarım boşluğu geçersiz kılma"},
    "Packing factor override": {"az": "Dolu faktorunun dəyişimi", "ru": "Переопределение коэф. заполнения", "tr": "Doluluk faktörü geçersiz kılma"},
    "Cable lines": {"az": "Kabel sətirləri", "ru": "Строки кабеля", "tr": "Kablo satırları"},
    "Cable code": {"az": "Kabelin kodu", "ru": "Код кабеля", "tr": "Kablo kodu"},
    "Cable name": {"az": "Kabelin adı", "ru": "Название кабеля", "tr": "Kablo adı"},
    "Order length, m": {"az": "Sifariş uzunluğu, m", "ru": "Длина заказа, м", "tr": "Sipariş uzunluğu, m"},
    "Mass, kg/m": {"az": "Kütlə, kq/m", "ru": "Масса, кг/м", "tr": "Kütle, kg/m"},
    "Diameter, mm": {"az": "Diametr, mm", "ru": "Диаметр, мм", "tr": "Çap, mm"},
    "Conductors": {"az": "Damar sayı", "ru": "Жилы", "tr": "İletkenler"},
    "Max length, m": {"az": "Maks. uzunluq, m", "ru": "Макс. длина, м", "tr": "Maks. uzunluk, m"},
    # ---- Results ----
    "Results per cable line": {"az": "Hər kabel sətri üçün nəticə", "ru": "Результаты по строкам кабеля", "tr": "Her kablo satırı için sonuç"},
    "Cable": {"az": "Kabel", "ru": "Кабель", "tr": "Kablo"},
    "Reel": {"az": "Baraban", "ru": "Барабан", "tr": "Makara"},
    "Length / reel, m": {"az": "Barabana uzunluq, m", "ru": "Длина/барабан, м", "tr": "Makara başına uzunluk, m"},
    "Reels": {"az": "Baraban sayı", "ru": "Барабаны", "tr": "Makaralar"},
    "Reel fill": {"az": "Baraban doluluğu", "ru": "Заполнение барабана", "tr": "Makara doluluğu"},
    "Netto 1, kg": {"az": "Netto 1, kq", "ru": "Нетто 1, кг", "tr": "Netto 1, kg"},
    "Brutto 1, kg": {"az": "Brutto 1, kq", "ru": "Брутто 1, кг", "tr": "Brutto 1, kg"},
    "Netto total, kg": {"az": "Netto ümumi, kq", "ru": "Нетто всего, кг", "tr": "Netto toplam, kg"},
    "Brutto total, kg": {"az": "Brutto ümumi, kq", "ru": "Брутто всего, кг", "tr": "Brutto toplam, kg"},
    "Bending, mm": {"az": "Əyilmə, mm", "ru": "Изгиб, мм", "tr": "Bükülme, mm"},
    "Status": {"az": "Status", "ru": "Статус", "tr": "Durum"},
    "OK": {"az": "OK", "ru": "ОК", "tr": "Tamam"},
    "No cable lines.": {"az": "Kabel sətirləri yoxdur.", "ru": "Нет строк кабеля.", "tr": "Kablo satırı yok."},
    "Cable inputs": {"az": "Kabel daxiletmələri", "ru": "Ввод кабеля", "tr": "Kablo girişleri"},
    "Line items": {"az": "Sətir sayı", "ru": "Строки", "tr": "Satır sayısı"},
    # ---- History ----
    "Date": {"az": "Tarix", "ru": "Дата", "tr": "Tarih"},
    "Lines": {"az": "Sətirlər", "ru": "Строки", "tr": "Satırlar"},
    "No calculations yet.": {"az": "Hesablama hələ yoxdur.", "ru": "Расчётов пока нет.", "tr": "Henüz hesaplama yok."},
    # ---- Reels ----
    "Name": {"az": "Ad", "ru": "Название", "tr": "Ad"},
    "Flange h, mm": {"az": "Çanaq h, mm", "ru": "Высота щеки, мм", "tr": "Yanak h, mm"},
    "Flange height, mm": {"az": "Çanaq hündürlüyü, mm", "ru": "Высота щеки, мм", "tr": "Yanak yüksekliği, mm"},
    "Width, mm": {"az": "En, mm", "ru": "Ширина, мм", "tr": "Genişlik, mm"},
    "Ø, mm": {"az": "Ø, mm", "ru": "Ø, мм", "tr": "Ø, mm"},
    "Core Ø, mm": {"az": "Boğaz Ø, mm", "ru": "Сердеч. Ø, мм", "tr": "Göbek Ø, mm"},
    "Barrel, mm": {"az": "Boğaz, mm", "ru": "Барабан, мм", "tr": "Gövde, mm"},
    "Type": {"az": "Növ", "ru": "Тип", "tr": "Tip"},
    "Mass, kg": {"az": "Kütlə, kq", "ru": "Масса, кг", "tr": "Kütle, kg"},
    "Max load, kg": {"az": "Maks. yükləmə, kq", "ru": "Макс. нагрузка, кг", "tr": "Maks. yük, kg"},
    "No reels yet.": {"az": "Baraban hələ yoxdur.", "ru": "Барабанов пока нет.", "tr": "Henüz makara yok."},
    "Core diameter, mm": {"az": "Boğaz diametri, mm", "ru": "Диаметр сердечника, мм", "tr": "Göbek çapı, mm"},
    "Barrel width, mm": {"az": "Boğaz eni, mm", "ru": "Ширина барабана, мм", "tr": "Gövde genişliği, mm"},
    "Reel type": {"az": "Baraban növü", "ru": "Тип барабана", "tr": "Makara tipi"},
    "Reel mass, kg": {"az": "Baraban çəkisi, kq", "ru": "Масса барабана, кг", "tr": "Makara kütlesi, kg"},
    "Delete reel": {"az": "Barabanı sil", "ru": "Удалить барабан", "tr": "Makarayı sil"},
    # ---- Transport ----
    "Height, mm": {"az": "Hündürlük, mm", "ru": "Высота, мм", "tr": "Yükseklik, mm"},
    "Length, mm": {"az": "Uzunluq, mm", "ru": "Длина, мм", "tr": "Uzunluk, mm"},
    "Transport name": {"az": "Nəqliyyat adı", "ru": "Название транспорта", "tr": "Taşıma adı"},
    "No transport yet.": {"az": "Nəqliyyat hələ yoxdur.", "ru": "Транспорта пока нет.", "tr": "Henüz taşıma yok."},
    "Delete transport": {"az": "Nəqliyyatı sil", "ru": "Удалить транспорт", "tr": "Taşımayı sil"},
    # ---- Delete confirmations (blocktrans with variables) ----
    "Delete calculation <strong>%(order)s</strong>? This cannot be undone.": {
        "az": "<strong>%(order)s</strong> hesablamasını silmək? Bu geri qaytarıla bilməz.",
        "ru": "Удалить расчёт <strong>%(order)s</strong>? Это действие необратимо.",
        "tr": "<strong>%(order)s</strong> hesaplamasını sil? Bu geri alınamaz."},
    "Delete reel <strong>%(name)s</strong>? This cannot be undone.": {
        "az": "<strong>%(name)s</strong> barabanını silmək? Bu geri qaytarıla bilməz.",
        "ru": "Удалить барабан <strong>%(name)s</strong>? Это действие необратимо.",
        "tr": "<strong>%(name)s</strong> makarasını sil? Bu geri alınamaz."},
    "Delete transport <strong>%(name)s</strong>? This cannot be undone.": {
        "az": "<strong>%(name)s</strong> nəqliyyatını silmək? Bu geri qaytarıla bilməz.",
        "ru": "Удалить транспорт <strong>%(name)s</strong>? Это действие необратимо.",
        "tr": "<strong>%(name)s</strong> taşımasını sil? Bu geri alınamaz."},
    # ---- View messages ----
    "Add at least one cable line.": {"az": "Ən azı bir kabel sətiri əlavə edin.", "ru": "Добавьте хотя бы одну строку кабеля.", "tr": "En az bir kablo satırı ekleyin."},
    "Row %(n)s: %(err)s": {"az": "Sətir %(n)s: %(err)s", "ru": "Строка %(n)s: %(err)s", "tr": "Satır %(n)s: %(err)s"},
    # ---- Model verbose names (admin + form labels) ----
    "Order": {"az": "Sifariş", "ru": "Заказ", "tr": "Sipariş"},
    "Orders": {"az": "Sifarişlər", "ru": "Заказы", "tr": "Siparişler"},
    "Reel name": {"az": "Baraban adı", "ru": "Название барабана", "tr": "Makara adı"},
    "Reel count": {"az": "Baraban sayı", "ru": "Кол-во барабанов", "tr": "Makara sayısı"},
    "Reel type name": {"az": "Baraban növünün adı", "ru": "Название типа барабана", "tr": "Makara tipi adı"},
    "Reel types": {"az": "Baraban növləri", "ru": "Типы барабанов", "tr": "Makara tipleri"},
    "Transports": {"az": "Nəqliyyatlar", "ru": "Транспорт", "tr": "Taşımalar"},
    "Winding margin (mm)": {"az": "Sarım kənarı (mm)", "ru": "Зазор намотки (мм)", "tr": "Sarım boşluğu (mm)"},
    "Winding margin override (mm)": {"az": "Sarım kənarının dəyişimi (mm)", "ru": "Переопр. зазора намотки (мм)", "tr": "Sarım boşluğu geçersiz kılma (mm)"},
    "Packing factor": {"az": "Dolu faktoru", "ru": "Коэф. заполнения", "tr": "Doluluk faktörü"},
    "Bending radius multiplier (x cable diameter)": {"az": "Əyilmə radiusu çarpanı (× kabel diametri)", "ru": "Множитель радиуса изгиба (× диаметр кабеля)", "tr": "Bükülme yarıçapı çarpanı (× kablo çapı)"},
    "Use flange height to bound winding": {"az": "Sarımı məhdudləşdirmək üçün çanaq hündürlüyünü istifadə et", "ru": "Ограничивать намотку высотой щеки", "tr": "Sarımı yanak yüksekliğiyle sınırla"},
    "Unwound margin per flange side.": {"az": "Hər çanaq tərəfindən sarılmayan kənar.", "ru": "Несмотанный зазор с каждой стороны щеки.", "tr": "Her yanak tarafında sarılmayan boşluk."},
    "Calculation settings": {"az": "Hesablama parametrləri", "ru": "Параметры расчёта", "tr": "Hesaplama ayarları"},
    "Cable line item": {"az": "Kabel sətiri", "ru": "Строка кабеля", "tr": "Kablo satırı"},
    "Cable line items": {"az": "Kabel sətirləri", "ru": "Строки кабеля", "tr": "Kablo satırları"},
    "Position": {"az": "Pozisiya", "ru": "Позиция", "tr": "Konum"},
    "Conductor count": {"az": "Damar sayı", "ru": "Кол-во жил", "tr": "İletken sayısı"},
    "Cable mass (kg/m)": {"az": "Kabel çəkisi (kq/m)", "ru": "Масса кабеля (кг/м)", "tr": "Kablo kütlesi (kg/m)"},
    "Cable outer diameter (mm)": {"az": "Kabelin xarici diametri (mm)", "ru": "Наружный диаметр кабеля (мм)", "tr": "Kablo dış çapı (mm)"},
    "Max production length (m)": {"az": "Maks. istehsalat uzunluğu (m)", "ru": "Макс. длина производства (м)", "tr": "Maks. üretim uzunluğu (m)"},
    "Chosen reel": {"az": "Seçilmiş baraban", "ru": "Выбранный барабан", "tr": "Seçili makara"},
    "Length per reel (m)": {"az": "Barabana düşən uzunluq (m)", "ru": "Длина на барабан (м)", "tr": "Makara başına uzunluk (m)"},
    "Netto 1 reel": {"az": "Netto 1 baraban", "ru": "Нетто 1 барабан", "tr": "Netto 1 makara"},
    "Brutto 1 reel": {"az": "Brutto 1 baraban", "ru": "Брутто 1 барабан", "tr": "Brutto 1 makara"},
    "Netto total": {"az": "Netto ümumi", "ru": "Нетто всего", "tr": "Netto toplam"},
    "Brutto total": {"az": "Brutto ümumi", "ru": "Брутто всего", "tr": "Brutto toplam"},
    "Netto 1 reel (kg)": {"az": "Netto 1 baraban (kq)", "ru": "Нетто 1 барабан (кг)", "tr": "Netto 1 makara (kg)"},
    "Brutto 1 reel (kg)": {"az": "Brutto 1 baraban (kq)", "ru": "Брутто 1 барабан (кг)", "tr": "Brutto 1 makara (kg)"},
    "Netto total (kg)": {"az": "Netto ümumi (kq)", "ru": "Нетто всего (кг)", "tr": "Netto toplam (kg)"},
    "Brutto total (kg)": {"az": "Brutto ümumi (kq)", "ru": "Брутто всего (кг)", "tr": "Brutto toplam (kg)"},
    "Bending radius": {"az": "Əyilmə radiusu", "ru": "Радиус изгиба", "tr": "Bükülme yarıçapı"},
    "Bending radius (mm)": {"az": "Əyilmə radiusu (mm)", "ru": "Радиус изгиба (мм)", "tr": "Bükülme yarıçapı (mm)"},
    "Warning": {"az": "Xəbərdarlıq", "ru": "Предупреждение", "tr": "Uyarı"},
    "Diameter (mm)": {"az": "Diametr (mm)", "ru": "Диаметр (мм)", "tr": "Çap (mm)"},
    "Width (mm)": {"az": "En (mm)", "ru": "Ширина (мм)", "tr": "Genişlik (mm)"},
    "Height (mm)": {"az": "Hündürlük (mm)", "ru": "Высота (мм)", "tr": "Yükseklik (mm)"},
    "Length (mm)": {"az": "Uzunluq (mm)", "ru": "Длина (мм)", "tr": "Uzunluk (mm)"},
    "Max load (kg)": {"az": "Maks. yükləmə (kq)", "ru": "Макс. нагрузка (кг)", "tr": "Maks. yük (kg)"},
    "Barrel width (mm)": {"az": "Boğaz eni (mm)", "ru": "Ширина барабана (мм)", "tr": "Gövde genişliği (mm)"},
    "Core diameter (mm)": {"az": "Boğaz diametri (mm)", "ru": "Диаметр сердечника (мм)", "tr": "Göbek çapı (mm)"},
    "Flange height (mm)": {"az": "Çanaq hündürlüyü (mm)", "ru": "Высота щеки (мм)", "tr": "Yanak yüksekliği (mm)"},
    "Reel mass (kg)": {"az": "Baraban çəkisi (kq)", "ru": "Масса барабана (кг)", "tr": "Makara kütlesi (kg)"},
    "Created at": {"az": "Yaradılma tarixi", "ru": "Создано", "tr": "Oluşturulma"},
    "Updated at": {"az": "Yenilənmə tarixi", "ru": "Обновлено", "tr": "Güncellenme"},
    "CRC — Cable Reels Calculator": {"az": "CRC — Kabel Baraban Kalkulyatoru", "ru": "CRC — Калькулятор кабельных барабанов", "tr": "CRC — Kablo Makara Hesaplayıcı"},
}


PLURALS = {
    "az": "nplurals=2; plural=(n != 1);",
    "ru": "nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);",
    "tr": "nplurals=2; plural=(n != 1);",
}


def po_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def write_po(lang: str, entries: list[tuple[str, str]]) -> Path:
    path = LOCALE / lang / "LC_MESSAGES" / "django.po"
    path.parent.mkdir(parents=True, exist_ok=True)
    header = (
        'msgid ""\n'
        'msgstr ""\n'
        f'"Content-Type: text/plain; charset=UTF-8\\n"\n'
        f'"Language: {lang}\\n"\n'
        f'"Plural-Forms: {PLURALS[lang]}\\n"\n'
    )
    lines = [header]
    for msgid, msgstr in entries:
        lines.append(f'msgid "{po_escape(msgid)}"\n')
        lines.append(f'msgstr "{po_escape(msgstr)}"\n\n')
    path.write_text("".join(lines), encoding="utf-8")
    return path


def write_mo(lang: str, entries: list[tuple[str, str]]) -> Path:
    # Header entry first (empty msgid).
    all_entries = [("", _meta_header(lang))] + entries
    all_entries.sort(key=lambda e: e[0])  # empty msgid sorts first
    n = len(all_entries)
    orig = [m.encode("utf-8") for m, _ in all_entries]
    trans = [t.encode("utf-8") for _, t in all_entries]
    orig_off, trans_off = 28, 28 + 8 * n
    strings_off = 28 + 16 * n
    o_off, cur = [], strings_off
    for s in orig:
        o_off.append(cur); cur += len(s) + 1
    t_off = []
    for s in trans:
        t_off.append(cur); cur += len(s) + 1
    buf = struct.pack("<7I", 0x950412DE, 0, n, orig_off, trans_off, 0, strings_off)
    for i in range(n):
        buf += struct.pack("<II", len(orig[i]), o_off[i])
    for i in range(n):
        buf += struct.pack("<II", len(trans[i]), t_off[i])
    for s in orig:
        buf += s + b"\x00"
    for s in trans:
        buf += s + b"\x00"
    path = LOCALE / lang / "LC_MESSAGES" / "django.mo"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(buf)
    return path


def _meta_header(lang: str) -> str:
    return (
        "Content-Type: text/plain; charset=UTF-8\n"
        f"Language: {lang}\n"
        f"Plural-Forms: {PLURALS[lang]}\n"
    )


def main() -> None:
    for lang in ("az", "ru", "tr"):
        entries = [(msgid, t[lang]) for msgid, t in TRANSLATIONS.items()]
        po = write_po(lang, entries)
        mo = write_mo(lang, entries)
        print(f"{lang}: {len(entries)} strings -> {po.relative_to(LOCALE.parent)} + .mo")


if __name__ == "__main__":
    main()