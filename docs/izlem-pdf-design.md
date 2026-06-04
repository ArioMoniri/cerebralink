# CerebraLink: Izlem Brief PDF Design System v2

## Current State (Problems)

Based on review of `izlem_brief_13025094_20260413_052519.pdf`:

1. **Cold clinical blue** — `#1e3a5f` headers feel like a hospital IT system, not a premium report
2. **Page 4 artifacts** — Colored horizontal bars/blocks on the last page (PyMuPDF Story overflow)
3. **No visual warmth** — All-white background with thin borders; no texture or depth
4. **Flat hierarchy** — Section headers look identical; alerts don't stand out enough
5. **Tables too plain** — Thin gray borders, no differentiation for abnormal values
6. **No brand identity** — No logo area, no consistent footer, no "CerebraLink" visual signature
7. **Turkish text renders OK** — but Inter font may not be loading in Docker (fallback to sans-serif)

## Design Philosophy

**"Clinical clarity meets editorial elegance."**

Think: a beautifully typeset medical journal, not a hospital form. Every page should be scannable in 3 seconds with warm earth tones that reduce eye strain during long shifts.

---

## Color Palette — Warm Earth Tones

### Primary Palette

| Role | Name | Hex | Usage |
|------|------|-----|-------|
| **Text Primary** | Warm Charcoal | `#2D2926` | Body text, headings |
| **Section Banner** | Terracotta | `#C4704B` | Major section headers (bg) |
| **Accent** | Deep Teal | `#2A6F6F` | Subsection titles, links, icons |
| **Alert Critical** | Warm Coral | `#D4534B` | Critical alerts, abnormal values |
| **Alert Warning** | Golden Sand | `#D4A03C` | Warnings, attention items |
| **Success/Normal** | Sage Green | `#6B8F71` | Normal values, checkmarks |
| **Page Background** | Warm Cream | `#FAF7F2` | Page body |
| **Card Surface** | Linen | `#F0EBE3` | Card backgrounds, alternating rows |
| **Muted Text** | Warm Gray | `#9C9590` | Timestamps, labels, secondary |
| **Divider** | Sandy Beige | `#DDD5CA` | Borders, table rules |

### Accent Palette (Condition Severity)

| Severity | Color | Hex | Usage |
|----------|-------|-----|-------|
| Active/Urgent | Coral | `#D4534B` | Active problems, critical labs |
| Monitoring | Amber | `#D4A03C` | Watch items, borderline values |
| Stable | Teal | `#2A6F6F` | Stable conditions, improving trends |
| Resolved | Sage | `#6B8F71` | Resolved conditions, normal values |
| Informational | Warm Gray | `#9C9590` | Background info, metadata |

---

## Typography — Inter Font Family

| Element | Weight | Size | Color | Notes |
|---------|--------|------|-------|-------|
| **Report Title** | 700 Bold | 22pt | `#2D2926` | Top of page 1 only |
| **Subtitle** | 400 Regular | 11pt | `#C4704B` | "Gunluk Klinik Izlem Ozeti" |
| **Section Banner** | 600 SemiBold | 13pt | `#FFFFFF` | White on terracotta bg |
| **Subsection Title** | 600 SemiBold | 11pt | `#2A6F6F` | With left accent border |
| **Body Text** | 400 Regular | 9.5pt | `#2D2926` | Main content |
| **Table Header** | 600 SemiBold | 8.5pt | `#2D2926` | Uppercase, letterspaced |
| **Table Cell** | 400 Regular | 8.5pt | `#2D2926` | Standard data |
| **Alert Title** | 700 Bold | 10pt | varies | Matches alert color |
| **Alert Body** | 400 Regular | 9pt | `#2D2926` | Alert description |
| **Footer** | 400 Regular | 7pt | `#9C9590` | Page numbers, disclaimers |
| **Badge/Tag** | 600 SemiBold | 7.5pt | varies | ICD codes, status tags |
| **Meta/Label** | 500 Medium | 8pt | `#9C9590` | Timestamps, field labels |

---

## CSS Implementation

```css
@page {
  size: A4;
  margin: 18mm 16mm 20mm 16mm;
  background: #FAF7F2;
}

body {
  font-family: "Inter", "InterBold", sans-serif;
  font-size: 9.5px;
  color: #2D2926;
  line-height: 1.55;
  background: #FAF7F2;
}

/* ── Report Title ── */
h1 {
  font-family: "InterBold";
  font-size: 22px;
  color: #2D2926;
  margin: 0 0 2px 0;
  font-weight: 700;
  letter-spacing: -0.03em;
}

.report-subtitle {
  font-size: 11px;
  color: #C4704B;
  margin-bottom: 6px;
  font-weight: 400;
}

.report-meta {
  font-size: 9px;
  color: #9C9590;
  margin-bottom: 4px;
}

/* ── Patient Identity Card (Hero) ── */
.patient-card {
  background: linear-gradient(135deg, #F0EBE3 0%, #FAF7F2 100%);
  border: 1.5px solid #DDD5CA;
  border-left: 5px solid #C4704B;
  border-radius: 8px;
  padding: 14px 18px;
  margin: 12px 0 16px 0;
}

.patient-name {
  font-family: "InterBold";
  font-size: 16px;
  color: #2D2926;
  font-weight: 700;
  margin-bottom: 6px;
}

.patient-meta-row {
  display: flex;
  gap: 16px;
  font-size: 9px;
  color: #9C9590;
}

.patient-meta-row b {
  color: #2D2926;
  font-family: "InterBold";
}

.allergy-alert {
  background: rgba(212, 83, 75, 0.08);
  border: 1px solid rgba(212, 83, 75, 0.3);
  border-radius: 6px;
  padding: 6px 12px;
  margin-top: 10px;
  font-size: 9px;
  color: #D4534B;
  font-family: "InterBold";
  font-weight: 700;
}

/* ── Section Banners ── */
h2, .section-banner {
  background: linear-gradient(90deg, #C4704B 0%, #B86040 100%);
  color: #FFFFFF;
  font-family: "InterBold";
  font-weight: 700;
  font-size: 12px;
  padding: 8px 16px;
  margin: 16px 0 10px 0;
  border-radius: 6px;
  letter-spacing: 0.02em;
  border: none;
}

.section-banner-alert {
  background: linear-gradient(90deg, #D4534B 0%, #C4443C 100%);
  color: #FFFFFF;
  font-family: "InterBold";
  font-weight: 700;
  font-size: 12px;
  padding: 8px 16px;
  margin: 16px 0 10px 0;
  border-radius: 6px;
}

.section-banner-accent {
  background: linear-gradient(90deg, #2A6F6F 0%, #236060 100%);
  color: #FFFFFF;
  font-family: "InterBold";
  font-weight: 700;
  font-size: 12px;
  padding: 8px 16px;
  margin: 16px 0 10px 0;
  border-radius: 6px;
}

/* ── Subsections ── */
h3 {
  font-family: "InterBold";
  font-size: 11px;
  color: #2A6F6F;
  margin: 12px 0 4px 0;
  font-weight: 700;
  padding-left: 10px;
  border-left: 3px solid #C4704B;
}

h4 {
  font-family: "InterMedium";
  font-size: 10px;
  color: #9C9590;
  margin: 6px 0 2px 0;
  font-weight: 500;
  font-style: italic;
}

/* ── Tables ── */
table {
  border-collapse: separate;
  border-spacing: 0;
  width: 100%;
  margin: 8px 0;
  border: 1px solid #DDD5CA;
  border-radius: 6px;
  overflow: hidden;
}

th {
  background: #F0EBE3;
  color: #2D2926;
  font-family: "InterBold";
  font-weight: 600;
  font-size: 8px;
  padding: 6px 10px;
  text-align: left;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #DDD5CA;
}

td {
  padding: 5px 10px;
  font-size: 8.5px;
  border-bottom: 1px solid #EDE8E0;
  color: #2D2926;
}

tr:nth-child(even) td { background: #FAF7F2; }
tr:nth-child(odd) td  { background: #FFFFFF; }

/* Abnormal values */
.value-high {
  color: #D4534B;
  font-family: "InterBold";
  font-weight: 700;
}

.value-low {
  color: #2A6F6F;
  font-family: "InterBold";
  font-weight: 700;
}

.value-normal {
  color: #6B8F71;
}

/* ── Alert Boxes ── */
.alert-critical {
  background: linear-gradient(135deg, rgba(212,83,75,0.07) 0%, rgba(212,83,75,0.03) 100%);
  border-left: 4px solid #D4534B;
  border: 1px solid rgba(212,83,75,0.25);
  border-left-width: 4px;
  padding: 8px 14px;
  margin: 8px 0;
  border-radius: 0 6px 6px 0;
  font-size: 9px;
  color: #2D2926;
  break-inside: avoid;
}

.alert-critical b,
.alert-critical strong {
  color: #D4534B;
}

.alert-warning {
  background: linear-gradient(135deg, rgba(212,160,60,0.07) 0%, rgba(212,160,60,0.03) 100%);
  border-left: 4px solid #D4A03C;
  border: 1px solid rgba(212,160,60,0.25);
  border-left-width: 4px;
  padding: 8px 14px;
  margin: 8px 0;
  border-radius: 0 6px 6px 0;
  font-size: 9px;
  color: #2D2926;
}

.alert-info {
  background: linear-gradient(135deg, rgba(42,111,111,0.06) 0%, rgba(42,111,111,0.02) 100%);
  border-left: 4px solid #2A6F6F;
  border: 1px solid rgba(42,111,111,0.2);
  border-left-width: 4px;
  padding: 8px 14px;
  margin: 8px 0;
  border-radius: 0 6px 6px 0;
  font-size: 9px;
  color: #2D2926;
}

/* ── Note Blocks ── */
.note-block {
  background: #FFFFFF;
  border: 1px solid #DDD5CA;
  border-left: 3px solid #C4704B;
  padding: 8px 14px;
  margin: 6px 0;
  border-radius: 0 6px 6px 0;
  font-size: 9px;
  break-inside: avoid;
}

.note-block-doctor {
  background: #FFFFFF;
  border: 1px solid #DDD5CA;
  border-left: 4px solid #2A6F6F;
  padding: 8px 14px;
  margin: 6px 0;
  border-radius: 0 6px 6px 0;
  font-size: 9px;
}

.note-block-nurse {
  background: #FFFFFF;
  border: 1px solid #DDD5CA;
  border-left: 4px solid #6B8F71;
  padding: 8px 14px;
  margin: 6px 0;
  border-radius: 0 6px 6px 0;
  font-size: 9px;
}

/* ── Badges / Tags ── */
.badge {
  display: inline;
  background: #F0EBE3;
  color: #2A6F6F;
  padding: 1px 8px;
  border-radius: 10px;
  font-size: 7.5px;
  font-family: "InterBold";
  font-weight: 700;
  border: 1px solid #DDD5CA;
}

.badge-red {
  display: inline;
  background: rgba(212,83,75,0.1);
  color: #D4534B;
  padding: 1px 8px;
  border-radius: 10px;
  font-size: 7.5px;
  font-family: "InterBold";
  font-weight: 700;
  border: 1px solid rgba(212,83,75,0.3);
}

.badge-green {
  display: inline;
  background: rgba(107,143,113,0.1);
  color: #6B8F71;
  padding: 1px 8px;
  border-radius: 10px;
  font-size: 7.5px;
  font-family: "InterBold";
  font-weight: 700;
  border: 1px solid rgba(107,143,113,0.3);
}

/* ── Separator Lines ── */
.sep {
  border-top: 1.5px solid #DDD5CA;
  margin: 12px 0;
}

.sep-heavy {
  border-top: 2.5px solid #C4704B;
  margin: 14px 0;
}

/* ── Footer ── */
.footer {
  font-size: 7px;
  color: #9C9590;
  border-top: 1px solid #DDD5CA;
  padding-top: 6px;
  margin-top: 12px;
}

/* ── Misc ── */
code {
  background: #F0EBE3;
  padding: 1px 4px;
  border-radius: 3px;
  font-size: 8px;
  font-family: monospace;
  color: #2A6F6F;
}

.muted { color: #9C9590; font-size: 8.5px; font-style: italic; }
.small { font-size: 7.5px; color: #9C9590; }
.page-break { break-before: page; }

/* ── Highlight Boxes ── */
.highlight-box {
  background: rgba(196,112,75,0.06);
  border: 1.5px solid rgba(196,112,75,0.25);
  padding: 8px 12px;
  margin: 6px 0;
  border-radius: 6px;
  font-size: 9px;
}

.highlight-green {
  background: rgba(107,143,113,0.06);
  border: 1.5px solid rgba(107,143,113,0.25);
  padding: 8px 12px;
  margin: 6px 0;
  border-radius: 6px;
  font-size: 9px;
}
```

---

## Page Layout

### Page 1: Patient Overview

```
┌─────────────────────────────────────────────┐
│  Hasta Izlem Raporu                         │ ← Warm charcoal, 22pt
│  Gunluk Klinik Izlem Ozeti                  │ ← Terracotta, 11pt
│  Protokol No: XXXXX | Tarih: DD.MM.YYYY     │ ← Muted gray, 9pt
├─────────────────────────────────────────────┤
│                                             │
│  ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┐ │
│  │ PATIENT CARD                           │ │ ← Linen bg, terracotta left border
│  │ Name · Age · Gender · Department        │ │
│  │ Sorumlu Hekim: Dr. XXX                  │ │
│  │ ⚠ ALLERJI: ...                         │ │ ← Coral alert inside card
│  └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┘ │
│                                             │
│  ╔══ 1. Degerlendirme ═══════════════════╗  │ ← Terracotta banner
│  ║ Assessment paragraph...               ║  │
│  ╚═══════════════════════════════════════╝  │
│                                             │
│  ╔══ 2. Aktif Klinik Sorunlar ═══════════╗  │ ← Terracotta banner
│  ║ ▸ Problem 1 (date — dept)            ║  │ ← Teal subsection
│  ║   • Detail bullets                    ║  │
│  ║ ▸ Problem 2 (date — dept)            ║  │
│  ╚═══════════════════════════════════════╝  │
│                                             │
│  ───── CerebraLink · Protokol XXXXX ─────   │ ← Footer
│  Sayfa 1/4 — DD.MM.YYYY HH:MM              │
└─────────────────────────────────────────────┘
```

### Page 2: Medications & History

- Kronik Hastalik Arka Plani (table)
- Komorbiditeler ve Aktif Tani Listesi (checklist with badges)
- Surekli Kullanilan Ilaclar (medication table with indication column)

### Page 3: Alerts & Recommendations

- **⚠ Uyarilar** section (coral banner) with alert cards
- Konsultasyon Onerileri (bulleted list)
- Izlem ve Takip (monitoring table)

### Page 4: References

- Referanslar (clean bulleted list with URLs)
- Generation disclaimer
- **NO overflow artifacts** — enforce page break control

---

## Implementation Notes

### Preventing Page 4 Artifacts

The colored bar artifacts on page 4 are caused by PyMuPDF Story API creating overflow content that renders as colored blocks. Fix:

```python
# After generating PDF, remove trailing pages with artifacts
doc = fitz.open(pdf_path)
for i in range(len(doc) - 1, 0, -1):
    page = doc[i]
    text = page.get_text().strip()
    # If page has less than 30 chars of text, it's an artifact page
    if len(text) < 30:
        doc.delete_page(i)
    else:
        break
doc.save(pdf_path, incremental=True, encryption=fitz.PDF_ENCRYPT_NONE)
doc.close()
```

### Font Loading

Ensure Inter fonts are loaded in this order:
1. Project `fonts/inter/` directory
2. System font directories (`/usr/share/fonts`, `/usr/local/share/fonts`)
3. Fallback to DejaVu Sans (guaranteed available in most Docker images)

### WeasyPrint Migration (Future)

When migrating to WeasyPrint:
1. HTML template with Jinja2 uses same CSS from this spec
2. `@page` rules handle headers/footers natively
3. `break-inside: avoid` prevents split cards
4. `@font-face` loads Inter from project fonts
5. No Story API artifacts possible

---

## Quality Checklist

- [ ] Warm cream background (`#FAF7F2`) not white
- [ ] Terracotta section banners, not blue
- [ ] Alert cards with left-border color coding
- [ ] No page 4 colored bar artifacts
- [ ] Abnormal lab values in coral with bold
- [ ] Tables with rounded corners and alternating warm-cream rows
- [ ] Turkish characters (ş, ç, ö, ü, ı, İ, ğ, Ğ) render correctly
- [ ] Allergy alert impossible to miss
- [ ] Footer on every page with page number
- [ ] No orphaned/widowed lines
- [ ] PDF under 2MB
