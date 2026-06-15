const ALIASES = {
  energy_mode: ["energy_mode", "energiemodus", "betrieb"],
  grid_import_power: ["grid_import_power", "netzbezug", "grid import"],
  grid_export_power: ["grid_export_power", "einspeisung", "grid export"],
  pv_power_total: ["pv_power_total", "pv gesamt", "pv total"],
  pv_window: ["pv_window", "pv fenster"],
  battery_soc_min: ["battery_soc_min", "batterie soc minimum", "batterie min"],
  virtual_battery_soc: ["virtual_battery_soc", "virtuelle batterie soc"],
  battery_charge_total: ["battery_charge_total", "batterie ladung gesamt", "batterie ladung"],
  battery_discharge_total: ["battery_discharge_total", "batterie entladung gesamt", "batterie entladung"],
  house_load_total: ["house_load_total", "hauslast", "house load"],
  available_surplus_budget: ["available_surplus_budget", "verfugbares uberschussbudget", "verfuegbares ueberschussbudget"],
  scheduled_surplus_power: ["scheduled_surplus_power", "geplante uberschussleistung", "geplante ueberschussleistung"],
  shifted_energy_today: ["shifted_energy_today", "hems verschobene energie heute"],
  estimated_savings_today: ["estimated_savings_today", "hems ersparnis heute"],
  savings_price: ["savings_price", "hems ersparnis je kwh"],
  shifted_energy_total: ["shifted_energy_total", "hems verschobene energie gesamt"],
  learning_samples: ["learning_samples", "hems erfahrungswerte"],
  seasonal_success_rate: ["seasonal_success_rate", "hems jahreszeit trefferquote"],
  active_flexible_loads: ["active_flexible_loads", "aktive flexible verbraucher"],
  surplus_available: ["surplus_available", "uberschuss verfugbar", "ueberschuss verfuegbar"],
  battery_protect: ["battery_protect", "batterieschutz"],
  good_weather: ["good_weather", "wetterfreigabe"],
  flexible_loads_allowed: ["flexible_loads_allowed", "flexible verbraucher erlaubt"],
  auto_enabled: ["auto_enabled", "automatik aktiv"],
  mode_select: ["select.bb_hems_mode", "betriebsart", "operating mode"],
};

const BB_HEMS_VERSION = "0.12.1";
const I18N = {
  de: {
    subtitle: "Was HEMS gerade entscheidet, schaltet und einspart",
    config: "Konfiguration",
    entities: "Entitäten",
    devices: "Geräte",
    energyStatus: "Energiezustand",
    energyStatusNote: "Normalisierte Werte aus Wechselrichter, Batterie, Netz und Hauslast",
    pv: "PV",
    pvSources: "PV-Quellen",
    battery: "Batterie",
    grid: "Netz",
    house: "Hauslast",
    export: "Einspeisung",
    import: "Bezug",
    charging: "lädt",
    discharging: "entlädt",
    noFlow: "kein Fluss",
    hemsBudget: "HEMS-Budget",
    today: "HEMS Nutzen",
    todayNote: "Nur HEMS-Werte, keine allgemeine Energiebilanz",
    shifted: "HEMS verschoben",
    shiftedNote: "Energie wurde in PV-/Überschusszeit gelegt.",
    savings: "geschätzte Ersparnis",
    savingsNote: "Netzbezugspreis minus Einspeisevergütung.",
    plannedPower: "geplante Leistung",
    plannedPowerNote: "Aktuell für HEMS-Verbraucher eingeplant.",
    experience: "HEMS Erfahrung",
    decisionNow: "Entscheidung jetzt",
    decisionNote: "Warum HEMS gerade schalten darf oder wartet",
    loads: "Verbraucher",
    loadsNote: "Was HEMS aktiv steuert",
    language: "Sprache",
    control: "Steuerung",
    controlNote: "Schnell umstellen, ohne die Integration zu öffnen",
    active: "HEMS aktiv",
    paused: "HEMS pausiert",
    status: "Status",
    batteryProtectActive: "Batterieschutz aktiv",
    surplusActive: "Überschuss aktiv",
    waitingRelease: "wartet auf Freigabe",
    noSurplus: "kein Überschuss",
    blocked: "gesperrt",
    free: "frei",
    waiting: "wartet",
    budget: "Überschussbudget",
    fits: "passt",
    tight: "knapp",
    noConfig: "nicht konfiguriert",
    missing: "fehlt",
    planned: "geplant",
    nextCandidate: "Nächster Kandidat",
    plannedNote: "Diese Verbraucher passen aktuell ins HEMS-Budget.",
    releaseNote: "Wird freigegeben, sobald Budget, PV-Fenster und Batterieschutz passen.",
    flexibleLoads: "Flexible Lasten",
    startOnly: "Nur starten",
    heatingRods: "Heizstäbe",
    wallboxes: "Wallboxen",
    heatPumps: "Wärmepumpen",
    ready: "bereit",
    activePill: "aktiv",
    temperature: "Temperatur",
    noDevice: "kein Gerät",
    device: "Gerät",
    devicesPlural: "Geräte",
    plannedPrefix: "Geplant",
    virtualBattery: "Virtuelle Batterie",
    hemsUse: "HEMS-Nutzung",
    confidence: "Vertrauen",
    calculatedSoc: "Berechneter SoC",
    blockers: "Blocker & Freigaben",
    batteryFree: "Batterieschutz frei",
    weatherRelease: "Wetterfreigabe",
    pvWindow: "PV-Fenster",
    seasonLearning: "Jahreszeit-Erfahrung",
    events: "HEMS Ereignisse",
    noEvents: "Noch keine HEMS-Ereignisse sichtbar.",
    event: "HEMS-Ereignis",
    learnedTolerance: "Gelernte Netztoleranz",
    notSet: "nicht gesetzt",
    rangeToday: "Heute",
    rangeYesterday: "Gestern",
    rangeBeforeYesterday: "Vorgestern",
    range7d: "7 Tage",
    range30d: "30 Tage",
    comparedPrevious: "gegen vorherigen Zeitraum",
    starts: "Starts",
    eventsShort: "Ereignisse",
    blocksShort: "Blocker",
    maxBudget: "Max. Budget",
    noHistory: "Noch keine HEMS-Historie für diesen Zeitraum.",
    more: "mehr",
    less: "weniger",
    unchanged: "unverändert",
  },
  en: {
    subtitle: "What HEMS decides, switches and saves right now",
    config: "Configuration",
    entities: "Entities",
    devices: "Devices",
    energyStatus: "Energy status",
    energyStatusNote: "Normalized values from inverter, battery, grid and house load",
    pv: "PV",
    pvSources: "PV sources",
    battery: "Battery",
    grid: "Grid",
    house: "House load",
    export: "Export",
    import: "Import",
    charging: "charging",
    discharging: "discharging",
    noFlow: "no flow",
    hemsBudget: "HEMS budget",
    today: "HEMS benefit",
    todayNote: "Only HEMS values, not a general energy balance",
    shifted: "HEMS shifted",
    shiftedNote: "Energy moved into PV/surplus time.",
    savings: "estimated savings",
    savingsNote: "Grid import price minus export compensation.",
    plannedPower: "planned power",
    plannedPowerNote: "Currently planned for HEMS loads.",
    experience: "HEMS experience",
    decisionNow: "Decision now",
    decisionNote: "Why HEMS may switch or waits right now",
    loads: "Loads",
    loadsNote: "What HEMS actively controls",
    language: "Language",
    control: "Control",
    controlNote: "Change mode without opening the integration",
    active: "HEMS active",
    paused: "HEMS paused",
    status: "Status",
    batteryProtectActive: "Battery protection active",
    surplusActive: "Surplus active",
    waitingRelease: "waiting for release",
    noSurplus: "no surplus",
    blocked: "blocked",
    free: "free",
    waiting: "waiting",
    budget: "Surplus budget",
    fits: "fits",
    tight: "tight",
    noConfig: "not configured",
    missing: "missing",
    planned: "planned",
    nextCandidate: "Next candidate",
    plannedNote: "These loads currently fit into the HEMS budget.",
    releaseNote: "Will be released once budget, PV window and battery protection match.",
    flexibleLoads: "Flexible loads",
    startOnly: "Start only",
    heatingRods: "Heating rods",
    wallboxes: "Wallboxes",
    heatPumps: "Heat pumps",
    ready: "ready",
    activePill: "active",
    temperature: "Temperature",
    noDevice: "no device",
    device: "device",
    devicesPlural: "devices",
    plannedPrefix: "Planned",
    virtualBattery: "Virtual battery",
    hemsUse: "HEMS use",
    confidence: "Confidence",
    calculatedSoc: "Calculated SoC",
    blockers: "Blockers & releases",
    batteryFree: "Battery protection free",
    weatherRelease: "Weather release",
    pvWindow: "PV window",
    seasonLearning: "Season experience",
    events: "HEMS events",
    noEvents: "No HEMS events visible yet.",
    event: "HEMS event",
    learnedTolerance: "Learned grid tolerance",
    notSet: "not set",
    rangeToday: "Today",
    rangeYesterday: "Yesterday",
    rangeBeforeYesterday: "Day before",
    range7d: "7 days",
    range30d: "30 days",
    comparedPrevious: "vs previous period",
    starts: "Starts",
    eventsShort: "Events",
    blocksShort: "Blocks",
    maxBudget: "Max. budget",
    noHistory: "No HEMS history for this period yet.",
    more: "more",
    less: "less",
    unchanged: "unchanged",
  },
};
const HISTORY_RANGES = ["today", "yesterday", "before_yesterday", "7d", "30d"];
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
    const lang = this.language();
    const tr = I18N[lang];
    const range = this.historyRange();
    const history = historySummary(attrs, range, tr);

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
          grid-template-columns: minmax(0, 1fr) auto auto;
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
        .segmented.compact {
          grid-template-columns: repeat(5, minmax(72px, auto));
          width: auto;
        }
        .segmented.compact .segment {
          min-height: 32px;
          padding: 5px 10px;
          font-size: 13px;
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
          min-height: 38px;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          padding: 7px 12px;
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
          width: 16px;
          height: 16px;
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
        .stack { display: grid; gap: 12px; align-content: start; }
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
            <p class="subtitle">Version ${BB_HEMS_VERSION} · ${tr.subtitle}</p>
          </div>
          <div class="link-row">
            <button class="link" data-lang-toggle>${tr.language}: ${lang.toUpperCase()}</button>
            <a class="link" href="/config/integrations/integration/bb_hems">${tr.config}</a>
            <a class="link" href="/config/entities">${tr.entities}</a>
            <a class="link" href="/config/devices/dashboard">${tr.devices}</a>
          </div>
        </section>

        ${controls(modeSelect, autoSwitch, tr)}

        <section class="section">
          <div class="section-head">
            <div>
              <h2>${esc(tr.energyStatus)}</h2>
              <span class="section-note">${esc(tr.energyStatusNote)}</span>
            </div>
          </div>
          <div class="tile-grid">
            ${energyStatusTile(tr.pv, powerValue(Number(attrs.pv_power || numericState(byKey(states, "pv_power_total")))), pvStatusNote(attrs, tr), "☀", "good")}
            ${energyStatusTile(tr.battery, batteryValue(attrs, states, tr), batteryNote(attrs, tr), "🔋", batteryClass(attrs))}
            ${energyStatusTile(tr.grid, gridValue(attrs, states, tr), gridNote(attrs, tr), "↔", gridClass(attrs))}
            ${energyStatusTile(tr.house, powerValue(Number(attrs.house_load || numericState(byKey(states, "house_load_total")))), `${tr.hemsBudget}: ${powerValue(Number(attrs.available_surplus_budget || numericState(byKey(states, "available_surplus_budget"))))}`, "⌂", "info")}
          </div>
        </section>

        <section class="section">
          <div class="section-head">
            <div>
              <h2>${tr.today}: ${esc(history.label)}</h2>
              <span class="section-note">${esc(tr.todayNote)}</span>
            </div>
            <div class="segmented compact">
              ${HISTORY_RANGES.map((item) => `<button class="segment ${item === range ? "active" : ""}" data-history-range="${esc(item)}">${esc(rangeLabel(item, tr))}</button>`).join("")}
            </div>
          </div>
          <div class="tile-grid">
            ${benefitTile(tr.shifted, energyValue(history.shiftedEnergy), comparisonNote(history, "shiftedEnergy", tr) || tr.shiftedNote, "↗", history.shiftedEnergy > 0 ? "good" : "info")}
            ${benefitTile(tr.savings, moneyValue(history.estimatedSavings), comparisonNote(history, "estimatedSavings", tr) || attrs.price_reason || tr.savingsNote, "€", history.estimatedSavings > 0 ? "good" : "info")}
            ${benefitTile(tr.plannedPower, powerValue(history.maxScheduledPower), `${tr.maxBudget}: ${powerValue(history.maxAvailableBudget)}`, "⚡", history.maxScheduledPower > 0 ? "good" : "info")}
            ${benefitTile(tr.eventsShort, String(history.events), `${history.switches} ${tr.starts} · ${history.blocks} ${tr.blocksShort}${history.hasData ? "" : ` · ${tr.noHistory}`}`, "✓", history.events > 0 ? "good" : "warn")}
          </div>
        </section>

        <section class="section main-layout">
          <div class="stack">
            <div>
              <div class="section-head">
                <h2>${tr.decisionNow}</h2>
                <span class="section-note">${tr.decisionNote}</span>
              </div>
              <div class="tile-grid wide">
                ${decisionStatusTile(states, attrs, tr)}
                ${decisionBudgetTile(states, attrs, tr)}
                ${nextCandidateTile(attrs, tr)}
              </div>
            </div>

            <div>
              <div class="section-head">
                <h2>${tr.loads}</h2>
                <span class="section-note">${tr.loadsNote}</span>
              </div>
              <div class="tile-grid loads">
                ${loadTiles(attrs, states, tr)}
              </div>
            </div>

            ${actionHistory(attrs, tr)}
          </div>

          <aside class="stack">
            ${pvSourceCard(attrs, tr)}
            ${blockerCard(states, attrs, tr)}
            ${virtualBatteryCard(states, attrs, tr)}
          </aside>
        </section>
      </main>
    `;
    this.bindControls(states);
  }

  language() {
    const stored = localStorage.getItem("bb_hems_language");
    if (stored === "de" || stored === "en") return stored;
    return String(this._hass?.locale?.language || this._hass?.language || "de").toLowerCase().startsWith("en") ? "en" : "de";
  }

  historyRange() {
    const stored = localStorage.getItem("bb_hems_history_range");
    return HISTORY_RANGES.includes(stored) ? stored : "today";
  }

  bindControls(states) {
    this.querySelector("[data-lang-toggle]")?.addEventListener("click", () => {
      localStorage.setItem("bb_hems_language", this.language() === "de" ? "en" : "de");
      this.render();
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
    this.querySelectorAll("[data-history-range]").forEach((button) => {
      button.addEventListener("click", () => {
        localStorage.setItem("bb_hems_history_range", button.dataset.historyRange);
        this.render();
      });
    });
  }
}

function controls(modeSelect, autoSwitch, tr) {
  const options = modeSelect?.attributes?.options || ["auto", "eco", "comfort", "force_surplus", "off"];
  const current = modeSelect?.state || "auto";
  return `<section class="section"><div class="control-panel">
    <div><h2>${esc(tr.control)}</h2><p class="section-note">${esc(tr.controlNote)}</p></div>
    <div class="segmented">${options.map((option) => `<button class="segment ${option === current ? "active" : ""}" data-select-entity="${esc(modeSelect?.entity_id || "")}" data-select-option="${esc(option)}" ${!modeSelect || option === current ? "disabled" : ""}>${esc(MODE_LABELS[option] || option)}</button>`).join("")}</div>
    <button class="power ${autoSwitch?.state === "off" ? "off" : ""}" data-switch-entity="${esc(autoSwitch?.entity_id || "")}" ${!autoSwitch ? "disabled" : ""}><span class="dot"></span>${autoSwitch?.state === "off" ? esc(tr.paused) : esc(tr.active)}</button>
  </div></section>`;
}

function benefitTile(label, value, note, icon, state) {
  return `<article class="tile ${state}"><div class="tile-top"><span>${esc(label)}</span><span class="icon">${esc(icon)}</span></div><div class="value">${esc(value)}</div><div class="note">${esc(note)}</div></article>`;
}

function energyStatusTile(label, value, note, icon, state) {
  return benefitTile(label, value, note, icon, state);
}

function batteryValue(attrs, states, tr) {
  const soc = attrs.battery_soc_min ?? numericState(byKey(states, "battery_soc_min"));
  const charge = Number(attrs.battery_charge || numericState(byKey(states, "battery_charge_total")));
  const discharge = Number(attrs.battery_discharge || numericState(byKey(states, "battery_discharge_total")));
  const flow = charge >= discharge ? `${tr.charging} ${powerValue(charge)}` : `${tr.discharging} ${powerValue(discharge)}`;
  if (soc === null || soc === undefined || Number.isNaN(Number(soc))) return flow;
  return `${Number(soc).toLocaleString("de-DE", { maximumFractionDigits: 0 })}% · ${flow}`;
}

function batteryNote(attrs, tr) {
  const usable = Number(attrs.usable_battery_charge || 0);
  if (usable > 0) return `${tr.hemsBudget}: ${powerValue(usable)}`;
  return attrs.battery_reason || tr.batteryFree;
}

function batteryClass(attrs) {
  if (attrs.battery_protect) return "bad";
  if (Number(attrs.usable_battery_charge || 0) > 0) return "good";
  if (Number(attrs.battery_charge || 0) > 0) return "warn";
  return "info";
}

function gridValue(attrs, states, tr) {
  const gridImport = Number(attrs.grid_import || numericState(byKey(states, "grid_import_power")));
  const gridExport = Number(attrs.grid_export || numericState(byKey(states, "grid_export_power")));
  if (gridExport > gridImport) return `${tr.export} ${powerValue(gridExport)}`;
  if (gridImport > 0) return `${tr.import} ${powerValue(gridImport)}`;
  return tr.noFlow;
}

function gridNote(attrs, tr) {
  const gridImport = Number(attrs.grid_import || 0);
  const gridExport = Number(attrs.grid_export || 0);
  return `${tr.import}: ${powerValue(gridImport)} · ${tr.export}: ${powerValue(gridExport)}`;
}

function gridClass(attrs) {
  const gridImport = Number(attrs.grid_import || 0);
  const gridExport = Number(attrs.grid_export || 0);
  if (gridExport > gridImport) return "good";
  if (gridImport > 300) return "bad";
  if (gridImport > 0) return "warn";
  return "info";
}

function pvStatusNote(attrs, tr) {
  const rows = Array.isArray(attrs.pv_source_details) ? attrs.pv_source_details : [];
  if (rows.length) {
    const top = rows.slice(0, 3).map((row) => `${row.name}: ${powerValue(Number(row.power || 0))}`).join(" · ");
    return `${top}${rows.length > 3 ? ` · +${rows.length - 3}` : ""}`;
  }
  return attrs.pv_window_reason || tr.pvWindow;
}

function pvSourceCard(attrs, tr) {
  const rows = Array.isArray(attrs.pv_source_details) ? attrs.pv_source_details.slice(0, 8) : [];
  if (!rows.length) return "";
  return `<section class="next-card">
    <h2>${esc(tr.pvSources)}</h2>
    ${rows.map((row) => {
      const meta = [
        row.category,
        row.peak_power ? `${Number(row.peak_power).toLocaleString("de-DE", { maximumFractionDigits: 0 })} Wp` : "",
        row.orientation_score !== null && row.orientation_score !== undefined ? `Score ${Number(row.orientation_score).toLocaleString("de-DE", { maximumFractionDigits: 2 })}` : "",
      ].filter(Boolean).join(" · ");
      return blockerItem(Number(row.power || 0) > 0, `${row.name}: ${powerValue(Number(row.power || 0))}`, meta || row.sensor);
    }).join("")}
  </section>`;
}

function decisionStatusTile(states, attrs, tr) {
  const allowed = isOn(byKey(states, "flexible_loads_allowed")) || attrs.flexible_loads_allowed;
  const protect = isOn(byKey(states, "battery_protect")) || attrs.battery_protect;
  const surplus = isOn(byKey(states, "surplus_available")) || attrs.surplus_available;
  const status = protect ? tr.batteryProtectActive : allowed ? tr.surplusActive : surplus ? tr.waitingRelease : tr.noSurplus;
  const state = protect ? "bad" : allowed ? "good" : surplus ? "warn" : "info";
  const pill = protect ? tr.blocked : allowed ? tr.free : tr.waiting;
  const reason = attrs.load_reason || attrs.surplus_reason || tr.decisionNote;
  return `<article class="tile ${state}"><div class="tile-top"><span>${esc(tr.status)}</span><span class="pill ${state}">${esc(pill)}</span></div><div class="value small-value">${esc(status)}</div><div class="note">${esc(reason)}</div></article>`;
}

function decisionBudgetTile(states, attrs, tr) {
  const budget = numericState(byKey(states, "available_surplus_budget"));
  const state = budget > 1000 ? "good" : budget > 0 ? "warn" : "bad";
  const pill = budget > 1000 ? tr.fits : budget > 0 ? tr.tight : tr.blocked;
  const note = attrs.scheduler_reason || tr.plannedPowerNote;
  return `<article class="tile ${state}"><div class="tile-top"><span>${esc(tr.budget)}</span><span class="pill ${state}">${esc(pill)}</span></div><div class="value">${esc(power(byKey(states, "available_surplus_budget")))}</div><div class="note">${esc(note)}</div></article>`;
}

function nextCandidateTile(attrs, tr) {
  const scheduled = list(attrs.scheduled_surplus_loads, tr);
  const hasScheduled = scheduled !== tr.notSet;
  const candidate = hasScheduled ? scheduled : nextConfiguredLoad(attrs, tr);
  const empty = candidate === tr.noConfig;
  const state = hasScheduled ? "good" : empty ? "bad" : "warn";
  const pill = hasScheduled ? tr.planned : empty ? tr.missing : tr.waiting;
  const note = hasScheduled ? tr.plannedNote : tr.releaseNote;
  return `<article class="tile ${state}"><div class="tile-top"><span>${esc(tr.nextCandidate)}</span><span class="pill ${state}">${esc(pill)}</span></div><div class="value small-value">${esc(empty ? tr.noConfig : candidate)}</div><div class="note">${esc(note)}</div></article>`;
}

function loadTiles(attrs, states, tr) {
  const flexibleCount = Number(attrs.configured_flexible_loads || 0) + Number(attrs.configured_profile_loads || 0);
  return [
    loadTile(tr.flexibleLoads, attrs.flexible_load_switches, flexibleCount, "info", tr.releaseNote, attrs.scheduled_surplus_loads, 0, tr),
    loadTile(tr.startOnly, attrs.start_only_appliance_switches, attrs.configured_start_only_appliances, "good", tr.plannedNote, attrs.scheduled_surplus_loads, 0, tr),
    loadTile(tr.heatingRods, attrs.heating_rod_switches, attrs.configured_heating_rods, "good", tr.plannedPowerNote, attrs.scheduled_surplus_loads, Number(attrs.blocked_heating_rods || 0), tr),
    loadTile(tr.wallboxes, attrs.wallbox_switches, attrs.configured_wallboxes, "warn", tr.releaseNote, attrs.scheduled_surplus_loads, 0, tr),
    loadTile(tr.heatPumps, attrs.heat_pump_switches, attrs.configured_heat_pumps, "warn", tr.releaseNote, attrs.scheduled_surplus_loads, 0, tr),
  ].join("");
}

function loadTile(title, entities, count, configuredState, fallbackNote, scheduledLoads, blockedCount = 0, tr = I18N.de) {
  const items = asArray(entities);
  const configured = Number(count ?? items.length);
  const scheduled = asArray(scheduledLoads).filter((entity) => items.includes(entity));
  const blocked = Number(blockedCount || 0);
  const state = configured <= 0 ? "bad" : blocked ? "warn" : scheduled.length ? "good" : configuredState;
  const pill = configured <= 0 ? tr.noConfig : blocked ? tr.temperature : scheduled.length ? tr.activePill : tr.ready;
  const value = configured <= 0 ? tr.noDevice : blocked ? `${blocked} ${tr.blocked}` : scheduled.length ? `${scheduled.length} ${tr.activePill}` : `${configured} ${configured === 1 ? tr.device : tr.devicesPlural}`;
  const note = scheduled.length ? `${tr.plannedPrefix}: ${scheduled.join(", ")}` : fallbackNote;
  return `<article class="tile ${state}"><div class="tile-top"><span>${esc(title)}</span><span class="pill ${state}">${esc(pill)}</span></div><div class="value small-value">${esc(value)}</div><div class="note">${esc(note)}</div></article>`;
}

function virtualBatteryCard(states, attrs, tr) {
  const enabled = Boolean(attrs.virtual_battery_enabled);
  if (!enabled) return "";
  const used = Boolean(attrs.virtual_battery_used);
  const soc = attrs.virtual_battery_soc ?? numericState(byKey(states, "virtual_battery_soc"));
  const confidence = Number(attrs.virtual_battery_confidence || 0);
  return `<section class="next-card">
    <h2>${esc(tr.virtualBattery)}</h2>
    ${blockerItem(used, tr.hemsUse, used ? attrs.virtual_battery_reason || tr.hemsUse : attrs.virtual_battery_reason || tr.releaseNote)}
    ${blockerItem(confidence >= 50, tr.confidence, `${confidence.toLocaleString("de-DE", { maximumFractionDigits: 0 })}% · ${attrs.virtual_battery_reason || tr.confidence}`)}
    ${blockerItem(Number(soc) > 0, tr.calculatedSoc, `${Number(soc || 0).toLocaleString("de-DE", { maximumFractionDigits: 1 })}%`)}
  </section>`;
}

function blockerCard(states, attrs, tr) {
  const protect = isOn(byKey(states, "battery_protect")) || attrs.battery_protect;
  const weather = isOn(byKey(states, "good_weather")) || attrs.good_weather;
  const pvWindow = attrs.pv_window || byKey(states, "pv_window")?.state;
  const budget = numericState(byKey(states, "available_surplus_budget"));
  return `<section class="next-card">
    <h2>${esc(tr.blockers)}</h2>
    ${blockerItem(!protect, tr.batteryFree, attrs.battery_reason || tr.batteryFree)}
    ${blockerItem(weather, tr.weatherRelease, attrs.weather_reason || tr.weatherRelease)}
    ${blockerItem(Boolean(pvWindow && !["night", "low_today", "weak_now"].includes(pvWindow)), tr.pvWindow, attrs.pv_window_reason || `${tr.pvWindow}: ${pvWindow || "-"}.`)}
    ${blockerItem(budget > 0, tr.budget, budget > 0 ? `${Math.round(budget)} W` : tr.noSurplus)}
    ${blockerItem(Number(attrs.learning_samples || 0) >= 12, tr.seasonLearning, learningReason(attrs, tr))}
  </section>`;
}

function blockerItem(ok, title, text) {
  return `<div class="next-item"><span class="marker" style="background:var(--${ok ? "good" : "warn"})"></span><div><strong>${esc(title)}</strong><p class="note">${esc(text)}</p></div></div>`;
}

function actionHistory(attrs, tr) {
  const rows = Array.isArray(attrs.action_history) ? attrs.action_history.slice(0, 8) : [];
  if (!rows.length) return `<section class="event-card"><h2>${esc(tr.events)}</h2><div class="note">${esc(tr.noEvents)}</div></section>`;
  return `<section class="event-card"><h2>${esc(tr.events)}</h2><div class="event-list">${rows.map((event) => {
    const blocked = String(event.kind || "").includes("block") || String(event.kind || "").includes("protect");
    return `<div class="event"><div class="event-time">${esc(formatTime(event.time))}</div><div><div class="event-title">${esc(event.title || tr.event)}</div><div class="event-reason">${esc(event.reason || "")}</div></div><span class="pill ${blocked ? "warn" : "good"}">${blocked ? esc(tr.waiting) : esc(tr.activePill)}</span></div>`;
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
  return powerValue(watts);
}

function powerValue(watts) {
  const kw = watts / 1000;
  return `${kw.toLocaleString("de-DE", { minimumFractionDigits: Math.abs(kw) >= 10 ? 0 : 1, maximumFractionDigits: 1 })} kW`;
}

function energy(entity) {
  if (!entity) return "0,00 kWh";
  return energyValue(numericState(entity));
}

function energyValue(value) {
  return `${Number(value || 0).toLocaleString("de-DE", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} kWh`;
}

function money(entity) {
  return moneyValue(numericState(entity));
}

function moneyValue(value) {
  return Number(value || 0).toLocaleString("de-DE", { style: "currency", currency: "EUR" });
}

function rangeLabel(range, tr = I18N.de) {
  const labels = {
    today: tr.rangeToday,
    yesterday: tr.rangeYesterday,
    before_yesterday: tr.rangeBeforeYesterday,
    "7d": tr.range7d,
    "30d": tr.range30d,
  };
  return labels[range] || tr.rangeToday;
}

function historySummary(attrs, range = "today", tr = I18N.de) {
  const current = periodForRange(range, 0);
  const previous = periodForRange(range, 1);
  const currentRows = collectHistory(attrs, current.start, current.days);
  const previousRows = collectHistory(attrs, previous.start, previous.days);
  return {
    label: rangeLabel(range, tr),
    hasData: currentRows.hasData,
    shiftedEnergy: currentRows.shiftedEnergy,
    estimatedSavings: currentRows.estimatedSavings,
    maxScheduledPower: currentRows.maxScheduledPower,
    maxAvailableBudget: currentRows.maxAvailableBudget,
    events: currentRows.events,
    switches: currentRows.switches,
    blocks: currentRows.blocks,
    previous: previousRows,
  };
}

function periodForRange(range, previousIndex) {
  if (range === "yesterday") {
    return { start: previousIndex ? 2 : 1, days: 1 };
  }
  if (range === "before_yesterday") {
    return { start: previousIndex ? 3 : 2, days: 1 };
  }
  if (range === "7d") {
    return { start: previousIndex ? 7 : 0, days: 7 };
  }
  if (range === "30d") {
    return { start: previousIndex ? 30 : 0, days: 30 };
  }
  return { start: previousIndex ? 1 : 0, days: 1 };
}

function collectHistory(attrs, startOffset, days) {
  const dates = new Set();
  for (let offset = startOffset; offset < startOffset + days; offset += 1) {
    dates.add(localIsoDate(offset));
  }
  const rows = Array.isArray(attrs.daily_history) ? attrs.daily_history : [];
  const selected = rows.filter((row) => dates.has(String(row.date || "")));
  if (dates.has(localIsoDate(0)) && !selected.some((row) => row.date === localIsoDate(0))) {
    selected.push({
      date: localIsoDate(0),
      shifted_energy: attrs.shifted_energy_today,
      estimated_savings: attrs.estimated_savings_today,
      max_scheduled_power: attrs.scheduled_surplus_power,
      max_available_budget: attrs.available_surplus_budget,
      events: 0,
      switches: 0,
      blocks: 0,
    });
  }
  return selected.reduce((summary, row) => {
    summary.hasData = true;
    summary.shiftedEnergy += Number(row.shifted_energy || 0);
    summary.estimatedSavings += Number(row.estimated_savings || 0);
    summary.maxScheduledPower = Math.max(summary.maxScheduledPower, Number(row.max_scheduled_power || 0));
    summary.maxAvailableBudget = Math.max(summary.maxAvailableBudget, Number(row.max_available_budget || 0));
    summary.events += Number(row.events || 0);
    summary.switches += Number(row.switches || 0);
    summary.blocks += Number(row.blocks || 0);
    return summary;
  }, {
    hasData: false,
    shiftedEnergy: 0,
    estimatedSavings: 0,
    maxScheduledPower: 0,
    maxAvailableBudget: 0,
    events: 0,
    switches: 0,
    blocks: 0,
  });
}

function comparisonNote(history, key, tr = I18N.de) {
  const previous = Number(history.previous?.[key] || 0);
  const current = Number(history[key] || 0);
  if (!history.hasData || previous <= 0 && current <= 0) return "";
  const delta = current - previous;
  if (Math.abs(delta) < 0.005) return `${tr.unchanged} ${tr.comparedPrevious}`;
  const direction = delta > 0 ? tr.more : tr.less;
  const formatted = key === "estimatedSavings" ? moneyValue(Math.abs(delta)) : energyValue(Math.abs(delta));
  return `${formatted} ${direction} ${tr.comparedPrevious}`;
}

function localIsoDate(offsetDays = 0) {
  const date = new Date();
  date.setHours(12, 0, 0, 0);
  date.setDate(date.getDate() - offsetDays);
  return date.toISOString().slice(0, 10);
}

function activeLoadClass(entity) {
  return numericState(entity) > 0 ? "good" : "warn";
}

function learningValue(states, attrs) {
  const rate = attrs.seasonal_success_rate ?? numericState(byKey(states, "seasonal_success_rate"));
  const samples = attrs.learning_samples ?? numericState(byKey(states, "learning_samples"));
  if (!samples) return "lernt";
  if (rate === null || rate === undefined || Number.isNaN(Number(rate))) return `${samples} Werte`;
  return `${Number(rate).toLocaleString("de-DE", { maximumFractionDigits: 0 })} %`;
}

function learningClass(attrs) {
  const samples = Number(attrs.learning_samples || 0);
  const rate = Number(attrs.seasonal_success_rate || 0);
  if (samples < 12) return "info";
  if (rate >= 60) return "good";
  if (rate >= 30) return "warn";
  return "bad";
}

function learningReason(attrs, tr = I18N.de) {
  const adjustment = Number(attrs.seasonal_grid_adjustment || 0);
  const recommendation = attrs.seasonal_recommendation || tr.experience;
  if (!adjustment) return recommendation;
  const sign = adjustment > 0 ? "+" : "";
  return `${recommendation} ${tr.learnedTolerance}: ${sign}${Math.round(adjustment)} W.`;
}

function asArray(value) {
  if (Array.isArray(value)) return value.filter(Boolean);
  if (!value) return [];
  return [value];
}

function list(value, tr = I18N.de) {
  const items = asArray(value);
  return items.length ? items.join(", ") : tr.notSet;
}

function nextConfiguredLoad(attrs, tr = I18N.de) {
  const groups = [
    attrs.heating_rod_switches,
    attrs.flexible_load_switches,
    attrs.start_only_appliance_switches,
    attrs.wallbox_switches,
    attrs.heat_pump_switches,
  ];
  for (const group of groups) {
    const items = asArray(group);
    if (items.length) return items[0];
  }
  return tr.noConfig;
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
