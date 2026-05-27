const ALIASES = {
  energy_mode: ["energy_mode", "energiemodus", "betrieb"],
  pv_window: ["pv_window", "pv fenster"],
  battery_soc_min: ["battery_soc_min", "batterie soc minimum", "batterie min"],
  battery_discharge_total: ["battery_discharge_total", "batterie entladung gesamt", "batterie entladung"],
  available_surplus_budget: ["available_surplus_budget", "verfugbares uberschussbudget", "verfuegbares ueberschussbudget"],
  scheduled_surplus_power: ["scheduled_surplus_power", "geplante uberschussleistung", "geplante ueberschussleistung"],
  shifted_energy_today: ["shifted_energy_today", "hems verschobene energie heute"],
  estimated_savings_today: ["estimated_savings_today", "hems ersparnis heute"],
  active_flexible_loads: ["active_flexible_loads", "aktive flexible verbraucher"],
  surplus_available: ["surplus_available", "uberschuss verfugbar", "ueberschuss verfuegbar"],
  battery_protect: ["battery_protect", "batterieschutz"],
  good_weather: ["good_weather", "wetterfreigabe"],
  flexible_loads_allowed: ["flexible_loads_allowed", "flexible verbraucher erlaubt"],
  auto_enabled: ["auto_enabled", "automatik aktiv"],
  mode_select: ["select.bb_hems_mode", "betriebsart", "operating mode"],
};

const BB_HEMS_VERSION = "0.2.3";
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
          --bg: var(--primary-background-color, #f6f7f9);
          --card: var(--card-background-color, #fff);
          --text: var(--primary-text-color, #202124);
          --muted: var(--secondary-text-color, #66727d);
          --line: var(--divider-color, #dfe3e8);
          --accent: var(--primary-color, #03a9c7);
          --good: #2e9f50;
          --warn: #d97904;
          --bad: #c93c37;
          --idle: #607d8b;
          --soft-good: #edf8f0;
          --soft-warn: #fff6e8;
          --soft-bad: #fff1ef;
          --soft-info: #eef7fb;
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
        .page { width: min(1480px, calc(100vw - 32px)); margin: 0 auto; padding: 24px 0 40px; }
        .headline {
          display: grid;
          grid-template-columns: minmax(0, 1fr) auto;
          gap: 14px;
          align-items: start;
          margin-bottom: 16px;
        }
        h1 { font-size: 30px; line-height: 1.1; font-weight: 650; }
        h2 { font-size: 18px; line-height: 1.2; font-weight: 650; }
        .subtitle { margin-top: 6px; color: var(--muted); font-size: 14px; }
        .link-row { display: flex; flex-wrap: wrap; gap: 8px; justify-content: end; }
        .link {
          min-height: 36px;
          display: inline-flex;
          align-items: center;
          padding: 8px 12px;
          border: 1px solid var(--line);
          border-radius: 8px;
          background: var(--card);
          color: #007fa3;
          font-size: 14px;
          text-decoration: none;
          box-shadow: var(--shadow);
        }
        .section { margin-top: 16px; }
        .section-head {
          display: flex;
          align-items: end;
          justify-content: space-between;
          gap: 12px;
          margin-bottom: 10px;
          padding: 0 2px;
        }
        .section-note { color: var(--muted); font-size: 13px; }
        .tile-grid {
          display: grid;
          grid-template-columns: repeat(4, minmax(0, 1fr));
          gap: 12px;
        }
        .tile-grid.wide { grid-template-columns: repeat(3, minmax(0, 1fr)); }
        .tile-grid.loads { grid-template-columns: repeat(4, minmax(0, 1fr)); }
        .tile {
          position: relative;
          min-height: 128px;
          padding: 14px;
          border: 1px solid var(--line);
          border-radius: 12px;
          background: var(--card);
          box-shadow: var(--shadow);
          overflow: hidden;
        }
        .tile::before {
          content: "";
          position: absolute;
          inset: 0 auto 0 0;
          width: 5px;
          background: var(--idle);
        }
        .tile.good::before { background: var(--good); }
        .tile.warn::before { background: var(--warn); }
        .tile.bad::before { background: var(--bad); }
        .tile.info::before { background: var(--accent); }
        .tile.good { background: linear-gradient(90deg, var(--soft-good), var(--card) 44%); }
        .tile.warn { background: linear-gradient(90deg, var(--soft-warn), var(--card) 44%); }
        .tile.bad { background: linear-gradient(90deg, var(--soft-bad), var(--card) 44%); }
        .tile.info { background: linear-gradient(90deg, var(--soft-info), var(--card) 44%); }
        .tile-top {
          display: flex;
          justify-content: space-between;
          gap: 10px;
          align-items: start;
          color: var(--muted);
          font-size: 13px;
          margin-bottom: 12px;
        }
        .icon {
          width: 34px;
          height: 34px;
          display: grid;
          place-items: center;
          border-radius: 50%;
          background: #edf1f4;
          color: var(--text);
          font-size: 18px;
          flex: 0 0 auto;
        }
        .value { font-size: 28px; line-height: 1.05; font-weight: 760; overflow-wrap: anywhere; }
        .small-value { font-size: 21px; }
        .note { margin-top: 8px; color: var(--muted); font-size: 12px; line-height: 1.35; }
        .pill {
          display: inline-flex;
          align-items: center;
          min-height: 24px;
          padding: 3px 8px;
          border-radius: 999px;
          background: #eef2f4;
          color: var(--muted);
          font-size: 12px;
          white-space: nowrap;
        }
        .pill.good { background: #e4f5e9; color: #17713a; }
        .pill.warn { background: #fff0d6; color: #9a5a00; }
        .pill.bad { background: #ffe5e1; color: #a9332f; }
        .control-panel {
          display: grid;
          grid-template-columns: minmax(0, 1fr) auto;
          gap: 12px;
          align-items: center;
          padding: 14px;
          border: 1px solid var(--line);
          border-radius: 12px;
          background: var(--card);
          box-shadow: var(--shadow);
        }
        .segmented {
          display: grid;
          grid-template-columns: repeat(5, minmax(82px, 1fr));
          gap: 4px;
          padding: 4px;
          border: 1px solid var(--line);
          border-radius: 10px;
          background: #f0f2f4;
        }
        .segment {
          min-height: 38px;
          border: 0;
          border-radius: 8px;
          background: transparent;
          color: var(--text);
          cursor: pointer;
          white-space: nowrap;
        }
        .segment.active {
          background: var(--card);
          color: var(--accent);
          font-weight: 700;
          box-shadow: var(--shadow);
        }
        .power {
          min-height: 46px;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          padding: 8px 14px;
          border: 1px solid #b9e2c9;
          border-radius: 10px;
          background: #eef9f2;
          color: #17713a;
          font-weight: 700;
          white-space: nowrap;
          cursor: pointer;
        }
        .power.off { color: var(--bad); border-color: #f2c2bd; background: #fff2f0; }
        .dot {
          width: 18px;
          height: 18px;
          border-radius: 50%;
          background: var(--good);
          box-shadow: inset 0 0 0 5px #fff;
        }
        .power.off .dot { background: var(--bad); }
        .main-layout {
          display: grid;
          grid-template-columns: minmax(0, 1.4fr) minmax(360px, .75fr);
          gap: 12px;
        }
        .stack { display: grid; gap: 12px; }
        .event-card, .next-card {
          padding: 14px 16px;
          border: 1px solid var(--line);
          border-radius: 12px;
          background: var(--card);
          box-shadow: var(--shadow);
        }
        .event-list { margin-top: 10px; display: grid; gap: 0; }
        .event {
          display: grid;
          grid-template-columns: 62px minmax(0, 1fr) auto;
          gap: 12px;
          align-items: start;
          padding: 12px 0;
          border-bottom: 1px solid var(--line);
          font-size: 13px;
        }
        .event:last-child { border-bottom: 0; }
        .event-time { color: var(--muted); white-space: nowrap; }
        .event-title { font-weight: 700; }
        .event-reason { margin-top: 4px; color: var(--muted); line-height: 1.35; }
        .next-item {
          display: grid;
          grid-template-columns: auto minmax(0, 1fr);
          gap: 10px;
          align-items: start;
          padding: 12px 0;
          border-bottom: 1px solid var(--line);
        }
        .next-item:last-child { border-bottom: 0; }
        .marker {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          margin-top: 5px;
          background: var(--accent);
        }
        @media (max-width: 1120px) {
          .headline, .main-layout, .control-panel { grid-template-columns: 1fr; }
          .link-row { justify-content: start; }
          .tile-grid, .tile-grid.wide, .tile-grid.loads { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        }
        @media (max-width: 680px) {
          .page { width: min(100vw - 20px, 100%); padding-top: 16px; }
          .tile-grid, .tile-grid.wide, .tile-grid.loads, .segmented { grid-template-columns: 1fr; }
          .event { grid-template-columns: 54px minmax(0, 1fr); }
          .event .pill { grid-column: 2; justify-self: start; }
          h1 { font-size: 26px; }
        }
      </style>

      <main class="page">
        <section class="headline">
          <div>
            <h1>BB HEMS</h1>
            <p class="subtitle">Version ${BB_HEMS_VERSION} · Was HEMS gerade entscheidet, schaltet und einspart</p>
          </div>
          <div class="link-row">
            <a class="link" href="/config/integrations/integration/bb_hems">Konfiguration</a>
            <a class="link" href="/config/entities">Entitäten</a>
            <a class="link" href="/config/devices/dashboard">Geräte</a>
          </div>
        </section>

        ${controls(modeSelect, autoSwitch)}

        <section class="section">
          <div class="section-head">
            <h2>Nutzen heute</h2>
            <span class="section-note">Nur HEMS-Werte, keine allgemeine Energiebilanz</span>
          </div>
          <div class="tile-grid">
            ${benefitTile("HEMS verschoben", energy(byKey(states, "shifted_energy_today")), "Energie wurde in PV-/Überschusszeit gelegt.", "↗", "good")}
            ${benefitTile("geschätzte Ersparnis", money(byKey(states, "estimated_savings_today")), "Berechnet mit 0,32 EUR/kWh als konservativer Schätzwert.", "€", "good")}
            ${benefitTile("geplante Leistung", power(byKey(states, "scheduled_surplus_power")), "Aktuell für HEMS-Verbraucher eingeplant.", "⚡", "info")}
            ${benefitTile("aktive HEMS-Lasten", val(byKey(states, "active_flexible_loads")), "Aktuell durch HEMS freigegebene oder laufende Verbraucher.", "✓", activeLoadClass(byKey(states, "active_flexible_loads")))}
          </div>
        </section>

        <section class="section main-layout">
          <div class="stack">
            <div>
              <div class="section-head">
                <h2>Entscheidung jetzt</h2>
                <span class="section-note">Warum HEMS gerade schalten darf oder wartet</span>
              </div>
              <div class="tile-grid wide">
                ${decisionStatusTile(states, attrs)}
                ${decisionBudgetTile(states, attrs)}
                ${nextCandidateTile(attrs)}
              </div>
            </div>

            <div>
              <div class="section-head">
                <h2>Verbraucher</h2>
                <span class="section-note">Was HEMS aktiv steuert</span>
              </div>
              <div class="tile-grid loads">
                ${loadTiles(attrs, states)}
              </div>
            </div>
          </div>

          <aside class="stack">
            ${blockerCard(states, attrs)}
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
  return `<section class="section"><div class="control-panel">
    <div><h2>Steuerung</h2><p class="section-note">Schnell umstellen, ohne die Integration zu öffnen</p></div>
    <div class="segmented">${options.map((option) => `<button class="segment ${option === current ? "active" : ""}" data-select-entity="${esc(modeSelect?.entity_id || "")}" data-select-option="${esc(option)}" ${!modeSelect || option === current ? "disabled" : ""}>${esc(MODE_LABELS[option] || option)}</button>`).join("")}</div>
    <button class="power ${autoSwitch?.state === "off" ? "off" : ""}" data-switch-entity="${esc(autoSwitch?.entity_id || "")}" ${!autoSwitch ? "disabled" : ""}><span class="dot"></span>${autoSwitch?.state === "off" ? "HEMS pausiert" : "HEMS aktiv"}</button>
  </div></section>`;
}

function benefitTile(label, value, note, icon, state) {
  return `<article class="tile ${state}"><div class="tile-top"><span>${esc(label)}</span><span class="icon">${esc(icon)}</span></div><div class="value">${esc(value)}</div><div class="note">${esc(note)}</div></article>`;
}

function decisionStatusTile(states, attrs) {
  const allowed = isOn(byKey(states, "flexible_loads_allowed")) || attrs.flexible_loads_allowed;
  const protect = isOn(byKey(states, "battery_protect")) || attrs.battery_protect;
  const surplus = isOn(byKey(states, "surplus_available")) || attrs.surplus_available;
  const status = protect ? "Batterieschutz aktiv" : allowed ? "Überschuss aktiv" : surplus ? "wartet auf Freigabe" : "kein Überschuss";
  const state = protect ? "bad" : allowed ? "good" : surplus ? "warn" : "info";
  const pill = protect ? "gesperrt" : allowed ? "frei" : "wartet";
  const reason = attrs.load_reason || attrs.surplus_reason || "HEMS bewertet PV-Fenster, Überschuss, Batterie und Wetter.";
  return `<article class="tile ${state}"><div class="tile-top"><span>Status</span><span class="pill ${state}">${pill}</span></div><div class="value small-value">${esc(status)}</div><div class="note">${esc(reason)}</div></article>`;
}

function decisionBudgetTile(states, attrs) {
  const budget = numericState(byKey(states, "available_surplus_budget"));
  const state = budget > 1000 ? "good" : budget > 0 ? "warn" : "bad";
  const pill = budget > 1000 ? "passt" : budget > 0 ? "knapp" : "blockiert";
  const note = attrs.scheduler_reason || "HEMS nutzt das verfügbare Überschussbudget für geplante Verbraucher.";
  return `<article class="tile ${state}"><div class="tile-top"><span>Überschussbudget</span><span class="pill ${state}">${pill}</span></div><div class="value">${esc(power(byKey(states, "available_surplus_budget")))}</div><div class="note">${esc(note)}</div></article>`;
}

function nextCandidateTile(attrs) {
  const scheduled = list(attrs.scheduled_surplus_loads);
  const hasScheduled = scheduled !== "nicht gesetzt";
  const candidate = hasScheduled ? scheduled : nextConfiguredLoad(attrs);
  const state = hasScheduled ? "good" : candidate === "nicht konfiguriert" ? "bad" : "warn";
  const pill = hasScheduled ? "geplant" : candidate === "nicht konfiguriert" ? "fehlt" : "wartet";
  const note = hasScheduled ? "Diese Verbraucher passen aktuell ins HEMS-Budget." : "Wird freigegeben, sobald Budget, PV-Fenster und Batterieschutz passen.";
  return `<article class="tile ${state}"><div class="tile-top"><span>Nächster Kandidat</span><span class="pill ${state}">${pill}</span></div><div class="value small-value">${esc(candidate)}</div><div class="note">${esc(note)}</div></article>`;
}

function loadTiles(attrs, states) {
  return [
    loadTile("Flexible Lasten", attrs.flexible_load_switches, attrs.configured_flexible_loads, "info", "Dürfen bei Überschuss starten.", attrs.scheduled_surplus_loads),
    loadTile("Heizstäbe", attrs.heating_rod_switches, attrs.configured_heating_rods, "good", "Werden als Überschussverbraucher priorisiert.", attrs.scheduled_surplus_loads),
    loadTile("Wallboxen", attrs.wallbox_switches, attrs.configured_wallboxes, "warn", "Aktuell als Gruppe erfasst, Detailstrategie folgt.", attrs.scheduled_surplus_loads),
    loadTile("Wärmepumpen", attrs.heat_pump_switches, attrs.configured_heat_pumps, "warn", "Aktuell als Gruppe erfasst, Detailstrategie folgt.", attrs.scheduled_surplus_loads),
  ].join("");
}

function loadTile(title, entities, count, configuredState, fallbackNote, scheduledLoads) {
  const items = asArray(entities);
  const configured = Number(count ?? items.length);
  const scheduled = asArray(scheduledLoads).filter((entity) => items.includes(entity));
  const state = configured <= 0 ? "bad" : scheduled.length ? "good" : configuredState;
  const pill = configured <= 0 ? "nicht konfiguriert" : scheduled.length ? "aktiv" : "bereit";
  const value = configured <= 0 ? "kein Gerät" : scheduled.length ? `${scheduled.length} aktiv` : `${configured} Gerät${configured === 1 ? "" : "e"}`;
  const note = scheduled.length ? `Geplant: ${scheduled.join(", ")}` : fallbackNote;
  return `<article class="tile ${state}"><div class="tile-top"><span>${esc(title)}</span><span class="pill ${state}">${esc(pill)}</span></div><div class="value small-value">${esc(value)}</div><div class="note">${esc(note)}</div></article>`;
}

function blockerCard(states, attrs) {
  const protect = isOn(byKey(states, "battery_protect")) || attrs.battery_protect;
  const weather = isOn(byKey(states, "good_weather")) || attrs.good_weather;
  const pvWindow = attrs.pv_window || byKey(states, "pv_window")?.state;
  const budget = numericState(byKey(states, "available_surplus_budget"));
  return `<section class="next-card">
    <h2>Blocker & Freigaben</h2>
    ${blockerItem(!protect, "Batterieschutz frei", attrs.battery_reason || "Batterie ist nicht im Schutzmodus.")}
    ${blockerItem(weather, "Wetterfreigabe", attrs.weather_reason || "Wetter- und Sonnenwerte werden bewertet.")}
    ${blockerItem(Boolean(pvWindow && !["night", "low_today", "weak_now"].includes(pvWindow)), "PV-Fenster", attrs.pv_window_reason || `PV-Fenster: ${pvWindow || "unbekannt"}.`)}
    ${blockerItem(budget > 0, "Überschussbudget", budget > 0 ? `${Math.round(budget)} W verfügbar.` : "Kein nutzbares Budget verfügbar.")}
  </section>`;
}

function blockerItem(ok, title, text) {
  return `<div class="next-item"><span class="marker" style="background:var(--${ok ? "good" : "warn"})"></span><div><strong>${esc(title)}</strong><p class="note">${esc(text)}</p></div></div>`;
}

function actionHistory(attrs) {
  const rows = Array.isArray(attrs.action_history) ? attrs.action_history.slice(0, 8) : [];
  if (!rows.length) return `<section class="event-card"><h2>HEMS Ereignisse</h2><div class="note">Noch keine HEMS-Ereignisse sichtbar.</div></section>`;
  return `<section class="event-card"><h2>HEMS Ereignisse</h2><div class="event-list">${rows.map((event) => {
    const blocked = String(event.kind || "").includes("block") || String(event.kind || "").includes("protect");
    return `<div class="event"><div class="event-time">${esc(formatTime(event.time))}</div><div><div class="event-title">${esc(event.title || "HEMS-Ereignis")}</div><div class="event-reason">${esc(event.reason || "")}</div></div><span class="pill ${blocked ? "warn" : "good"}">${blocked ? "wartet" : "aktiv"}</span></div>`;
  }).join("")}</div></section>`;
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

function val(entity) {
  if (!entity) return "nicht vorhanden";
  if (["unknown", "unavailable"].includes(entity.state)) return entity.state;
  const unit = entity.attributes.unit_of_measurement || "";
  return `${entity.state}${unit ? ` ${unit}` : ""}`;
}

function power(entity) {
  const watts = numericState(entity);
  const kw = watts / 1000;
  return `${kw.toLocaleString("de-DE", { minimumFractionDigits: Math.abs(kw) >= 10 ? 0 : 1, maximumFractionDigits: 1 })} kW`;
}

function energy(entity) {
  if (!entity) return "0,00 kWh";
  return `${numericState(entity).toLocaleString("de-DE", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} kWh`;
}

function money(entity) {
  return numericState(entity).toLocaleString("de-DE", { style: "currency", currency: "EUR" });
}

function activeLoadClass(entity) {
  return numericState(entity) > 0 ? "good" : "warn";
}

function asArray(value) {
  if (Array.isArray(value)) return value.filter(Boolean);
  if (!value) return [];
  return [value];
}

function list(value) {
  const items = asArray(value);
  return items.length ? items.join(", ") : "nicht gesetzt";
}

function nextConfiguredLoad(attrs) {
  const groups = [
    attrs.heating_rod_switches,
    attrs.flexible_load_switches,
    attrs.wallbox_switches,
    attrs.heat_pump_switches,
  ];
  for (const group of groups) {
    const items = asArray(group);
    if (items.length) return items[0];
  }
  return "nicht konfiguriert";
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
