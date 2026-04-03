# Planner21 — Zen Redesign Spec
**Date:** 2026-04-03  
**Scope:** All 5 pages — Planner, Dashboard, Finance, Driving, Exercise

---

## Goal

Apply a Japanese-minimalism aesthetic to every page: warm parchment backgrounds, Georgia serif typography, generous spacing, and quiet UI chrome. Both light and dark modes should feel intentional and calm.

No functional or layout changes. This is purely a visual layer.

---

## Approach

1. Add `.streamlit/config.toml` to set Streamlit's native theme for light mode (beige background, stone accent).
2. Update each page's `<style>` block to replace current design tokens with zen tokens, add `font-family: Georgia`, increase spacing, and soften visual weight.
3. Add CSS dark-mode overrides using `html[data-theme="dark"]` so dark mode uses walnut tones instead of Streamlit's default grey.

---

## 1. Streamlit Config (`config.toml`)

Create `.streamlit/config.toml` (at repo root, alongside `planner21.py`):

```toml
[theme]
primaryColor     = "#8a7055"   # warm stone — buttons, links, focus rings
backgroundColor  = "#f5f0e8"   # parchment — main page background
secondaryBackgroundColor = "#ede8de"  # slightly darker beige — cards, sidebar
textColor        = "#3a3028"   # dark warm brown
font             = "serif"
```

This handles the base light-mode feel without any CSS. Streamlit's own component system picks up `secondaryBackgroundColor` for cards via `var(--secondary-background-color)`.

---

## 2. Shared Design Tokens (applied to every page's `<style>` block)

Replace existing `:root` blocks with:

```css
:root {
  /* spacing */
  --r-lg: 18px; --r-md: 12px; --r-sm: 8px;
  --border: 1px solid rgba(0,0,0,0.07);
  --shadow: 0 1px 3px rgba(0,0,0,0.04);

  /* colour */
  --accent: #8a7055;
  --accent-soft: rgba(138,112,85,0.09);
  --pos: #5a9a6a;
  --neg: #b87070;
}
```

Dark-mode override block (added once per page, after `:root`). Uses `@media (prefers-color-scheme: dark)` — the reliable cross-version Streamlit selector. Streamlit's dark toggle follows OS preference by default, so this fires correctly:

```css
@media (prefers-color-scheme: dark) {
  :root {
    --accent: #b08a65;
    --accent-soft: rgba(176,138,101,0.12);
    --border: 1px solid rgba(255,255,255,0.07);
    --shadow: 0 1px 3px rgba(0,0,0,0.12);
    --pos: #7ab88a;
    --neg: #c87878;
  }
}
```

---

## 3. Typography

Add to every page's `<style>` block:

```css
html, body, [class*="css"] {
  font-family: Georgia, 'Times New Roman', serif !important;
}
div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input {
  font-family: Georgia, 'Times New Roman', serif !important;
}
```

Font-weight changes (applied to existing classes):
- `.page-title`: `font-weight: 500` (was 900)
- `.score-value`: `font-weight: 500` (was 900)
- `.section-label`: `font-weight: 400`, `opacity: 0.55` (was font-weight 800, opacity 0.5)
- `.section-title`: `font-weight: 500` (was 800)

---

## 4. Spacing

`.block-container` padding:
```css
.block-container {
  max-width: 1100px;
  padding-top: 4rem !important;
  padding-bottom: 4rem !important;
}
```

Cards — increase padding:
```css
.section-card { padding: 28px 32px; margin-bottom: 20px; }
.score-card   { padding: 28px 32px; }
.ins-card     { padding: 20px 24px; }
```

---

## 5. Progress Bars

Thinner, quieter:
```css
.progress-shell { height: 3px; }   /* was 6px */
.hist-bar-wrap  { height: 3px; }
.week-bar-wrap  { height: 3px; }
```

---

## 6. Accent Bar on Cards — Remove

The `::before` / `::after` pseudo-element accent lines on `.score-card` and `.ins-card` add visual weight that conflicts with zen. Remove them:

```css
.score-card::before { display: none; }
.ins-card::after    { display: none; }
```

---

## 7. Buttons

Remove the `transform: translateY(-1px)` hover effect; keep only the border-color change:
```css
div.stButton > button:hover {
  border-color: var(--accent) !important;
  box-shadow: 0 2px 8px rgba(138,112,85,0.12) !important;
  /* no transform */
}
```

---

## 8. Per-Page Notes

| Page | Note |
|---|---|
| `planner21.py` | Largest CSS block — all token + spacing changes apply |
| `dashboard.py` | Has `detail-row`, `section-card` classes — same token update |
| `finance.py` | CSS injected inline as a string; same token update |
| `driving.py` | Minimal CSS block; add font + token update |
| `excercise.py` | Has its own `.block-container` + accent refs; same token update |

No functional or data changes to any page.

---

## 9. Emojis in Labels

Page titles use emoji in `st.title()` / `st.set_page_config(page_icon=...)` calls (e.g. `🚗 Driving Command Center`). These are Streamlit native calls and don't affect the CSS redesign. Leave them as-is unless the user requests text-only labels — this is out of scope for this spec.

---

## Out of Scope

- Layout restructuring
- New components or features
- Shared CSS module / `theme.py` extraction
- Font loading from Google Fonts
- Emoji removal from page titles
