// Mobile nav toggle
const toggle = document.querySelector(".nav-toggle");
const links = document.querySelector(".nav-links");
if (toggle && links) {
  toggle.addEventListener("click", () => {
    const open = links.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(open));
  });
  links.querySelectorAll("a").forEach((a) => {
    a.addEventListener("click", () => {
      links.classList.remove("open");
      toggle.setAttribute("aria-expanded", "false");
    });
  });
}

// Footer year
const yearEl = document.getElementById("year");
if (yearEl) yearEl.textContent = new Date().getFullYear();

// ---------------- Language toggle (EN / DE) ----------------
function applyLanguage(lang) {
  const attr = lang === "de" ? "data-de" : "data-en";
  document.querySelectorAll("[data-en]").forEach((el) => {
    const val = el.getAttribute(attr);
    if (val !== null) el.innerHTML = val;
  });
  document.documentElement.setAttribute("lang", lang);
  document.querySelectorAll(".lang-opt").forEach((opt) => {
    opt.classList.toggle("active", opt.getAttribute("data-lang") === lang);
  });
  try { localStorage.setItem("mcv-lang", lang); } catch (e) {}
}

const langToggle = document.getElementById("lang-toggle");
if (langToggle) {
  langToggle.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("lang") === "de" ? "de" : "en";
    applyLanguage(current === "de" ? "en" : "de");
  });
}

(function initLang() {
  let saved = "en";
  try { saved = localStorage.getItem("mcv-lang") || "en"; } catch (e) {}
  applyLanguage(saved);
})();

// ---------------- Scroll reveal ----------------
(function () {
  const items = document.querySelectorAll(".section, .metrics");
  items.forEach((el) => el.classList.add("reveal"));
  if (!("IntersectionObserver" in window)) {
    items.forEach((el) => el.classList.add("in"));
    return;
  }
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add("in");
          io.unobserve(e.target);
        }
      });
    },
    { threshold: 0.12 }
  );
  items.forEach((el) => io.observe(el));
})();

// ---------------- Animated counters ----------------
(function () {
  const nums = document.querySelectorAll(".metric-num[data-count]");
  if (!nums.length) return;
  const run = (el) => {
    const target = parseInt(el.getAttribute("data-count"), 10);
    const suffix = el.getAttribute("data-suffix") || "";
    const dur = 1100;
    const start = performance.now();
    const step = (now) => {
      const p = Math.min((now - start) / dur, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(target * eased) + suffix;
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };
  if (!("IntersectionObserver" in window)) { nums.forEach(run); return; }
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => { if (e.isIntersecting) { run(e.target); io.unobserve(e.target); } });
  }, { threshold: 0.5 });
  nums.forEach((n) => io.observe(n));
})();

// ---------------- CV download modal ----------------
const dlBtn = document.getElementById("download-cv");
const cvModal = document.getElementById("cv-modal");
const cvClose = document.getElementById("cv-modal-close");
function openCvModal() { if (cvModal) { cvModal.classList.add("open"); cvModal.setAttribute("aria-hidden", "false"); } }
function closeCvModal() { if (cvModal) { cvModal.classList.remove("open"); cvModal.setAttribute("aria-hidden", "true"); } }
if (dlBtn) dlBtn.addEventListener("click", openCvModal);
if (cvClose) cvClose.addEventListener("click", closeCvModal);
if (cvModal) cvModal.addEventListener("click", (e) => { if (e.target === cvModal) closeCvModal(); });
document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeCvModal(); });
