(window.webpackJsonp=window.webpackJsonp||[]).push([[19],{586:function(e,t,i){"use strict";i.r(t),i(143),i(142),i(102),i(60),i(127),i(151),i(50);var s=i(0),a=i(2),n=(i(158),i(154),i(11)),r=(i(145),i(99)),o=i(61);i(166),customElements.define("hui-error-card",class extends a.a{static get template(){return s["a"]`
      <style>
        :host {
          display: block;
          background-color: red;
          color: white;
          text-align: center;
          padding: 8px;
        }
      </style>
      [[config.error]]
    `}static get properties(){return{config:Object}}getCardSize(){return 1}}),customElements.define("hui-camera-preview-card",class extends a.a{static get properties(){return{hass:{type:Object,observer:"_hassChanged"},config:{type:Object,observer:"_configChanged"}}}getCardSize(){return 4}_configChanged(e){this._entityId=null,this.lastChild&&this.removeChild(this.lastChild);let t,i,s=null;const a=e&&e.entity;a?"camera"===Object(o.a)(a)?(this._entityId=a,i="ha-camera-card",t=e):s='Entity domain must be "camera"':s="Entity not defined in card config",s&&(i="hui-error-card",t={error:s});const n=document.createElement(i);s||(n.stateObj=this.hass.states[a],n.hass=this.hass),n.config=t,this.appendChild(n)}_hassChanged(e){if(this.lastChild&&this._entityId){const t=this.lastChild,i=e.states[this._entityId];t.stateObj=i,t.hass=e}}}),i(25);var c=i(134),l=i(33);i(86),i(149),customElements.define("hui-entities-card",class extends(Object(n.a)(a.a)){static get template(){return s["a"]`
    <style>
      ha-card {
        padding: 16px;
      }
      #states {
        margin: -4px 0;
      }
      #states > * {
        display: block;
        margin: 4px 0;
      }
      .header {
        @apply --paper-font-headline;
        /* overwriting line-height +8 because entity-toggle can be 40px height,
           compensating this with reduced padding */
        line-height: 40px;
        color: var(--primary-text-color);
        padding: 4px 0 12px;
      }
      .header .name {
        @apply --paper-font-common-nowrap;
      }
      .state-card-dialog {
        cursor: pointer;
      }
    </style>

    <ha-card>
      <div class='header'>
        <div class="name">[[_computeTitle(config)]]</div>
      </div>
      <div id="states"></div>
    </ha-card>
`}static get properties(){return{hass:{type:Object,observer:"_hassChanged"},config:{type:Object,observer:"_configChanged"}}}constructor(){super(),this._elements=[]}getCardSize(){return 1+(this.config?this.config.entities.length:0)}_computeTitle(e){return e.title}_configChanged(e){const t=this.$.states;for(;t.lastChild;)t.removeChild(t.lastChild);this._elements=[];for(let i=0;i<e.entities.length;i++){const s=e.entities[i],a=this.hass.states[s],n=a?`state-card-${Object(c.a)(this.hass,a)}`:"state-card-display",r=document.createElement(n);l.c.includes(Object(o.a)(s))||(r.classList.add("state-card-dialog"),r.addEventListener("click",()=>this.fire("hass-more-info",{entityId:s}))),r.stateObj=a,r.hass=this.hass,this._elements.push({entityId:s,element:r}),t.appendChild(r)}}_hassChanged(e){for(let t=0;t<this._elements.length;t++){const{entityId:i,element:s}=this._elements[t],a=e.states[i];s.stateObj=a,s.hass=e}}});var h=i(92),d=i(16),p=(i(109),i(12));customElements.define("hui-glance-card",class extends(Object(p.a)(Object(n.a)(a.a))){static get template(){return s["a"]`
      <style>
        ha-card {
          padding: 16px;
        }
        .header {
          @apply --paper-font-headline;
          /* overwriting line-height +8 because entity-toggle can be 40px height,
            compensating this with reduced padding */
          line-height: 40px;
          color: var(--primary-text-color);
          padding: 4px 0 12px;
        }
        .header .name {
          @apply --paper-font-common-nowrap;
        }
        .entities {
          padding: 4px 0;
          display: flex;
          margin-bottom: -12px;
          flex-wrap: wrap;
        }
        .entity {
          box-sizing: border-box;
          padding: 0 4px;
          display: flex;
          flex-direction: column;
          cursor: pointer;
          margin-bottom: 12px;
          width: 20%;
        }
        .entity div, .entity state-badge {
          width: 100%;
          text-align: center;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        .error {
          background-color: red;
          color: white;
          text-align: center;
        }
      </style>

      <ha-card>
        <div class="header">
          <div class="name">[[_computeTitle(config)]]</div>
        </div>
        <div class="entities">
          <template is="dom-repeat" items="[[_entities]]">
            <template is="dom-if" if="[[_showEntity(item, hass.states)]]">
              <div class="entity" on-click="_openDialog">
                <div>[[_computeName(item, hass.states)]]</div>
                <state-badge state-obj="[[_computeStateObj(item, hass.states)]]"></state-badge>
                <div>[[_computeState(item, hass.states)]]</div>
              </div>
            </template>
          </template>
        </div>
        <template is="dom-if" if="[[_error]]">
          <div class="error">[[_error]]</div>
        </template>
      </ha-card>
    `}static get properties(){return{hass:Object,config:Object,_entities:{type:Array,computed:"_computeEntities(config)"},_error:String}}getCardSize(){return 3}_computeTitle(e){return e.title}_computeEntities(e){return e&&e.entities&&Array.isArray(e.entities)?(this._error=null,e.entities):(this._error="Error in card configuration.",[])}_showEntity(e,t){return e in t}_computeName(e,t){return Object(d.a)(t[e])}_computeStateObj(e,t){return t[e]}_computeState(e,t){return Object(h.a)(this.localize,t[e])}_openDialog(e){this.fire("hass-more-info",{entityId:e.model.item})}}),i(156),customElements.define("hui-history-graph-card",class extends a.a{static get properties(){return{hass:{type:Object,observer:"_hassChanged"},config:{type:Object,observer:"_configChanged"}}}getCardSize(){return 4}_configChanged(e){this._entityId=null,this.lastChild&&this.removeChild(this.lastChild);let t,i,s=null;const a=e&&e.entity;a?"history_graph"===Object(o.a)(a)?(this._entityId=a,i="ha-history_graph-card",t=e):s='Entity domain must be "history_graph"':s="Entity not defined in card config",s&&(i="hui-error-card",t={error:s});const n=document.createElement(i);s||(n.stateObj=this.hass.states[a],n.hass=this.hass),n.config=t,this.appendChild(n)}_hassChanged(e){if(this.lastChild&&this._entityId){const t=this.lastChild,i=e.states[this._entityId];t.stateObj=i,t.hass=e}}}),i(162),customElements.define("hui-media-control-card",class extends a.a{static get properties(){return{hass:{type:Object,observer:"_hassChanged"},config:{type:Object,observer:"_configChanged"}}}getCardSize(){return 3}_configChanged(e){this._entityId=null,this.lastChild&&this.removeChild(this.lastChild);let t,i,s=null;const a=e&&e.entity;a?"media_player"===Object(o.a)(a)?(this._entityId=a,i="ha-media_player-card",t=e):s='Entity domain must be "media_player"':s="Entity not defined in card config",s&&(i="hui-error-card",t={error:s});const n=document.createElement(i);s||(n.stateObj=this.hass.states[a],n.hass=this.hass),n.config=t,this.appendChild(n)}_hassChanged(e){if(this.lastChild&&this._entityId){const t=this.lastChild,i=e.states[this._entityId];t.stateObj=i,t.hass=e}}});var m=i(95);const u=["binary_sensor","device_tracker","sensor"];customElements.define("hui-picture-glance-card",class extends(Object(p.a)(Object(n.a)(a.a))){static get template(){return s["a"]`
      <style>
        ha-card {
          position: relative;
          min-height: 48px;
          line-height: 0;
        }
        img {
          width: 100%;
          height: auto;
          border-radius: 2px;
        }
        .box {
          @apply --paper-font-common-nowrap;
          position: absolute;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: rgba(0, 0, 0, 0.3);
          padding: 4px 16px;
          font-size: 16px;
          line-height: 40px;
          color: white;
          border-bottom-left-radius: 2px;
          border-bottom-right-radius: 2px;
          display: flex;
          justify-content: space-between;
        }
        .box .title {
          font-weight: 500;
        }
        paper-icon-button, iron-icon {
          color: #A9A9A9;
        }
        paper-icon-button.state-on, iron-icon.state-on {
          color: white;
        }
        iron-icon {
          padding: 8px;
        }
        .error {
          background-color: red;
          color: white;
          text-align: center;
        }
      </style>

      <ha-card>
        <img src="[[config.image]]">
        <div class="box">
          <div class="title">[[config.title]]</div>
          <div>
            <template is="dom-repeat" items="[[_entitiesDialog]]">
              <template is="dom-if" if="[[_showEntity(item, hass.states)]]">
                <paper-icon-button
                  on-click="_openDialog"
                  class$="[[_computeClass(item, hass.states)]]"
                  icon="[[_computeIcon(item, hass.states)]]"
                  title="[[_computeTooltip(item, hass.states)]]"
                ></paper-icon-button>
              </template>
            </template>
          </div>
          <div>
            <template is="dom-repeat" items="[[_entitiesService]]">
              <template is="dom-if" if="[[_showEntity(item, hass.states)]]">
                <paper-icon-button
                  on-click="_callService"
                  class$="[[_computeClass(item, hass.states)]]"
                  icon="[[_computeIcon(item, hass.states)]]"
                  title="[[_computeTooltip(item, hass.states)]]"
                ></paper-icon-button>
              </template>
            </template>
          </div>
        </div>
        <template is="dom-if" if="[[_error]]">
          <div class="error">[[_error]]</div>
        </template>
      </ha-card>
    `}static get properties(){return{hass:Object,config:{type:Object,observer:"_configChanged"},_entitiesDialog:Array,_entitiesService:Array,_error:String}}getCardSize(){return 3}_configChanged(e){let t=[],i=[],s=null;e&&e.entities&&Array.isArray(e.entities)&&e.image?e.force_dialog?t=e.entities:(t=e.entities.filter(e=>u.includes(Object(o.a)(e))),i=e.entities.filter(e=>!t.includes(e))):s="Error in card configuration.",this.setProperties({_entitiesDialog:t,_entitiesService:i,_error:s})}_showEntity(e,t){return e in t}_computeIcon(e,t){return Object(m.a)(t[e])}_computeClass(e,t){return l.h.includes(t[e].state)?"state-on":""}_computeTooltip(e,t){return`${Object(d.a)(t[e])}: ${Object(h.a)(this.localize,t[e])}`}_openDialog(e){this.fire("hass-more-info",{entityId:e.model.item})}_callService(e){const t=e.model.item,i=Object(o.a)(t),s=l.h.includes(this.hass.states[t].state);let a;switch(i){case"lock":a=s?"unlock":"lock";break;case"cover":a=s?"close":"open";break;case"scene":a="turn_on";break;default:a=s?"turn_off":"turn_on"}this.hass.callService(i,a,{entity_id:t})}}),i(161),customElements.define("hui-plant-status-card",class extends a.a{static get properties(){return{hass:{type:Object,observer:"_hassChanged"},config:{type:Object,observer:"_configChanged"}}}getCardSize(){return 3}_configChanged(e){this._entityId=null,this.lastChild&&this.removeChild(this.lastChild);let t,i,s=null;const a=e&&e.entity;a?"plant"===Object(o.a)(a)?(this._entityId=a,i="ha-plant-card",t=e):s='Entity domain must be "plant"':s="Entity not defined in card config",s&&(i="hui-error-card",t={error:s});const n=document.createElement(i);s||(n.stateObj=this.hass.states[a],n.hass=this.hass),n.config=t,this.appendChild(n)}_hassChanged(e){if(this.lastChild&&this._entityId){const t=this.lastChild,i=e.states[this._entityId];t.stateObj=i,t.hass=e}}}),i(160),customElements.define("hui-weather-forecast-card",class extends a.a{static get properties(){return{hass:{type:Object,observer:"_hassChanged"},config:{type:Object,observer:"_configChanged"}}}getCardSize(){return 4}_configChanged(e){this._entityId=null,this.lastChild&&this.removeChild(this.lastChild);let t,i,s=null;const a=e&&e.entity;a?"weather"===Object(o.a)(a)?(this._entityId=a,i="ha-weather-card",t=e):s='Entity domain must be "weather"':s="Entity not defined in card config",s&&(i="hui-error-card",t={error:s});const n=document.createElement(i);s||(n.stateObj=this.hass.states[a],n.hass=this.hass),n.config=t,this.appendChild(n)}_hassChanged(e){if(this.lastChild&&this._entityId){const t=this.lastChild,i=e.states[this._entityId];t.stateObj=i,t.hass=e}}});var g=i(15);customElements.define("hui-entity-filter-card",class extends a.a{static get properties(){return{hass:{type:Object,observer:"_hassChanged"},config:{type:Object,observer:"_configChanged"}}}constructor(){super(),this._whenDefined={}}getCardSize(){return this.lastChild?this.lastChild.getCardSize():1}_getEntities(e,t){const i=new Set;return t.forEach(t=>{const s=[];t.domain&&s.push(e=>Object(g.a)(e)===t.domain),t.entity_id&&s.push(e=>this._filterEntityId(e,t.entity_id)),t.state&&s.push(e=>e.state===t.state),Object.values(e.states).forEach(e=>{s.every(t=>t(e))&&i.add(e.entity_id)})}),Array.from(i)}_filterEntityId(e,t){if(-1===t.indexOf("*"))return e.entity_id===t;const i=new RegExp(`^${t.replace(/\*/g,".*")}$`);return 0===e.entity_id.search(i)}_configChanged(e){this.lastChild&&this.removeChild(this.lastChild);let t,i=null,s=e.card?y(e.card):"hui-entities-card";null===s?i=`Unknown card type encountered: "${e.card}".`:customElements.get(s)?e.filter&&Array.isArray(e.filter)||(i="No or incorrect filter."):(i=`Custom element doesn't exist: "${s}".`,s in this._whenDefined||(this._whenDefined[s]=customElements.whenDefined(s).then(()=>this._configChanged(this.config)))),i?(s="hui-error-card",t={error:i}):t=this._computeCardConfig(e);const a=document.createElement(s);a.config=t,a.hass=this.hass,this.appendChild(a)}_hassChanged(e){const t=this.lastChild;t&&(t.hass=e,t.config=this._computeCardConfig(this.config))}_computeCardConfig(e){return Object.assign({},e.card_config,{entities:this._getEntities(this.hass,e.filter)})}}),i(147),customElements.define("hui-markdown-card",class extends a.a{static get template(){return s["a"]`
      <style>
        :host {
          @apply --paper-font-body1;
        }
        ha-markdown {
          display: block;
          padding: 0 16px 16px;
          -ms-user-select: initial;
          -webkit-user-select: initial;
          -moz-user-select: initial;
        }
        :host([no-title]) ha-markdown {
          padding-top: 16px;
        }
        ha-markdown p:first-child {
          margin-top: 0;
        }
        ha-markdown p:last-child {
          margin-bottom: 0;
        }
        ha-markdown a {
          color: var(--primary-color);
        }
        ha-markdown img {
          max-width: 100%;
        }
        paper-button {
          margin: 8px;
          font-weight: 500;
        }
      </style>
      <ha-card header="[[config.title]]">
        <ha-markdown content='[[config.content]]'></ha-markdown>
      </ha-card>
    `}static get properties(){return{config:Object,noTitle:{type:Boolean,reflectToAttribute:!0,computed:"_computeNoTitle(config.title)"}}}getCardSize(){return this.config.content.split("\n").length}_computeNoTitle(e){return!e}});const f=["scene","script","weblink"];customElements.define("hui-entity-picture-card",class extends(Object(p.a)(a.a)){static get template(){return s["a"]`
      <style>
        ha-card {
          position: relative;
          cursor: pointer;
          min-height: 48px;
          line-height: 0;
        }
        img {
          width: 100%;
          height: auto;
          border-radius: 2px;
        }
        img.state-off {
          filter: grayscale(100%);
        }
        .text {
          @apply --paper-font-common-nowrap;
          position: absolute;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: rgba(0, 0, 0, 0.3);
          padding: 16px;
          font-size: 16px;
          line-height: 16px;
          color: white;
          border-bottom-left-radius: 2px;
          border-bottom-right-radius: 2px;
          display: flex;
          justify-content: space-between;
        }
        .text .title {
          font-weight: 500;
        }
        .error {
          background-color: red;
          color: white;
          text-align: center;
        }
      </style>

      <ha-card on-click="_cardClicked">
        <img class$="[[_computeClass(config.entity, hass.states)]]" src="[[config.image]]">
        <div class="text">
          <div class="title">[[_computeTitle(config.entity, hass.states)]]</div>
          <div>[[_computeState(config.entity, hass.states)]]</div>
        </div>
        <template is="dom-if" if="[[_error]]">
          <div class="error">[[_error]]</div>
        </template>
      </ha-card>
    `}static get properties(){return{hass:Object,config:{type:Object,observer:"_configChanged"},_error:String}}getCardSize(){return 3}_configChanged(e){e&&e.entity&&e.image?this._error=null:this._error="Error in card configuration."}_computeClass(e,t){return f.includes(Object(o.a)(e))||l.h.includes(t[e].state)?"":"state-off"}_computeTitle(e,t){return e&&e in t&&Object(d.a)(t[e])}_computeState(e,t){switch(Object(o.a)(e)){case"scene":return this.localize("ui.card.scene.activate");case"script":return this.localize("ui.card.script.execute");case"weblink":return"Open";default:return Object(h.a)(this.localize,t[e])}}_cardClicked(){const e=this.config.entity,t=Object(o.a)(e);if("weblink"===t)window.open(this.hass.states[e].state);else{const i=l.h.includes(this.hass.states[e].state);let s;switch(t){case"lock":s=i?"unlock":"lock";break;case"cover":s=i?"close":"open";break;default:s=i?"turn_off":"turn_on"}this.hass.callService(t,s,{entity_id:e})}}});const _=["camera-preview","entities","entity-filter","entity-picture","glance","history-graph","markdown","media-control","picture-glance","plant-status","weather-forecast"],b="custom:";function y(e){return _.includes(e)?`hui-${e}-card`:e.startsWith(b)?e.substr(b.length):null}customElements.define("hui-view",class extends a.a{static get template(){return s["a"]`
      <style>
      :host {
        display: block;
        padding: 4px 4px 0;
        transform: translateZ(0);
        position: relative;
      }

      #columns {
        display: flex;
        flex-direction: row;
        justify-content: center;
      }

      .column {
        flex-basis: 0;
        flex-grow: 1;
        max-width: 500px;
        overflow-x: hidden;
      }

      .column > * {
        display: block;
        margin: 4px 4px 8px;
      }

      @media (max-width: 500px) {
        :host {
          padding-left: 0;
          padding-right: 0;
        }

        .column > * {
          margin-left: 0;
          margin-right: 0;
        }
      }

      @media (max-width: 599px) {
        .column {
          max-width: 600px;
        }
      }
      </style>
      <div id='columns'></div>
    `}static get properties(){return{hass:{type:Object,observer:"_hassChanged"},columns:{type:Number,observer:"_configChanged"},config:{type:Object,observer:"_configChanged"}}}constructor(){super(),this._elements=[],this._whenDefined={}}_getElements(e){const t=[];for(let i=0;i<e.length;i++){let s,a=null,n=e[i];n.type?null===(s=y(n.type))?a=`Unknown card type encountered: "${n.type}".`:customElements.get(s)||(a=`Custom element doesn't exist: "${s}".`,s in this._whenDefined||(this._whenDefined[s]=customElements.whenDefined(s).then(()=>this._configChanged()))):a="Card type not configured.",a&&(s="hui-error-card",n={error:a});const r=document.createElement(s);r.config=n,r.hass=this.hass,t.push(r)}return t}_configChanged(){const e=this.$.columns,t=this.config;for(;e.lastChild;)e.removeChild(e.lastChild);if(!t)return void(this._elements=[]);const i=this._getElements(t.cards);let s=[];const a=[];for(let e=0;e<this.columns;e++)s.push([]),a.push(0);i.forEach(e=>{const t="function"==typeof e.getCardSize?e.getCardSize():1;s[function(e){let t=0;for(let e=0;e<a.length;e++){if(a[e]<5){t=e;break}a[e]<a[t]&&(t=e)}return a[t]+=e,t}(t)].push(e)}),(s=s.filter(e=>e.length>0)).forEach(t=>{const i=document.createElement("div");i.classList.add("column"),t.forEach(e=>i.appendChild(e)),e.appendChild(i)}),this._elements=i,"theme"in t&&Object(r.a)(e,this.hass.themes,t.theme)}_hassChanged(e){for(let t=0;t<this._elements.length;t++)this._elements[t].hass=e}}),customElements.define("hui-root",class extends(Object(n.a)(a.a)){static get template(){return s["a"]`
    <style include='ha-style'>
      :host {
        -ms-user-select: none;
        -webkit-user-select: none;
        -moz-user-select: none;
      }

      ha-app-layout {
        min-height: 100%;
      }
      paper-tabs {
        margin-left: 12px;
        --paper-tabs-selection-bar-color: var(--text-primary-color, #FFF);
        text-transform: uppercase;
      }
      app-toolbar a {
        color: var(--text-primary-color, white);
      }
    </style>
    <ha-app-layout id="layout">
      <app-header slot="header" fixed>
        <app-toolbar>
          <ha-menu-button narrow='[[narrow]]' show-menu='[[showMenu]]'></ha-menu-button>
          <div main-title>[[_computeTitle(config)]]</div>
          <a href='https://developers.home-assistant.io/docs/en/lovelace_index.html' tabindex='-1' target='_blank'>
            <paper-icon-button icon='hass:help-circle-outline'></paper-icon-button>
          </a>
          <paper-icon-button icon='hass:refresh' on-click='_handleRefresh'></paper-icon-button>
        </app-toolbar>

        <div sticky hidden$="[[_computeTabsHidden(config.views)]]">
          <paper-tabs scrollable selected="[[_curView]]" on-iron-activate="_handleViewSelected">
            <template is="dom-repeat" items="[[config.views]]">
              <paper-tab on-click="_scrollToTop">
                <template is="dom-if" if="[[item.tab_icon]]">
                  <iron-icon title$="[[item.name]]" icon="[[item.tab_icon]]"></iron-icon>
                </template>
                <template is="dom-if" if="[[!item.tab_icon]]">
                  [[_computeTabTitle(item)]]
                </template>
              </paper-tab>
            </template>
          </paper-tabs>
        </div>
      </app-header>

      <span id='view'></span>
    </app-header-layout>
    `}static get properties(){return{narrow:Boolean,showMenu:Boolean,hass:{type:Object,observer:"_hassChanged"},config:{type:Object,observer:"_configChanged"},columns:{type:Number,observer:"_columnsChanged"},_curView:{type:Number,value:0}}}ready(){super.ready(),this._selectView(0)}_computeTitle(e){return e.name||"Home Assistant"}_computeTabsHidden(e){return e.length<2}_computeTabTitle(e){return e.tab_title||e.name||"Unnamed View"}_handleRefresh(){this.fire("config-refresh")}_handleViewSelected(e){this._selectView(e.detail.selected)}_selectView(e){this._curView=e;const t=this.$.view;t.lastChild&&t.removeChild(t.lastChild);const i=document.createElement("hui-view");i.setProperties({hass:this.hass,config:this.config.views[this._curView],columns:this.columns}),t.appendChild(i)}_hassChanged(e){this.$.view.lastChild&&(this.$.view.lastChild.hass=e)}_configChanged(){this._selectView(this._curView)}_columnsChanged(e){this.$.view.lastChild&&(this.$.view.lastChild.columns=e)}_scrollToTop(){var e=this.$.layout.header.scrollTarget,t=Math.random(),i=Date.now(),s=e.scrollTop,a=0-s;this._currentAnimationId=t,function n(){var r,o=Date.now()-i;o>200?e.scrollTop=0:this._currentAnimationId===t&&(e.scrollTop=(r=o,-a*(r/=200)*(r-2)+s),requestAnimationFrame(n.bind(this)))}.call(this)}}),customElements.define("ha-panel-lovelace",class extends a.a{static get template(){return s["a"]`
      <template is='dom-if' if='[[_equal(_state, "loaded")]]' restamp>
        <hui-root
          narrow="[[narrow]]"
          show-menu="[[showMenu]]"
          hass='[[hass]]'
          config='[[_config]]'
          columns='[[_columns]]'
          on-config-refresh='_fetchConfig'
        ></hui-root>
      </template>
      <template is='dom-if' if='[[_equal(_state, "loading")]]' restamp>
        <hass-loading-screen
          narrow="[[narrow]]"
          show-menu="[[showMenu]]"
        ></hass-loading-screen>
      </template>
      <template is='dom-if' if='[[_equal(_state, "error")]]' restamp>
        <hass-error-screen
          title='Lovelace'
          error='[[_errorMsg]]'
          narrow="[[narrow]]"
          show-menu="[[showMenu]]"
        ></hass-error-screen>
      </template>
    `}static get properties(){return{hass:Object,narrow:{type:Boolean,value:!1},showMenu:{type:Boolean,value:!1},_columns:{type:Number,value:1},_state:{type:String,value:"loading"},_errorMsg:String,_config:{type:Object,value:null}}}ready(){super.ready(),this._fetchConfig(),this._handleWindowChange=this._handleWindowChange.bind(this),this.mqls=[300,600,900,1200].map(e=>{const t=matchMedia(`(min-width: ${e}px)`);return t.addListener(this._handleWindowChange),t}),this._handleWindowChange()}_handleWindowChange(){const e=this.mqls.reduce((e,t)=>e+t.matches,0);this._columns=Math.max(1,e-(!this.narrow&&this.showMenu))}_fetchConfig(){this.hass.connection.sendMessagePromise({type:"frontend/lovelace_config"}).then(e=>this.setProperties({_config:e.result,_state:"loaded"}),e=>this.setProperties({_state:"error",_errorMsg:e.message}))}_equal(e,t){return e===t}})}}]);
//# sourceMappingURL=2de91f8ab087324f74ce.chunk.js.map