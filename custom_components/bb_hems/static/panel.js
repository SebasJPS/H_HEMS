const ALIASES = {
  energy_mode: ["energy_mode", "energiemodus", "betrieb"],
  grid_power: ["grid_power", "netzleistung aktuell"],
  grid_average: ["grid_average", "netzleistung 15 min", "netzleistung 15 minuten mittel"],
  pv_power_total: ["pv_power_total", "pv leistung gesamt", "pv gesamt"],
  pv_average: ["pv_average", "pv leistung 15 min", "pv 15 minuten mittel"],
  pv_window: ["pv_window", "pv fenster"],
  battery_soc_min: ["battery_soc_min", "batterie soc minimum", "batterie min"],
  battery_discharge_total: ["battery_discharge_total", "batterie entladung gesamt", "batterie entladung"],
  grid_tolerance: ["grid_tolerance", "netztoleranz"],
  surplus_available: ["surplus_available", "uberschuss verfugbar", "ueberschuss verfuegbar"],
  battery_protect: ["battery_protect", "batterieschutz"],
  good_weather: ["good_weather", "wetterfreigabe"],
  flexible_loads_allowed: ["flexible_loads_allowed", "flexible verbraucher erlaubt"],
};

const BB_HEMS_VERSION = "0.1.15";

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
    const surplus = isOn(byKey(states, "surplus_available"));
    const protect = isOn(byKey(states, "battery_protect"));
    const weather = isOn(byKey(states, "good_weather"));
    const allowed = isOn(byKey(states, "flexible_loads_allowed"));

    this.innerHTML = `
      <style>
        :host {
          --bg: var(--primary-background-color, #f6f7f9);
          --card: var(--card-background-color, #fff);
          --text: var(--primary-text-color, #17212b);
          --muted: var(--secondary-text-color, #66727d);
          --line: var(--divider-color, #dde3e8);
          --accent: var(--primary-color, #007a7a);
          --good: #0b7a53;
          --warn: #a86400;
          --bad: #b42318;
          display: block;
          min-height: 100vh;
          background: var(--bg);
          color: var(--text);
          font-family: var(--paper-font-body1_-_font-family, Roboto, system-ui, sans-serif);
        }
        * { box-sizing: border-box; }
        .page { width: min(1480px, calc(100vw - 32px)); margin: 0 auto; padding: 24px 0 36px; }
        .top { display: grid; grid-template-columns: 1fr auto; gap: 16px; align-items: start; margin-bottom: 16px; }
        h1, h2, h3, p { margin: 0; letter-spacing: 0; }
        h1 { font-size: 28px; line-height: 1.1; }
        h2 { font-size: 16px; }
        h3 { font-size: 13px; color: var(--muted); }
        .sub { margin-top: 6px; color: var(--muted); font-size: 14px; }
        .pill { display: inline-flex; align-items: center; gap: 8px; padding: 7px 12px; border: 1px solid var(--line); border-radius: 999px; background: var(--card); white-space: nowrap; }
        .dot { width: 10px; height: 10px; border-radius: 50%; background: var(--muted); flex: 0 0 auto; }
        .good { background: var(--good); }
        .warn { background: var(--warn); }
        .bad { background: var(--bad); }
        .grid { display: grid; gap: 14px; }
        .hero { grid-template-columns: repeat(4, minmax(0, 1fr)); }
        .layout { grid-template-columns: minmax(0, 1.45fr) minmax(360px, .85fr); align-items: start; margin-top: 14px; }
        .stack { display: grid; gap: 14px; }
        .card, .metric, .node, .decision, .asset { background: var(--card); border: 1px solid var(--line); border-radius: 8px; }
        .card { overflow: hidden; }
        .head { display: flex; justify-content: space-between; gap: 12px; padding: 14px 16px; border-bottom: 1px solid var(--line); }
        .body { padding: 16px; }
        .metric { min-height: 104px; padding: 14px; }
        .metric.primary { border-color: var(--accent); background: color-mix(in srgb, var(--accent), transparent 91%); }
        .label { display: flex; justify-content: space-between; gap: 8px; margin-bottom: 10px; color: var(--muted); font-size: 13px; }
        .value { font-size: 26px; line-height: 1.05; font-weight: 720; overflow-wrap: anywhere; }
        .small { font-size: 20px; }
        .note { margin-top: 8px; color: var(--muted); font-size: 12px; }
        .flow { grid-template-columns: 1fr auto 1fr auto 1fr; align-items: center; }
        .node { min-height: 112px; padding: 14px; background: color-mix(in srgb, var(--card), var(--bg) 28%); }
        .arrow { color: var(--muted); font-size: 26px; }
        .decisions { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .decision { display: grid; grid-template-columns: auto 1fr; gap: 10px; padding: 12px; background: color-mix(in srgb, var(--card), var(--bg) 28%); }
        .asset-grid { grid-template-columns: repeat(6, minmax(0, 1fr)); }
        .asset { padding: 12px; background: color-mix(in srgb, var(--card), var(--bg) 28%); }
        .count { margin-top: 8px; font-size: 24px; font-weight: 720; }
        .actions { display: grid; gap: 10px; }
        .event { display: grid; grid-template-columns: 88px auto 1fr; gap: 10px; align-items: start; padding: 10px 0; border-bottom: 1px solid var(--line); }
        .event:last-child { border-bottom: 0; }
        .event-time { color: var(--muted); font-size: 12px; white-space: nowrap; padding-top: 2px; }
        .event-title { font-weight: 700; }
        .event-reason { margin-top: 3px; color: var(--muted); font-size: 13px; line-height: 1.35; }
        .muted { color: var(--muted); }
        table { width: 100%; border-collapse: collapse; font-size: 14px; }
        td, th { padding: 10px 8px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
        tr:last-child td { border-bottom: 0; }
        .rows { display: grid; gap: 8px; }
        .row { display: grid; grid-template-columns: minmax(120px, .8fr) minmax(0, 1.2fr); gap: 10px; padding: 9px 0; border-bottom: 1px solid var(--line); font-size: 14px; }
        .row:last-child { border-bottom: 0; }
        .empty { padding: 14px; border: 1px dashed var(--line); border-radius: 8px; color: var(--muted); font-size: 14px; }
        .control { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 10px; align-items: center; padding: 9px 0; border-bottom: 1px solid var(--line); }
        .control:last-child { border-bottom: 0; }
        .control.select-control { grid-template-columns: minmax(0, 1fr); }
        .control input { min-height: 34px; border: 1px solid var(--line); border-radius: 6px; padding: 4px 8px; background: var(--card); color: var(--text); font: inherit; }
        .control button, .action { min-height: 34px; border: 1px solid var(--accent); border-radius: 6px; padding: 5px 10px; background: color-mix(in srgb, var(--accent), transparent 88%); color: var(--accent); font: inherit; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; justify-content: center; }
        .mode-buttons { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; margin-top: 8px; }
        .mode-option { width: 100%; min-height: 38px; }
        .mode-option.active { background: var(--accent); color: var(--card); }
        .mode-option[disabled] { cursor: default; opacity: 1; }
        .hint { margin-top: 8px; color: var(--muted); font-size: 12px; }
        @media (max-width: 1100px) { .layout, .hero, .asset-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .flow { grid-template-columns: 1fr; } .arrow { display: none; } }
        @media (max-width: 720px) { .page { width: min(100vw - 20px, 100%); padding-top: 12px; } .top, .layout, .hero, .decisions, .asset-grid { grid-template-columns: 1fr; } .pill { justify-self: start; white-space: normal; } }
      </style>

      <main class="page">
        <header class="top">
          <div>
            <h1>BB HEMS</h1>
            <p class="sub">Version ${BB_HEMS_VERSION} · Live-Status, Freigaben, Schutzlogik und konfigurierte Energiequellen</p>
          </div>
          <div class="pill"><span class="dot ${protect ? "bad" : allowed ? "good" : "warn"}"></span>${mode ? `Aktuell: ${esc(mode.state)}` : "BB HEMS-Entitäten nicht gefunden"}</div>
        </header>

        <section class="grid hero">
          ${metric(states, "energy_mode", "Betrieb", "Aktueller HEMS-Modus", true)}
          ${metric(states, "grid_power", "Netz", "Negativ = Einspeisung")}
          ${metric(states, "pv_power_total", "PV", "Summe aller PV-Quellen")}
          ${metric(states, "pv_window", "PV-Fenster", "Forecast und Sonnenstand")}
        </section>

        <section class="grid layout">
          <div class="stack">
            <section class="card">
              <div class="head"><h2>Energiefluss</h2><span class="muted">${new Date().toLocaleString("de-DE")}</span></div>
              <div class="body"><div class="grid flow">${flow(states)}</div></div>
            </section>
            <section class="card">
              <div class="head"><h2>Entscheidung</h2><span class="muted">Warum Verbraucher freigegeben oder gesperrt sind</span></div>
              <div class="body"><div class="grid decisions">
                ${decision("Überschuss", surplus, attrs.surplus_reason || `PV ${val(byKey(states, "pv_power_total"))}, PV 15 min ${val(byKey(states, "pv_average"))}, Netz ${val(byKey(states, "grid_power"))}, Toleranz ${val(byKey(states, "grid_tolerance"))}.`)}
                ${decision("Batterieschutz", protect, attrs.battery_reason || "Aktiv bei niedrigem SoC, hoher Batterieentladung oder sehr schlechtem Wetter.", true)}
                ${decision("Wetterfreigabe", weather, attrs.weather_reason || "Bewertet Wetterzustand, Bewölkung, Sonne und Batterie-SoC.")}
                ${decision("Flexible Verbraucher", allowed, attrs.scheduler_reason || attrs.load_reason || "Nur aktiv, wenn Überschuss, Wetterfreigabe und Batterieschutz zusammen passen.")}
                ${decision("PV-Fenster", !["night", "low_today", "weak_now"].includes(attrs.pv_window), attrs.pv_window_reason || "Bewertet PV-Forecast, Sonnenstand und PV-Ausrichtung.")}
              </div></div>
            </section>
            <section class="card">
              <div class="head"><h2>Anlagen</h2><span class="muted">Skaliert für mehrere Quellen und Verbraucher</span></div>
              <div class="body"><div class="grid asset-grid">${assets(attrs)}</div></div>
            </section>
            <section class="card">
              <div class="head"><h2>Was zuletzt passiert ist</h2><span class="muted">Letzte 10 HEMS-Ereignisse</span></div>
              <div class="body">${actionHistory(attrs)}</div>
            </section>
          </div>

          <div class="stack">
            <section class="card"><div class="head"><h2>Letzte HEMS-Werte</h2></div><div class="body">${recent(states)}</div></section>
            <section class="card"><div class="head"><h2>Konfiguration</h2></div><div class="body">${config(attrs)}</div></section>
            <section class="card"><div class="head"><h2>Einstellungen</h2></div><div class="body">${settings(states, attrs)}</div></section>
          </div>
        </section>
      </main>
    `;
    this.bindControls(states);
  }

  bindControls(states) {
    this.querySelectorAll("[data-number-entity]").forEach((input) => {
      input.addEventListener("change", () => {
        this._hass.callService("number", "set_value", {
          entity_id: input.dataset.numberEntity,
          value: Number(input.value),
        });
      });
    });
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
  return aliases.some((alias) => text.includes(norm(alias)));
}

function norm(value) {
  return String(value || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[_-]+/g, " ");
}

function isOn(entity) {
  return entity?.state === "on";
}

function name(entity) {
  return entity?.attributes?.friendly_name || entity?.entity_id || "nicht vorhanden";
}

function val(entity) {
  if (!entity) return "nicht vorhanden";
  if (["unknown", "unavailable"].includes(entity.state)) return entity.state;
  const unit = entity.attributes.unit_of_measurement || "";
  return `${entity.state}${unit ? ` ${unit}` : ""}`;
}

function esc(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function metric(states, key, label, note, primary = false) {
  const entity = byKey(states, key);
  return `<article class="metric ${primary ? "primary" : ""}"><div class="label"><span>${label}</span><span>${esc(entity?.entity_id || "")}</span></div><div class="value ${key === "energy_mode" ? "small" : ""}">${esc(val(entity))}</div><div class="note">${note}</div></article>`;
}

function flow(states) {
  const items = [
    ["pv_power_total", "PV-Erzeugung", "Aus allen PV- und Balkonkraftwerk-Sensoren"],
    ["battery_discharge_total", "Batterie", "Entladung und SoC-Schutz"],
    ["grid_power", "Netzanschluss", "Bezug oder Einspeisung"],
  ];
  return items.map(([key, title, note], index) => {
    const node = `<div class="node"><h3>${title}</h3><div class="value" style="margin-top:10px">${esc(val(byKey(states, key)))}</div><div class="note">${note}</div></div>`;
    return index < items.length - 1 ? `${node}<div class="arrow">></div>` : node;
  }).join("");
}

function decision(title, active, text, badWhenTrue = false) {
  const state = badWhenTrue ? (active ? "bad" : "good") : (active ? "good" : "warn");
  return `<div class="decision"><span class="dot ${state}"></span><div><strong>${title}: ${active ? "ja" : "nein"}</strong><div class="muted">${esc(text)}</div></div></div>`;
}

function assets(attrs) {
  return [
    ["PV-Quellen", attrs.configured_pv_sources ?? 0],
    ["Batterien", attrs.configured_batteries ?? 0],
    ["Verbraucher", attrs.configured_flexible_loads ?? 0],
    ["Wallboxen", attrs.configured_wallboxes ?? 0],
    ["Wärmepumpen", attrs.configured_heat_pumps ?? 0],
    ["Heizstäbe", attrs.configured_heating_rods ?? 0],
  ].map(([label, count]) => `<div class="asset"><h3>${label}</h3><div class="count">${count}</div></div>`).join("");
}

function actionHistory(attrs) {
  const rows = Array.isArray(attrs.action_history) ? attrs.action_history.slice(0, 10) : [];
  if (!rows.length) return `<div class="empty">Noch keine HEMS-Ereignisse sichtbar. Die Historie startet nach dem nächsten Update der Integration.</div>`;
  return `<div class="actions">${rows.map((event) => {
    const kind = event.kind || "";
    const state = kind.includes("protect") || kind.includes("block") ? "bad" : kind.includes("allow") || kind.includes("surplus") ? "good" : "warn";
    return `<div class="event"><span class="event-time">${esc(formatTime(event.time))}</span><span class="dot ${state}"></span><div><div class="event-title">${esc(event.title || "HEMS-Ereignis")}</div><div class="event-reason">${esc(event.reason || "")}</div></div></div>`;
  }).join("")}</div>`;
}

function settings(states, attrs) {
  const rows = states
    .filter((entity) => ["number", "select", "switch"].includes(entity.entity_id.split(".")[0]))
    .filter((entity) => shouldShowSetting(entity, attrs))
    .sort((a, b) => name(a).localeCompare(name(b)));
  if (!rows.length) return `<div class="empty">Keine HEMS-Einstellungen gefunden.</div>`;
  return `<div>${rows.map((entity) => settingControl(entity)).join("")}<div class="hint">Änderungen werden direkt an Home Assistant gesendet.</div></div>`;
}

function shouldShowSetting(entity, attrs) {
  const entityId = entity.entity_id || "";
  if (entityId.includes("flexible_load_power") && hasItems(attrs.flexible_load_power_sensors)) return false;
  if (entityId.includes("heating_rod_power") && hasItems(attrs.heating_rod_power_sensors)) return false;
  return true;
}

function settingControl(entity) {
  const domain = entity.entity_id.split(".")[0];
  if (domain === "number") {
    const min = entity.attributes.min ?? "";
    const max = entity.attributes.max ?? "";
    const step = entity.attributes.step ?? 1;
    return `<label class="control"><span>${esc(name(entity))}</span><input data-number-entity="${esc(entity.entity_id)}" type="number" value="${esc(entity.state)}" min="${esc(min)}" max="${esc(max)}" step="${esc(step)}"></label>`;
  }
  if (domain === "select") {
    const options = entity.attributes.options || [];
    return `<div class="control select-control"><span>${esc(name(entity))}</span><div class="mode-buttons">${options.map((option) => {
      const active = option === entity.state;
      return `<button class="mode-option ${active ? "active" : ""}" data-select-entity="${esc(entity.entity_id)}" data-select-option="${esc(option)}" ${active ? "disabled" : ""}>${esc(option)}</button>`;
    }).join("")}</div></div>`;
  }
  return `<div class="control"><span>${esc(name(entity))}</span><button data-switch-entity="${esc(entity.entity_id)}">${entity.state === "on" ? "Ausschalten" : "Einschalten"}</button></div>`;
}

function list(value) {
  if (Array.isArray(value)) return value.length ? value.join(", ") : "nicht gesetzt";
  return value || "nicht gesetzt";
}

function hasItems(value) {
  return Array.isArray(value) && value.length > 0;
}

function config(attrs) {
  if (!Object.keys(attrs).length) return `<div class="empty">Die Konfiguration ist noch nicht sichtbar. Erwartet wird der BB HEMS Energiemodus-Sensor mit Attributen.</div><div class="hint"><a class="action" href="/config/integrations/integration/bb_hems">Konfiguration öffnen</a></div>`;
  const rows = [
    ["Netz aktuell", attrs.grid_power_sensor],
    ["Netz 15 min", attrs.grid_average_sensor],
    ["PV-Quellen", attrs.pv_power_sensors],
    ["PV 15 min", attrs.pv_average_sensor],
    ["PV Forecast heute", attrs.pv_forecast_today_sensor],
    ["PV Forecast nächste Stunde", attrs.pv_forecast_next_hour_sensor],
    ["PV Forecast nächste 3 h", attrs.pv_forecast_next_3h_sensor],
    ["Sonne", attrs.sun_entity],
    ["Batterie-SoC", attrs.battery_soc_sensors],
    ["Batterie-Entladung", attrs.battery_discharge_sensors],
    ["Wetter", attrs.weather_state_sensor],
    ["Flexible Verbraucher", attrs.flexible_load_switches],
    ["Leistung flexible Verbraucher", attrs.flexible_load_power_sensors],
    ["Wallboxen", attrs.wallbox_switches],
    ["Wärmepumpen", attrs.heat_pump_switches],
    ["Heizstäbe", attrs.heating_rod_switches],
    ["Leistung Heizstäbe", attrs.heating_rod_power_sensors],
    ["Reaktionsmodus", attrs.response_profile],
    ["Einschaltverzögerung", formatSeconds(attrs.switch_on_delay_seconds)],
    ["Ausschaltverzögerung", formatSeconds(attrs.switch_off_delay_seconds)],
    ["Verfügbares Budget", formatWatts(attrs.available_surplus_budget)],
    ["Geplante Verbraucher", attrs.scheduled_surplus_loads],
    ["Geplante Leistung", formatWatts(attrs.scheduled_surplus_power)],
  ];
  return `<div class="rows">${rows.map(([label, value]) => `<div class="row"><strong>${label}</strong><span>${esc(list(value))}</span></div>`).join("")}</div><div class="hint"><a class="action" href="/config/integrations/integration/bb_hems">Konfiguration ändern</a></div>`;
}

function recent(states) {
  const rows = states
    .filter((entity) => Object.keys(ALIASES).some((key) => matches(entity, ALIASES[key])))
    .sort((a, b) => new Date(b.last_changed) - new Date(a.last_changed))
    .slice(0, 8);
  if (!rows.length) return `<div class="empty">Noch keine BB HEMS-Entitäten sichtbar.</div>`;
  return `<table><thead><tr><th>Entität</th><th>Wert</th></tr></thead><tbody>${rows.map((entity) => `<tr><td>${esc(name(entity))}</td><td>${esc(val(entity))}</td></tr>`).join("")}</tbody></table>`;
}

function formatTime(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function formatSeconds(value) {
  const seconds = Number(value);
  if (!Number.isFinite(seconds)) return "nicht gesetzt";
  if (seconds === 0) return "sofort";
  if (seconds < 60) return `${seconds} s`;
  return `${Math.round(seconds / 60)} min`;
}

function formatWatts(value) {
  const watts = Number(value);
  if (!Number.isFinite(watts)) return "nicht gesetzt";
  return `${Math.round(watts)} W`;
}

customElements.define("bb-hems-panel", BbHemsPanel);
