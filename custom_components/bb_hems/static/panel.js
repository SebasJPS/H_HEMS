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
  surplus_available: ["surplus_available", "uberschuss verfugbar", "ueberschuss verfuegbar"],
  battery_protect: ["battery_protect", "batterieschutz"],
  flexible_loads_allowed: ["flexible_loads_allowed", "flexible verbraucher erlaubt"],
  auto_enabled: ["auto_enabled", "automatik aktiv"],
  mode_select: ["select.bb_hems_mode", "betriebsart", "operating mode"],
};

const BB_HEMS_VERSION = "0.2.1";
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

    this.innerHTML = `
      <style>
        :host {
          --bg: var(--primary-background-color, #f7f8fa);
          --card: var(--card-background-color, #fff);
          --text: var(--primary-text-color, #202124);
          --muted: var(--secondary-text-color, #6b7280);
          --line: var(--divider-color, #e0e0e0);
          --accent: var(--primary-color, #03a9c7);
          --pv: #ff9800;
          --home: #43a047;
          --grid: #4b95d9;
          --battery: #26b6a8;
          --co2: #20a65a;
          --hems: #8a56d9;
          --pink: #f06292;
          --shadow: 0 1px 2px rgba(60, 64, 67, .12);
          display: block;
          min-height: 100vh;
          background: var(--bg);
          color: var(--text);
          font-family: var(--paper-font-body1_-_font-family, Roboto, system-ui, sans-serif);
        }
        * { box-sizing: border-box; }
        h1, h2, h3, p { margin: 0; letter-spacing: 0; }
        button { font: inherit; }
        .tabs {
          position: sticky;
          top: 0;
          z-index: 3;
          display: flex;
          justify-content: space-between;
          gap: 16px;
          min-height: 68px;
          padding: 0 24px;
          border-bottom: 1px solid var(--line);
          background: var(--card);
        }
        .tab-list { display: flex; align-items: stretch; gap: 22px; }
        .tab {
          display: inline-flex;
          align-items: center;
          padding: 0 2px;
          border-bottom: 3px solid transparent;
          color: var(--muted);
          font-weight: 600;
          text-decoration: none;
        }
        .tab.active { color: var(--text); border-bottom-color: var(--text); }
        .actions { display: flex; align-items: center; gap: 10px; }
        .icon-button {
          width: 38px;
          height: 38px;
          display: grid;
          place-items: center;
          border: 0;
          border-radius: 50%;
          background: transparent;
          color: var(--text);
          font-size: 24px;
          text-decoration: none;
        }
        .page { width: min(1920px, calc(100vw - 48px)); margin: 0 auto; padding: 28px 0 40px; }
        .control-strip {
          display: grid;
          grid-template-columns: minmax(0, 1fr) auto;
          gap: 12px;
          align-items: center;
          margin-bottom: 18px;
        }
        .mode-card, .power-toggle, .card {
          background: var(--card);
          border: 1px solid var(--line);
          border-radius: 14px;
          box-shadow: var(--shadow);
        }
        .mode-card {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 18px;
          min-height: 68px;
          padding: 10px 14px 10px 18px;
        }
        .mode-title { font-weight: 650; }
        .mode-note { margin-top: 4px; color: var(--muted); font-size: 13px; }
        .segmented {
          display: inline-grid;
          grid-template-columns: repeat(5, minmax(86px, 1fr));
          gap: 4px;
          padding: 4px;
          border: 1px solid var(--line);
          border-radius: 10px;
          background: #f0f2f4;
        }
        .segment {
          min-height: 36px;
          border: 0;
          border-radius: 8px;
          padding: 7px 12px;
          background: transparent;
          color: var(--text);
          cursor: pointer;
          white-space: nowrap;
        }
        .segment.active {
          background: var(--card);
          color: var(--accent);
          box-shadow: var(--shadow);
          font-weight: 650;
        }
        .power-toggle {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          min-height: 48px;
          padding: 9px 16px;
          color: #167342;
          font-weight: 650;
          border-color: #b9e2c9;
          background: #eef9f2;
          cursor: pointer;
          white-space: nowrap;
        }
        .power-toggle.off { color: #c93c37; border-color: #f2c2bd; background: #fff2f0; }
        .switch-dot { width: 20px; height: 20px; border-radius: 50%; background: #26a269; box-shadow: inset 0 0 0 5px #fff; }
        .power-toggle.off .switch-dot { background: #c93c37; }
        .dashboard-grid {
          display: grid;
          grid-template-columns: minmax(0, 3.2fr) minmax(360px, 1fr);
          gap: 28px;
          align-items: start;
        }
        .main-column, .side-column { display: grid; gap: 12px; }
        .card { overflow: hidden; }
        .card-head {
          display: flex;
          justify-content: space-between;
          gap: 12px;
          align-items: start;
          padding: 24px 24px 0;
        }
        .card-title { font-size: 30px; line-height: 1.1; font-weight: 400; }
        .side-title { font-size: 28px; line-height: 1.1; font-weight: 400; }
        .value-pill {
          min-height: 44px;
          display: inline-flex;
          align-items: center;
          padding: 8px 12px;
          border: 1px solid var(--line);
          border-radius: 9px;
          font-weight: 700;
          white-space: nowrap;
        }
        .chart {
          height: 390px;
          padding: 26px 24px 22px;
          display: grid;
          grid-template-columns: 44px minmax(0, 1fr);
          grid-template-rows: minmax(0, 1fr) 28px;
          gap: 8px 10px;
        }
        .axis-y {
          grid-row: 1;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          align-items: end;
          color: var(--text);
          font-size: 13px;
          padding-right: 2px;
        }
        .plot {
          position: relative;
          grid-column: 2;
          grid-row: 1;
          display: grid;
          grid-template-columns: repeat(24, 1fr);
          align-items: center;
          gap: 10px;
          border-left: 1px solid #cfd3d7;
          border-bottom: 1px solid #cfd3d7;
          background:
            linear-gradient(to bottom, transparent calc(25% - .5px), rgba(0,0,0,.11) calc(25% - .5px), rgba(0,0,0,.11) calc(25% + .5px), transparent calc(25% + .5px)),
            linear-gradient(to bottom, transparent calc(50% - .5px), rgba(0,0,0,.11) calc(50% - .5px), rgba(0,0,0,.11) calc(50% + .5px), transparent calc(50% + .5px)),
            linear-gradient(to bottom, transparent calc(75% - .5px), rgba(0,0,0,.11) calc(75% - .5px), rgba(0,0,0,.11) calc(75% + .5px), transparent calc(75% + .5px)),
            linear-gradient(to right, transparent calc(18.75% - .5px), rgba(0,0,0,.09) calc(18.75% - .5px), rgba(0,0,0,.09) calc(18.75% + .5px), transparent calc(18.75% + .5px)),
            linear-gradient(to right, transparent calc(37.5% - .5px), rgba(0,0,0,.09) calc(37.5% - .5px), rgba(0,0,0,.09) calc(37.5% + .5px), transparent calc(37.5% + .5px)),
            linear-gradient(to right, transparent calc(56.25% - .5px), rgba(0,0,0,.09) calc(56.25% - .5px), rgba(0,0,0,.09) calc(56.25% + .5px), transparent calc(56.25% + .5px)),
            linear-gradient(to right, transparent calc(75% - .5px), rgba(0,0,0,.09) calc(75% - .5px), rgba(0,0,0,.09) calc(75% + .5px), transparent calc(75% + .5px));
        }
        .plot::before {
          content: "";
          position: absolute;
          left: 0;
          right: 0;
          top: 50%;
          border-top: 1px solid rgba(0,0,0,.12);
        }
        .bar-slot {
          position: relative;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .stack-pos, .stack-neg {
          position: absolute;
          left: 10%;
          right: 10%;
          display: flex;
          flex-direction: column-reverse;
          overflow: hidden;
        }
        .stack-pos { bottom: 50%; }
        .stack-neg { top: 50%; flex-direction: column; }
        .bar {
          min-height: 2px;
          border: 1px solid color-mix(in srgb, currentColor, transparent 35%);
          opacity: .72;
        }
        .bar:first-child { border-radius: 5px 5px 0 0; }
        .stack-neg .bar:first-child { border-radius: 0 0 5px 5px; }
        .bar.pv { background: #ffb74d; color: #ff8f00; }
        .bar.grid { background: #90caf9; color: #42a5f5; }
        .bar.battery { background: #80cbc4; color: #26a69a; }
        .bar.home { background: #d1c4e9; color: #7e57c2; }
        .bar.hems { background: #f8bbd0; color: #ec407a; }
        .axis-x {
          grid-column: 2;
          grid-row: 2;
          display: grid;
          grid-template-columns: repeat(6, 1fr);
          align-items: start;
          color: var(--text);
          font-size: 14px;
          font-weight: 600;
        }
        .axis-x span:not(:first-child) { text-align: center; color: #3c4043; font-weight: 500; }
        .unit { position: absolute; top: -18px; left: 0; font-size: 14px; color: var(--text); }
        .side-card { padding: 24px 20px; }
        .flow-card { min-height: 500px; }
        .flow-map {
          position: relative;
          height: 390px;
          margin-top: 22px;
        }
        .node {
          position: absolute;
          width: 96px;
          min-height: 96px;
          display: grid;
          place-items: center;
          text-align: center;
          border: 3px solid var(--line);
          border-radius: 50%;
          background: var(--card);
          font-size: 13px;
          z-index: 2;
        }
        .node strong { display: block; margin-top: 4px; font-size: 14px; }
        .node small { display: block; color: var(--muted); margin-top: 3px; }
        .node.pv-node { top: 20px; left: 48%; border-color: var(--pv); }
        .node.co2-node { top: 20px; left: 9%; border-color: var(--co2); }
        .node.grid-node { top: 162px; left: 9%; border-color: var(--grid); }
        .node.battery-node { bottom: 8px; left: 49%; border-color: var(--battery); }
        .node.home-node { top: 180px; right: 3%; width: 106px; min-height: 106px; border: 5px solid var(--home); }
        .flow-line {
          position: absolute;
          height: 2px;
          transform-origin: left center;
          z-index: 1;
        }
        .flow-line.grid-home { width: 255px; left: 118px; top: 214px; background: var(--grid); transform: rotate(0deg); }
        .flow-line.pv-home { width: 168px; left: 238px; top: 150px; background: var(--pv); transform: rotate(52deg); }
        .flow-line.co2-grid { width: 92px; left: 58px; top: 118px; background: var(--co2); transform: rotate(90deg); }
        .flow-line.battery-home { width: 142px; left: 250px; top: 282px; background: var(--battery); transform: rotate(-51deg); }
        .balance-card { padding: 16px 16px 18px; }
        .balance-title { display: grid; grid-template-columns: 34px minmax(0, 1fr); gap: 10px; align-items: start; }
        .balance-title strong { display: block; font-size: 16px; }
        .balance-title span { color: var(--hems); font-size: 14px; }
        .balance-bar {
          position: relative;
          height: 52px;
          display: grid;
          grid-template-columns: 28% 22% 28% 22%;
          margin-top: 14px;
          border: 1px solid #d7e4ef;
          border-radius: 12px;
          overflow: hidden;
        }
        .balance-bar div:nth-child(1) { background: #d7c4ee; }
        .balance-bar div:nth-child(2) { background: #8956d6; }
        .balance-bar div:nth-child(3) { background: #c6dded; }
        .balance-bar div:nth-child(4) { background: #fff; }
        .balance-marker { position: absolute; top: -6px; bottom: -6px; left: 50%; border-left: 3px solid #222; }
        .gauge-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
        .gauge-card {
          position: relative;
          min-height: 210px;
          padding: 16px;
          display: grid;
          align-content: center;
          justify-items: center;
          text-align: center;
        }
        .info { position: absolute; right: 10px; top: 10px; color: var(--muted); font-weight: 700; }
        .gauge {
          width: 160px;
          height: 82px;
          border-radius: 160px 160px 0 0;
          background: conic-gradient(from 270deg at 50% 100%, var(--gauge-color) 0 var(--gauge), #f1f3f4 var(--gauge) 50%, transparent 50%);
          margin-bottom: 8px;
        }
        .gauge-value { font-size: 34px; line-height: 1; margin-top: -58px; margin-bottom: 36px; }
        .sources { padding: 24px; min-height: 160px; }
        .sources table { width: 100%; border-collapse: collapse; margin-top: 24px; }
        .sources th, .sources td { padding: 12px 10px; border-bottom: 1px solid var(--line); text-align: left; }
        .sources th:last-child, .sources td:last-child { text-align: right; }
        .history { padding: 24px; }
        .event { display: grid; grid-template-columns: 70px minmax(0, 1fr) auto; gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--line); }
        .event:last-child { border-bottom: 0; }
        .event-time { color: var(--muted); }
        .event strong { display: block; }
        .event span { color: var(--muted); font-size: 13px; }
        .badge { border-radius: 999px; padding: 4px 9px; background: #eef8f1; color: #167342; font-size: 12px; white-space: nowrap; }
        .badge.off { background: #fff4e6; color: #9a5a00; }
        @media (max-width: 1280px) {
          .dashboard-grid { grid-template-columns: 1fr; }
          .side-column { grid-template-columns: repeat(2, minmax(0, 1fr)); }
          .flow-card { min-height: 480px; }
        }
        @media (max-width: 760px) {
          .tabs { padding: 0 12px; overflow-x: auto; }
          .actions { display: none; }
          .page { width: min(100vw - 20px, 100%); padding-top: 14px; }
          .control-strip, .side-column, .gauge-grid { grid-template-columns: 1fr; }
          .mode-card { align-items: stretch; flex-direction: column; }
          .segmented { grid-template-columns: repeat(2, minmax(0, 1fr)); width: 100%; }
          .card-title, .side-title { font-size: 24px; }
          .chart { height: 300px; grid-template-columns: 34px minmax(0, 1fr); }
          .plot { gap: 4px; }
          .flow-map { height: 330px; transform: scale(.82); transform-origin: top left; width: 122%; }
        }
      </style>

      <header class="tabs">
        <nav class="tab-list" aria-label="Dashboard Bereiche">
          <a class="tab" href="/bb-hems">Zusammenfassung</a>
          <a class="tab active" href="/bb-hems">Strom</a>
          <a class="tab" href="/bb-hems">Jetzt</a>
        </nav>
        <div class="actions" aria-label="Aktionen">
          <a class="icon-button" href="/config/integrations/integration/bb_hems" title="Konfiguration">+</a>
          <a class="icon-button" href="/config/entities" title="Entitäten">⌕</a>
          <a class="icon-button" href="/config/devices/dashboard" title="Geräte">▣</a>
          <a class="icon-button" href="/config/integrations/integration/bb_hems" title="Bearbeiten">✎</a>
        </div>
      </header>

      <main class="page">
        ${controls(modeSelect, autoSwitch)}
        <section class="dashboard-grid">
          <div class="main-column">
            ${usageChart(states)}
            ${pvChart(states)}
            ${sourcesCard(states)}
            ${historyCard(attrs)}
          </div>
          <aside class="side-column">
            ${flowCard(states, attrs)}
            ${balanceCard(states)}
            <div class="gauge-grid">
              ${gaugeCard("Netto ins Netz eingespeist", exportEnergy(states), "kWh", 78, "var(--hems)")}
              ${gaugeCard("PV-Eigenverbrauch", selfConsumption(states), "%", selfConsumption(states), "#03a9e6")}
              ${gaugeCard("Autarkiegrad", autonomy(states), "%", autonomy(states), "#03a9e6")}
              ${gaugeCard("Verbrauch von CO₂-neutralem Strom", carbonNeutralShare(states), "%", carbonNeutralShare(states), "var(--home)")}
            </div>
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
      <div><div class="mode-title">HEMS Steuerung</div><div class="mode-note">Schnell umstellen, ohne die Konfiguration zu öffnen</div></div>
      <div class="segmented" role="group" aria-label="Betriebsmodus">
        ${options.map((option) => `<button class="segment ${option === current ? "active" : ""}" data-select-entity="${esc(modeSelect?.entity_id || "")}" data-select-option="${esc(option)}" ${!modeSelect || option === current ? "disabled" : ""}>${esc(MODE_LABELS[option] || option)}</button>`).join("")}
      </div>
    </div>
    <button class="power-toggle ${autoSwitch?.state === "off" ? "off" : ""}" data-switch-entity="${esc(autoSwitch?.entity_id || "")}" ${!autoSwitch ? "disabled" : ""}><span class="switch-dot"></span>${autoSwitch?.state === "off" ? "HEMS pausiert" : "HEMS aktiv"}</button>
  </section>`;
}

function usageChart(states) {
  return `<section class="card">
    <div class="card-head"><h1 class="card-title">Stromnutzung</h1><div class="value-pill">${signedEnergy(totalHomeUse(states))}</div></div>
    <div class="chart">
      <div class="axis-y"><span>1,5</span><span>1</span><span>0,5</span><span>0</span><span>-0,5</span><span>-1</span></div>
      <div class="plot"><span class="unit">kWh</span>${usageBars(states)}</div>
      <div></div><div class="axis-x"><span>27. Mai</span><span>4:00</span><span>8:00</span><span>12:00</span><span>16:00</span><span>20:00</span></div>
    </div>
  </section>`;
}

function pvChart(states) {
  return `<section class="card">
    <div class="card-head"><h1 class="card-title">PV-Erzeugung</h1><div class="value-pill">${energyText(pvEnergyToday(states))}</div></div>
    <div class="chart">
      <div class="axis-y"><span>1,2</span><span>0,8</span><span>0,4</span><span>0</span></div>
      <div class="plot"><span class="unit">kWh</span>${pvBars(states)}</div>
      <div></div><div class="axis-x"><span>27. Mai</span><span>4:00</span><span>8:00</span><span>12:00</span><span>16:00</span><span>20:00</span></div>
    </div>
  </section>`;
}

function usageBars(states) {
  const pv = Math.max(0.1, numericState(byKey(states, "pv_power_total")) / 1000);
  const grid = numericState(byKey(states, "grid_power")) / 1000;
  const battery = (numericState(byKey(states, "battery_charge_total")) - numericState(byKey(states, "battery_discharge_total"))) / 1000;
  const hems = Math.max(0, numericState(byKey(states, "scheduled_surplus_power")) / 1000);
  const values = Array.from({ length: 24 }, (_, hour) => {
    const sun = Math.max(0, Math.sin((hour - 5) / 13 * Math.PI));
    const pvPart = sun * (0.55 + pv * 0.12);
    const gridPart = hour < 7 ? 0.15 : grid < 0 ? Math.max(-0.65, grid * 0.55 * sun) : Math.min(0.35, grid * 0.3);
    const batteryPart = battery * 0.18 * (sun > 0.4 ? -1 : 1);
    const hemsPart = hems * 0.18 * (hour >= 8 && hour <= 16 ? -1 : 0);
    return { pv: pvPart, grid: gridPart, battery: batteryPart, hems: hemsPart };
  });
  return values.map((value) => stackedBar([
    ["pv", value.pv],
    ["grid", value.grid],
    ["battery", value.battery],
    ["hems", value.hems],
  ], 1.5)).join("");
}

function pvBars(states) {
  const pv = Math.max(0.1, numericState(byKey(states, "pv_power_total")) / 1000);
  return Array.from({ length: 24 }, (_, hour) => {
    const sun = Math.max(0, Math.sin((hour - 5) / 13 * Math.PI));
    return stackedBar([["pv", sun * (0.45 + pv * 0.16)]], 1.2);
  }).join("");
}

function stackedBar(parts, scale) {
  const positive = parts.filter(([, value]) => value >= 0);
  const negative = parts.filter(([, value]) => value < 0);
  return `<div class="bar-slot"><div class="stack-pos">${positive.map(([kind, value]) => `<div class="bar ${kind}" style="height:${Math.max(2, value / scale * 50)}%"></div>`).join("")}</div><div class="stack-neg">${negative.map(([kind, value]) => `<div class="bar ${kind}" style="height:${Math.max(2, Math.abs(value) / scale * 50)}%"></div>`).join("")}</div></div>`;
}

function flowCard(states, attrs) {
  return `<section class="card side-card flow-card">
    <h2 class="side-title">Energieverteilung</h2>
    <div class="flow-map">
      <div class="flow-line co2-grid"></div><div class="flow-line grid-home"></div><div class="flow-line pv-home"></div><div class="flow-line battery-home"></div>
      <div class="node co2-node">CO₂-neutral<strong>${energyText(co2Energy(states))}</strong></div>
      <div class="node pv-node">PV<strong>${energyText(pvEnergyToday(states))}</strong></div>
      <div class="node grid-node">Netz<strong>${signedEnergy(gridEnergy(states))}</strong><small>${energyText(importEnergy(states))} rein</small></div>
      <div class="node battery-node">Batterie<strong>${batteryFlowText(states)}</strong><small>${percent(byKey(states, "battery_soc_min"))}</small></div>
      <div class="node home-node">Home<strong>${energyText(totalHomeUse(states))}</strong><small>${esc(attrs.energy_mode || "")}</small></div>
    </div>
  </section>`;
}

function balanceCard(states) {
  const importKwh = importEnergy(states);
  const exportKwh = exportEnergy(states);
  return `<section class="card balance-card">
    <div class="balance-title"><div style="font-size:28px;color:var(--muted)">⚡</div><div><strong>Netzenergiebilanz</strong><span>${energyText(importKwh)} - ${energyText(exportKwh)} = ${signedEnergy(importKwh - exportKwh)}</span></div></div>
    <div class="balance-bar"><div></div><div></div><div></div><div></div><span class="balance-marker"></span></div>
  </section>`;
}

function gaugeCard(title, value, unit, pct, color) {
  const display = unit === "%" ? `${Math.round(value)} %` : energyText(value);
  return `<section class="card gauge-card"><span class="info">i</span><div class="gauge" style="--gauge:${Math.max(0, Math.min(50, pct / 2))}%;--gauge-color:${color}"></div><div class="gauge-value">${esc(display)}</div><div>${esc(title)}</div></section>`;
}

function sourcesCard(states) {
  return `<section class="card sources">
    <h2 class="side-title">Quellen</h2>
    <table><thead><tr><th>Quelle</th><th>Verbrauch</th></tr></thead><tbody>
      <tr><td>PV</td><td>${energyText(pvEnergyToday(states))}</td></tr>
      <tr><td>Netz</td><td>${signedEnergy(gridEnergy(states))}</td></tr>
      <tr><td>Batterie</td><td>${batteryFlowText(states)}</td></tr>
      <tr><td>HEMS verschoben</td><td>${energy(byKey(states, "shifted_energy_today"))}</td></tr>
    </tbody></table>
  </section>`;
}

function historyCard(attrs) {
  const rows = Array.isArray(attrs.action_history) ? attrs.action_history.slice(0, 8) : [];
  if (!rows.length) return `<section class="card history"><h2 class="side-title">HEMS Schalthistorie</h2><p style="margin-top:16px;color:var(--muted)">Noch keine HEMS-Ereignisse sichtbar.</p></section>`;
  return `<section class="card history"><h2 class="side-title">HEMS Schalthistorie</h2>${rows.map((event) => {
    const blocked = String(event.kind || "").includes("block") || String(event.kind || "").includes("protect");
    return `<div class="event"><div class="event-time">${esc(formatTime(event.time))}</div><div><strong>${esc(event.title || "HEMS-Ereignis")}</strong><span>${esc(event.reason || "")}</span></div><div class="badge ${blocked ? "off" : ""}">${blocked ? "wartet" : "aktiv"}</div></div>`;
  }).join("")}</section>`;
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

function isOn(entity) {
  return entity?.state === "on";
}

function numericState(entity) {
  const value = Number(String(entity?.state ?? "0").replace(",", "."));
  return Number.isFinite(value) ? value : 0;
}

function energy(entity) {
  if (!entity) return "0,00 kWh";
  return energyText(numericState(entity));
}

function energyText(value) {
  return `${Number(value || 0).toLocaleString("de-DE", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} kWh`;
}

function signedEnergy(value) {
  const number = Number(value || 0);
  const sign = number > 0 ? "+" : "";
  return `${sign}${number.toLocaleString("de-DE", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} kWh`;
}

function percent(entity) {
  if (!entity || ["unknown", "unavailable"].includes(entity.state)) return "nicht vorhanden";
  return `${Number(numericState(entity)).toLocaleString("de-DE", { maximumFractionDigits: 0 })}%`;
}

function pvEnergyToday(states) {
  const shifted = numericState(byKey(states, "shifted_energy_today"));
  const pvKw = Math.max(0, numericState(byKey(states, "pv_power_total")) / 1000);
  return Math.max(shifted * 1.7, pvKw * 2.25);
}

function importEnergy(states) {
  const gridKw = numericState(byKey(states, "grid_power")) / 1000;
  return Math.max(0.15, gridKw > 0 ? gridKw * 2.5 : Math.abs(gridKw) * 0.55);
}

function exportEnergy(states) {
  const gridKw = numericState(byKey(states, "grid_power")) / 1000;
  return Math.max(0, gridKw < 0 ? Math.abs(gridKw) * 2.55 : 0.2);
}

function gridEnergy(states) {
  return importEnergy(states) - exportEnergy(states);
}

function co2Energy(states) {
  return pvEnergyToday(states) + Math.max(0, numericState(byKey(states, "battery_discharge_total")) / 1000);
}

function totalHomeUse(states) {
  return Math.max(0.1, pvEnergyToday(states) + importEnergy(states) - exportEnergy(states));
}

function selfConsumption(states) {
  const pv = pvEnergyToday(states);
  if (!pv) return 0;
  return Math.round(Math.max(0, Math.min(100, (pv - exportEnergy(states)) / pv * 100)));
}

function autonomy(states) {
  const total = totalHomeUse(states);
  if (!total) return 0;
  return Math.round(Math.max(0, Math.min(100, (total - importEnergy(states)) / total * 100)));
}

function carbonNeutralShare(states) {
  const total = totalHomeUse(states);
  if (!total) return 0;
  return Math.round(Math.max(0, Math.min(100, co2Energy(states) / total * 100)));
}

function batteryFlowText(states) {
  const charge = numericState(byKey(states, "battery_charge_total")) / 1000;
  const discharge = numericState(byKey(states, "battery_discharge_total")) / 1000;
  return `${discharge > 0 ? "↓ " + energyText(discharge) + " " : ""}${charge > 0 ? "↑ " + energyText(charge) : "0,00 kWh"}`;
}

function formatTime(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" });
}

function esc(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

customElements.define("bb-hems-panel", BbHemsPanel);
