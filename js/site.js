/* Teddy's Burger · interactions du site
   © 2026 Chrisnaël Berdier (chrisnaelberdier.com). Tous droits réservés.
   Toute copie ou réutilisation sans autorisation écrite est interdite. */
(function () {
  "use strict";

  /* Le site ne s'affiche dans le cadre d'un autre site que sur le portfolio de l'auteur
     (et en local pour le développement). Ailleurs, la page se masque et tente de sortir du cadre. */
  var FRAME_OK = /^(https:\/\/(www\.)?chrisnaelberdier\.com|https:\/\/yui971\.github\.io|https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?|file:\/\/)$/;
  if (window.top !== window.self) {
    var ancestors = window.location.ancestorOrigins;
    var origins = ancestors && ancestors.length
      ? Array.prototype.slice.call(ancestors)
      : [(document.referrer.match(/^[a-z]+:\/\/[^\/]*/i) || [""])[0]];
    var framedOk = origins.every(function (o) { return FRAME_OK.test(o); });
    if (!framedOk) {
      document.documentElement.style.display = "none";
      try { window.top.location = window.self.location.href; } catch (err) { /* navigation bloquée : la page reste masquée */ }
    }
  }

  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  document.documentElement.classList.add("js-ready");

  /* =========================================================
     Loader
     Garde-fous pour qu'il ne reste jamais bloqué :
     1. il n'existe que si le JS tourne (classe .js posée dans le <head>) ;
     2. il se retire sur DOMContentLoaded (on n'attend pas les images) ;
     3. un minuteur le retire au plus tard après 3 s ;
     4. une animation CSS le cache au bout de 4,5 s même si ce script plante ;
     5. au retour arrière (cache du navigateur), il est retiré tout de suite.
     ========================================================= */
  var loader = document.getElementById("loader");
  var MIN_SHOW = reduceMotion ? 150 : 900;
  var start = (window.performance && performance.now) ? performance.now() : 0;
  var hideTimer = null;

  function now() { return (window.performance && performance.now) ? performance.now() : Date.now(); }

  function hideLoader(immediate) {
    if (!loader || loader.classList.contains("is-gone")) return;
    clearTimeout(hideTimer);
    if (immediate || reduceMotion) {
      loader.classList.add("is-gone");
      loader.classList.remove("is-leaving", "is-replay");
      loader.setAttribute("aria-hidden", "true");
      return;
    }
    loader.classList.add("is-leaving");
    hideTimer = setTimeout(function () {
      loader.classList.add("is-gone");
      loader.classList.remove("is-leaving", "is-replay");
      loader.setAttribute("aria-hidden", "true");
    }, 450);
  }

  function scheduleHide() {
    var wait = Math.max(0, MIN_SHOW - (now() - start));
    setTimeout(function () { hideLoader(false); }, wait);
  }

  function restartLayers() {
    var stack = loader && loader.querySelector(".loader__stack");
    if (!stack) return;
    var fresh = stack.cloneNode(true);
    stack.parentNode.replaceChild(fresh, stack);
    var label = loader.querySelector(".loader__label");
    if (label) { var l2 = label.cloneNode(true); label.parentNode.replaceChild(l2, label); }
  }

  function showLoader() {
    if (!loader) return;
    clearTimeout(hideTimer);
    restartLayers();
    loader.classList.remove("is-gone", "is-leaving");
    loader.classList.add("is-replay");
    loader.setAttribute("aria-hidden", "false");
  }

  if (loader) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", scheduleHide);
    } else {
      scheduleHide();
    }
    // Plafond : jamais plus de 3 s, quoi qu'il arrive.
    setTimeout(function () { hideLoader(false); }, 3000);
    // Retour arrière / avant servi depuis le cache : on retire le loader.
    window.addEventListener("pageshow", function (e) {
      if (e.persisted) hideLoader(true);
    });
  }

  // Clic sur le logo : on rejoue le loader puis on revient à l'accueil.
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[data-logo]");
    if (!a || !loader) return;
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    var href = a.getAttribute("href");
    var target = new URL(href, location.href);
    var samePage = target.pathname.replace(/index\.html$/, "") === location.pathname.replace(/index\.html$/, "");
    showLoader();
    if (samePage) {
      setTimeout(function () {
        window.scrollTo(0, 0);
        if (location.hash) history.replaceState(null, "", target.pathname);
      }, 250);
      setTimeout(function () { hideLoader(false); }, reduceMotion ? 300 : 1100);
    } else {
      setTimeout(function () { location.href = target.href; }, reduceMotion ? 50 : 650);
      // Si la navigation est annulée (hors ligne, double clic…), on ne reste pas coincé.
      setTimeout(function () { hideLoader(false); }, 4000);
    }
  });

  /* =========================================================
     Horaires et statut en direct (heure de Guadeloupe)
     ========================================================= */
  var TZ = "America/Guadeloupe";
  // 0 = dimanche … 6 = samedi ; minutes depuis minuit
  var OPEN = {
    0: [17 * 60 + 30, 21 * 60],
    3: [18 * 60 + 30, 22 * 60],
    4: [18 * 60 + 30, 22 * 60],
    5: [18 * 60 + 30, 22 * 60],
    6: [18 * 60 + 30, 22 * 60]
  };
  var ONLINE = {
    0: [17 * 60 + 30, 20 * 60 + 45],
    3: [18 * 60 + 25, 21 * 60 + 45],
    4: [18 * 60 + 25, 21 * 60 + 45],
    5: [18 * 60 + 25, 21 * 60 + 45],
    6: [18 * 60 + 25, 21 * 60 + 45]
  };
  var DAYS = ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"];

  function gpNow() {
    try {
      var parts = new Intl.DateTimeFormat("en-GB", { timeZone: TZ, weekday: "short", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).formatToParts(new Date());
      var map = {};
      parts.forEach(function (p) { map[p.type] = p.value; });
      var wd = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].indexOf(map.weekday);
      return { day: wd, min: parseInt(map.hour, 10) * 60 + parseInt(map.minute, 10) };
    } catch (err) {
      // Repli : la Guadeloupe est à UTC-4 toute l'année.
      var d = new Date(Date.now() - 4 * 3600 * 1000);
      return { day: d.getUTCDay(), min: d.getUTCHours() * 60 + d.getUTCMinutes() };
    }
  }

  function hhmm(m) {
    var h = Math.floor(m / 60), mm = m % 60;
    return h + "h" + (mm < 10 ? "0" + mm : mm);
  }
  function inDuration(m) {
    if (m < 60) return m + " min";
    var h = Math.floor(m / 60), r = m % 60;
    return h + " h" + (r ? " " + (r < 10 ? "0" + r : r) : "");
  }

  function computeStatus() {
    var t = gpNow();
    var today = OPEN[t.day];
    var online = ONLINE[t.day];
    if (today && t.min >= today[0] && t.min < today[1]) {
      var sub = (online && t.min < online[1])
        ? "Commande en ligne jusqu'à " + hhmm(online[1])
        : "Commande en ligne fermée, appelle-nous";
      return { state: "open", text: "Ouvert jusqu'à " + hhmm(today[1]), sub: sub, short: "Ouvert jusqu'à " + hhmm(today[1]) };
    }
    if (today && t.min < today[0]) {
      var wait = today[0] - t.min;
      return { state: wait <= 120 ? "soon" : "closed", text: "Fermé · ouvre à " + hhmm(today[0]), sub: "Dans " + inDuration(wait) + ", ce soir", short: "Ouvre à " + hhmm(today[0]) };
    }
    for (var i = 1; i <= 7; i++) {
      var d = (t.day + i) % 7;
      if (OPEN[d]) {
        var label = i === 1 ? "demain" : DAYS[d];
        var shortDay = i === 1 ? "demain" : ["dim.", "lun.", "mar.", "mer.", "jeu.", "ven.", "sam."][d];
        return { state: "closed", text: "Fermé · ouvre " + label + " à " + hhmm(OPEN[d][0]), sub: "Ouvert du mercredi au dimanche, le soir", short: "Fermé · " + shortDay + " " + hhmm(OPEN[d][0]) };
      }
    }
    return { state: "closed", text: "Fermé", sub: "", short: "Fermé" };
  }

  function renderStatus() {
    var s = computeStatus();
    document.querySelectorAll("[data-status]").forEach(function (el) {
      el.setAttribute("data-state", s.state);
      var main = el.querySelector(".status__text");
      var sub = el.querySelector(".status__sub");
      if (main) main.textContent = el.classList.contains("mbar__status") ? s.short : s.text;
      if (sub) sub.textContent = s.sub;
    });
    var t = gpNow();
    document.querySelectorAll(".hours tr[data-days]").forEach(function (tr) {
      var days = tr.getAttribute("data-days").split(",").map(Number);
      var isToday = days.indexOf(t.day) !== -1;
      tr.classList.toggle("is-today", isToday);
      var tag = tr.querySelector(".today-tag");
      if (tag) tag.hidden = !isToday;
    });
  }
  renderStatus();
  setInterval(renderStatus, 30000);
  document.addEventListener("visibilitychange", function () { if (!document.hidden) renderStatus(); });

  /* =========================================================
     Copier l'adresse
     ========================================================= */
  document.querySelectorAll("[data-copy]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var text = btn.getAttribute("data-copy");
      var done = function () {
        var old = btn.textContent;
        btn.classList.add("is-done");
        btn.textContent = "Adresse copiée";
        setTimeout(function () { btn.classList.remove("is-done"); btn.textContent = old; }, 2200);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () { window.prompt("Copie l'adresse :", text); });
      } else {
        window.prompt("Copie l'adresse :", text);
      }
    });
  });

  /* =========================================================
     Socle du hero : fondu enchaîné lent
     ========================================================= */
  var plinthItems = document.querySelectorAll(".plinth__item");
  if (plinthItems.length > 1 && !reduceMotion) {
    var idx = 0, plinthTimer = null;
    var step = function () {
      plinthItems[idx].classList.remove("is-on");
      idx = (idx + 1) % plinthItems.length;
      plinthItems[idx].classList.add("is-on");
    };
    var startPlinth = function () { stopPlinth(); plinthTimer = setInterval(step, 5500); };
    var stopPlinth = function () { clearInterval(plinthTimer); };
    startPlinth();
    document.addEventListener("visibilitychange", function () { document.hidden ? stopPlinth() : startPlinth(); });
  }

  /* =========================================================
     Liste des burgers : l'objet affiche le burger survolé
     ========================================================= */
  var obj = document.querySelector(".ride__object");
  if (obj) {
    var photo = obj.querySelector(".obj-photo");
    var clearT = null;
    document.querySelectorAll(".ride__list .row[data-photo]").forEach(function (row) {
      var show = function () {
        clearTimeout(clearT);
        photo.src = row.getAttribute("data-photo");
        photo.alt = row.getAttribute("data-name") || "";
        obj.classList.add("is-photo");
      };
      var hide = function () { clearT = setTimeout(function () { obj.classList.remove("is-photo"); }, 120); };
      row.addEventListener("mouseenter", show);
      row.addEventListener("mouseleave", hide);
      row.addEventListener("focusin", show);
      row.addEventListener("focusout", hide);
    });
  }

  /* =========================================================
     404 : arrivée depuis une recherche sans résultat
     ========================================================= */
  var lostText = document.querySelector("[data-lost-text]");
  var lostQuery = lostText && new URLSearchParams(window.location.search).get("recherche");
  if (lostQuery) {
    lostText.textContent = "« " + lostQuery.slice(0, 60) + " » n'est pas sur la carte : on ne le fait pas, ou quelqu'un l'a mangé. Le reste du snack est toujours là.";
  }

  /* =========================================================
     Carte : recherche et catégories
     ========================================================= */
  var search = document.getElementById("menu-search");
  var cats = document.querySelectorAll(".cats [data-cat]");
  var sections = document.querySelectorAll(".menu-cat");
  var empty = document.querySelector(".menu-empty");
  var activeCat = "all";

  function norm(s) { return (s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); }

  function applyFilter() {
    var q = norm(search ? search.value.trim() : "");
    var shown = 0;
    sections.forEach(function (sec) {
      var catOk = activeCat === "all" || sec.id === activeCat;
      var anyInSec = 0;
      sec.querySelectorAll(".dish").forEach(function (dish) {
        var hay = norm(dish.getAttribute("data-search"));
        var ok = catOk && (!q || hay.indexOf(q) !== -1);
        dish.classList.toggle("is-filtered-out", !ok);
        if (ok) anyInSec++;
      });
      sec.classList.toggle("is-filtered-out", anyInSec === 0);
      shown += anyInSec;
    });
    if (empty) {
      empty.hidden = shown !== 0;
      var qEl = empty.querySelector("[data-q]");
      if (qEl) qEl.textContent = search ? search.value.trim() : "";
    }
    var count = document.querySelector("[data-count]");
    if (count) count.textContent = shown + (shown > 1 ? " produits" : " produit");
    return shown;
  }

  if (search) {
    search.addEventListener("input", applyFilter);
    search.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { search.value = ""; applyFilter(); }
      // Entrée sur une recherche sans résultat : page « Burger introuvable »
      if (e.key === "Enter" && search.value.trim() && applyFilter() === 0) {
        e.preventDefault();
        window.location.href = "404.html?recherche=" + encodeURIComponent(search.value.trim());
      }
    });
  }
  cats.forEach(function (btn) {
    btn.addEventListener("click", function () {
      activeCat = btn.getAttribute("data-cat");
      cats.forEach(function (b) { b.setAttribute("aria-pressed", String(b === btn)); });
      applyFilter();
      var tools = document.querySelector(".menu-tools");
      var menu = document.getElementById("menu");
      if (menu && tools) {
        var y = menu.getBoundingClientRect().top + window.scrollY - tools.offsetHeight - 8;
        if (window.scrollY > y) window.scrollTo({ top: y, behavior: reduceMotion ? "auto" : "smooth" });
      }
    });
  });
  var resetBtn = document.querySelector("[data-reset]");
  if (resetBtn) resetBtn.addEventListener("click", function () {
    if (search) search.value = "";
    activeCat = "all";
    cats.forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-cat") === "all")); });
    applyFilter();
    if (search) search.focus();
  });
  if (search || cats.length) applyFilter();

  var tools = document.querySelector(".menu-tools");
  if (tools && "IntersectionObserver" in window) {
    var sentinel = document.createElement("div");
    sentinel.style.height = "1px";
    tools.parentNode.insertBefore(sentinel, tools);
    new IntersectionObserver(function (entries) {
      tools.classList.toggle("is-stuck", !entries[0].isIntersecting);
    }).observe(sentinel);
  }

  /* =========================================================
     Entrées au défilement (titre, texte, image, en cascade)
     ========================================================= */
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && !reduceMotion) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    reveals.forEach(function (el) { io.observe(el); });
    // Sécurité : tout ce qui est déjà au-dessus du bas de l'écran s'affiche, même si l'observateur rate un élément.
    var sweep = function () {
      var limit = window.innerHeight;
      reveals.forEach(function (el) {
        if (!el.classList.contains("is-in") && el.getBoundingClientRect().top < limit) el.classList.add("is-in");
      });
    };
    var sweepT = null;
    window.addEventListener("scroll", function () { clearTimeout(sweepT); sweepT = setTimeout(sweep, 250); }, { passive: true });
    window.addEventListener("load", function () { setTimeout(sweep, 400); });
  } else {
    document.documentElement.classList.add("no-io");
  }

  /* Avis : bouton pause du défilement (accessibilité) */
  document.querySelectorAll("[data-marquee-toggle]").forEach(function (btn) {
    var mq = document.querySelector("[data-marquee]");
    btn.addEventListener("click", function () {
      var paused = mq.classList.toggle("is-paused");
      btn.setAttribute("aria-pressed", String(paused));
      btn.textContent = paused ? "Reprendre le défilement" : "Mettre en pause";
    });
  });

  /* Barre mobile : cachée tant que le bouton Commander du haut est visible */
  var mbar = document.querySelector(".mbar");
  var topCta = document.querySelector(".hero__actions, .menu-hero__side, .lost__actions");
  if (mbar && "IntersectionObserver" in window) {
    var seen = new Map();
    var watch = [topCta, document.querySelector(".site-footer")].filter(Boolean);
    var mio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { seen.set(en.target, en.isIntersecting); });
      var anyVisible = false;
      seen.forEach(function (v) { if (v) anyVisible = true; });
      mbar.classList.toggle("is-hidden", anyVisible);
    });
    watch.forEach(function (el) { mio.observe(el); });
  }

  /* Année du pied de page */
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
