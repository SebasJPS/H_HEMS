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

    const states = Object.values(this._hass.states);
    const energyMode = findByKey(states, "energy_mode");
    const data = energyMode?.attributes || {};
    const protect = findByKey(states, "battery_protect")?.state === "on";
    const allowed = findByKey(states, "flexible_loads_allowed")?.state === "on";
    const surplus = findByKey(states, "surplus_available")?.state === "on";
    const weather = findByKey(states, "good_weather")?.state === "on";

    this.innerHTML = `
      <style>
        :host {
          --bb-bg: var(--primary-background-color, #f4f6f8);
          --bb-card: var(--card-background-color, #ffffff);
          --bb-text: var(--primary-text-color, #17212b);
          --bb-muted: var(--secondary-text-color, #64727f);
          --bb-line: var(--divider-color, #d8e0e7);
          --bb-accent: var(--primary-color, #007a7a);
          --bb-good: #0b7a53;
          --bb-warn: #a86400;
          --bb-bad: #b42318;
          display: block;
          min-height: 100vh;
          background: var(--bb-bg);
          color: var(--bb-text);
          font-family: var(--paper-font-body1_-_font-family, Roboto, system-ui, sans-serif);
        }
        * { box-sizing: border-box; }
        .page { width: min(1480px, calc(100vw - 32px)); margin: 0 auto; padding: 24px 0 36px; }
        .masthead { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 16px; align-items: start; margin-bottom: 16px; }
        h1, h2, h3, p { margin: 0; letter-spacing: 0; }
        h1 { font-size: 28px; line-height: 1.1; }
        h2 { font-size: 16px; line-height: 1.2; }
        h3 { color: var(--bb-muted); font-size: 13px; font-weight: 650; }
        .subline { margin-top: 6px; color: var(--bb-muted); font-size: 14px; }
        .pill { display: inline-flex; align-items: center; gap: 8px; min-height: 34px; padding: 7px 12px; border: 1px solid var(--bb-line); border-radius: 999px; background: var(--bb-card); font-size: 14px; white-space: nowrap; }
        .dot { width: 10px; height: 10px; border-radius: 50%; background: var(--bb-muted); flex: 0 0 auto; }
        .good { background: var(--bb-good); }
        .warn { background: var(--bb-warn); }
        .bad { background: var(--bb-bad); }
        .grid { display: grid; gap: 14px; }
        .hero { grid-template-columns: repeat(4, minmax(0, 1fr)); }
        .layout { grid-template-columns: minmax(0, 1.5fr) minmax(360px, .8fr); align-items: start; margin-top: 14px; }
        .stack { display: grid; gap: 14px; }
        .card { background: var(--bb-card); border: 1px solid var(--bb-line); border-radius: 8px; overflow: hidden; }
        .card-head { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 14px 16px; border-bottom: 1px solid var(--bb-line); }
        .card-body { padding: 16px; }
        .metric { min-height: 104px; padding: 14px; border: 1px solid var(--bb-line); border-radius: 8px; background: var(--bb-card); }
        .metric.primary { border-color: var(--bb-accent); background: color-mix(in srgb, var(--bb-accent), transparent 90%); }
        .label { display: flex; justify-content: space-between; gap: 8px; margin-bottom: 10px; color: var(--bb-muted); font-size: 13px; }
        .value { font-size: 26px; line-height: 1.05; font-weight: 720; overflow-wrap: anywhere; }
        .value.small { font-size: 20px; }
        .note { margin-top: 8px; color: var(--bb-muted); font-size: 12px; }
        .flow { display: grid; grid-template-columns: 1fr auto 1fr auto 1fr; gap: 10px; align-items: center; }
        .flow-node, .asset, .decision { border: 1px solid var(--bb-line); border-radius: 8px; background: color-mix(in srgb, var(--bb-card), var(--bb-bg) 28%); }
        .flow-node { min-height: 112px; padding: 14px; }
        .flow-arrow { color: var(--bb-muted); font-size: 26px; }
        .decision-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .decision { display: grid; grid-template-columns: auto minmax(0, 1fr); gap: 10px; align-items: start; padding: 12px; }
        .decision strong { display: block; margin-bottom: 3px; }
        .asset-grid { grid-template-columns: repeat(5, minmax(0, 1fr)); }
        .asset { padding: 12px; }
        .asset-count { margin-top: 8px; font-size: 24px; font-weight: 720; }
        .muted { color: var(--bb-muted); }
        table { width: 100%; border-collapse: collapse; font-size: 14px; }
        th, td { padding: 10px 8px; border-bottom: 1px solid var(--bb-line); text-align: left; vertical-align: top; }
        th { color: var(--bb-muted); font-weight: 650; }
        tr:last-child td { border-bottom: 0; }
        .entity-list { display: grid; gap: 8px; }
        .entity-row { display: grid; grid-template-columns: minmax(120px, .8fr) minmax(0, 1.2fr); gap: 10px; padding: 9px 0; border-bottom: 1px solid var(--bb-line); font-size: 14px; }
        .entity-row:last-child { border-bottom: 0; }
        .empty { padding: 14px; border: 1px dashed var(--bb-line); border-radius: 8px; color: var(--bb-muted); font-size: 14px; }
        @media (max-width: 1100px) {
          .layout, .hero, .asset-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
          .flow { grid-template-columns: 1fr; }
          .flow-arrow { display: none; }
        }
        @media (max-width: 720px) {
          .page { width: min(100vw - 20px, 100%); padding-top: 12px; }
          .masthead, .layout, .hero, .decision-grid, .asset-grid { grid-template-columns: 1fr; }
          .pill { justify-self: start; white-space: normal; }
        }
      </style>

      <main class="page">
        <header class="masthead">
          <div>
            <h1>BB HEMS</h1>
            <p class="subline">Live-Status, Freigaben, Schutzlogik und konfigurierte Energiequellen</p>
          </div>
          <div class="pill">
            <span class="dot ${protect ? "bad" : allowed ? "good" : "warn"}"></span>
            <span>${energyMode ? `Aktuell: ${escapeHtml(energyMode.state)}` : "BB HEMS-Entitaeten nicht gefunden"}</span>
          </div>
        </header>

        <section class="grid hero">
          ${metric(states, "energy_mode", "Betrieb", "Aktueller HEMS-Modus", true)}
          ${metric(states, "grid_power", "Netz", "Negativ = Einspeisung")}
          ${metric(states, "pv_power_total", "PV", "Summe aller PV-Quellen")}
          ${metric(states, "battery_soc_min", "Batterie", "Niedrigster SoC")}
        </section>

        <section class="grid layout">
          <div class="stack">
            <section class="card">
              <div class="card-head"><h2>Energiefluss</h2><span class="muted">${new Date().toLocaleString("de-DE")}</span></div>
              <div class="card-body"><div class="flow">${flow(states)}</div></div>
            </section>

            <section class="card">
              <div class="card-head"><h2>Entscheidung</h2><span class="muted">Warum Verbraucher freigegeben oder gesperrt sind</span></div>
              <div class="card-body"><div class="grid decision-grid">
                ${decision("Ueberschuss", surplus, `PV ${valueOf(findByKey(states, "pv_power_total"))}, PV 15 min ${valueOf(findByKey(states, "pv_average"))}, Netz ${valueOf(findByKey(states, "grid_power"))}, Toleranz ${valueOf(findByKey(states, "grid_tolerance"))}.`)}
                ${decision("Batterieschutz", protect, "Aktiv bei niedrigem SoC, hoher Batterieentladung oder sehr schlechtem Wetter.", true)}
                ${decision("Wetterfreigabe", weather, "Bewertet Wetterzustand, Bewoelkung, Sonne und Batterie-SoC.")}
                ${decision("Flexible Verbraucher", allowed, "Nur aktiv, wenn Ueberschuss, Wetterfreigabe und Batterieschutz zusammen passen.")}
              </div></div>
            </section>

            <section class="card">
              <div class="card-head"><h2>Anlagen</h2><span class="muted">Skaliert fuer mehrere Quellen und Verbraucher</span></div>
              <div class="card-body"><div class="grid asset-grid">${assets(data)}</div></div>
            </section>
          </div>

          <div class="stack">
            <section class="card"><div class="card-head"><h2>Einstellungen</h2></div><div class="card-body">${settings(states)}</div></section>
            <section class="card"><div class="card-head"><h2>Konfiguration</h2></div><div class="card-body">${config(data)}</div></section>
            <section class="card"><div class="card-head"><h2>Letzte HEMS-Werte</h2></div><div class="card-body">${recent(states)}</div></section>
          </div>
        </section>
      </main>
    `;
  }
}

function isHemsEntity(entity) {
  const friendly = entity.attributes.friendly_name || "";
  return entity.entity_id.includes("bb_hems") || friendly.includes("BB HEMS");
}

function findByKey(states, key) {
  return states.find((entity) => isHemsEntity(entity) && entity.entity_id.endsWith(`_${key}`));
}

function nameOf(entity) {
  return entity?.attributes?.friendly_name || entity?.entity_id || "nicht vorhanden";
}

function valueOf(entity) {
  if (!entity) return "nicht vorhanden";
  if (entity.state === "unknown" || entity.state === "unavailable") return entity.state;
  const unit = entity.attributes.unit_of_measurement || "";
  return `${entity.state}${unit ? ` ${unit}` : ""}`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function metric(states, key, label, note, primary = false) {
  const entity = findByKey(states, key);
  return `
    <article class="metric ${primary ? "primary" : ""}">
      <div class="label"><span>${label}</span><span>${entity?.entity_id || ""}</span></div>
      <div class="value ${key === "energy_mode" ? "small" : ""}">${escapeHtml(valueOf(entity))}</div>
      <div class="note">${note}</div>
    </article>
  `;
}

function flow(states) {
  const items = [
    ["pv_power_total", "PV-Erzeugung", "Aus allen PV- und Balkonkraftwerk-Sensoren"],
    ["battery_discharge_total", "Batterie", "Entladung und SoC-Schutz"],
    ["grid_power", "Netzanschluss", "Bezug oder Einspeisung"],
  ];
  return items.map(([key, title, note], index) => {
    const entity = findByKey(states, key);
    const node = `
      <div class="flow-node">
        <h3>${title}</h3>
        <div class="value" style="margin-top: 10px">${escapeHtml(valueOf(entity))}</div>
        <div class="note">${note}</div>
      </div>
    `;
    return index < items.length - 1 ? `${node}<div class="flow-arrow">></div>` : node;
  }).join("");
}

function decision(title, active, text, badWhenTrue = false) {
  const state = badWhenTrue ? (active ? "bad" : "good") : (active ? "good" : "warn");
  return `
    <div class="decision">
      <span class="dot ${state}"></span>
      <div>
        <strong>${title}: ${active ? "ja" : "nein"}</strong>
        <div class="muted">${escapeHtml(text)}</div>
      </div>
    </div>
  `;
}

function assets(data) {
  return [
    ["PV-Quellen", data.configured_pv_sources ?? 0],
    ["Batterien", data.configured_batteries ?? 0],
    ["Verbraucher", data.configured_flexible_loads ?? 0],
    ["Wallboxen", data.configured_wallboxes ?? 0],
    ["Waermepumpen", data.configured_heat_pumps ?? 0],
  ].map(([label, count]) => `
    <div class="asset">
      <h3>${label}</h3>
      <div class="asset-count">${count}</div>
    </div>
  `).join("");
}

function settings(states) {
  const rows = states
    .filter(isHemsEntity)
    .filter((entity) => ["number", "select", "switch"].includes(entity.entity_id.split(".")[0]))
    .sort((a, b) => nameOf(a).localeCompare(nameOf(b)));

  if (!rows.length) {
    return `<div class="empty">Keine HEMS-Einstellungen gefunden. Nach einem HACS-Update Home Assistant neu starten.</div>`;
  }

  return `<table><tbody>${rows.map((entity) => `<tr><td>${escapeHtml(nameOf(entity))}</td><td>${escapeHtml(valueOf(entity))}</td></tr>`).join("")}</tbody></table>`;
}

function list(value) {
  if (Array.isArray(value)) return value.length ? value.join(", ") : "nicht gesetzt";
  return value || "nicht gesetzt";
}

function config(data) {
  if (!Object.keys(data).length) {
    return `<div class="empty">Die Konfiguration ist noch nicht sichtbar. Erwartet wird sensor.bb_hems_energy_mode mit Attributen.</div>`;
  }

  const rows = [
    ["Netz aktuell", data.grid_power_sensor],
    ["Netz 15 min", data.grid_average_sensor],
    ["PV-Quellen", data.pv_power_sensors],
    ["PV 15 min", data.pv_average_sensor],
    ["Batterie-SoC", data.battery_soc_sensors],
    ["Batterie-Entladung", data.battery_discharge_sensors],
    ["Wetter", data.weather_state_sensor],
    ["Flexible Verbraucher", data.flexible_load_switches],
    ["Wallboxen", data.wallbox_switches],
    ["Waermepumpen", data.heat_pump_switches],
  ];

  return `<div class="entity-list">${rows.map(([label, value]) => `<div class="entity-row"><strong>${label}</strong><span>${escapeHtml(list(value))}</span></div>`).join("")}</div>`;
}

function recent(states) {
  const keys = [
    "energy_mode",
    "grid_power",
    "grid_average",
    "pv_power_total",
    "pv_average",
    "battery_soc_min",
    "battery_discharge_total",
    "grid_tolerance",
    "cloud_coverage",
    "sunshine_minutes",
    "active_flexible_loads",
    "configured_assets",
    "surplus_available",
    "battery_protect",
    "good_weather",
    "flexible_loads_allowed",
  ];
  const rows = states
    .filter(isHemsEntity)
    .filter((entity) => keys.some((key) => entity.entity_id.endsWith(`_${key}`)))
    .sort((a, b) => new Date(b.last_changed) - new Date(a.last_changed))
    .slice(0, 8);

  if (!rows.length) return `<div class="empty">Noch keine BB HEMS-Entitaeten sichtbar.</div>`;
  return `<table><thead><tr><th>Entitaet</th><th>Wert</th></tr></thead><tbody>${rows.map((entity) => `<tr><td>${escapeHtml(nameOf(entity))}</td><td>${escapeHtml(valueOf(entity))}</td></tr>`).join("")}</tbody></table>`;
}

customElements.define("bb-hems-panel", BbHemsPanel);
