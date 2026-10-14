/*
 * Ehda Portal: shared Leaflet helpers (Leaflet must be loaded first).
 *
 * PRIVACY: these helpers only ever receive approximate donor coordinates
 * from the server. Never add code that sends exact positions here.
 */
var EhdaMap = (function () {
    "use strict";

    var COLORS = {
        donor: "#b3261e",
        hospital: "#1f5fa8",
        center: "#00796b",
        pin: "#1f1b1a"
    };

    // Map with OpenStreetMap tiles (free, no API key).
    function create(elementId, center) {
        var map = L.map(elementId, { scrollWheelZoom: false })
            .setView([center.lat, center.lng], center.zoom || 6);

        L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 19,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        // Let people scroll the page past the map; zoom on click/focus.
        map.on("focus click", function () {
            map.scrollWheelZoom.enable();
        });

        return map;
    }

    // --- Marker icons (inline SVG, no image downloads) ------------------

    function dropSvg(color) {
        return '<svg class="marker" width="28" height="36" viewBox="0 0 28 36" aria-hidden="true">' +
            '<path fill="' + color + '" stroke="#fff" stroke-width="2" ' +
            'd="M14 1.5S2.5 14.6 2.5 22.3a11.5 11.5 0 0 0 23 0C25.5 14.6 14 1.5 14 1.5z"/>' +
            '<circle cx="14" cy="23" r="4" fill="#fff"/></svg>';
    }

    function donorIcon(count) {
        var badge = count > 1 ? '<span class="marker-count">' + count + "</span>" : "";

        return L.divIcon({
            className: "",
            html: '<div style="position:relative">' + dropSvg(COLORS.donor) + badge + "</div>",
            iconSize: [28, 36],
            iconAnchor: [14, 34],
            popupAnchor: [0, -30]
        });
    }

    var hospitalIcon = L.divIcon({
        className: "",
        html: '<svg class="marker" width="30" height="30" viewBox="0 0 30 30" aria-hidden="true">' +
            '<rect x="1.5" y="1.5" width="27" height="27" rx="7" fill="' + COLORS.hospital + '" stroke="#fff" stroke-width="2"/>' +
            '<path fill="#fff" d="M12.5 7.5h5v5h5v5h-5v5h-5v-5h-5v-5h5z"/></svg>',
        iconSize: [30, 30],
        iconAnchor: [15, 15],
        popupAnchor: [0, -14]
    });

    var centerIcon = L.divIcon({
        className: "",
        html: '<svg class="marker" width="30" height="30" viewBox="0 0 30 30" aria-hidden="true">' +
            '<circle cx="15" cy="15" r="13.5" fill="' + COLORS.center + '" stroke="#fff" stroke-width="2"/>' +
            '<path fill="#fff" d="M15 7s-5.5 6.2-5.5 9.8a5.5 5.5 0 0 0 11 0C20.5 13.2 15 7 15 7z"/></svg>',
        iconSize: [30, 30],
        iconAnchor: [15, 15],
        popupAnchor: [0, -14]
    });

    // A pin for "the point I picked" on location and search maps.
    var pinIcon = L.divIcon({
        className: "",
        html: '<svg class="marker" width="30" height="40" viewBox="0 0 30 40" aria-hidden="true">' +
            '<path fill="' + COLORS.pin + '" stroke="#fff" stroke-width="2" ' +
            'd="M15 1.5C7.5 1.5 1.5 7.4 1.5 14.8 1.5 24.5 15 38.5 15 38.5S28.5 24.5 28.5 14.8C28.5 7.4 22.5 1.5 15 1.5z"/>' +
            '<circle cx="15" cy="15" r="5" fill="#fff"/></svg>',
        iconSize: [30, 40],
        iconAnchor: [15, 38]
    });

    // --- Popups: built with DOM + textContent, never HTML strings, ------
    // --- because donor names are user input.                       ------

    function element(tag, className, text) {
        var node = document.createElement(tag);

        if (className) {
            node.className = className;
        }

        if (text) {
            node.textContent = text;
        }

        return node;
    }

    function popup(kind, title, lines) {
        var box = element("div");

        box.appendChild(element("div", "popup-kind", kind));
        box.appendChild(element("div", "popup-title", title));

        (lines || []).forEach(function (line) {
            if (line) {
                box.appendChild(element("div", "popup-line", line));
            }
        });

        return box;
    }

    function bloodSymbol(type) {
        return String(type || "").replace("-", "−");
    }

    function donorPopup(donors) {
        var title = donors.length === 1
            ? "1 available donor"
            : donors.length + " available donors";

        var box = popup("Approximate area", title, []);
        var list = element("ul", "popup-donors");

        donors.forEach(function (donor) {
            var item = element("li");
            item.appendChild(element("span", "", donor.name));
            item.appendChild(element("span", "badge-blood", bloodSymbol(donor.blood_type)));
            list.appendChild(item);
        });

        box.appendChild(list);
        return box;
    }

    // --- Click-to-pick a point --------------------------------------------

    /*
     * Lets the user click the map to drop a pin and writes the point into
     * two (hidden) inputs. Returns { clear: function } so pages can offer
     * a "clear" button.
     */
    function pickPoint(map, options) {
        var latInput = options.latInput;
        var lngInput = options.lngInput;
        var decimals = options.decimals || 6;
        var marker = null;

        function place(latlng) {
            if (marker) {
                marker.setLatLng(latlng);
            } else {
                marker = L.marker(latlng, { icon: pinIcon, keyboard: false }).addTo(map);
            }
        }

        if (latInput.value && lngInput.value) {
            var start = [parseFloat(latInput.value), parseFloat(lngInput.value)];
            place(start);
            map.setView(start, Math.max(map.getZoom(), 11));
        }

        map.on("click", function (event) {
            latInput.value = event.latlng.lat.toFixed(decimals);
            lngInput.value = event.latlng.lng.toFixed(decimals);
            place(event.latlng);

            if (options.onPick) {
                options.onPick();
            }
        });

        return {
            clear: function () {
                latInput.value = "";
                lngInput.value = "";

                if (marker) {
                    map.removeLayer(marker);
                    marker = null;
                }
            }
        };
    }

    // Move the map when a province is chosen from a <select>.
    function followProvince(map, select, centres, zoom) {
        select.addEventListener("change", function () {
            var centre = centres[select.value];

            if (centre) {
                map.setView([centre.lat, centre.lng], zoom || 10);
            }
        });
    }

    function readJson(id) {
        var node = document.getElementById(id);
        return node ? JSON.parse(node.textContent) : null;
    }

    return {
        COLORS: COLORS,
        create: create,
        donorIcon: donorIcon,
        hospitalIcon: hospitalIcon,
        centerIcon: centerIcon,
        popup: popup,
        donorPopup: donorPopup,
        pickPoint: pickPoint,
        followProvince: followProvince,
        readJson: readJson
    };
})();
