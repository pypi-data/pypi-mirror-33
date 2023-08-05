(window.webpackJsonp=window.webpackJsonp||[]).push([[20],{584:function(e,t,s){"use strict";s.r(t),s(143),s(142),s(121),s(59),s(127),s(151),s(50);var i=s(0),a=s(3),n=(s(157),s(11)),r=(s(145),s(27),s(134)),o=s(60),h=s(33);s(91),s(149),customElements.define("hui-entities-card",class extends(Object(n.a)(a.a)){static get template(){return i["a"]`
    <style>
      ha-card {
        padding: 16px;
      }
      .state {
        padding: 4px 0;
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
`}static get properties(){return{hass:{type:Object,observer:"_hassChanged"},config:{type:Object,observer:"_configChanged"}}}constructor(){super(),this._elements=[]}getCardSize(){return 1+(this.config?this.config.entities.length:0)}_computeTitle(e){return e.title}_configChanged(e){const t=this.$.states;for(;t.lastChild;)t.removeChild(t.lastChild);this._elements=[];for(let s=0;s<e.entities.length;s++){const i=e.entities[s],a=this.hass.states[i],n=a?`state-card-${Object(r.a)(this.hass,a)}`:"state-card-display",c=document.createElement(n);h.c.includes(Object(o.a)(i))||(c.classList.add("state-card-dialog"),c.addEventListener("click",()=>this.fire("hass-more-info",{entityId:i}))),c.stateObj=a,c.hass=this.hass,this._elements.push({entityId:i,element:c}),t.appendChild(c)}}_hassChanged(e){for(let t=0;t<this._elements.length;t++){const{entityId:s,element:i}=this._elements[t],a=e.states[s];i.stateObj=a,i.hass=e}}});var c=s(15);customElements.define("hui-entity-filter-card",class extends a.a{static get template(){return i["a"]`
    <hui-entities-card
      hass='[[hass]]'
      config='[[_computeCardConfig(hass, config)]]'
    ></hui-entities-card>
`}static get properties(){return{hass:Object,config:Object}}getCardSize(){return 1+this._getEntities(this.hass,this.config.filter).length}_getEntities(e,t){const s=[];if(t.domain){const e=t.domain;s.push(t=>Object(c.a)(t)===e)}if(t.state){const e=t.state;s.push(t=>t.state===e)}return Object.values(e.states).filter(e=>s.every(t=>t(e))).map(e=>e.entity_id)}_computeCardConfig(e,t){return Object.assign({},t.card_config||{},{entities:this._getEntities(e,t.filter)})}}),s(165),customElements.define("hui-error-card",class extends a.a{static get template(){return i["a"]`
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
    `}static get properties(){return{config:Object}}getCardSize(){return 1}}),customElements.define("hui-camera-preview-card",class extends a.a{static get properties(){return{hass:{type:Object,observer:"_hassChanged"},config:{type:Object,observer:"_configChanged"}}}getCardSize(){return 4}_configChanged(e){this._entityId=null,this.lastChild&&this.removeChild(this.lastChild);let t,s,i=null;const a=e&&e.entity;a?"camera"===Object(o.a)(a)?(this._entityId=a,s="ha-camera-card",t=e):i='Entity domain must be "camera"':i="Entity not defined in card config",i&&(s="hui-error-card",t={error:i});const n=document.createElement(s);i||(n.stateObj=this.hass.states[a],n.hass=this.hass),n.config=t,this.appendChild(n)}_hassChanged(e){if(this.lastChild&&this._entityId){const t=this.lastChild,s=e.states[this._entityId];t.stateObj=s,t.hass=e}}}),s(155),customElements.define("hui-history-graph-card",class extends a.a{static get properties(){return{hass:{type:Object,observer:"_hassChanged"},config:{type:Object,observer:"_configChanged"}}}getCardSize(){return 4}_configChanged(e){this._entityId=null,this.lastChild&&this.removeChild(this.lastChild);let t,s,i=null;const a=e&&e.entity;a?"history_graph"===Object(o.a)(a)?(this._entityId=a,s="ha-history_graph-card",t=e):i='Entity domain must be "history_graph"':i="Entity not defined in card config",i&&(s="hui-error-card",t={error:i});const n=document.createElement(s);i||(n.stateObj=this.hass.states[a],n.hass=this.hass),n.config=t,this.appendChild(n)}_hassChanged(e){if(this.lastChild&&this._entityId){const t=this.lastChild,s=e.states[this._entityId];t.stateObj=s,t.hass=e}}}),s(161),customElements.define("hui-media-control-card",class extends a.a{static get properties(){return{hass:{type:Object,observer:"_hassChanged"},config:{type:Object,observer:"_configChanged"}}}getCardSize(){return 3}_configChanged(e){this._entityId=null,this.lastChild&&this.removeChild(this.lastChild);let t,s,i=null;const a=e&&e.entity;a?"media_player"===Object(o.a)(a)?(this._entityId=a,s="ha-media_player-card",t=e):i='Entity domain must be "media_player"':i="Entity not defined in card config",i&&(s="hui-error-card",t={error:i});const n=document.createElement(s);i||(n.stateObj=this.hass.states[a],n.hass=this.hass),n.config=t,this.appendChild(n)}_hassChanged(e){if(this.lastChild&&this._entityId){const t=this.lastChild,s=e.states[this._entityId];t.stateObj=s,t.hass=e}}}),s(160),customElements.define("hui-plant-status-card",class extends a.a{static get properties(){return{hass:{type:Object,observer:"_hassChanged"},config:{type:Object,observer:"_configChanged"}}}getCardSize(){return 3}_configChanged(e){this._entityId=null,this.lastChild&&this.removeChild(this.lastChild);let t,s,i=null;const a=e&&e.entity;a?"plant"===Object(o.a)(a)?(this._entityId=a,s="ha-plant-card",t=e):i='Entity domain must be "plant"':i="Entity not defined in card config",i&&(s="hui-error-card",t={error:i});const n=document.createElement(s);i||(n.stateObj=this.hass.states[a],n.hass=this.hass),n.config=t,this.appendChild(n)}_hassChanged(e){if(this.lastChild&&this._entityId){const t=this.lastChild,s=e.states[this._entityId];t.stateObj=s,t.hass=e}}}),s(159),customElements.define("hui-weather-forecast-card",class extends a.a{static get properties(){return{hass:{type:Object,observer:"_hassChanged"},config:{type:Object,observer:"_configChanged"}}}getCardSize(){return 4}_configChanged(e){this._entityId=null,this.lastChild&&this.removeChild(this.lastChild);let t,s,i=null;const a=e&&e.entity;a?"weather"===Object(o.a)(a)?(this._entityId=a,s="ha-weather-card",t=e):i='Entity domain must be "weather"':i="Entity not defined in card config",i&&(s="hui-error-card",t={error:i});const n=document.createElement(s);i||(n.stateObj=this.hass.states[a],n.hass=this.hass),n.config=t,this.appendChild(n)}_hassChanged(e){if(this.lastChild&&this._entityId){const t=this.lastChild,s=e.states[this._entityId];t.stateObj=s,t.hass=e}}});var l=s(98);const d=["camera-preview","entities","entity-filter","history-graph","media-control","plant-status","weather-forecast"];customElements.define("hui-view",class extends a.a{static get template(){return i["a"]`
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
    `}static get properties(){return{hass:{type:Object,observer:"_hassChanged"},columns:{type:Number,observer:"_configChanged"},config:{type:Object,observer:"_configChanged"}}}constructor(){super(),this._elements=[]}_getElements(e){const t=[];for(let i=0;i<e.length;i++){let a,n=null,r=e[i];r.type?(s=r.type,null===(a=d.includes(s)?`hui-${s}-card`:s.startsWith("custom:")?s.substr("custom:".length):null)?n=`Unknown card type encountered: "${r.type}".`:customElements.get(a)||(n=`Custom element doesn't exist: "${a}".`)):n="Card type not configured.",n&&(a="hui-error-card",r={error:n});const o=document.createElement(a);o.config=r,o.hass=this.hass,t.push(o)}var s;return t}_configChanged(){const e=this.$.columns,t=this.config;for(;e.lastChild;)e.removeChild(e.lastChild);if(!t)return void(this._elements=[]);const s=this._getElements(t.cards);let i=[];const a=[];for(let e=0;e<this.columns;e++)i.push([]),a.push(0);s.forEach(e=>{const t="function"==typeof e.getCardSize?e.getCardSize():1;i[function(e){let t=0;for(let e=0;e<a.length;e++){if(a[e]<5){t=e;break}a[e]<a[t]&&(t=e)}return a[t]+=e,t}(t)].push(e)}),(i=i.filter(e=>e.length>0)).forEach(t=>{const s=document.createElement("div");s.classList.add("column"),t.forEach(e=>s.appendChild(e)),e.appendChild(s)}),this._elements=s,"theme"in t&&Object(l.a)(e,this.hass.themes,t.theme)}_hassChanged(e){for(let t=0;t<this._elements.length;t++)this._elements[t].hass=e}}),customElements.define("hui-root",class extends(Object(n.a)(a.a)){static get template(){return i["a"]`
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
    </style>
    <ha-app-layout id="layout">
      <app-header slot="header" fixed>
        <app-toolbar>
          <ha-menu-button narrow='[[narrow]]' show-menu='[[showMenu]]'></ha-menu-button>
          <div main-title>[[_computeTitle(config)]]</div>
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

      <hui-view
        hass='[[hass]]'
        config='[[_computeViewConfig(config.views, _curView)]]'
        columns='[[columns]]'
      ></hui-view>
    </app-header-layout>
    `}static get properties(){return{hass:Object,narrow:Boolean,showMenu:Boolean,config:Object,columns:Number,_curView:{type:Number,value:0}}}_computeTitle(e){return e.title||"Experimental UI"}_computeTabsHidden(e){return e.length<2}_computeTabTitle(e){return e.tab_title||e.name||"Unnamed View"}_computeViewConfig(e,t){return e[t]}_handleRefresh(){this.fire("config-refresh")}_handleViewSelected(e){this._curView=e.detail.selected}_scrollToTop(){var e=this.$.layout.header.scrollTarget,t=Math.random(),s=Date.now(),i=e.scrollTop,a=0-i;this._currentAnimationId=t,function n(){var r,o=Date.now()-s;o>200?e.scrollTop=0:this._currentAnimationId===t&&(e.scrollTop=(r=o,-a*(r/=200)*(r-2)+i),requestAnimationFrame(n.bind(this)))}.call(this)}}),customElements.define("ha-panel-experimental-ui",class extends a.a{static get template(){return i["a"]`
      <template is='dom-if' if='[[!_config]]' restamp>
        <hass-loading-screen
          narrow="[[narrow]]"
          show-menu="[[showMenu]]"
        ></hass-loading-screen>
      </template>
      <template is='dom-if' if='[[_config]]' restamp>
        <hui-root
          hass='[[hass]]'
          config='[[_config]]'
          columns='[[_columns]]'
          on-config-refresh='_fetchConfig'
        ></hui-root>
      </template>
    `}static get properties(){return{hass:Object,narrow:{type:Boolean,value:!1},showMenu:{type:Boolean,value:!1},_columns:{type:Number,value:1},_config:{type:Object,value:null}}}ready(){super.ready(),this._fetchConfig(),this._handleWindowChange=this._handleWindowChange.bind(this),this.mqls=[300,600,900,1200].map(e=>{const t=matchMedia(`(min-width: ${e}px)`);return t.addListener(this._handleWindowChange),t}),this._handleWindowChange()}_handleWindowChange(){const e=this.mqls.reduce((e,t)=>e+t.matches,0);this._columns=Math.max(1,e-(!this.narrow&&this.showMenu))}_fetchConfig(){this.hass.connection.sendMessagePromise({type:"frontend/experimental_ui"}).then(e=>{this._config=e.result})}})}}]);
//# sourceMappingURL=3ba05d36718362ad5edb.chunk.js.map