# Planner21 Premium Dark Redesign — Design Spec

## Overview

Full visual redesign of the Planner21 Streamlit app from warm-brown serif aesthetic to a premium dark SaaS/trading-dashboard look. Includes breaking sub-pages out of planner21.py into top-level pages and consolidating all CSS into a shared theme module.

## Decisions

| Decision | Choice |
|----------|--------|
| Background | `#0d0d0d` (near-black) |
| Accent color | Electric blue `#00d4ff` |
| Positive/Negative | `#00e68a` / `#ff4d6a` |
| Display font | Syne (headers, titles) |
| Body font | DM Sans (body, data, inputs) |
| Mode | Dark only — remove light mode toggle |
| Sidebar | Collapsed icon rail, expands on hover via CSS |
| Navigation | Break History, Insights, AI Coach, Settings out of planner21.py into `pages/` |
| CSS strategy | Shared `theme.py` module — single source of truth |

---

## 1. Theme System (`theme.py`)

New file in project root. Exports:

- `inject_theme()` — injects full CSS via `st.markdown(..., unsafe_allow_html=True)`
- `inject_sidebar()` — sidebar-specific CSS overrides
- Constants for design tokens usable in Python-generated HTML

### Design Tokens

```
--bg-primary:       #0d0d0d
--bg-secondary:     #111111
--bg-card:          rgba(255,255,255,0.04)
--bg-card-hover:    rgba(255,255,255,0.07)
--accent:           #00d4ff
--accent-glow:      0 0 20px rgba(0,212,255,0.15)
--pos:              #00e68a
--neg:              #ff4d6a
--text-primary:     #f0f0f0
--text-secondary:   rgba(255,255,255,0.55)
--border:           1px solid rgba(255,255,255,0.06)
--glass:            backdrop-filter: blur(16px)
--radius-lg:        16px
--radius-md:        10px
--font-display:     'Syne', sans-serif
--font-body:        'DM Sans', sans-serif
```

### Google Fonts Import

```css
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:wght@400;500;700&display=swap');
```

### Glass-morphism Card

```css
.card {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 16px;
  backdrop-filter: blur(16px);
  padding: 24px;
  transition: all 0.3s ease;
}
.card:hover {
  background: rgba(255,255,255,0.07);
  border-color: rgba(0,212,255,0.2);
  box-shadow: 0 0 20px rgba(0,212,255,0.08);
}
```

### Typography Scale

| Element | Font | Size | Weight |
|---------|------|------|--------|
| Page title | Syne | 28px | 700 |
| Section header | Syne | 18px | 600 |
| Body text | DM Sans | 14px | 400 |
| Metric value | DM Sans | 36px | 700 |
| Label | DM Sans | 11px | 500, uppercase, 0.08em spacing |

### Buttons

- Default: transparent bg, `#00d4ff` border, 10px radius
- Hover: filled `#00d4ff` bg, dark text, subtle glow
- Transition: 0.25s ease

### Dividers

- `1px solid rgba(255,255,255,0.06)` — thin and elegant everywhere

---

## 2. Sidebar (Icon Rail)

CSS-only override of Streamlit's native sidebar:

- **Default**: ~70px wide, emoji icons only, vertically stacked
- **Hover**: expands to ~240px, reveals full page labels, slide transition
- **Background**: `#0a0a0a`
- **Active page**: electric blue left border + glow + blue text
- **Inactive pages**: `rgba(255,255,255,0.4)` text, brightens on hover
- **Top**: "M21" logo mark in Syne bold, blue glow
- **Bottom**: settings gear icon

Streamlit's native multi-page routing handles nav. We style `st.page_link` / sidebar radio elements via CSS.

---

## 3. Component Patterns

### Metric Cards (Trading-Dashboard Style)

- Label: 11px uppercase, `--text-secondary`, above number
- Value: 36px DM Sans bold, white or colored
- Sub-info: 13px `--text-secondary`, below number
- Glass card container with hover animation

### Detail Rows (Financial Breakdowns)

- Flexbox: label left, value right (`justify-content: space-between`)
- Thin bottom border separator
- Value colored by `.positive` / `.negative` class

### Progress Bars

- 4px height, rounded corners
- Track: `rgba(255,255,255,0.08)`
- Fill: `#00d4ff` with subtle glow
- Green variant for completion metrics

### Status Badges

- Pill-shaped, 11px uppercase
- Colored backgrounds at 15% opacity with matching text
- No emoji prefixes — clean text only

### Form Inputs

- Transparent background, bottom-border only (`1px rgba(255,255,255,0.15)`)
- Focus: bottom-border turns `#00d4ff`
- Labels: `--text-secondary`, 11px uppercase, above input

### Tables

- No visible cell borders
- Header: uppercase, 11px, `--text-secondary`, bottom border
- Body: alternating `rgba(255,255,255,0.02)` rows
- Hover: `rgba(255,255,255,0.05)` highlight

### Charts

- Transparent background
- Line/bar color: `#00d4ff`
- Grid: `rgba(255,255,255,0.05)`
- Axis labels: `--text-secondary`

---

## 4. Page Designs

### Planner (planner21.py) — Today Only

After breakout, this file contains only the Today view:

- **Hero metric**: Score at 48px, centered, circular radial progress ring (CSS)
- **3 execution pills**: Priorities / Run / Income — glow green when done
- **Daily entry form**: glass card, bottom-border inputs, clean spacing
- **Focus quote**: subtle card, italic Syne, low opacity

### Dashboard (dashboard.py)

- **Top row**: 3 large metric cards — Net, Exercise, Score — big numbers, small labels, sub-info
- **Rule banner**: thin accent-left-bordered card
- **2-column**: Financial breakdown + System Insights — glass cards, detail rows
- **Monthly overview**: horizontal progress bar (spend vs budget)

### Finance (finance.py)

- **Summary row**: 4 metric cards, big bold numbers
- **Input form**: sleek single-column glass card
- **Expense list**: clean rows, subtle separators, inline edit/delete icons
- **Budget alert**: thin red/amber top-border card (not `st.error`)

### Exercise (excercise.py)

- **Hero banner**: status icon + text + key metric
- **3 stat cards**: distance, time, total
- **Log form**: glass card, clean inputs
- **History**: clean table with alternating rows, blue trend chart

### Driving (driving.py)

- **2-column**: Input left, dashboard right
- **Dashboard**: big earnings number, hourly rate below, glowing target badge
- **Times**: digital-clock style display

### Journal (journal.py)

- **Entry form**: full-width glass card, large textarea
- **Past entries**: cards with faint date header, comfortable line-height

### News (news.py)

- **Section headers**: thin accent underline, Syne font
- **Article cards**: horizontal layout, glass card, hover lift

### Weekly Review (weekly_review.py)

- **4 metric cards**: Week Income, Expenses, Net, Avg Score
- **2-column**: Financial + Execution breakdowns — glass cards, detail rows
- **Day-by-day table**: styled rows, color-coded cells

---

## 5. New Pages (Broken Out)

### pages/history.py

Extracted from planner21.py. Score history with:
- Filter toggle (show only scored days)
- Glass history cards: date, progress bar, score, status badge
- 2-column: priorities + execution checkmarks
- Reflection text, delete button

### pages/insights.py

Extracted from planner21.py. Analytics view:
- 4-card stat grid (Days Logged, Perfect Days, Avg, Streak)
- Score trend line chart (blue on dark)
- 3-column habit cards with blue progress bars
- Streak cards
- Last 7 days table

### pages/ai_coach.py

Extracted from planner21.py. Chat interface:
- API key check
- Context builder (loads all CSV data)
- Dark chat bubbles, blue accent for user messages
- System prompt preserved

### pages/settings.py

Extracted from planner21.py. Settings form:
- Glass card container
- All current settings fields (goals, targets, budgets, checklist, categories)
- Save with backup

---

## 6. File Changes Summary

### New Files
| File | Purpose |
|------|---------|
| `theme.py` | Shared CSS + design tokens |
| `pages/history.py` | Score history (from planner21.py) |
| `pages/insights.py` | Analytics (from planner21.py) |
| `pages/ai_coach.py` | AI Coach chat (from planner21.py) |
| `pages/settings.py` | App settings (from planner21.py) |

### Modified Files
| File | Changes |
|------|---------|
| `planner21.py` | Remove sub-pages, dark mode toggle, inline CSS. Keep Today logic only. Import theme.py |
| `pages/dashboard.py` | Replace CSS with theme import, redesign all components |
| `pages/finance.py` | Same |
| `pages/excercise.py` | Same |
| `pages/driving.py` | Same |
| `pages/journal.py` | Same |
| `pages/news.py` | Same |
| `pages/weekly_review.py` | Same |

### Deleted Code
- Dark mode toggle logic (all files)
- All inline `<style>` blocks (replaced by theme.py)
- Dead History/Insights handlers in planner21.py
- `st.session_state["dark_mode"]` references

### Not Touched
- `utils.py` — data layer unchanged
- `data/` — CSV structure unchanged
- All business logic (scoring, calculations, data loading)
