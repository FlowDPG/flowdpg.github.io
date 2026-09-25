/* FlowDPG project page: scroll-triggered chart animation, tooltips, videos in view, rubric toggle, BibTeX copy. */
(function () {
  "use strict";
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- count-up for value labels ---------- */
  function fmt(v, dec, suf) { return v.toFixed(dec) + (suf || ""); }
  function stopCount(el) {
    if (el._cu) { clearTimeout(el._cu.t); cancelAnimationFrame(el._cu.r); el._cu = null; }
    if (el._final !== undefined) el.textContent = el._final;
  }
  function countUp(root) {
    if (reduce) return;
    root.querySelectorAll("[data-v]").forEach(function (el) {
      stopCount(el);
      if (el._final === undefined) el._final = el.textContent;
      var end = parseFloat(el.getAttribute("data-v"));
      var dec = parseInt(el.getAttribute("data-dec") || "0", 10);
      var suf = el.getAttribute("data-suf") || "";
      var delay = parseFloat(getComputedStyle(el).getPropertyValue("--d")) || 0;
      var dur = 900, t0 = null, h = { t: 0, r: 0 };
      el._cu = h;
      el.textContent = fmt(0, dec, suf);
      h.t = setTimeout(function () {
        function step(ts) {
          if (t0 === null) t0 = ts;
          var p = Math.min((ts - t0) / dur, 1);
          var e = 1 - Math.pow(1 - p, 3);
          el.textContent = p < 1 ? fmt(end * e, dec, suf) : el._final;
          if (p < 1) h.r = requestAnimationFrame(step); else el._cu = null;
        }
        h.r = requestAnimationFrame(step);
      }, Math.max(0, delay * 1000 - 350));
    });
  }

  /* ---------- play charts every time they scroll into view ---------- */
  function play(el) { el.classList.add("in"); countUp(el); }
  function reset(el) {                       // snap back (no reverse animation) once fully off screen
    el.classList.add("noanim");
    el.classList.remove("in");
    el.querySelectorAll("[data-v]").forEach(stopCount);
    void el.offsetWidth;
    el.classList.remove("noanim");
  }
  var charts = document.querySelectorAll("[data-anim]");
  if (reduce || !("IntersectionObserver" in window)) {
    charts.forEach(function (el) { el.classList.add("in"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var el = e.target;
        if (e.isIntersecting && e.intersectionRatio >= 0.3) { if (!el.classList.contains("in")) play(el); }
        else if (!e.isIntersecting) { if (el.classList.contains("in")) reset(el); }
      });
    }, { threshold: [0, 0.3] });
    charts.forEach(function (el) { io.observe(el); });
  }

  /* ---------- tooltip ---------- */
  var tip = document.createElement("div");
  tip.className = "tip"; tip.setAttribute("role", "status");
  document.body.appendChild(tip);
  function place(ev) {
    var pad = 14, w = tip.offsetWidth, h = tip.offsetHeight;
    var x = ev.clientX + pad, y = ev.clientY - h - pad;
    if (x + w > window.innerWidth - 8) x = ev.clientX - w - pad;
    if (y < 8) y = ev.clientY + pad;
    tip.style.left = x + "px"; tip.style.top = y + "px";
  }
  function simpleTip(text) {
    var parts = text.split("|");
    tip.textContent = "";
    var v = document.createElement("span"); v.className = "v"; v.textContent = parts[1] || "";
    var k = document.createElement("span"); k.className = "k"; k.textContent = parts[0];
    tip.appendChild(v); tip.appendChild(k);
  }
  document.addEventListener("pointermove", function (ev) {
    var t = ev.target.closest && ev.target.closest("[data-tip]");
    if (t) { simpleTip(t.getAttribute("data-tip")); tip.classList.add("on"); place(ev); }
    else if (!ev.target.closest || !ev.target.closest(".lhit")) tip.classList.remove("on");
  });
  document.addEventListener("pointerleave", function () { tip.classList.remove("on"); });

  /* ---------- crosshair on line panels ---------- */
  document.querySelectorAll(".lhit").forEach(function (r) {
    var m = JSON.parse(r.getAttribute("data-lines"));
    var svg = r.ownerSVGElement, xh = svg.querySelector(".xh");
    var ln = xh.querySelector(".xh-l"), dots = xh.querySelectorAll(".xh-d");
    function show(ev) {
      var pt = svg.createSVGPoint(); pt.x = ev.clientX; pt.y = ev.clientY;
      var p = pt.matrixTransform(svg.getScreenCTM().inverse());
      var xv = Math.max(0, Math.min(m.xmax, (p.x - m.x0) / (m.x1 - m.x0) * m.xmax));
      var xs = m.s[0].x, i = 0, best = 1e9;
      for (var j = 0; j < xs.length; j++) { var dd = Math.abs(xs[j] - xv); if (dd < best) { best = dd; i = j; } }
      var X = m.x0 + (m.x1 - m.x0) * xs[i] / m.xmax;
      ln.setAttribute("x1", X); ln.setAttribute("x2", X);
      tip.textContent = "";
      var hd = document.createElement("div"); hd.className = "hd"; hd.textContent = "step " + xs[i].toFixed(1) + "k";
      tip.appendChild(hd);
      m.s.forEach(function (s, k) {
        var y = s.y[i], Y = m.yb - (m.yb - m.yt) * y / m.top;
        dots[k].setAttribute("cx", X); dots[k].setAttribute("cy", Y);
        var row = document.createElement("div"); row.className = "row";
        var key = document.createElement("i"); key.style.background = s.c;
        var b = document.createElement("b"); b.textContent = y.toFixed(3);
        var n = document.createElement("span"); n.className = "k"; n.textContent = s.n;
        row.appendChild(key); row.appendChild(b); row.appendChild(n); tip.appendChild(row);
      });
      xh.classList.add("on"); tip.classList.add("on"); place(ev);
    }
    r.addEventListener("pointermove", show);
    r.addEventListener("pointerleave", function () { xh.classList.remove("on"); tip.classList.remove("on"); });
  });

  /* ---------- play videos only while visible ---------- */
  var vids = document.querySelectorAll("video[data-autoplay]");
  if ("IntersectionObserver" in window) {
    var vo = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var v = e.target;
        if (e.isIntersecting) { var p = v.play(); if (p && p.catch) p.catch(function () {}); }
        else v.pause();
      });
    }, { threshold: 0.35 });
    vids.forEach(function (v) { v.muted = true; vo.observe(v); });
  }

  /* ---------- rubric toggle opens when linked to ---------- */
  function openFromHash() {
    if (location.hash === "#rubrics") {
      var d = document.getElementById("rubrics");
      if (d && d.tagName === "DETAILS") d.open = true;
    }
  }
  window.addEventListener("hashchange", openFromHash); openFromHash();
  document.querySelectorAll('a[href="#rubrics"]').forEach(function (a) {
    a.addEventListener("click", function () { var d = document.getElementById("rubrics"); if (d) d.open = true; });
  });

  /* ---------- BibTeX copy ---------- */
  var cb = document.getElementById("copy-bib");
  if (cb) cb.addEventListener("click", function () {
    var txt = document.getElementById("bibtex-code").textContent;
    function done() { cb.textContent = "Copied"; cb.classList.add("done"); setTimeout(function () { cb.textContent = "Copy"; cb.classList.remove("done"); }, 1600); }
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(txt).then(done, fallback);
    else fallback();
    function fallback() {
      var ta = document.createElement("textarea"); ta.value = txt; ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy"); done(); } catch (e) {}
      document.body.removeChild(ta);
    }
  });

  /* ---------- top bar: border on scroll, active section ---------- */
  var bar = document.querySelector(".topbar");
  function onScroll() { if (bar) bar.classList.toggle("scrolled", window.scrollY > 8); }
  window.addEventListener("scroll", onScroll, { passive: true }); onScroll();
  var links = {};
  document.querySelectorAll(".topbar nav a").forEach(function (a) { links[a.getAttribute("href").slice(1)] = a; });
  if ("IntersectionObserver" in window) {
    var so = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var a = links[e.target.id];
        if (a && e.isIntersecting) {
          Object.keys(links).forEach(function (k) { links[k].classList.remove("active"); });
          a.classList.add("active");
        }
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    Object.keys(links).forEach(function (id) { var s = document.getElementById(id); if (s) so.observe(s); });
  }
})();
