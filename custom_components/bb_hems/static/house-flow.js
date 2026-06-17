const BB_HEMS_FLOW_STYLES = `
  :host {
    --bb-flow-bg: var(--card-background-color, #ffffff);
    --bb-flow-page: var(--primary-background-color, #f6f7f9);
    --bb-flow-text: var(--primary-text-color, #17202a);
    --bb-flow-muted: var(--secondary-text-color, #66727d);
    --bb-flow-line: var(--divider-color, #d8dde3);
    --bb-flow-solar: #f5b118;
    --bb-flow-battery: #2f7de1;
    --bb-flow-grid-in: #e76f51;
    --bb-flow-grid-out: #21a67a;
    --bb-flow-load: #5b6472;
    display: block;
    color: var(--bb-flow-text);
  }
  .wrap {
    position: relative;
    overflow: hidden;
    min-height: 520px;
    border: 1px solid var(--bb-flow-line);
    border-radius: 8px;
    background:
      radial-gradient(circle at 12% 8%, rgba(245, 177, 24, 0.15), transparent 20%),
      linear-gradient(180deg, #ffffff 0%, var(--bb-flow-page) 100%);
  }
  .scene {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
  }
  svg {
    width: 100%;
    height: 100%;
    display: block;
  }
  .house-wall { fill: #ffffff; stroke: #aeb5bc; stroke-width: 4; }
  .house-side { fill: #f1f4f6; stroke: #aeb5bc; stroke-width: 4; }
  .room-line { stroke: #d1d7dd; stroke-width: 3; }
  .roof { fill: #f7f8f9; stroke: #aeb5bc; stroke-width: 4; }
  .panel { fill: #dfe6ec; stroke: #aab2ba; stroke-width: 2; }
  .icon-stroke { fill: none; stroke: currentColor; stroke-width: 4; stroke-linecap: round; stroke-linejoin: round; }
  .flow-path {
    fill: none;
    stroke-width: var(--flow-width, 4);
    stroke-linecap: round;
    stroke-dasharray: 2 11;
    opacity: 0.95;
    animation: bb-flow-dash 1.2s linear infinite;
  }
  .flow-muted { opacity: 0.22; animation: none; }
  .solar { stroke: var(--bb-flow-solar); color: var(--bb-flow-solar); }
  .battery { stroke: var(--bb-flow-battery); color: var(--bb-flow-battery); }
  .grid-in { stroke: var(--bb-flow-grid-in); color: var(--bb-flow-grid-in); }
  .grid-out { stroke: var(--bb-flow-grid-out); color: var(--bb-flow-grid-out); }
  .load { stroke: var(--bb-flow-load); color: var(--bb-flow-load); }
  .metric {
    position: absolute;
    display: grid;
    gap: 3px;
    min-width: 116px;
    padding: 9px 10px;
    border: 1px solid rgba(160, 169, 178, 0.42);
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.92);
    box-shadow: 0 10px 28px rgba(31, 41, 51, 0.08);
    backdrop-filter: blur(4px);
    box-sizing: border-box;
  }
  .metric strong {
    font-size: 12px;
    line-height: 1.2;
    font-weight: 700;
  }
  .metric .value {
    font-size: 19px;
    line-height: 1.1;
    font-weight: 800;
    letter-spacing: 0;
    white-space: nowrap;
  }
  .metric .sub {
    color: var(--bb-flow-muted);
    font-size: 11px;
    line-height: 1.25;
    white-space: nowrap;
  }
  .metric.solar { border-color: rgba(245, 177, 24, 0.38); }
  .metric.battery { border-color: rgba(47, 125, 225, 0.34); }
  .metric.grid-in { border-color: rgba(231, 111, 81, 0.34); }
  .metric.grid-out { border-color: rgba(33, 166, 122, 0.34); }
  .metric.house { left: 44%; top: 42%; transform: translate(-50%, -50%); }
  .metric.pv { left: 35%; top: 10%; }
  .metric.bkw { left: 15%; bottom: 9%; }
  .metric.grid { right: 6%; top: 34%; }
  .metric.pvbat { left: 33%; bottom: 18%; }
  .metric.acbat { left: 49%; top: 52%; }
  .metric.ev { left: 6%; bottom: 14%; }
  .metric.heat { left: 55%; bottom: 15%; }
  .status {
    position: absolute;
    left: 18px;
    top: 16px;
    display: flex;
    gap: 8px;
    align-items: center;
    color: var(--bb-flow-muted);
    font-size: 12px;
  }
  .dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: var(--bb-flow-grid-out);
    box-shadow: 0 0 0 4px rgba(33, 166, 122, 0.12);
  }
  @keyframes bb-flow-dash {
    to { stroke-dashoffset: -52; }
  }
  @media (prefers-reduced-motion: reduce) {
    .flow-path { animation: none; }
  }
  @media (max-width: 760px) {
    .wrap { min-height: 760px; }
    .scene { top: 120px; height: 520px; }
    .metric {
      min-width: 0;
      width: calc(50% - 18px);
      transform: none;
    }
    .metric .value { font-size: 16px; }
    .metric.house { left: 9px; top: 50px; }
    .metric.pv { left: calc(50% + 9px); top: 50px; }
    .metric.grid { right: auto; left: 9px; top: auto; bottom: 80px; }
    .metric.pvbat { left: calc(50% + 9px); bottom: 80px; }
    .metric.acbat { left: 9px; top: auto; bottom: 9px; }
    .metric.heat { left: calc(50% + 9px); bottom: 9px; }
    .metric.ev { left: 9px; bottom: 151px; }
    .metric.bkw { left: calc(50% + 9px); bottom: 151px; }
  }
`;

class BbHemsHouseFlow extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._data = defaultFlowData();
  }

  set data(value) {
    this._data = normalizeFlowData(value);
    this.render();
  }

  get data() {
    return this._data;
  }

  connectedCallback() {
    this.render();
  }

  render() {
    const data = normalizeFlowData(this._data);
    const gridClass = data.grid.power < 0 ? "grid-out" : "grid-in";
    const gridLabel = data.grid.power < 0 ? "Einspeisung" : "Bezug";
    this.shadowRoot.innerHTML = `
      <style>${BB_HEMS_FLOW_STYLES}</style>
      <section class="wrap" aria-label="BB HEMS Energiefluss">
        <div class="status"><span class="dot"></span><span>${esc(data.status || "Live Energiefluss")}</span></div>
        <div class="scene">${houseSvg(data)}</div>
        ${metric("house", "Haus", formatPower(data.house.power), formatEnergy(data.house.energy, data.house.energySource))}
        ${metric("pv solar", "PV Dach", formatPower(data.pvRoof.power), formatEnergy(data.pvRoof.energy))}
        ${metric("bkw solar", "BKW Garage", formatPower(data.bkwGarage.power), formatEnergy(data.bkwGarage.energy))}
        ${metric(`grid ${gridClass}`, "Netz", formatPower(Math.abs(data.grid.power)), gridLabel)}
        ${metric("pvbat battery", "PV Batterie", formatPower(Math.abs(data.pvBattery.power)), batterySub(data.pvBattery))}
        ${metric("acbat battery", "AC Batterie", formatPower(Math.abs(data.acBattery.power)), batterySub(data.acBattery))}
        ${metric("ev", "Elektroauto", formatPower(data.ev.power), formatEnergy(data.ev.energy))}
        ${metric("heat", "Wärmepumpe", formatPower(data.heatPump.power), formatEnergy(data.heatPump.energy))}
      </section>
    `;
  }
}

function houseSvg(data) {
  const gridClass = data.grid.power < 0 ? "grid-out" : "grid-in";
  const pvActive = data.pvRoof.power > 10;
  const bkwActive = data.bkwGarage.power > 10;
  const gridActive = Math.abs(data.grid.power) > 10;
  const pvBatActive = Math.abs(data.pvBattery.power) > 10;
  const acBatActive = Math.abs(data.acBattery.power) > 10;
  const evActive = data.ev.power > 10;
  const heatActive = data.heatPump.power > 10;
  return `
    <svg viewBox="0 0 1000 560" role="img" aria-label="Haus mit Energieflüssen">
      <g transform="translate(54 28)">
        <g class="solar">
          <circle cx="52" cy="52" r="26" fill="none" stroke="currentColor" stroke-width="8"/>
          <path class="icon-stroke" d="M52 5v18M52 82v18M5 52h18M82 52h18M18 18l13 13M73 73l13 13M86 18 73 31M31 73 18 86"/>
        </g>
        <path class="${pathClass("flow-path solar", pvActive)}" style="${flowWidth(data.pvRoof.power)}" d="M108 70 C205 90 245 155 305 184"/>
      </g>

      <g transform="translate(235 25)">
        <polygon class="roof" points="80,0 485,0 550,130 18,130"/>
        <g transform="translate(110 22)">
          ${solarPanels()}
        </g>
        <polygon class="house-wall" points="18,130 430,130 430,455 18,455"/>
        <polygon class="house-side" points="430,130 550,130 550,455 430,455"/>
        <line class="room-line" x1="18" y1="250" x2="430" y2="250"/>
        <line class="room-line" x1="18" y1="350" x2="430" y2="350"/>
        <line class="room-line" x1="225" y1="130" x2="225" y2="455"/>
        <path class="room-line" d="M475 180h38v72h-38zM475 300h38v72h-38z"/>
        <g color="#35404a" transform="translate(280 205)">
          <rect x="0" y="0" width="58" height="40" rx="2" fill="none" stroke="currentColor" stroke-width="4"/>
          <path class="icon-stroke" d="M-4 48h66M29 40v8"/>
        </g>
        <g color="#35404a" transform="translate(95 215)">
          <rect x="0" y="0" width="58" height="74" rx="3" fill="#f7f8f9" stroke="currentColor" stroke-width="4"/>
          <circle cx="29" cy="46" r="20" fill="none" stroke="currentColor" stroke-width="4"/>
          <path class="icon-stroke" d="M16 16h26"/>
        </g>
        <g color="#35404a" transform="translate(306 346)">
          <path d="M0 20h58v76H0z" fill="#f7f8f9" stroke="currentColor" stroke-width="4"/>
          <path d="M58 20l24-10v76L58 96z" fill="#e9eef2" stroke="currentColor" stroke-width="4"/>
          <path class="icon-stroke" d="M14 40h28M14 58h28"/>
        </g>
        <g color="#35404a" transform="translate(172 340)">
          <rect x="0" y="0" width="70" height="86" rx="4" fill="#f7f8f9" stroke="currentColor" stroke-width="4"/>
          <path class="icon-stroke" d="M18 20h34M18 42h34M18 64h24"/>
        </g>
        <g color="#35404a" transform="translate(86 348)">
          <rect x="0" y="25" width="42" height="42" rx="4" fill="#fff4c2" stroke="currentColor" stroke-width="4"/>
          <path class="icon-stroke" d="M12 25v-10h18v10"/>
        </g>
        <g color="#35404a" transform="translate(15 395)">
          <path d="M0 25h130v60H0z" fill="#f7f8f9" stroke="currentColor" stroke-width="4"/>
          <path d="M18 25 42 0h54l22 25" fill="none" stroke="currentColor" stroke-width="4"/>
          <circle cx="34" cy="85" r="12" fill="#fff" stroke="currentColor" stroke-width="4"/>
          <circle cx="100" cy="85" r="12" fill="#fff" stroke="currentColor" stroke-width="4"/>
          <path class="icon-stroke" d="M-12 42h12M130 42h18"/>
        </g>
      </g>

      <g color="#9ba3aa" transform="translate(830 206)">
        <path class="icon-stroke" d="M70 0 0 68h140L70 0ZM70 0v216M18 68v148M122 68v148M0 216h140M28 112h84M18 216 70 68l52 148"/>
      </g>

      <path class="${pathClass(`flow-path ${gridClass}`, gridActive)}" style="${flowWidth(Math.abs(data.grid.power))}" d="M815 392 C735 392 705 360 667 343"/>
      <path class="${pathClass("flow-path solar", pvActive)}" style="${flowWidth(data.pvRoof.power)}" d="M520 165 C520 235 483 265 450 284"/>
      <path class="${pathClass("flow-path solar", bkwActive)}" style="${flowWidth(data.bkwGarage.power)}" d="M258 486 C365 485 410 420 438 354"/>
      <path class="${pathClass("flow-path battery", pvBatActive)}" style="${flowWidth(Math.abs(data.pvBattery.power))}" d="M455 418 C505 395 516 356 500 320"/>
      <path class="${pathClass("flow-path battery", acBatActive)}" style="${flowWidth(Math.abs(data.acBattery.power))}" d="M593 378 C564 354 548 331 525 310"/>
      <path class="${pathClass("flow-path load", evActive)}" style="${flowWidth(data.ev.power)}" d="M426 336 C358 365 315 420 246 460"/>
      <path class="${pathClass("flow-path load", heatActive)}" style="${flowWidth(data.heatPump.power)}" d="M536 324 C600 345 642 382 675 438"/>
    </svg>
  `;
}

function solarPanels() {
  const cells = [];
  for (let row = 0; row < 2; row += 1) {
    for (let col = 0; col < 4; col += 1) {
      cells.push(`<rect class="panel" x="${col * 72}" y="${row * 44}" width="68" height="40"/>`);
    }
  }
  return cells.join("");
}

function metric(className, title, value, sub) {
  return `
    <article class="metric ${className}">
      <strong>${esc(title)}</strong>
      <span class="value">${esc(value)}</span>
      <span class="sub">${esc(sub || "Heute")}</span>
    </article>
  `;
}

function normalizeFlowData(value) {
  const data = value && typeof value === "object" ? value : {};
  const base = defaultFlowData();
  return {
    status: data.status || base.status,
    house: normalizeNode(data.house, base.house),
    pvRoof: normalizeNode(data.pvRoof, base.pvRoof),
    bkwGarage: normalizeNode(data.bkwGarage, base.bkwGarage),
    grid: normalizeNode(data.grid, base.grid),
    pvBattery: normalizeNode(data.pvBattery, base.pvBattery),
    acBattery: normalizeNode(data.acBattery, base.acBattery),
    ev: normalizeNode(data.ev, base.ev),
    heatPump: normalizeNode(data.heatPump, base.heatPump),
  };
}

function normalizeNode(value, fallback) {
  const node = value && typeof value === "object" ? value : {};
  return {
    power: numberOr(node.power, fallback.power),
    energy: numberOr(node.energy, fallback.energy),
    soc: numberOr(node.soc, fallback.soc),
    energySource: node.energySource || fallback.energySource,
  };
}

function defaultFlowData() {
  return {
    status: "Live Energiefluss",
    house: { power: 1820, energy: null, energySource: "Haus-Sensor" },
    pvRoof: { power: 3240, energy: null },
    bkwGarage: { power: 410, energy: null },
    grid: { power: -340, energy: null },
    pvBattery: { power: -850, soc: 62, energy: null },
    acBattery: { power: 420, soc: 76, energy: null },
    ev: { power: 2800, energy: null },
    heatPump: { power: 1120, energy: null },
  };
}

function batterySub(node) {
  const direction = node.power < 0 ? "Entlädt" : node.power > 0 ? "Lädt" : "Standby";
  return node.soc == null ? direction : `${Math.round(node.soc)}% · ${direction}`;
}

function formatPower(value) {
  const watts = Number(value || 0);
  const abs = Math.abs(watts);
  if (abs >= 1000) {
    return `${(abs / 1000).toLocaleString("de-DE", { maximumFractionDigits: 2 })} kW`;
  }
  return `${Math.round(abs).toLocaleString("de-DE")} W`;
}

function formatEnergy(value, fallback = "Heute") {
  if (value == null || value === "") return fallback || "Heute";
  return `${Number(value).toLocaleString("de-DE", { maximumFractionDigits: 1 })} kWh heute`;
}

function flowWidth(value) {
  const width = Math.min(9, Math.max(3, Math.abs(Number(value || 0)) / 700 + 3));
  return `--flow-width:${width.toFixed(1)}px`;
}

function pathClass(className, active) {
  return active ? className : `${className} flow-muted`;
}

function numberOr(value, fallback) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[char]));
}

if (!customElements.get("bb-hems-house-flow")) {
  customElements.define("bb-hems-house-flow", BbHemsHouseFlow);
}

window.BbHemsHouseFlow = {
  normalizeFlowData,
  defaultFlowData,
};
