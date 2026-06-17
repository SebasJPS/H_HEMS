const BB_HEMS_VERSION = "1.0.2b0";

const I18N = {
  de: {
    title: "BB HEMS",
    subtitle: "Strikte Überschusssteuerung ohne Wetter-, Lern- und Batterie-Magie",
    config: "Konfiguration",
    energy: "Energie",
    decision: "Entscheidung",
    loads: "Verbraucher",
    acBattery: "AC-Akku",
    events: "Ereignisse",
    grid: "Netz",
    export: "Einspeisung",
    import: "Bezug",
    pv: "PV + BKW",
    battery: "PV-Batterie",
    budget: "Freies Budget",
    planned: "Geplant",
    active: "Automatik aktiv",
    paused: "Automatik pausiert",
    mode: "Modus",
    pool: "Pool",
    dehumidifier: "Lufttrockner",
    startOnly: "Startfreigaben",
    manualPaused: "Manuell pausiert",
    noDevices: "keine Geräte",
    noEvents: "Noch keine Ereignisse.",
    target: "Ziel",
    charging: "Laden",
    discharging: "Entladen",
  },
  en: {
    title: "BB HEMS",
    subtitle: "Strict surplus control without weather, learning or virtual battery magic",
    config: "Configuration",
    energy: "Energy",
    decision: "Decision",
    loads: "Loads",
    acBattery: "AC battery",
    events: "Events",
    grid: "Grid",
    export: "Export",
    import: "Import",
    pv: "PV + BKW",
    battery: "PV battery",
    budget: "Free budget",
    planned: "Planned",
    active: "Automation active",
    paused: "Automation paused",
    mode: "Mode",
    pool: "Pool",
    dehumidifier: "Dehumidifier",
    startOnly: "Start releases",
    manualPaused: "Manually paused",
    noDevices: "no devices",
    noEvents: "No events yet.",
    target: "Target",
    charging: "Charge",
    discharging: "Discharge",
  },
};

class BbHemsPanel extends HTMLElement {
  set hass(hass) {
    this._hass = hass;
    this.render();
  }

  connectedCallback() {
    this.render();
  }

  language() {
    return localStorage.getItem("bb_hems_lang") || (this._hass?.language || "de").slice(0, 2);
  }

  render() {
    if (!this._hass) return;
    const states = Object.values(this._hass.states).filter((entity) => entity.entity_id.includes("bb_hems"));
    const mode = findEntity(states, "energy_mode");
    const attrs = mode?.attributes || {};
    const autoSwitch = findEntity(states, "auto_enabled");
    const modeSelect = findEntity(states, "mode");
    const lang = this.language() === "en" ? "en" : "de";
    const tr = I18N[lang];
    const planned = asArray(attrs.scheduled_surplus_loads);
    const manualPaused = asArray(attrs.manually_paused_loads);

    this.innerHTML = `
      <style>
        :host {
          --bg: var(--primary-background-color, #f6f7f9);
          --card: var(--card-background-color, #fff);
          --text: var(--primary-text-color, #1f2933);
          --muted: var(--secondary-text-color, #66727d);
          --line: var(--divider-color, #d8dde3);
          --good: #168a4a;
          --warn: #b7791f;
          --bad: #c53030;
          --accent: #2563eb;
          display: block;
          color: var(--text);
        }
        .page { padding: 24px; background: var(--bg); min-height: 100vh; box-sizing: border-box; }
        .head { display: grid; grid-template-columns: minmax(0,1fr) auto; gap: 16px; align-items: start; margin-bottom: 18px; }
        h1, h2, p { margin: 0; }
        h1 { font-size: 28px; font-weight: 700; letter-spacing: 0; }
        h2 { font-size: 15px; font-weight: 700; margin-bottom: 10px; }
        .sub { color: var(--muted); margin-top: 4px; font-size: 14px; }
        .links { display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }
        .link, button { border: 1px solid var(--line); background: var(--card); color: var(--text); border-radius: 8px; padding: 8px 10px; text-decoration: none; cursor: pointer; font: inherit; }
        .grid { display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 12px; margin-bottom: 12px; }
        .wide { grid-template-columns: minmax(0,1.2fr) minmax(320px,.8fr); }
        .card { background: var(--card); border: 1px solid var(--line); border-radius: 8px; padding: 14px; min-width: 0; }
        .value { font-size: 24px; font-weight: 700; margin-top: 6px; overflow-wrap: anywhere; }
        .note { color: var(--muted); font-size: 13px; margin-top: 6px; line-height: 1.35; overflow-wrap: anywhere; }
        .pill { display: inline-flex; align-items: center; border-radius: 999px; padding: 3px 8px; font-size: 12px; color: white; background: var(--accent); }
        .good { background: var(--good); }
        .warn { background: var(--warn); }
        .bad { background: var(--bad); }
        .row { display: grid; grid-template-columns: minmax(0,1fr) auto; gap: 10px; padding: 8px 0; border-top: 1px solid var(--line); }
        .row:first-of-type { border-top: 0; }
        .controls { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
        .active-button { border-color: var(--accent); color: var(--accent); }
        @media (max-width: 900px) {
          .head, .wide { grid-template-columns: 1fr; }
          .links { justify-content: flex-start; }
          .grid { grid-template-columns: repeat(2, minmax(0,1fr)); }
        }
        @media (max-width: 560px) {
          .page { padding: 14px; }
          .grid { grid-template-columns: 1fr; }
        }
      </style>
      <main class="page">
        <section class="head">
          <div>
            <h1>${esc(tr.title)}</h1>
            <p class="sub">Version ${BB_HEMS_VERSION} · ${esc(tr.subtitle)}</p>
          </div>
          <div class="links">
            <button data-lang>${lang.toUpperCase()}</button>
            <a class="link" href="/config/integrations/integration/bb_hems">${esc(tr.config)}</a>
          </div>
        </section>

        <section class="grid">
          ${tile(tr.grid, gridText(attrs, tr), `${tr.import}: ${power(attrs.grid_import)} · ${tr.export}: ${power(attrs.grid_export)}`)}
          ${tile(tr.pv, power(attrs.pv_power), "")}
          ${tile(tr.battery, attrs.battery_soc_min == null ? "-" : `${Number(attrs.battery_soc_min).toFixed(1)}%`, `Entladung: ${power(attrs.battery_discharge)}`)}
          ${tile(tr.budget, power(attrs.available_surplus_budget), attrs.surplus_reason || "")}
        </section>

        <section class="grid wide">
          <div class="card">
            <h2>${esc(tr.decision)} <span class="pill ${planned.length ? "good" : attrs.grid_import > attrs.grid_tolerance ? "bad" : "warn"}">${esc(mode?.state || "-")}</span></h2>
            <div class="value">${planned.length ? planned.join(", ") : esc(attrs.load_reason || attrs.scheduler_reason || "-")}</div>
            <p class="note">${esc(attrs.scheduler_reason || "")}</p>
            <div class="controls">
              ${modeButtons(modeSelect, tr)}
              <button data-switch="${esc(autoSwitch?.entity_id || "")}" ${!autoSwitch ? "disabled" : ""}>${autoSwitch?.state === "off" ? esc(tr.paused) : esc(tr.active)}</button>
            </div>
          </div>
          <div class="card">
            <h2>${esc(tr.manualPaused)}</h2>
            <div class="value">${manualPaused.length ? manualPaused.length : "0"}</div>
            <p class="note">${manualPaused.length ? manualPaused.join(", ") : "-"}</p>
          </div>
        </section>

        <section class="grid">
          ${loadCard(tr.pool, attrs.pool_loads, planned, attrs.active_loads, tr)}
          ${loadCard(tr.dehumidifier, attrs.dehumidifier_loads, planned, attrs.active_loads, tr)}
          ${loadCard(tr.startOnly, attrs.start_only_loads, planned, attrs.active_loads, tr)}
          ${acBatteryCard(attrs, tr)}
        </section>

        ${events(attrs, tr)}
      </main>
    `;
    this.bind(states);
  }

  bind(states) {
    this.querySelector("[data-lang]")?.addEventListener("click", () => {
      localStorage.setItem("bb_hems_lang", this.language() === "de" ? "en" : "de");
      this.render();
    });
    this.querySelectorAll("[data-mode]").forEach((button) => {
      button.addEventListener("click", () => {
        this._hass.callService("select", "select_option", {
          entity_id: button.dataset.entity,
          option: button.dataset.mode,
        });
      });
    });
    this.querySelectorAll("[data-switch]").forEach((button) => {
      button.addEventListener("click", () => {
        const entity = states.find((item) => item.entity_id === button.dataset.switch);
        this._hass.callService("switch", entity?.state === "on" ? "turn_off" : "turn_on", {
          entity_id: button.dataset.switch,
        });
      });
    });
  }
}

function tile(title, value, note) {
  return `<article class="card"><h2>${esc(title)}</h2><div class="value">${esc(value)}</div><p class="note">${esc(note)}</p></article>`;
}

function loadCard(title, configured, planned, active, tr) {
  const items = asArray(configured);
  const scheduled = planned.filter((item) => items.includes(item));
  const running = asArray(active).filter((item) => items.includes(item));
  const value = items.length ? `${running.length}/${items.length}` : tr.noDevices;
  const note = scheduled.length ? `${tr.planned}: ${scheduled.join(", ")}` : items.join(", ");
  return tile(title, value, note || "-");
}

function acBatteryCard(attrs, tr) {
  const rows = Array.isArray(attrs.ac_battery_details) ? attrs.ac_battery_details : [];
  if (!rows.length) return tile(tr.acBattery, "-", attrs.ac_battery_reason || "");
  const first = rows[0];
  const value = first.soc == null ? "-" : `${Number(first.soc).toFixed(1)}%`;
  const note = `${tr.target}: ${tr.charging} ${power(first.target_charge)} · ${tr.discharging} ${power(first.target_discharge)}. ${first.reason || ""}`;
  return tile(tr.acBattery, value, note);
}

function events(attrs, tr) {
  const rows = Array.isArray(attrs.action_history) ? attrs.action_history.slice(0, 8) : [];
  if (!rows.length) return `<section class="card"><h2>${esc(tr.events)}</h2><p class="note">${esc(tr.noEvents)}</p></section>`;
  return `<section class="card"><h2>${esc(tr.events)}</h2>${rows.map((row) => `<div class="row"><div><strong>${esc(row.title || "")}</strong><p class="note">${esc(row.reason || "")}</p></div><span class="note">${esc(formatTime(row.time))}</span></div>`).join("")}</section>`;
}

function modeButtons(modeSelect, tr) {
  const options = modeSelect?.attributes?.options || ["auto", "off"];
  return options.map((option) => `<button class="${modeSelect?.state === option ? "active-button" : ""}" data-entity="${esc(modeSelect?.entity_id || "")}" data-mode="${esc(option)}" ${!modeSelect || modeSelect.state === option ? "disabled" : ""}>${esc(option === "auto" ? tr.active : "Off")}</button>`).join("");
}

function gridText(attrs, tr) {
  const gridImport = Number(attrs.grid_import || 0);
  const gridExport = Number(attrs.grid_export || 0);
  if (gridExport > gridImport) return `${tr.export} ${power(gridExport)}`;
  if (gridImport > 0) return `${tr.import} ${power(gridImport)}`;
  return "0 W";
}

function findEntity(states, key) {
  return states.find((entity) => entity.entity_id.endsWith(`_${key}`) || entity.entity_id.includes(key));
}

function asArray(value) {
  return Array.isArray(value) ? value : value ? [value] : [];
}

function power(value) {
  const watts = Number(value || 0);
  if (Math.abs(watts) >= 1000) return `${(watts / 1000).toLocaleString("de-DE", { maximumFractionDigits: 2 })} kW`;
  return `${Math.round(watts).toLocaleString("de-DE")} W`;
}

function formatTime(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
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

customElements.define("bb-hems-panel", BbHemsPanel);
