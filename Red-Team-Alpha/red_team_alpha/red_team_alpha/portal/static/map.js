(function () {
  "use strict";

  var dots = JSON.parse(document.getElementById("dots-data").textContent);
  var agents = JSON.parse(document.getElementById("agents-data").textContent);
  var canvas = document.getElementById("worldmap");
  var ctx = canvas.getContext("2d");
  var tip = document.getElementById("tooltip");
  var wrap = canvas.parentElement;

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var COL = {
    land: "#2b3742",
    landLit: "#44525f",
    active: "#ffffff",
    standby: "#5f6b78",
    deploy: "#d98a82"
  };

  function markerColor(s) { return s === "DEPLOYED" ? COL.deploy : s === "STANDBY" ? COL.standby : COL.active; }

  var W = 0, H = 0, dpr = Math.min(window.devicePixelRatio || 1, 2);
  var padX = 0.02, padY = 0.06;

  function px(nx) { return (padX + nx * (1 - 2 * padX)) * W; }
  function py(ny) { return (padY + ny * (1 - 2 * padY)) * H; }

  function resize() {
    W = wrap.clientWidth;
    H = Math.max(220, Math.round(W * 0.52));
    canvas.style.height = H + "px";
    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  var t0 = null;
  var SWEEP_MS = reduce ? 0 : 900;
  var PING_MS = reduce ? 0 : 1400;

  function draw(now) {
    if (t0 === null) t0 = now;
    var t = now - t0;
    ctx.clearRect(0, 0, W, H);

    var scan = reduce ? 1 : Math.min(1, t / SWEEP_MS);
    var scanX = scan * W;

    for (var i = 0; i < dots.length; i++) {
      var dx = px(dots[i][0]), dy = py(dots[i][1]);
      if (dx > scanX + 40) continue;
      var edge = dx > scanX - 40 ? 1 - (scanX - dx + 40) / 80 : 0;
      ctx.globalAlpha = 0.75;
      ctx.fillStyle = edge > 0.15 ? COL.landLit : COL.land;
      ctx.beginPath();
      ctx.arc(dx, dy, edge > 0.15 ? 1.5 : 1.1, 0, 6.2832);
      ctx.fill();
    }
    ctx.globalAlpha = 1;

    for (var a = 0; a < agents.length; a++) {
      var g = agents[a];
      var mx = px(g.x), my = py(g.y);
      var passed = reduce ? true : px(g.x) <= scanX;
      if (!passed) continue;

      var col = markerColor(g.status);
      var since = reduce ? PING_MS : t - (g.x * SWEEP_MS);
      var pingT = Math.max(0, Math.min(1, since / PING_MS));

      if (!reduce && pingT < 1) {
        ctx.globalAlpha = (1 - pingT) * 0.8;
        ctx.strokeStyle = col; ctx.lineWidth = 1;
        ctx.beginPath(); ctx.arc(mx, my, 3 + pingT * 22, 0, 6.2832); ctx.stroke();
      }

      var pulse = g.status === "STANDBY" ? 0.5
        : 0.55 + 0.45 * Math.sin(now / 620 + a);
      ctx.globalAlpha = 0.28 * (reduce ? 0.6 : pulse);
      ctx.fillStyle = col;
      ctx.beginPath(); ctx.arc(mx, my, 6.5, 0, 6.2832); ctx.fill();

      ctx.globalAlpha = 1;
      ctx.fillStyle = col;
      ctx.beginPath(); ctx.arc(mx, my, 2.6, 0, 6.2832); ctx.fill();
      ctx.fillStyle = "#ffffff";
      ctx.beginPath(); ctx.arc(mx, my, 1.1, 0, 6.2832); ctx.fill();
    }
    ctx.globalAlpha = 1;

    if (!reduce) requestAnimationFrame(draw);
  }

  function nearest(mx, my) {
    var best = null, bd = 16 * 16;
    for (var a = 0; a < agents.length; a++) {
      var g = agents[a];
      var dx = mx - px(g.x), dy = my - py(g.y);
      var d = dx * dx + dy * dy;
      if (d < bd) { bd = d; best = g; }
    }
    return best;
  }
  canvas.addEventListener("mousemove", function (e) {
    var r = canvas.getBoundingClientRect();
    var mx = e.clientX - r.left, my = e.clientY - r.top;
    var g = nearest(mx, my);
    if (g) {
      tip.innerHTML = "<b>" + g.callsign + "</b> · " + g.name +
        "<br><small>" + g.city + ", " + g.country + " · " + g.status + "</small>";
      tip.style.left = px(g.x) + "px";
      tip.style.top = py(g.y) + "px";
      tip.style.opacity = 1;
      canvas.style.cursor = "crosshair";
    } else {
      tip.style.opacity = 0; canvas.style.cursor = "default";
    }
  });
  canvas.addEventListener("mouseleave", function () { tip.style.opacity = 0; });

  var rt;
  window.addEventListener("resize", function () {
    clearTimeout(rt);
    rt = setTimeout(function () { resize(); if (reduce) { t0 = null; requestAnimationFrame(draw); } }, 120);
  });

  resize();
  requestAnimationFrame(draw);
})();
