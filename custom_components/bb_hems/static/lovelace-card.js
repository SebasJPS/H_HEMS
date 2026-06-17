import "./house-flow.js";

class BbHemsHouseFlowCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
  }

  setConfig(config) {
    if (!config) {
      throw new Error("Invalid BB HEMS house flow card configuration");
    }
    this._config = config;
    this.render();
  }

  set hass(hass) {
    this._hass = hass;
    this.render();
  }

  getCardSize() {
    return 6;
  }

  render() {
    if (!this._hass || !this._config) return;
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        ha-card {
          overflow: hidden;
          border-radius: var(--ha-card-border-radius, 8px);
        }
        .head {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 12px;
          padding: 16px 16px 0;
        }
        h2 {
          margin: 0;
          color: var(--primary-text-color);
          font-size: 18px;
          line-height: 1.2;
          font-weight: 700;
        }
        .sub {
          color: var(--secondary-text-color);
          font-size: 12px;
        }
        bb-hems-house-flow {
          display: block;
          padding: 16px;
        }
      </style>
      <ha-card>
        <div class="head">
          <h2>${esc(this._config.title || "BB HEMS")}</h2>
          <span class="sub">Live</span>
        </div>
        <bb-hems-house-flow></bb-hems-house-flow>
      </ha-card>
    `;
    this.shadowRoot.querySelector("bb-hems-house-flow").data = this.flowData();
  }

  flowData() {
    const source = this.entity(this._config.entity || "sensor.bb_hems_energy_mode");
    const attrs = source?.attributes || {};
    return {
      status: this._config.status || "Live Energiefluss",
      house: this.node("house", attrs.house_load, null, "Haus-Sensor"),
      pvRoof: this.node("pv_roof", attrs.pv_power),
      bkwGarage: this.node("bkw_garage", 0),
      grid: this.gridNode(attrs),
      pvBattery: this.batteryNode("pv_battery", -Number(attrs.battery_discharge || 0), attrs.battery_soc_min),
      acBattery: this.acBatteryNode(attrs),
      ev: this.node("ev", 0),
      heatPump: this.node("heat_pump", 0),
    };
  }

  gridNode(attrs) {
    const configured = this._config.grid || {};
    if (configured.power) {
      return { power: this.stateNumber(configured.power), energy: this.stateNumber(configured.energy) };
    }
    return {
      power: Number(attrs.grid_import || 0) - Number(attrs.grid_export || 0),
      energy: null,
    };
  }

  batteryNode(key, fallbackPower, fallbackSoc) {
    const configured = this._config[key] || {};
    return {
      power: configured.power ? this.stateNumber(configured.power) : fallbackPower,
      energy: configured.energy ? this.stateNumber(configured.energy) : null,
      soc: configured.soc ? this.stateNumber(configured.soc) : fallbackSoc,
    };
  }

  acBatteryNode(attrs) {
    const configured = this._config.ac_battery || {};
    if (configured.power || configured.soc) {
      return this.batteryNode("ac_battery", 0, null);
    }
    const rows = Array.isArray(attrs.ac_battery_details) ? attrs.ac_battery_details : [];
    const first = rows[0] || {};
    const charge = Number(first.charge_power || first.target_charge || 0);
    const discharge = Number(first.discharge_power || first.target_discharge || 0);
    return {
      power: charge > 0 ? charge : -discharge,
      soc: first.soc,
      energy: null,
    };
  }

  node(key, fallbackPower, fallbackEnergy = null, fallbackSource = "Heute") {
    const configured = this._config[key] || {};
    return {
      power: configured.power ? this.stateNumber(configured.power) : Number(fallbackPower || 0),
      energy: configured.energy ? this.stateNumber(configured.energy) : fallbackEnergy,
      soc: configured.soc ? this.stateNumber(configured.soc) : null,
      energySource: fallbackSource,
    };
  }

  entity(entityId) {
    return entityId ? this._hass.states[entityId] : null;
  }

  stateNumber(entityId) {
    const state = this.entity(entityId);
    const value = Number(state?.state);
    return Number.isFinite(value) ? value : 0;
  }
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

if (!customElements.get("bb-hems-house-flow-card")) {
  customElements.define("bb-hems-house-flow-card", BbHemsHouseFlowCard);
}

window.customCards = window.customCards || [];
window.customCards.push({
  type: "bb-hems-house-flow-card",
  name: "BB HEMS House Flow",
  description: "Modernes Haus-Energiefluss-Dashboard fuer BB HEMS.",
});
