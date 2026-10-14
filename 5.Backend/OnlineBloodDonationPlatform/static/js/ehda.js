/*
 * Ehda Portal: small progressive enhancements.
 * Every page works without this file; it only adds convenience.
 */
(function () {
    "use strict";

    // Mobile navigation (hamburger) --------------------------------------
    var toggle = document.querySelector("[data-nav-toggle]");
    var nav = document.getElementById("site-nav");

    function setNavOpen(open) {
        toggle.setAttribute("aria-expanded", open ? "true" : "false");
        nav.classList.toggle("is-open", open);
    }

    if (toggle && nav) {
        toggle.addEventListener("click", function () {
            setNavOpen(toggle.getAttribute("aria-expanded") !== "true");
        });

        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape" && nav.classList.contains("is-open")) {
                setNavOpen(false);
                toggle.focus();
            }
        });
    }

    // Show / hide password -----------------------------------------------
    document.querySelectorAll("[data-password-toggle]").forEach(function (button) {
        var input = document.getElementById(button.getAttribute("data-password-toggle"));

        if (!input) {
            return;
        }

        button.hidden = false;

        button.addEventListener("click", function () {
            var show = input.type === "password";

            input.type = show ? "text" : "password";
            button.textContent = show ? "Hide" : "Show";
            button.setAttribute("aria-pressed", show ? "true" : "false");
        });
    });

    // Password strength hint (guidance only; the server validates) --------
    document.querySelectorAll("[data-strength-for]").forEach(function (meter) {
        var input = document.getElementById(meter.getAttribute("data-strength-for"));
        var label = meter.querySelector("[data-strength-text]");

        if (!input || !label) {
            return;
        }

        meter.hidden = false;

        input.addEventListener("input", function () {
            var value = input.value;
            var score = 0;

            if (value.length >= 8) { score++; }
            if (value.length >= 12) { score++; }
            if (/[A-Z]/.test(value)) { score++; }
            if (/[a-z]/.test(value)) { score++; }
            if (/[0-9]/.test(value)) { score++; }
            if (/[^A-Za-z0-9]/.test(value)) { score++; }

            var level = "";
            var text = "Password strength";

            if (value.length > 0) {
                if (score <= 2) {
                    level = "weak";
                    text = "Weak password";
                } else if (score <= 4) {
                    level = "medium";
                    text = "Okay password";
                } else {
                    level = "strong";
                    text = "Strong password";
                }
            }

            meter.setAttribute("data-strength", level);
            label.textContent = text;
        });
    });

    // Submit a filter form as soon as a choice changes --------------------
    document.querySelectorAll("form[data-autosubmit]").forEach(function (form) {
        form.addEventListener("change", function () {
            form.submit();
        });
    });
})();
