# Ehda Portal UI guidelines

How to build pages that match the rest of Ehda Portal. Read this before
adding or changing a template.

All paths below are inside `5.Backend/OnlineBloodDonationPlatform/`.

## Principles

- **Plain and functional.** Flat white boxes with a thin border, small
  corners (4–8px), no drop shadows, no gradients, no tinted highlight
  backgrounds. Colour is for meaning (primary actions, blood type,
  status), not decoration.
- **Mobile first.** Most people will use a cheap Android phone on a slow
  connection. Check every page at 375px wide first.
- **Fast.** System fonts only, inline SVG icons, no images or web fonts,
  no JavaScript frameworks, no build step.
- **Private by default.** Never show a donor's email, phone, last name or
  exact location in search, map or any shared page (see [Privacy](#privacy)).
- **Accessible.** WCAG AA contrast, 44px minimum tap targets, visible
  focus, every input has a label.

## Files

| File | Purpose |
|---|---|
| `static/css/ehda.css` | The only stylesheet. Design tokens at the top, then components. |
| `static/css/ehda-admin.css` | Ehda colours for the built-in Django admin (`/admin/`). |
| `static/js/ehda.js` | Mobile menu, show/hide password, password strength, auto-submit filters. |
| `static/js/maps.js` | Leaflet helpers (`EhdaMap`): map, markers, popups, pin picking. |
| `templates/base.html` | Page layout every page extends. |
| `templates/partials/` | Reusable pieces (see [Components](#components)). |
| `locations/templatetags/ehda_ui.py` | `blood_symbol` and `blood_name` filters. |

No inline `style="..."` attributes and no `<style>` blocks in templates.
Add a class to `ehda.css` instead.

## A new page

```django
{% extends "base.html" %}

{% block title %}Page name{% endblock %}

{% block content %}
    <div class="page-header">
        <h1>Page name</h1>
        <p class="lead">One sentence saying what this page is for.</p>
    </div>

    <section class="card section">
        ...
    </section>
{% endblock %}
```

`base.html` blocks:

| Block | Use |
|---|---|
| `title` | Page name (“ \| Ehda Portal” is added) |
| `content` | Normal page content, inside the page container, after messages |
| `page` | Replace the whole body area (full-width pages like the map and landing) |
| `main_class` | Extra class on `<main>`; `is-flush` removes the top/bottom padding |
| `extra_head` | Extra `<head>` tags, loaded before `ehda.css` (e.g. Leaflet) |
| `extra_js` | Page scripts at the end of `<body>` |

The navbar changes by role automatically. Add new navigation links in
`templates/partials/navbar.html` and use `aria-current="page"` for the
current page.

## Design tokens

Use the CSS variables from the top of `ehda.css`, never raw hex values.

| Token | Value | Use |
|---|---|---|
| `--color-primary` | `#b3261e` | Primary buttons, links, blood type badges |
| `--color-primary-hover` | `#8c1d18` | Hover/pressed state of primary |
| `--color-bg` | `#fbf8f6` | Page background |
| `--color-surface` | `#ffffff` | Cards, inputs |
| `--color-text` / `--color-text-muted` | `#1f1b1a` / `#5f5654` | Body text / secondary text |
| `--color-border` / `--color-border-strong` | `#e7dfdc` / `#c9bdb9` | Card borders / input borders |
| `--color-available` | `#1e6b3a` | “Available” status text |
| `--color-unavailable` | `#4b5157` | “Unavailable” status text |
| `--color-pending` | `#7a4a00` | “Pending” status (blood requests) |
| `--color-danger` | `#a11d16` | Errors, destructive actions |
| `--color-hospital` / `--color-center` | `#1f5fa8` / `#00796b` | Map markers |
| `--space-1` … `--space-8` | 4px … 64px | Margins, padding, gaps |
| `--radius-sm` / `--radius` / `--radius-lg` | 4 / 6 / 8px | Corners |
| `--tap` | 44px | Minimum height of anything clickable |

Body text is 16px (`--text-base`) with a 1.6 line height. Do not go
below 14px (`--text-sm`), and use that only for secondary text.

## Components

### Buttons

```html
<a class="btn btn-primary" href="...">Main action</a>
<button class="btn btn-secondary">Other action</button>
<button class="btn btn-ghost">Low-emphasis action</button>
<button class="btn btn-danger">Delete</button>
```

Sizes: add `btn-sm` or `btn-lg`; `btn-block` for full width. Use one
primary button per area. A disabled feature uses a `disabled` button,
never a fake link.

### Cards and lists

- `card`: white box with a border. Add `section` for spacing below.
- `link-list`: a bordered list of links, each with a title and a short
  description. Use it for “what can I do here” navigation on dashboards.
- `soon-card` + `<span class="tag">Coming soon</span>`: a feature that
  is planned but not built yet.

```html
<ul class="link-list">
    <li>
        <a href="{% url 'locations:map' %}">
            <span>
                <span class="link-title">Map</span>
                <span class="link-text">Donors, hospitals and donation centres</span>
            </span>
            {% include "partials/icon.html" with name="arrow" class="flip-rtl" %}
        </a>
    </li>
</ul>
```

### Partials

| Partial | Parameters | Use |
|---|---|---|
| `partials/form_field.html` | `field`, `label`, `optional`, `help`, `password` | Any form field: label, input, help text, inline errors |
| `partials/blood_badge.html` | `type`, `large` | Blood type as a red outlined tag (O−, AB+) |
| `partials/donor_card.html` | `result` | One donor in search results |
| `partials/empty_state.html` | `title`, `text`, `action_url`, `action_label` | “Nothing here yet” message |
| `partials/stat_card.html` | `label`, `value`, `note` | A number on a dashboard |
| `partials/request_status.html` | `blood_request` | A blood request's status as a coloured dot |
| `partials/request_actions.html` | `blood_request` | Hospital status buttons (in review, accept, complete, cancel) |
| `partials/account_status.html` | `account` | Active / inactive dot for a user account |
| `partials/user_status_toggle.html` | `account`, `next`, `label` | Admin activate / deactivate button (none on your own row) |
| `partials/admin_back_link.html` | none | “Back to dashboard” link on admin tool pages |
| `partials/icon.html` | `name`, `class` | Inline SVG icon (see the file for names) |
| `partials/messages.html` | none | Django messages (already in `base.html`) |
| `partials/leaflet_assets.html` | none | Leaflet + `maps.js`; include in `extra_head` |

### Blood type and availability

```django
{% include "partials/blood_badge.html" with type=user.blood_type %}

<span class="availability is-available">Available</span>
<span class="availability is-unavailable">Unavailable</span>
<span class="availability is-pending">Pending</span>
```

A count that needs attention (e.g. new blood requests in the donor
navbar) uses `<span class="count-badge">3</span>`. Give screen readers
the meaning too, e.g. a `visually-hidden` “(3 new)”.

Donor names shown to hospitals or other users go through the
`public_name` filter (`{% load ehda_ui %}`, then `{{ donor|public_name }}`
gives “Ahmad S.”). Never show a donor’s email, phone or exact location
outside their own pages and the site admin. The one exception: while a
donor has accepted a request, that hospital’s request page shows the
donor’s full name and phone with the note “Shared because the donor
accepted” (`DonorResponse.shares_contact`), and the donor sees the
hospital’s phone in a `contact-box`.

Blood types are stored as `O-`, `AB+` and so on. Show them with the
badge partial or the `blood_symbol` filter (real minus sign, “O−”), and
give screen readers `blood_name` (“O negative”).

### Forms

- Keep Django field names, `{% csrf_token %}` and `method` as the view
  expects. Tests rely on them.
- Use `partials/form_field.html` for each field so labels, help text
  and errors look the same everywhere.
- For a choice the user should see at a glance (blood type, distance),
  use radio “chips”: `<input class="chip-input" type="radio" ...>`
  followed by `<label class="chip">`. Add `is-blood` for blood types.
- Show errors next to the field (inline), plus a summary
  `alert alert-error` for errors that are not about one field.

### Icons

Use `partials/icon.html` (stroke icons that inherit the text colour).
Icons are decorative (`aria-hidden`), so always put text next to them.
Arrows that mean “forward” get `class="flip-rtl"`; “back” arrows get
`class="flip"`.

## Maps

- Include `partials/leaflet_assets.html` in `extra_head`, then use the
  `EhdaMap` helpers from `static/js/maps.js` (`create`, `pickPoint`,
  `donorIcon`, `hospitalIcon`, `centerIcon`, `popup`, `donorPopup`).
- Pass data to the page with Django’s `json_script`, never by building
  JSON strings by hand, and read it with `EhdaMap.readJson(id)`.
- Build popup content with DOM nodes and `textContent` (the helpers do
  this). Donor names are user input; never put them in an HTML string.

## Privacy

These rules are covered by tests. Do not break them.

- Search results, the map and any page another user can see may show
  only: first name + last initial, blood type, availability,
  province/district, and a rounded distance (“about 4 km”).
- Never show a donor’s email, phone number, full last name or exact
  coordinates. Only `DonorLocation.approximate_coordinates` (rounded to
  about 1 km) may reach a template, JSON or the browser.
- Even a donor’s own location page does not receive their stored exact
  point; it shows a ~1 km circle instead.

## Accessibility checklist

- [ ] Every input has a `<label for>`; groups of radios use
      `<fieldset>` + `<legend>`.
- [ ] Every clickable thing is at least 44px tall.
- [ ] You can reach and use everything with the keyboard, and the focus
      outline is visible.
- [ ] Text contrast meets WCAG AA (use the colour tokens).
- [ ] Icons are paired with text; SVG illustrations have `aria-hidden`.
- [ ] The page works at 375px, 768px and 1280px wide with no sideways
      scrolling.

## Right-to-left (Dari)

`base.html` sets `lang` and `dir` on `<html>`. The stylesheet uses
logical properties (`margin-inline-start`, `padding-block`,
`inset-inline-end`, `text-align: start`) so a Dari version only needs
`dir="rtl"`. Use logical properties in new CSS too; avoid `left`/`right`.

## Django admin

`/admin/` uses the same colours through `static/css/ehda-admin.css`
(light and dark mode) and `templates/admin/base_site.html` (logo and
links back to the app). Change admin colours there, not in `ehda.css`.
