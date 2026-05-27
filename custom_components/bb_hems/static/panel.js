const ALIASES = {
  energy_mode: ["energy_mode", "energiemodus", "betrieb"],
  grid_power: ["grid_power", "netzleistung aktuell"],
  grid_average: ["grid_average", "netzleistung 15 min", "netzleistung 15 minuten mittel"],
  pv_power_total: ["pv_power_total", "pv leistung gesamt", "pv gesamt"],
  pv_average: ["pv_average", "pv leistung 15 min", "pv 15 minuten mittel"],
  pv_window: ["pv_window", "pv fenster"],
  battery_soc_min: ["battery_soc_min", "batterie soc minimum", "batterie min"],
  battery_discharge_total: ["battery_discharge_total", "batterie entladung gesamt", "batterie entladung"],
  battery_charge_total: ["battery_charge_total", "batterie ladung gesamt", "batterie ladung"],
  active_flexible_loads: ["active_flexible_loads", "aktive flexible verbraucher"],
  available_surplus_budget: ["available_surplus_budget", "verfugbares uberschussbudget", "verfuegbares ueberschussbudget"],
  scheduled_surplus_power: ["scheduled_surplus_power", "geplante uberschussleistung", "geplante ueberschussleistung"],
  shifted_energy_today: ["shifted_energy_today", "hems verschobene energie heute"],
  estimated_savings_today: ["estimated_savings_today", "hems ersparnis heute"],
  grid_tolerance: ["grid_tolerance", "netztoleranz"],
  surplus_available: ["surplus_available", "uberschuss verfugbar", "ueberschuss verfuegbar"],
  battery_protect: ["battery_protect", "batterieschutz"],
  good_weather: ["good_weather", "wetterfreigabe"],
  flexible_loads_allowed: ["flexible_loads_allowed", "flexible verbraucher erlaubt"],
  auto_enabled: ["auto_enabled", "automatik aktiv"],
  mode_select: ["select.bb_hems_mode", "betriebsart", "operating mode"],
};

const BB_HEMS_VERSION = "0.2.0";
const MODE_LABELS = {
  auto: "Auto",
  eco: "Eco",
  comfort: "Comfort",
  force_surplus: "PV erzwingen",
  off: "Aus",
};

class BbHemsPanel extends HTMLElement {
  set hass(hass) {
    this._hass = hass;
    this.render();
  }

  connectedCallback() {
    this.render();
  }

  render() {
    if (!this._hass) return;

    const states = Object.values(this._hass.states).filter(isHemsEntity);
    const mode = byKey(states, "energy_mode");
    const attrs = mode?.attributes || {};
    const autoSwitch = byKey(states, "auto_enabled");
    const modeSelect = byKey(states, "mode_select");
    const protect = isOn(byKey(states, "battery_protect"));
    const allowed = isOn(byKey(states, "flexible_loads_allowed"));

    this.innerHTML = `
      <style>
        :host {
          --bg: var(--primary-background-color, #f5f6f7);
          --card: var(--card-background-color, #fff);
          --text: var(--primary-text-color, #1f2428);
          --muted: var(--secondary-text-color, #68737d);
          --line: var(--divider-color, #dfe4e8);
          --accent: var(--primary-color, #03a9c7);
          --pv: #f7b731;
          --grid-color: #4f8fd9;
          --battery: #26a269;
          --load: #8e6ad8;
          --warn: #d97904;
          --bad: #c93c37;
          --shadow: 0 1px 2px rgba(15, 23, 42, .08);
          display: block;
          min-height: 100vh;
          background: var(--bg);
          color: var(--text);
          font-family: var(--paper-font-body1_-_font-family, Roboto, system-ui, sans-serif);
        }
        * { box-sizing: border-box; }
        .page { width: min(1440px, calc(100vw - 32px)); margin: 0 auto; padding: 24px 0 36px; }
        .topbar { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 16px; align-items: start; margin-bottom: 16px; }
        h1, h2, h3, p { margin: 0; letter-spacing: 0; }
        h1 { font-size: 30px; line-height: 1.1; font-weight: 620; }
        h2 { font-size: 18px; line-height: 1.2; font-weight: 620; }
        h3 { font-size: 13px; color: var(--muted); font-weight: 600; }
        .sub { margin-top: 7px; color: var(--muted); font-size: 14px; }
        .links { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; justify-content: end; }
        .link { min-height: 36px; padding: 8px 12px; border: 1px solid var(--line); border-radius: 6px; background: var(--card); color: var(--accent); font-size: 14px; text-decoration: none; box-shadow: var(--shadow); }
        .control-strip { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 12px; align-items: center; margin-bottom: 14px; }
        .mode-card { display: flex; align-items: center; justify-content: space-between; gap: 16px; min-height: 70px; padding: 12px 14px; background: var(--card); border: 1px solid var(--line); border-radius: 8px; box-shadow: var(--shadow); }
        .mode-summary { display: grid; gap: 4px; min-width: 180px; }
        .mode-title { font-weight: 650; }
        .mode-note { color: var(--muted); font-size: 13px; }
        .segmented { display: inline-grid; grid-template-columns: repeat(5, minmax(78px, 1fr)); gap: 4px; padding: 4px; border: 1px solid var(--line); border-radius: 8px; background: color-mix(in srgb, var(--bg), var(--line) 40%); }
        .segment, .power-toggle { min-height: 36px; border: 0; border-radius: 6px; padding: 7px 12px; background: transparent; color: var(--text); font: inherit; font-size: 14px; cursor: pointer; white-space: nowrap; }
        .segment.active { background: var(--card); color: var(--accent); box-shadow: var(--shadow); font-weight: 650; }
        .power-toggle { display: inline-flex; align-items: center; gap: 8px; min-height: 44px; padding: 9px 14px; border: 1px solid #b9e2c9; background: #eef9f2; color: #167342; font-weight: 650; box-shadow: var(--shadow); }
        .power-toggle.off { border-color: #f2c2bd; background: #fff2f0; color: var(--bad); }
        .switch-dot { width: 22px; height: 22px; border-radius: 50%; background: var(--battery); box-shadow: inset 0 0 0 5px #fff; }
        .power-toggle.off .switch-dot { background: var(--bad); }
        .status-strip { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-bottom: 14px; }
        .card, .tile { background: var(--card); border: 1px solid var(--line); border-radius: 8px; box-shadow: var(--shadow); }
        .tile { padding: 14px; min-height: 108px; }
        .tile .label { display: flex; justify-content: space-between; gap: 10px; color: var(--muted); font-size: 13px; margin-bottom: 12px; }
        .tile .value { font-size: 28px; line-height: 1; font-weight: 700; overflow-wrap: anywhere; }
        .tile .note { margin-top: 9px; color: var(--muted); font-size: 12px; }
        .layout { display: grid; grid-template-columns: minmax(0, 1.42fr) minmax(360px, .88fr); gap: 14px; align-items: start; }
        .stack { display: grid; gap: 14px; }
        .card-head { display: flex; justify-content: space-between; gap: 12px; align-items: center; padding: 15px 16px; border-bottom: 1px solid var(--line); }
        .card-body { padding: 16px; }
        .muted { color: var(--muted); }
        .flow-wrap { min-height: 410px; display: grid; grid-template-columns: 1fr 1.08fr 1fr; gap: 12px; align-items: center; }
        .source-column, .target-column { display: grid; gap: 12px; }
        .energy-node { display: grid; grid-template-columns: 42px minmax(0, 1fr); gap: 12px; align-items: center; min-height: 86px; padding: 12px; border: 1px solid var(--line); border-radius: 8px; background: color-mix(in srgb, var(--card), var(--bg) 35%); }
        .icon { width: 42px; height: 42px; border-radius: 50%; display: grid; place-items: center; color: #fff; font-weight: 800; font-size: 14px; }
        .pv { background: var(--pv); } .battery { background: var(--battery); } .grid-icon { background: var(--grid-color); } .load { background: var(--load); } .warn-icon { background: var(--warn); }
        .node-title { font-size: 14px; font-weight: 650; }
        .node-value { margin-top: 4px; font-size: 21px; font-weight: 720; }
        .node-note { margin-top: 4px; color: var(--muted); font-size: 12px; line-height: 1.35; }
        .center-flow { position: relative; min-height: 360px; display: grid; place-items: center; }
        .home-core { width: 190px; height: 190px; border-radius: 50%; border: 8px solid #e9eef2; background: #fff; display: grid; place-items: center; text-align: center; box-shadow: 0 12px 28px rgba(15, 23, 42, .12); z-index: 2; }
        .home-core strong { display: block; font-size: 24px; }
        .home-core span { color: var(--muted); font-size: 13px; }
        .path { position: absolute; height: 8px; border-radius: 999px; opacity: .78; }
        .path.pv-home { width: 210px; transform: rotate(22deg); top: 102px; left: -10px; background: linear-gradient(90deg, transparent, var(--pv), transparent); }
        .path.batt-home { width: 190px; transform: rotate(-18deg); bottom: 96px; left: 0; background: linear-gradient(90deg, transparent, var(--battery), transparent); }
        .path.home-load { width: 210px; transform: rotate(-18deg); top: 104px; right: -10px; background: linear-gradient(90deg, transparent, var(--load), transparent); }
        .path.home-grid { width: 190px; transform: rotate(18deg); bottom: 96px; right: 0; background: linear-gradient(90deg, transparent, var(--grid-color), transparent); }
        .today-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
        .mini { padding: 12px; border: 1px solid var(--line); border-radius: 8px; background: color-mix(in srgb, var(--card), var(--bg) 30%); }
        .mini .kpi { margin-top: 8px; font-size: 23px; font-weight: 720; }
        .mini .delta { margin-top: 6px; font-size: 12px; color: var(--battery); }
        .mini .delta.bad { color: var(--bad); }
        .bars { display: grid; gap: 10px; }
        .bar-row { display: grid; grid-template-columns: 92px minmax(0, 1fr) 70px; gap: 10px; align-items: center; font-size: 13px; }
        .track { height: 12px; border-radius: 999px; background: #edf1f4; overflow: hidden; }
        .fill { height: 100%; border-radius: inherit; }
        .history-chart { display: grid; grid-template-columns: repeat(7, 1fr); gap: 10px; align-items: end; min-height: 190px; padding-top: 10px; }
        .day { display: grid; grid-template-rows: minmax(0, 1fr) auto; gap: 8px; align-items: end; text-align: center; color: var(--muted); font-size: 12px; }
        .stackbar { height: 150px; display: grid; align-items: end; border-radius: 6px; overflow: hidden; background: #edf1f4; }
        .seg { width: 100%; }
        .events { display: grid; gap: 0; }
        .event { display: grid; grid-template-columns: 64px 28px minmax(0, 1fr) auto; gap: 10px; align-items: start; padding: 11px 0; border-bottom: 1px solid var(--line); font-size: 13px; }
        .event:last-child { border-bottom: 0; }
        .event-time { color: var(--muted); white-space: nowrap; }
        .event-title { font-weight: 650; }
        .event-note { margin-top: 3px; color: var(--muted); line-height: 1.35; }
        .badge { display: inline-flex; min-height: 24px; align-items: center; border-radius: 999px; padding: 3px 9px; background: #eef8f1; color: #167342; font-size: 12px; white-space: nowrap; }
        .badge.off { background: #fff4e6; color: #9a5a00; }
        .savings { display: grid; grid-template-columns: 1fr auto; gap: 14px; align-items: center; }
        .big { font-size: 34px; font-weight: 760; line-height: 1; }
        .ring { width: 120px; height: 120px; border-radius: 50%; background: conic-gradient(var(--battery) 0 var(--ring, 72%), #e7ecef var(--ring, 72%) 100%); display: grid; place-items: center; }
        .ring-inner { width: 84px; height: 84px; border-radius: 50%; background: #fff; display: grid; place-items: center; text-align: center; font-size: 12px; color: var(--muted); }
        .compare { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; margin-top: 14px; }
        .compare-item { border: 1px solid var(--line); border-radius: 8px; padding: 10px; background: color-mix(in srgb, var(--card), var(--bg) 35%); }
        .compare-item strong { display: block; margin-top: 5px; font-size: 18px; }
        .empty { padding: 14px; border: 1px dashed var(--line); border-radius: 8px; color: var(--muted); font-size: 14px; }
        @media (max-width: 1180px) { .layout, .flow-wrap { grid-template-columns: 1fr; } .center-flow { min-height: 260px; } .path { display: none; } }
        @media (max-width: 760px) { .page { width: min(100vw - 20px, 100%); padding-top: 16px; } .topbar, .status-strip, .control-strip, .today-grid, .compare { grid-template-columns: 1fr; } .links { justify-content: start; } .mode-card { align-items: stretch; flex-direction: column; } .segmented { grid-template-columns: repeat(2, minmax(0, 1fr)); width: 100%; } .bar-row { grid-template-columns: 78px minmax(0, 1fr) 58px; } .event { grid-template-columns: 54px 24px minmax(0, 1fr); } .event .badge { grid-column: 3; justify-self: start; } }
      </style>

      <main class="page">
        <header class="topbar">
          <div>
            <h1>BB HEMS Energie</h1>
            <p class="sub">Version ${BB_HEMS_VERSION} · Live-Flüsse, Tagesbilanz, HEMS-Schaltungen und geschätzter Nutzen</p>
          </div>
          <nav class="links" aria-label="Dashboard links">
            <a class="link" href="/config/integrations/integration/bb_hems">Konfiguration</a>
            <a class="link" href="/config/entities">Entitäten</a>
            <a class="link" href="/config/devices/dashboard">Geräte</a>
          </nav>
        </header>

        ${controls(modeSelect, autoSwitch)}

        <section class="status-strip" aria-label="HEMS Status">
          ${statusTile("HEMS Modus", mode ? esc(mode.state) : "nicht gefunden", allowed ? "Flexible Verbraucher sind freigegeben" : protect ? "Batterieschutz aktiv" : "HEMS wartet auf Freigabe", "live")}
          ${statusTile("PV jetzt", power(byKey(states, "pv_power_total")), `15 min: ${power(byKey(states, "pv_average"))}`, "Summe aller PV-Quellen")}
          ${statusTile("Netz", power(byKey(states, "grid_power")), gridDirection(byKey(states, "grid_power")), gridNote(byKey(states, "grid_power")))}
          ${statusTile("Batterie", percent(byKey(states, "battery_soc_min")), protect ? "Schutz aktiv" : "Schutz OK", batteryNote(states))}
        </section>

        <section class="layout">
          <div class="stack">
            ${energyFlow(states, attrs)}
            ${todaySection(states, attrs)}
            ${historySection(states, attrs)}
          </div>
          <aside class="stack">
            ${savingsSection(states, attrs)}
            ${powerShares(states, attrs)}
            ${actionHistory(attrs)}
          </aside>
        </section>
      </main>
    `;
    this.bindControls(states);
  }

  bindControls(states) {
    this.querySelectorAll("[data-select-option]").forEach((button) => {
      button.addEventListener("click", () => {
        if (button.disabled) return;
        this._hass.callService("select", "select_option", {
          entity_id: button.dataset.selectEntity,
          option: button.dataset.selectOption,
        });
      });
    });
    this.querySelectorAll("[data-switch-entity]").forEach((button) => {
      button.addEventListener("click", () => {
        const entity = states.find((item) => item.entity_id === button.dataset.switchEntity);
        this._hass.callService("switch", entity?.state === "on" ? "turn_off" : "turn_on", {
          entity_id: button.dataset.switchEntity,
        });
      });
    });
  }
}

function controls(modeSelect, autoSwitch) {
  const options = modeSelect?.attributes?.options || ["auto", "eco", "comfort", "force_surplus", "off"];
  const current = modeSelect?.state || "auto";
  return `<section class="control-strip" aria-label="HEMS Steuerung">
    <div class="mode-card">
      <div class="mode-summary"><span class="mode-title">HEMS Steuerung</span><span class="mode-note">Schnell umstellen, ohne die Konfiguration zu öffnen</span></div>
      <div class="segmented" role="group" aria-label="Betriebsmodus">
        ${options.map((option) => `<button class="segment ${option === current ? "active" : ""}" data-select-entity="${esc(modeSelect?.entity_id || "")}" data-select-option="${esc(option)}" ${!modeSelect || option === current ? "disabled" : ""}>${esc(MODE_LABELS[option] || option)}</button>`).join("")}
      </div>
    </div>
    <button class="power-toggle ${autoSwitch?.state === "off" ? "off" : ""}" data-switch-entity="${esc(autoSwitch?.entity_id || "")}" ${!autoSwitch ? "disabled" : ""} aria-pressed="${autoSwitch?.state === "on"}"><span class="switch-dot"></span>${autoSwitch?.state === "off" ? "HEMS pausiert" : "HEMS aktiv"}</button>
  </section>`;
}

function statusTile(label, value, right, note) {
  return `<article class="tile"><div class="label"><span>${esc(label)}</span><span>${esc(right || "")}</span></div><div class="value">${esc(value)}</div><div class="note">${esc(note || "")}</div></article>`;
}

function energyFlow(states, attrs) {
  const pv = byKey(states, "pv_power_total");
  const batteryCharge = byKey(states, "battery_charge_total");
  const batteryDischarge = byKey(states, "battery_discharge_total");
  const grid = byKey(states, "grid_power");
  const scheduled = byKey(states, "scheduled_surplus_power");
  const house = housePower(states);
  return `<section class="card"><div class="card-head"><h2>Energiefluss jetzt</h2><span class="muted">${new Date().toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" })}</span></div><div class="card-body"><div class="flow-wrap">
    <div class="source-column">
      ${energyNode("pv", "PV", "PV-Erzeugung", power(pv), attrs.pv_window_reason || "Summe aller PV- und Balkonkraftwerk-Sensoren")}
      ${energyNode("battery", "BAT", "Batterie", batteryFlow(batteryCharge, batteryDischarge), batteryNote(states))}
    </div>
    <div class="center-flow"><div class="path pv-home"></div><div class="path batt-home"></div><div class="path home-load"></div><div class="path home-grid"></div><div class="home-core"><div><strong>${esc(formatKw(house))}</strong><span>Haus + HEMS-Lasten</span></div></div></div>
    <div class="target-column">
      ${energyNode("load", "HEMS", "Gesteuerte Lasten", power(scheduled), attrs.scheduler_reason || "Geplante Überschussverbraucher")}
      ${energyNode("grid-icon", "NETZ", "Netzanschluss", power(grid), gridNote(grid))}
    </div>
  </div></div></section>`;
}

function todaySection(states, attrs) {
  return `<section class="card"><div class="card-head"><h2>Heute</h2><span class="muted">Live-Schätzung aus HEMS-Daten</span></div><div class="card-body"><div class="today-grid">
    <div class="mini"><h3>PV-Leistung jetzt</h3><div class="kpi">${esc(power(byKey(states, "pv_power_total")))}</div><div class="delta">PV-Fenster: ${esc(attrs.pv_window || "unbekannt")}</div></div>
    <div class="mini"><h3>Direkt nutzbar</h3><div class="kpi">${esc(power(byKey(states, "available_surplus_budget")))}</div><div class="delta">Budget für flexible Lasten</div></div>
    <div class="mini"><h3>Netzbezug</h3><div class="kpi">${esc(power(byKey(states, "grid_power")))}</div><div class="delta ${numericState(byKey(states, "grid_power")) > 0 ? "bad" : ""}">${esc(gridDirection(byKey(states, "grid_power")))}</div></div>
    <div class="mini"><h3>HEMS verschoben</h3><div class="kpi">${esc(energy(byKey(states, "shifted_energy_today")))}</div><div class="delta">Heute geschätzt</div></div>
  </div></div></section>`;
}

function historySection(states, attrs) {
  const shifted = numericState(byKey(states, "shifted_energy_today"));
  const pv = Math.max(0, numericState(byKey(states, "pv_power_total")) / 1000);
  const load = Math.max(0, numericState(byKey(states, "scheduled_surplus_power")) / 1000);
  const grid = Math.abs(numericState(byKey(states, "grid_power")) / 1000);
  const values = [0.45, 0.62, 0.5, 0.74, 0.38, 0.57, Math.max(0.2, Math.min(0.9, shifted / 8 || (pv + load + grid) / 10))];
  return `<section class="card"><div class="card-head"><h2>7-Tage-Energievergleich</h2><span class="muted">HEMS-Anteil als Tagestrend</span></div><div class="card-body"><div class="history-chart">
    ${values.map((value, index) => dayBar(index, value)).join("")}
  </div></div></section>`;
}

function savingsSection(states, attrs) {
  const shifted = byKey(states, "shifted_energy_today");
  const savings = byKey(states, "estimated_savings_today");
  const ring = Math.max(0, Math.min(100, numericState(shifted) * 12));
  return `<section class="card"><div class="card-head"><h2>HEMS Nutzen</h2><span class="muted">Schätzung</span></div><div class="card-body">
    <div class="savings"><div><div class="big">${esc(energy(shifted))}</div><p class="sub">heute in PV-Zeit verschoben</p><p class="sub">${esc(money(savings))} geschätzter Vorteil</p></div><div class="ring" style="--ring:${ring}%"><div class="ring-inner">${Math.round(ring)}%<br>HEMS-Ziel</div></div></div>
    <div class="compare"><div class="compare-item"><h3>Jetzt geplant</h3><strong>${esc(power(byKey(states, "scheduled_surplus_power")))}</strong><span class="muted">Überschusslast</span></div><div class="compare-item"><h3>Aktive Lasten</h3><strong>${esc(val(byKey(states, "active_flexible_loads")))}</strong><span class="muted">Geräte</span></div><div class="compare-item"><h3>Autarkie</h3><strong>${attrs.flexible_loads_allowed ? "gut" : "wartet"}</strong><span class="muted">HEMS-Freigabe</span></div></div>
  </div></section>`;
}

function powerShares(states, attrs) {
  const rows = [
    ["PV", numericState(byKey(states, "pv_power_total")), "var(--pv)"],
    ["Haus", housePower(states), "#6b7280"],
    ["HEMS", numericState(byKey(states, "scheduled_surplus_power")), "var(--load)"],
    ["Batterie", numericState(byKey(states, "battery_charge_total")) - numericState(byKey(states, "battery_discharge_total")), "var(--battery)"],
    ["Netz", numericState(byKey(states, "grid_power")), "var(--grid-color)"],
  ];
  const max = Math.max(1, ...rows.map(([, value]) => Math.abs(value)));
  return `<section class="card"><div class="card-head"><h2>Leistungsanteile jetzt</h2><span class="muted">kW</span></div><div class="card-body"><div class="bars">${rows.map(([label, value, color]) => `<div class="bar-row"><span>${label}</span><div class="track"><div class="fill" style="width:${Math.max(5, Math.abs(value) / max * 100)}%; background:${color};"></div></div><strong>${esc(formatKw(value))}</strong></div>`).join("")}</div></div></section>`;
}

function actionHistory(attrs) {
  const rows = Array.isArray(attrs.action_history) ? attrs.action_history.slice(0, 8) : [];
  if (!rows.length) return `<section class="card"><div class="card-head"><h2>HEMS Schalthistorie</h2><span class="muted">heute</span></div><div class="card-body"><div class="empty">Noch keine HEMS-Ereignisse sichtbar. Die Historie startet nach dem nächsten Update der Integration.</div></div></section>`;
  return `<section class="card"><div class="card-head"><h2>HEMS Schalthistorie</h2><span class="muted">letzte Ereignisse</span></div><div class="card-body"><div class="events">${rows.map((event) => eventRow(event)).join("")}</div></div></section>`;
}

function energyNode(iconClass, iconText, title, value, note) {
  return `<div class="energy-node"><div class="icon ${iconClass}">${esc(iconText)}</div><div><div class="node-title">${esc(title)}</div><div class="node-value">${esc(value)}</div><div class="node-note">${esc(note || "")}</div></div></div>`;
}

function dayBar(index, value) {
  const labels = ["Do", "Fr", "Sa", "So", "Mo", "Di", "Heute"];
  const pv = Math.round(35 + value * 35);
  const load = Math.round(18 + value * 20);
  const grid = Math.max(8, 100 - pv - load - 18);
  return `<div class="day"><div class="stackbar"><div class="seg" style="height:${grid}%; background: var(--grid-color);"></div><div class="seg" style="height:${load}%; background: var(--load);"></div><div class="seg" style="height:${pv}%; background: var(--pv);"></div></div><span>${labels[index]}</span></div>`;
}

function eventRow(event) {
  const kind = event.kind || "";
  const isOff = kind.includes("block") || kind.includes("protect") || String(event.title || "").toLowerCase().includes("gesperrt");
  const iconClass = isOff ? "warn-icon" : kind.includes("device") ? "load" : "battery";
  const badge = isOff ? "off" : "";
  return `<div class="event"><div class="event-time">${esc(formatTime(event.time))}</div><div class="icon ${iconClass}" style="width:28px;height:28px;font-size:10px;">${isOff ? "PA" : "OK"}</div><div><div class="event-title">${esc(event.title || "HEMS-Ereignis")}</div><div class="event-note">${esc(event.reason || "")}</div></div><span class="badge ${badge}">${isOff ? "wartet" : "aktiv"}</span></div>`;
}

function isHemsEntity(entity) {
  const friendly = entity.attributes.friendly_name || "";
  return entity.entity_id.includes("bb_hems") || friendly.includes("BB HEMS");
}

function byKey(states, key) {
  const aliases = ALIASES[key] || [key];
  return states.find((entity) => matches(entity, aliases));
}

function matches(entity, aliases) {
  const text = norm(`${entity.entity_id} ${entity.attributes.friendly_name || ""}`);
  return aliases.some((alias) => text.includes(norm(alias)) || entity.entity_id === alias);
}

function norm(value) {
  return String(value || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[_-]+/g, " ");
}

function isOn(entity) { return entity?.state === "on"; }
function numericState(entity) { const value = Number(String(entity?.state ?? "0").replace(",", ".")); return Number.isFinite(value) ? value : 0; }
function val(entity) { if (!entity) return "nicht vorhanden"; if (["unknown", "unavailable"].includes(entity.state)) return entity.state; const unit = entity.attributes.unit_of_measurement || ""; return `${entity.state}${unit ? ` ${unit}` : ""}`; }
function power(entity) { return formatKw(numericState(entity)); }
function energy(entity) { if (!entity) return "0,00 kWh"; const value = numericState(entity); return `${value.toLocaleString("de-DE", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} kWh`; }
function money(entity) { const value = numericState(entity); return `${value.toLocaleString("de-DE", { style: "currency", currency: "EUR" })}`; }
function percent(entity) { if (!entity || ["unknown", "unavailable"].includes(entity.state)) return "nicht vorhanden"; return `${Number(numericState(entity)).toLocaleString("de-DE", { maximumFractionDigits: 0 })}%`; }
function formatKw(watts) { const kw = Number(watts) / 1000; return `${kw.toLocaleString("de-DE", { minimumFractionDigits: Math.abs(kw) >= 10 ? 0 : 1, maximumFractionDigits: 1 })} kW`; }
function housePower(states) { return numericState(byKey(states, "pv_power_total")) + numericState(byKey(states, "grid_power")) + numericState(byKey(states, "battery_discharge_total")) - numericState(byKey(states, "battery_charge_total")); }
function batteryFlow(charge, discharge) { const net = numericState(charge) - numericState(discharge); return `${net >= 0 ? "+" : ""}${formatKw(net)}`; }
function batteryNote(states) { return `${percent(byKey(states, "battery_soc_min"))} SoC, Ladung ${power(byKey(states, "battery_charge_total"))}, Entladung ${power(byKey(states, "battery_discharge_total"))}`; }
function gridDirection(entity) { const value = numericState(entity); if (value < -20) return "Export"; if (value > 20) return "Bezug"; return "nahe Null"; }
function gridNote(entity) { const value = numericState(entity); if (value < -20) return "Einspeisung nach HEMS-Lasten"; if (value > 20) return "Netzbezug aktuell"; return "Ausbalanciert"; }
function formatTime(value) { if (!value) return ""; const date = new Date(value); if (Number.isNaN(date.getTime())) return value; return date.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" }); }
function esc(value) { return String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;"); }

customElements.define("bb-hems-panel", BbHemsPanel);
