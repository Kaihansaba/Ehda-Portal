# Frontend

There is no separate frontend app. Ehda Portal is a Django project whose
pages are rendered on the server, so the frontend lives inside the
Django project:

| What | Where |
|---|---|
| Page templates (HTML) | [`5.Backend/OnlineBloodDonationPlatform/templates/`](../5.Backend/OnlineBloodDonationPlatform/templates/) |
| Account pages (login, register, dashboards, profile) | [`5.Backend/OnlineBloodDonationPlatform/templates/accounts/`](../5.Backend/OnlineBloodDonationPlatform/templates/accounts/) |
| Search, map and location pages | [`5.Backend/OnlineBloodDonationPlatform/templates/locations/`](../5.Backend/OnlineBloodDonationPlatform/templates/locations/) |
| Shared page layout | [`5.Backend/OnlineBloodDonationPlatform/templates/base.html`](../5.Backend/OnlineBloodDonationPlatform/templates/base.html) |
| Reusable pieces (navbar, form field, donor card, icons) | [`5.Backend/OnlineBloodDonationPlatform/templates/partials/`](../5.Backend/OnlineBloodDonationPlatform/templates/partials/) |
| Stylesheet and scripts | [`5.Backend/OnlineBloodDonationPlatform/static/`](../5.Backend/OnlineBloodDonationPlatform/static/) |
| Django admin branding | [`5.Backend/OnlineBloodDonationPlatform/templates/admin/`](../5.Backend/OnlineBloodDonationPlatform/templates/admin/) |

Design rules, components and the accessibility checklist are in
[`docs/UI_GUIDELINES.md`](../docs/UI_GUIDELINES.md).

Maps use [Leaflet](https://leafletjs.com/) with OpenStreetMap tiles,
loaded from a CDN. No build step or JavaScript framework is used.
