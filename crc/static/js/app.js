/* CRC application script — vanilla JS, no jQuery.
 * Theme toggle, mobile sidebar drawer, and dynamic formset rows.
 */
(() => {
  

  /* ---- Theme ------------------------------------------------------------ */
  function resolvedTheme() {
    var saved;
    try {
      saved = localStorage.getItem("crc-theme");
    } catch (e) {}
    if (saved === "light" || saved === "dark") return saved;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-bs-theme", theme);
    try {
      localStorage.setItem("crc-theme", theme);
    } catch (e) {}
    var toggle = document.getElementById("theme-toggle");
    if (toggle) {
      toggle.setAttribute("aria-pressed", String(theme === "dark"));
      var icon = toggle.querySelector(".bi");
      if (icon) {
        icon.className = theme === "dark" ? "bi bi-sun-fill" : "bi bi-moon-stars-fill";
      }
    }
  }

  window.crcApplyTheme = applyTheme;

  document.addEventListener("DOMContentLoaded", () => {
    applyTheme(resolvedTheme());
    var toggle = document.getElementById("theme-toggle");
    if (toggle) {
      toggle.addEventListener("click", () => {
        var current = document.documentElement.getAttribute("data-bs-theme");
        applyTheme(current === "dark" ? "light" : "dark");
      });
    }

    /* ---- Mobile sidebar drawer ---------------------------------------- */
    var sidebar = document.getElementById("app-sidebar");
    var backdrop = document.getElementById("app-sidebar-backdrop");
    var opener = document.getElementById("app-sidebar-toggle");
    function openSidebar(open) {
      if (!sidebar) return;
      sidebar.classList.toggle("open", open);
      if (backdrop) backdrop.classList.toggle("show", open);
      if (opener) opener.setAttribute("aria-expanded", String(open));
    }
    if (opener) {
      opener.addEventListener("click", () => {
        openSidebar(!sidebar.classList.contains("open"));
      });
    }
    if (backdrop) backdrop.addEventListener("click", () => { openSidebar(false); });
    // Close on Escape.
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") openSidebar(false);
    });
  });

  /* ---- Formset row management ------------------------------------------ */
  function totalFormsInput(root) {
    return root.querySelector("input[name$='-TOTAL_FORMS']");
  }

  document.addEventListener("click", (e) => {
    // Add row
    var addBtn = e.target.closest("[data-formset-add]");
    if (addBtn) {
      e.preventDefault();
      var root = document.getElementById(addBtn.getAttribute("data-formset-add"));
      if (!root) return;
      var total = totalFormsInput(root);
      var idx = parseInt(total.value, 10) || 0;
      var template = root.querySelector("[data-formset-empty]");
      if (!template) return;
      var row = template.cloneNode(true);
      row.removeAttribute("data-formset-empty");
      row.setAttribute("data-formset-row", "");
      row.classList.remove("d-none", "visually-hidden-fake-row");
      row.removeAttribute("aria-hidden");
      // Replace __prefix__ in element attributes (id/name/for/...) with the
      // new index. DOM attribute editing — no innerHTML, no XSS surface.
      row.querySelectorAll("*").forEach(function (el) {
        Array.prototype.forEach.call(el.attributes, function (attr) {
          if (attr.value.indexOf("__prefix__") !== -1) {
            el.setAttribute(attr.name, attr.value.replace(/__prefix__/g, String(idx)));
          }
        });
      });
      template.parentNode.insertBefore(row, template);
      total.value = String(idx + 1);
      var firstInput = row.querySelector("input,select");
      if (firstInput) firstInput.focus();
      return;
    }

    // Delete row
    var delBtn = e.target.closest("[data-formset-delete]");
    if (delBtn) {
      e.preventDefault();
      var rowEl = delBtn.closest("[data-formset-row]") || delBtn.closest("tr");
      if (!rowEl) return;
      var delInput = rowEl.querySelector("input[name$='-DELETE']");
      if (delInput) {
        delInput.checked = true;
        rowEl.classList.add("d-none", "opacity-50");
      } else {
        rowEl.remove();
      }
    }
  });
})();