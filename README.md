# ⌨️ Tezyoz (TypeMaster)

Windows uchun minimalist, oflayn rejimda ishlovchi professional tez terish trenajyori.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-orange.svg)](https://microsoft.com)
[![Tests: 194 Passed](https://img.shields.io/badge/Tests-194%20Passed-brightgreen.svg)](tests/)

---

## 💡 Concept & Values

**Tezyoz** – internet aloqasini talab qilmaydigan (100% lokal), Monkeytype dizaynidan andoza olgan kompyuterda tez yozish simulyatoridir. Dastur foydalanuvchining klaviatura mahoratini oshirish, kunlik motivatsiyani ko'taruvchi XP daraja tizimi, zaif tugmalarni aniqlovchi **Aqlli Mashq (Smart Adaptive Practice)** va batafsil jismoniy klaviatura barmoq yordamchisini taqdim etadi.

---

## ⚡ Asosiy Imkoniyatlar (Key Features)

| Funksiya | Natija / Imkoniyati | Texnik yechim |
| :--- | :--- | :--- |
| **Aqlli Mashq (Smart Adaptive)** | Foydalanuvchi ko'p xato qiladigan tugmalarni tahlil qilib, unga moslashtirilgan aqlli matn mashqini yaratadi | Multi-key error frequency analyzer & generator |
| **Uch Tilli i18n Interfeys** | O'zbek (`uz`), Ingliz (`en`) va Rus (`ru`) tillarida to'liq interfeys, sozlamalar va bildirishnomalar | Dynamic i18n translation service |
| **Visual Hands Tutor** | Real vaqtda qaysi barmoq va klavishni bosish kerakligini interaktiv ko'rsatish | Tkinter Canvas yordamida qo'llar simulyatsiyasi |
| **JCUKEN & QWERTY Qo'llab-quvvatlash** | Mashq darsida klaviatura tugmalarini dinamik ruscha JCUKENga hamda lotincha QWERTYga o'tkazish | Kirill/Lotin harf-jismoniy klavish xaritalash algoritmi |
| **Event Bus Arxitekturasi** | Event-driven UI va xizmatlar o'rtasida bo'sh bog'liqlik (decoupling) | Centralized EventBus pattern (`app/event_bus.py`) |
| **3x3 Results Grid** | Net WPM, Raw WPM, Aniqlik, Ritm va Jami bosilgan belgilar doimo aniq tartibda | Symmetrik 3x3 to'rli Natijalar paneli |
| **Off-line Analytics** | Yutuqlar chiziqli grafigi, foydalanish vaqti, zaif klavishlar issiqlik diagrammasi | Line/Bar charts & Interactive Heatmap Canvas |
| **Gamification Core** | XP yig'ish, darajalar (Level) oshishi, streak hisobi va kunlik topshiriqlar paneli | SQLite & Local progressive formulas |

> 🔑 **Xavfsizlik:** PBKDF2-HMAC-SHA256 (100k iteratsiya) algoritmi yordamida parollar lokal shifrlanadi.
> 🔊 **Auditoriya va Ovoz:** SoundService orqali dinamik audio toggle va tovush effektlari sozlamalari.

---

## 🛠️ Tizim Arxitekturasi (System Engine)

Tezyoz modulli, oson kengayuvchi va unit-testlashga qulay **Layered & Event-Driven Architecture** arxitekturasida yozilgan:

```mermaid
graph LR
    UI[GUI qatlami] -->|Events| EventBus[Event Bus Engine]
    EventBus -->|Publish/Subscribe| Services[Biznes mantiq qatlami]
    Services -->|Repos| DB[Lokal SQL Repozitoriy]
    DB -->|SQL3| Data[(typemaster.db)]
```

### Papka Tuzilishi
- `app/` — Dasturning GUI boshlang'ich nuqtasi (`application.py`), `event_bus.py` va sozlamalar.
- `database/` — Ma'lumotlar bazasi relyatsion sxemasi (`schema.py`) hamda repository klasterlari.
- `services/` — Auth seansi, i18n tarjima xizmati (`i18n_service.py`), ovoz (`sound_service.py`), fayl parserlar.
- `engine/` — WPM / Aniqlik hisoblagichlar hamda typing simulyator mashinasi.
- `ui/` — Ekranga yuklanadigan visual CustomTkinter/Tkinter darchalari, jumladan `keyboard_visualizer.py`.
- `charts/` — Canvas yordamida chizilgan progress jadvallari, heatmap rendereri.
- `tests/` — Loyiha ishonchliligini ta'minlovchi 194 ta to'liq avtomatlashtirilgan unit-testlar.

---

## 🚀 Texnik O'rnatish va Sozlash (Run Deck)

### Minimal Talablar:
- Windows 8 / 10 / 11.
- Python 3.8+ versiyasi.

### Bosqichma-bosqich yuritish:

```powershell
# 1. Loyihani yuklab oling (Clone)
git clone https://github.com/Valijon21/Tezyoz.git
cd Tezyoz

# 2. Virtual muhitni tayyorlang va ishga tushiring
python -m venv .venv
.venv\Scripts\Activate.ps1

# 3. Kerakli kutubxonalarni yuklang
pip install -r requirements.txt

# 4. Dasturni ishga tushiring
python main.py
```

### 🚦 Test Verifikatsiyasi

Dasturning barcha visual va logic qismlari 194 ta avtomatlashtirilgan testlar to'plami bilan to'liq qoplangan:

```powershell
pytest
```

---

## 👥 Mualliflar

- **Dastur Muallifi:** Valijon Ergashev
- **Bog'lanish:** [+998 (77) 342-33-21](tel:+998773423321)

---

## 📄 Litsenziya
Ushbu dastur MIT Litsenziyasi ostida ochiq manba etib belgilangan.
