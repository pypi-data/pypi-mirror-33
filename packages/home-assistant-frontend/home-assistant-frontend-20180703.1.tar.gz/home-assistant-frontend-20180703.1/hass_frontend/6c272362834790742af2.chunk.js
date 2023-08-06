(window.webpackJsonp=window.webpackJsonp||[]).push([[19],{198:function(e,t,i){"use strict";var s=i(0),a=i(2),r=(i(206),i(11));customElements.define("ha-call-service-button",class extends(Object(r.a)(a.a)){static get template(){return s["a"]`
    <ha-progress-button id="progress" progress="[[progress]]" on-click="buttonTapped"><slot></slot></ha-progress-button>
`}static get properties(){return{hass:{type:Object},progress:{type:Boolean,value:!1},domain:{type:String},service:{type:String},serviceData:{type:Object,value:{}}}}buttonTapped(){this.progress=!0;var e=this,t={domain:this.domain,service:this.service,serviceData:this.serviceData};this.hass.callService(this.domain,this.service,this.serviceData).then(function(){e.progress=!1,e.$.progress.actionSuccess(),t.success=!0},function(){e.progress=!1,e.$.progress.actionError(),t.success=!1}).then(function(){e.fire("hass-service-called",t)})}})},206:function(e,t,i){"use strict";i(61),i(124);var s=i(0),a=i(2);customElements.define("ha-progress-button",class extends a.a{static get template(){return s["a"]`
    <style>
      .container {
        position: relative;
        display: inline-block;
      }

      paper-button {
        transition: all 1s;
      }

      .success paper-button {
        color: white;
        background-color: var(--google-green-500);
        transition: none;
      }

      .error paper-button {
        color: white;
        background-color: var(--google-red-500);
        transition: none;
      }

      paper-button[disabled] {
        color: #c8c8c8;
      }

      .progress {
        @apply --layout;
        @apply --layout-center-center;
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
      }
    </style>
    <div class="container" id="container">
      <paper-button id="button" disabled="[[computeDisabled(disabled, progress)]]" on-click="buttonTapped">
        <slot></slot>
      </paper-button>
      <template is="dom-if" if="[[progress]]">
        <div class="progress">
          <paper-spinner active=""></paper-spinner>
        </div>
      </template>
    </div>
`}static get properties(){return{hass:{type:Object},progress:{type:Boolean,value:!1},disabled:{type:Boolean,value:!1}}}tempClass(e){var t=this.$.container.classList;t.add(e),setTimeout(()=>{t.remove(e)},1e3)}ready(){super.ready(),this.addEventListener("click",e=>this.buttonTapped(e))}buttonTapped(e){this.progress&&e.stopPropagation()}actionSuccess(){this.tempClass("success")}actionError(){this.tempClass("error")}computeDisabled(e,t){return e||t}})},595:function(e,t,i){"use strict";i.r(t);var s=i(0),a=i(2);i(61),i(162),i(158),i(147),i(146),i(104),i(89),i(59),i(134),i(160);var r=i(11),n=i(67),o=(i(149),i(159),i(76),i(70)),c=i(101),l=i(85),h=(i(25),i(136)),d=i(60),p=i(33);function u(e){if(!e||!Array.isArray(e))throw new Error("Entities need to be an array");return e.map((e,i)=>{if("string"==typeof e)e={entity:e};else{if("object"!=typeof e||Array.isArray(e))throw new Error(`Invalid entity specified at position ${i}.`);if(!e.entity)throw new Error(`Entity object at position ${i} is missing entity field.`)}if(t=e.entity,!/^(\w+)\.(\w+)$/.test(t))throw new Error(`Invalid entity ID at position ${i}: ${e.entity}`);return e});var t}i(88),i(152);var g=i(95);customElements.define("hui-entities-toggle",class extends a.a{static get template(){return s["a"]`
    <style>
      :host {
        width: 38px;
        display: block;
      }
      paper-toggle-button {
        cursor: pointer;
        --paper-toggle-button-label-spacing: 0;
        padding: 13px 5px;
        margin: -4px -5px;
      }
    </style>
    <template is="dom-if" if="[[_toggleEntities.length]]">
      <paper-toggle-button checked="[[_computeIsChecked(hass, _toggleEntities)]]" on-change="_callService"></paper-toggle-button>
    </template>
`}static get properties(){return{hass:Object,entities:Array,_toggleEntities:{type:Array,computed:"_computeToggleEntities(hass, entities)"}}}_computeToggleEntities(e,t){return t.filter(t=>t in e.states&&Object(g.a)(e,e.states[t]))}_computeIsChecked(e,t){return t.some(t=>!p.g.includes(e.states[t].state))}_callService(e){const t=e.target.checked;!function(e,t,i=!0){const s={};t.forEach(t=>{if(p.g.includes(e.states[t].state)===i){const e=Object(d.a)(t),i=["cover","lock"].includes(e)?e:"homeassistant";i in s||(s[i]=[]),s[i].push(t)}}),Object.keys(s).forEach(t=>{let a;switch(t){case"lock":a=i?"unlock":"lock";break;case"cover":a=i?"open_cover":"close_cover";break;default:a=i?"turn_on":"turn_off"}const r=s[t];e.callService(t,a,{entity_id:r})})}(this.hass,this._toggleEntities,t)}}),i(155),customElements.define("hui-entities-card",class extends(Object(r.a)(a.a)){static get template(){return s["a"]`
    <style>
      ha-card {
        padding: 16px;
      }
      #states {
        margin: -4px 0;
      }
      #states > div {
        margin: 4px 0;
      }
      .header {
        @apply --paper-font-headline;
        /* overwriting line-height +8 because entity-toggle can be 40px height,
           compensating this with reduced padding */
        line-height: 40px;
        color: var(--primary-text-color);
        padding: 4px 0 12px;
        display: flex;
        justify-content: space-between;
      }
      .header .name {
        @apply --paper-font-common-nowrap;
      }
      .state-card-dialog {
        cursor: pointer;
      }
    </style>

    <ha-card>
      <template is='dom-if' if='[[_showHeader(_config)]]'>
        <div class='header'>
          <div class="name">[[_config.title]]</div>
          <template is="dom-if" if="[[_showHeaderToggle(_config.show_header_toggle)]]">
            <hui-entities-toggle hass="[[hass]]" entities="[[_config.entities]]"></hui-entities-toggle>
          </template>
        </div>
      </template>
      <div id="states"></div>
    </ha-card>
`}static get properties(){return{hass:{type:Object,observer:"_hassChanged"},_config:Object}}constructor(){super(),this._elements=[]}ready(){super.ready(),this._config&&this._buildConfig()}getCardSize(){return 1+(this._config?this._config.entities.length:0)}_showHeaderToggle(e){return!1!==e}_showHeader(e){return e.title||e.show_header_toggle}setConfig(e){this._config=e,this._configEntities=u(e.entities),this.$&&this._buildConfig()}_buildConfig(){const e=this.$.states,t=this._configEntities;for(;e.lastChild;)e.removeChild(e.lastChild);this._elements=[];for(let i=0;i<t.length;i++){const s=t[i],a=s.entity;if(!(a in this.hass.states))continue;const r=this.hass.states[a],n=r?`state-card-${Object(h.a)(this.hass,r)}`:"state-card-display",o=document.createElement(n);p.c.includes(Object(d.a)(a))||(o.classList.add("state-card-dialog"),o.addEventListener("click",()=>this.fire("hass-more-info",{entityId:a}))),o.stateObj=r,o.hass=this.hass,s.name&&(o.overrideName=s.name),this._elements.push({entityId:a,element:o});const c=document.createElement("div");c.appendChild(o),e.appendChild(c)}}_hassChanged(e){for(let t=0;t<this._elements.length;t++){const{entityId:i,element:s}=this._elements[t],a=e.states[i];s.stateObj=a,s.hass=e}}}),customElements.define("hui-entity-filter-card",class extends a.a{static get properties(){return{hass:{type:Object,observer:"_hassChanged"}}}getCardSize(){return this.lastChild?this.lastChild.getCardSize():1}setConfig(e){if(!e.state_filter||!Array.isArray(e.state_filter))throw new Error("Incorrect filter config.");this._config=e,this._configEntities=u(e.entities),this.lastChild&&this.removeChild(this.lastChild);const t="card"in e?Object.assign({},e.card):{};t.type||(t.type="entities"),t.entities=[];const i=S(t);i._filterRawConfig=t,this._updateCardConfig(i),i.hass=this.hass,this.appendChild(i)}_hassChanged(e){const t=this.lastChild;this._updateCardConfig(t),t.hass=e}_updateCardConfig(e){if(!e||"HUI-ERROR-CARD"===e.tagName||!this.hass)return;const t=(i=this.hass,s=this._config.state_filter,this._configEntities.filter(e=>{const t=i.states[e.entity];return t&&s.includes(t.state)}));var i,s;0!==t.length||!1!==this._config.show_empty?(this.style.display="block",e.setConfig(Object.assign({},e._filterRawConfig,{entities:t}))):this.style.display="none"}}),customElements.define("hui-error-card",class extends a.a{static get template(){return s["a"]`
      <style>
        :host {
          display: block;
          background-color: red;
          color: white;
          padding: 8px;
        }
      </style>
      [[_config.error]]
      <pre>[[_toStr(_config.origConfig)]]</pre>
    `}static get properties(){return{_config:Object}}setConfig(e){this._config=e}getCardSize(){return 4}_toStr(e){return JSON.stringify(e,null,2)}});var m=i(92),f=i(16),_=(i(107),i(12));function b(e){return"function"==typeof e.getCardSize?e.getCardSize():1}function y(e,t){return{type:"error",error:e,origConfig:t}}customElements.define("hui-glance-card",class extends(Object(_.a)(Object(r.a)(a.a))){static get template(){return s["a"]`
      <style>
        ha-card {
          padding: 16px;
        }
        ha-card[header] {
          padding-top: 0;
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
          align-items: center;
          cursor: pointer;
          margin-bottom: 12px;
          width: 20%;
        }
        .entity div {
          width: 100%;
          text-align: center;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
      </style>

      <ha-card header$="[[_config.title]]">
        <div class="entities">
          <template is="dom-repeat" items="[[_configEntities]]">
            <template is="dom-if" if="[[_showEntity(item, hass.states)]]">
              <div class="entity" on-click="_openDialog">
                <div>[[_computeName(item, hass.states)]]</div>
                <state-badge state-obj="[[_computeStateObj(item, hass.states)]]"></state-badge>
                <div>[[_computeState(item, hass.states)]]</div>
              </div>
            </template>
          </template>
        </div>
      </ha-card>
    `}static get properties(){return{hass:Object,_config:Object,_configEntities:Array}}getCardSize(){return 3}setConfig(e){this._config=e,this._configEntities=u(e.entities)}_showEntity(e,t){return e.entity in t}_computeName(e,t){return e.name||Object(f.a)(t[e.entity])}_computeStateObj(e,t){return t[e.entity]}_computeState(e,t){return Object(m.a)(this.localize,t[e.entity])}_openDialog(e){this.fire("hass-more-info",{entityId:e.model.item.entity})}}),i(154),i(156),customElements.define("hui-history-graph-card",class extends a.a{static get template(){return s["a"]`
      <style>
        ha-card {
          padding: 16px;
        }
        ha-card[header] {
          padding-top: 0;
        }
      </style>

      <ha-card header$='[[_config.title]]'>
        <ha-state-history-data
          hass="[[hass]]"
          filter-type="recent-entity"
          entity-id="[[_config.entities]]"
          data="{{stateHistory}}"
          is-loading="{{stateHistoryLoading}}"
          cache-config="[[_computeCacheConfig(_config)]]"
        ></ha-state-history-data>
        <state-history-charts
          hass="[[hass]]"
          history-data="[[stateHistory]]"
          is-loading-data="[[stateHistoryLoading]]"
          up-to-now
          no-single
        ></state-history-charts>
      </ha-card>
    `}static get properties(){return{hass:Object,_config:Object,stateHistory:Object,stateHistoryLoading:Boolean}}getCardSize(){return 4}setConfig(e){if(!e.entities||!Array.isArray(e.entities))throw new Error("Error in card configuration.");this._config=e}_computeCacheConfig(e){return{cacheKey:e.entities,hoursToShow:e.hours_to_show||24,refresh:e.refresh_interval||0}}}),customElements.define("hui-horizontal-stack-card",class extends a.a{static get template(){return s["a"]`
      <style>
        #root {
          display: flex;
        }
        #root > * {
          flex: 1 1 0;
          margin: 0 4px;
        }
        #root > *:first-child {
          margin-left: 0;
        }
        #root > *:last-child {
          margin-right: 0;
        }
      </style>
      <div id="root"></div>
    `}static get properties(){return{hass:{type:Object,observer:"_hassChanged"}}}constructor(){super(),this._elements=[]}ready(){super.ready(),this._config&&this._buildConfig()}getCardSize(){let e=1;return this._elements.forEach(t=>{const i=b(t);i>e&&(e=i)}),e}setConfig(e){if(!e||!e.cards||!Array.isArray(e.cards))throw new Error("Card config incorrect.");this._config=e,this.$&&this._buildConfig()}_buildConfig(){const e=this._config;this._elements=[];const t=this.$.root;for(;t.lastChild;)t.removeChild(t.lastChild);const i=[];e.cards.forEach(e=>{const s=S(e);s.hass=this.hass,i.push(s),t.appendChild(s)}),this._elements=i}_hassChanged(e){this._elements.forEach(t=>{t.hass=e})}}),customElements.define("hui-iframe-card",class extends a.a{static get template(){return s["a"]`
      <style>
        ha-card {
          line-height: 0;
          overflow: hidden;
        }
        #root {
          width: 100%;
          position: relative;
        }
        iframe {
          border: none;
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
        }
      </style>
      <ha-card header="[[_config.title]]">
        <div id="root">
          <iframe src="[[_config.url]]"></iframe>
        </div>
      </ha-card>
    `}static get properties(){return{_config:Object}}ready(){super.ready(),this._config&&this._buildConfig()}setConfig(e){this._config=e,this.$&&this._buildConfig()}_buildConfig(){const e=this._config;this.$.root.style.paddingTop=e.aspect_ratio||"50%"}getCardSize(){return 1+this.offsetHeight/50}}),i(151),customElements.define("hui-markdown-card",class extends a.a{static get template(){return s["a"]`
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
        ha-markdown > *:first-child {
          margin-top: 0;
        }
        ha-markdown > *:last-child {
          margin-bottom: 0;
        }
        ha-markdown a {
          color: var(--primary-color);
        }
        ha-markdown img {
          max-width: 100%;
        }
      </style>
      <ha-card header="[[_config.title]]">
        <ha-markdown content='[[_config.content]]'></ha-markdown>
      </ha-card>
    `}static get properties(){return{_config:Object,noTitle:{type:Boolean,reflectToAttribute:!0,computed:"_computeNoTitle(_config.title)"}}}setConfig(e){this._config=e}getCardSize(){return this._config.content.split("\n").length}_computeNoTitle(e){return!e}}),i(164);class v extends HTMLElement{constructor(e,t){super(),this._tag=e.toUpperCase(),this._domain=t,this._element=null}getCardSize(){return 3}setConfig(e){if(!e.entity)throw new Error("No entity specified");if(Object(d.a)(e.entity)!==this._domain)throw new Error(`Specified entity needs to be of domain ${this._domain}.`);this._config=e}set hass(e){const t=this._config.entity;t in e.states?(this._ensureElement(this._tag),this.lastChild.hass=e,this.lastChild.stateObj=e.states[t]):(this._ensureElement("HUI-ERROR-CARD"),this.lastChild.setConfig(y(`No state available for ${t}`,this._config)))}_ensureElement(e){this.lastChild&&this.lastChild.tagName===e||(this.lastChild&&this.removeChild(this.lastChild),this.appendChild(document.createElement(e)))}}function w(e,t){!function(e,t,i=!0){const s=Object(d.a)(t),a="group"===s?"homeassistant":s;let r;switch(s){case"lock":r=i?"unlock":"lock";break;case"cover":r=i?"open_cover":"close_cover";break;default:r=i?"turn_on":"turn_off"}e.callService(a,r,{entity_id:t})}(e,t,p.g.includes(e.states[t].state))}customElements.define("hui-media-control-card",class extends v{constructor(){super("ha-media_player-card","media_player")}}),customElements.define("hui-picture-card",class extends(Object(n.a)(a.a)){static get template(){return s["a"]`
      <style>
        ha-card {
          overflow: hidden;
        }
        ha-card[clickable] {
          cursor: pointer;
        }
        img {
          display: block;
          width: 100%;
        }
      </style>

      <ha-card on-click="_cardClicked" clickable$='[[_computeClickable(_config)]]'>
        <img src='[[_config.image]]' />
      </ha-card>
    `}static get properties(){return{hass:Object,_config:Object}}getCardSize(){return 3}setConfig(e){if(!e||!e.image)throw new Error("Error in card configuration.");this._config=e}_computeClickable(e){return e.navigation_path||e.service}_cardClicked(){if(this._config.navigation_path&&this.navigate(this._config.navigation_path),this._config.service){const[e,t]=this._config.service.split(".",2);this.hass.callService(e,t,this._config.service_data)}}}),i(198),i(169);const C=new Set(["navigation","service-button","state-badge","state-icon","state-label"]);customElements.define("hui-picture-elements-card",class extends(Object(n.a)(Object(r.a)(Object(_.a)(a.a)))){static get template(){return s["a"]`
    <style>
      ha-card {
        overflow: hidden;
      }
      #root {
        position: relative;
        overflow: hidden;
      }
      #root img {
        display: block;
        width: 100%;
      }
      .element {
        position: absolute;
        transform: translate(-50%, -50%);
      }
      .state-label {
        padding: 8px;
        white-space: nowrap;
      }
      .clickable {
        cursor: pointer;
      }
      ha-call-service-button {
        color: var(--primary-color);
        white-space: nowrap;
      }
    </style>

    <ha-card header="[[_config.title]]">
      <div id="root"></div>
    </ha-card>
`}static get properties(){return{hass:{type:Object,observer:"_hassChanged"},_config:Object}}constructor(){super(),this._stateBadges=[],this._stateIcons=[],this._stateLabels=[]}ready(){super.ready(),this._config&&this._buildConfig()}getCardSize(){return 4}setConfig(e){if(!e||!e.image||!Array.isArray(e.elements))throw new Error("Invalid card configuration");const t=e.elements.map(e=>e.type).filter(e=>!C.has(e));if(t.length)throw new Error(`Incorrect element types: ${t.join(", ")}`);this._config=e,this.$&&this._buildConfig()}_buildConfig(){const e=this._config,t=this.$.root;for(this._stateBadges=[],this._stateIcons=[],this._stateLabels=[];t.lastChild;)t.removeChild(t.lastChild);const i=document.createElement("img");i.src=e.image,t.appendChild(i),e.elements.forEach(e=>{const i=e.entity;let s;switch(e.type){case"service-button":s=document.createElement("ha-call-service-button"),[s.domain,s.service]=e.service.split(".",2),s.serviceData=e.service_data||{},s.innerText=e.title,s.hass=this.hass;break;case"state-badge":(s=document.createElement("ha-state-label-badge")).state=this.hass.states[i],this._stateBadges.push({el:s,entityId:i});break;case"state-icon":(s=document.createElement("state-badge")).addEventListener("click",()=>this._handleClick(i,"toggle"===e.tap_action)),s.classList.add("clickable"),this._stateIcons.push({el:s,entityId:i});break;case"state-label":(s=document.createElement("div")).addEventListener("click",()=>this._handleClick(i,!1)),s.classList.add("clickable","state-label"),this._stateLabels.push({el:s,entityId:i});break;case"navigation":(s=document.createElement("ha-icon")).icon=e.icon||"hass:image-filter-center-focus",s.addEventListener("click",()=>this.navigate(e.navigation_path)),s.title=e.navigation_path,s.classList.add("clickable")}s.classList.add("element"),Object.keys(e.style).forEach(t=>{s.style.setProperty(t,e.style[t])}),t.appendChild(s)}),this.hass&&this._hassChanged(this.hass)}_hassChanged(e){this._stateBadges.forEach(t=>{const{el:i,entityId:s}=t;i.state=e.states[s],i.hass=e}),this._stateIcons.forEach(t=>{const{el:i,entityId:s}=t,a=e.states[s];a&&(i.stateObj=a,i.title=this._computeTooltip(a))}),this._stateLabels.forEach(t=>{const{el:i,entityId:s}=t,a=e.states[s];a?(i.innerText=Object(m.a)(this.localize,a),i.title=this._computeTooltip(a)):(i.innerText="N/A",i.title="")})}_computeTooltip(e){return`${Object(f.a)(e)}: ${Object(m.a)(this.localize,e)}`}_handleClick(e,t){t?w(this.hass,e):this.fire("hass-more-info",{entityId:e})}});customElements.define("hui-image",class extends(Object(_.a)(a.a)){static get template(){return s["a"]`
      <style>
        .state-off {
          filter: grayscale(100%);
        } 
        
        img {
          display: block;
          height: auto;
          transition: filter .2s linear;
          width: 100%;
        }
        
        .error {
          width: 100%;
          height: auto;
          text-align: center;
        }
        
      </style>
      
      <template is="dom-if" if="[[_imageSrc]]">
        <img 
          src="[[_imageSrc]]" 
          on-error="_onImageError" 
          on-load="_onImageLoad" 
          class$="[[_imageClass]]" />
      </template>
      <template is="dom-if" if="[[_error]]">
        <div class="error">[[localize('ui.card.camera.not_available')]]</div>
      </template>
`}static get properties(){return{hass:{type:Object,observer:"_hassChanged"},entity:String,image:String,stateImage:Object,cameraImage:String,_error:{type:Boolean,value:!1},_imageClass:String,_imageSrc:String}}static get observers(){return["_configChanged(image, stateImage, cameraImage)"]}connectedCallback(){super.connectedCallback(),this.cameraImage&&(this.timer=setInterval(()=>this._updateCameraImageSrc(),1e4))}disconnectedCallback(){super.disconnectedCallback(),clearInterval(this.timer)}_configChanged(e,t,i){i?this._updateCameraImageSrc():e&&!t&&(this._imageSrc=e)}_onImageError(){this.setProperties({_imageSrc:null,_error:!0})}_onImageLoad(){this._error=!1}_hassChanged(e){if(this.cameraImage||!this.entity)return;const t=e.states[this.entity],i=!function(e,t=[]){return e&&"object"==typeof e&&!Array.isArray(e)&&t.every(t=>t in e)}(t,["state"]);if(!this.stateImage)return void(this._imageClass=i||p.g.includes(t.state)?"state-off":"");const s=i?this.stateImage.unavailable:this.stateImage[t.state];this.setProperties({_imageClass:s||!i&&!p.g.includes(t.state)?"":"state-off",_imageSrc:s||this.image})}_updateCameraImageSrc(){this.hass.connection.sendMessagePromise({type:"camera_thumbnail",entity_id:this.cameraImage}).then(e=>{e.success?this.setProperties({_imageSrc:`data:${e.result.content_type};base64, ${e.result.content}`,_error:!1}):this.setProperties({_imageSrc:null,_error:!0})})}});customElements.define("hui-picture-entity-card",class extends(Object(r.a)(Object(_.a)(a.a))){static get template(){return s["a"]`
      <style>
        ha-card {
          min-height: 75px;
          overflow: hidden;
          position: relative;
        }
        ha-card.canInteract {
          cursor: pointer;
        }
        .info {
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
          display: flex;
          justify-content: space-between;
        }
        #title {
          font-weight: 500;
        }
        [hidden] {
          display: none;
        }
      </style>

      <ha-card id='card' on-click="_cardClicked">
        <hui-image
          hass="[[hass]]"
          image="[[_config.image]]"
          state-image="[[_config.state_image]]"
          camera-image="[[_getCameraImage(_config)]]" 
          entity="[[_config.entity]]"
        ></hui-image>
        <div class="info" hidden$='[[_computeHideInfo(_config)]]'>
          <div id="name"></div>
          <div id="state"></div>
        </div>
      </ha-card>
    `}static get properties(){return{hass:{type:Object,observer:"_hassChanged"},_config:Object}}getCardSize(){return 3}setConfig(e){if(!e||!e.entity)throw new Error("Error in card configuration.");if(this._entityDomain=Object(d.a)(e.entity),"camera"!==this._entityDomain&&!e.image&&!e.state_image&&!e.camera_image)throw new Error("No image source configured.");this._config=e}_hassChanged(e){const t=this._config,i=t.entity,s=e.states[i];if(!s&&"Unavailable"===this._oldState||s&&s.state===this._oldState)return;let a,r,n,o=!0;s?(a=t.name||Object(f.a)(s),r=s.state,n=this._computeStateLabel(s)):(a=t.name||i,r="Unavailable",n="Unavailable",o=!1),this.$.name.innerText=a,this.$.state.innerText=n,this._oldState=r,this.$.card.classList.toggle("canInteract",o)}_computeStateLabel(e){switch(this._entityDomain){case"scene":return this.localize("ui.card.scene.activate");case"script":return this.localize("ui.card.script.execute");case"weblink":return"Open";default:return Object(m.a)(this.localize,e)}}_computeHideInfo(e){return!1===e.show_info}_cardClicked(){const e=this._config&&this._config.entity;e&&e in this.hass.states&&("toggle"===this._config.tap_action?"weblink"===this._entityDomain?window.open(this.hass.states[e].state):w(this.hass,e):this.fire("hass-more-info",{entityId:e}))}_getCameraImage(e){return"camera"===this._entityDomain?e.entity:e.camera_image}});var x=i(98);customElements.define("hui-picture-glance-card",class extends(Object(n.a)(Object(_.a)(Object(r.a)(a.a)))){static get template(){return s["a"]`
      <style>
        ha-card {
          position: relative;
          min-height: 48px;
          overflow: hidden;
        }
        hui-image.clickable {
          cursor: pointer;
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
      </style>

      <ha-card>
        <hui-image
          class$='[[_computeImageClass(_config)]]'
          on-click='_handleImageClick'
          hass="[[hass]]"
          image="[[_config.image]]"
          state-image="[[_config.state_image]]"
          camera-image="[[_config.camera_image]]"
          entity="[[_config.entity]]"
        ></hui-image>
        <div class="box">
          <div class="title">[[_config.title]]</div>
          <div>
            <template is="dom-repeat" items="[[_entitiesDialog]]">
              <template is="dom-if" if="[[_showEntity(item, hass.states)]]">
                <paper-icon-button
                  on-click="_openDialog"
                  class$="[[_computeButtonClass(item, hass.states)]]"
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
                  class$="[[_computeButtonClass(item, hass.states)]]"
                  icon="[[_computeIcon(item, hass.states)]]"
                  title="[[_computeTooltip(item, hass.states)]]"
                ></paper-icon-button>
              </template>
            </template>
          </div>
        </div>
      </ha-card>
    `}static get properties(){return{hass:Object,_config:Object,_entitiesDialog:{type:Array,computed:"_computeEntitiesDialog(hass, _config, _entitiesService)"},_entitiesService:{type:Array,value:[],computed:"_computeEntitiesService(hass, _config)"}}}getCardSize(){return 3}setConfig(e){if(!e||!e.entities||!Array.isArray(e.entities)||!(e.image||e.camera_image||e.state_image)||e.state_image&&!e.entity)throw new Error("Invalid card configuration");this._config=e}_computeEntitiesDialog(e,t,i){return t.force_dialog?t.entities:t.entities.filter(e=>!i.includes(e))}_computeEntitiesService(e,t){return t.force_dialog?[]:t.entities.filter(e=>Object(g.a)(this.hass,this.hass.states[e]))}_showEntity(e,t){return e in t}_computeIcon(e,t){return Object(x.a)(t[e])}_computeButtonClass(e,t){return p.g.includes(t[e].state)?"":"state-on"}_computeTooltip(e,t){return`${Object(f.a)(t[e])}: ${Object(m.a)(this.localize,t[e])}`}_computeImageClass(e){return e.navigation_path?"clickable":""}_openDialog(e){this.fire("hass-more-info",{entityId:e.model.item})}_callService(e){const t=e.model.item;w(this.hass,t)}_handleImageClick(){this._config.navigation_path&&this.navigate(this._config.navigation_path)}}),i(163),customElements.define("hui-plant-status-card",class extends v{constructor(){super("ha-plant-card","plant")}}),customElements.define("hui-vertical-stack-card",class extends a.a{static get template(){return s["a"]`
      <style>
        #root {
          display: flex;
          flex-direction: column;
        }
        #root > * {
          margin: 4px 0 8px 0;
        }
        #root > *:first-child {
          margin-top: 0;
        }
        #root > *:last-child {
          margin-bottom: 0;
        }
      </style>
      <div id="root"></div>
    `}static get properties(){return{hass:{type:Object,observer:"_hassChanged"}}}constructor(){super(),this._elements=[]}ready(){super.ready(),this._config&&this._buildConfig()}getCardSize(){let e=0;return this._elements.forEach(t=>{e+=b(t)}),e}setConfig(e){if(!e||!e.cards||!Array.isArray(e.cards))throw new Error("Card config incorrect");this._config=e,this.$&&this._buildConfig()}_buildConfig(){const e=this._config;this._elements=[];const t=this.$.root;for(;t.lastChild;)t.removeChild(t.lastChild);const i=[];e.cards.forEach(e=>{const s=S(e);s.hass=this.hass,i.push(s),t.appendChild(s)}),this._elements=i}_hassChanged(e){this._elements.forEach(t=>{t.hass=e})}}),i(168),customElements.define("hui-weather-forecast-card",class extends v{constructor(){super("ha-weather-card","weather")}getCardSize(){return 4}});const E=["entities","entity-filter","error","glance","history-graph","horizontal-stack","iframe","markdown","media-control","picture","picture-elements","picture-entity","picture-glance","plant-status","vertical-stack","weather-forecast"],k="custom:";function j(e,t){const i=document.createElement(e);try{i.setConfig(t)}catch(i){return console.error(e,i),O(i.message,t)}return i}function O(e,t){return j("hui-error-card",y(e,t))}function S(e){let t;if(!e||"object"!=typeof e||!e.type)return O("No card type configured.",e);if(e.type.startsWith(k)){if(t=e.type.substr(k.length),customElements.get(t))return j(t,e);const i=O(`Custom element doesn't exist: ${t}.`,e);return customElements.whenDefined(t).then(()=>Object(l.a)(i,"rebuild-view")),i}return E.includes(e.type)?j(`hui-${e.type}-card`,e):O(`Unknown card type encountered: ${e.type}.`,e)}customElements.define("hui-view",class extends a.a{static get template(){return s["a"]`
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
      <div id='columns' on-rebuild-view='_debouncedConfigChanged'></div>
    `}static get properties(){return{hass:{type:Object,observer:"_hassChanged"},columns:{type:Number},config:{type:Object}}}static get observers(){return["_configChanged(columns, config)"]}constructor(){super(),this._elements=[],this._debouncedConfigChanged=function(e,t,i){let s;return function(...t){const i=this;clearTimeout(s),s=setTimeout(()=>{s=null,e.apply(i,t)},100)}}(this._configChanged)}_configChanged(){const e=this.$.columns,t=this.config;for(;e.lastChild;)e.removeChild(e.lastChild);if(!t)return void(this._elements=[]);const i=t.cards.map(e=>{const t=S(e);return t.hass=this.hass,t});let s=[];const a=[];for(let e=0;e<this.columns;e++)s.push([]),a.push(0);i.forEach(e=>{this.appendChild(e);const t="function"==typeof e.getCardSize?e.getCardSize():1;s[function(e){let t=0;for(let e=0;e<a.length;e++){if(a[e]<5){t=e;break}a[e]<a[t]&&(t=e)}return a[t]+=e,t}(t)].push(e)}),(s=s.filter(e=>e.length>0)).forEach(t=>{const i=document.createElement("div");i.classList.add("column"),t.forEach(e=>i.appendChild(e)),e.appendChild(i)}),this._elements=i,"theme"in t&&Object(c.a)(e,this.hass.themes,t.theme)}_hassChanged(e){for(let t=0;t<this._elements.length;t++)this._elements[t].hass=e}});const I={};customElements.define("hui-root",class extends(Object(n.a)(Object(r.a)(a.a))){static get template(){return s["a"]`
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
    <app-route route="[[route]]" pattern="/:view" data="{{routeData}}"></app-route>
    <ha-app-layout id="layout">
      <app-header slot="header" fixed>
        <app-toolbar>
          <ha-menu-button narrow='[[narrow]]' show-menu='[[showMenu]]'></ha-menu-button>
          <div main-title>[[_computeTitle(config)]]</div>
          <a href='https://developers.home-assistant.io/docs/en/lovelace_index.html' tabindex='-1' target='_blank'>
            <paper-icon-button icon='hass:help-circle-outline'></paper-icon-button>
          </a>
          <paper-icon-button icon='hass:refresh' on-click='_handleRefresh'></paper-icon-button>
          <ha-start-voice-button hass="[[hass]]"></ha-start-voice-button>
        </app-toolbar>

        <div sticky hidden$="[[_computeTabsHidden(config.views)]]">
          <paper-tabs scrollable selected="[[_curView]]" on-iron-activate="_handleViewSelected">
            <template is="dom-repeat" items="[[config.views]]">
              <paper-tab>
                <template is="dom-if" if="[[item.icon]]">
                  <ha-icon title$="[[item.title]]" icon="[[item.icon]]"></ha-icon>
                </template>
                <template is="dom-if" if="[[!item.icon]]">
                  [[_computeTabTitle(item.title)]]
                </template>
              </paper-tab>
            </template>
          </paper-tabs>
        </div>
      </app-header>

      <span id='view'></span>
    </app-header-layout>
    `}static get properties(){return{narrow:Boolean,showMenu:Boolean,hass:{type:Object,observer:"_hassChanged"},config:{type:Object,observer:"_configChanged"},columns:{type:Number,observer:"_columnsChanged"},_curView:{type:Number,value:0},route:{type:Object,observer:"_routeChanged"},routeData:Object}}_routeChanged(e){const t=this.config&&this.config.views;if(""===e.path&&"/lovelace"===e.prefix&&t)this.navigate(`/lovelace/${t[0].id||0}`,!0);else if(this.routeData.view){const e=this.routeData.view;let i=0;for(let s=0;s<t.length;s++)if(t[s].id===e||s===parseInt(e)){i=s;break}i!==this._curView&&this._selectView(i)}}_computeViewId(e,t){return e||t}_computeTitle(e){return e.title||"Home Assistant"}_computeTabsHidden(e){return e.length<2}_computeTabTitle(e){return e||"Unnamed view"}_handleRefresh(){this.fire("config-refresh")}_handleViewSelected(e){const t=e.detail.selected;if(t!==this._curView){const e=this.config.views[t].id||t;this.navigate(`/lovelace/${e}`)}var i,s,a,r,n,o,c;i=this,s=this.$.layout.header.scrollTarget,a=s,r=Math.random(),n=Date.now(),o=a.scrollTop,c=0-o,i._currentAnimationId=r,function e(){var t,s=Date.now()-n;s>200?a.scrollTop=0:i._currentAnimationId===r&&(a.scrollTop=(t=s,-c*(t/=200)*(t-2)+o),requestAnimationFrame(e.bind(i)))}.call(i)}_selectView(e){this._curView=e;const t=this.$.view;t.lastChild&&t.removeChild(t.lastChild);const i=this.config.views[this._curView];let s;i.panel?s=S(i.cards[0]):((s=document.createElement("hui-view")).config=i,s.columns=this.columns),s.hass=this.hass,t.appendChild(s)}_hassChanged(e){this.$.view.lastChild&&(this.$.view.lastChild.hass=e)}_configChanged(e){this._loadResources(e.resources||[]),this._selectView(this._curView)}_columnsChanged(e){this.$.view.lastChild&&(this.$.view.lastChild.columns=e)}_loadResources(e){e.forEach(e=>{switch(e.type){case"js":if(e.url in I)break;I[e.url]=Object(o.a)(e.url);break;case"module":Object(o.b)(e.url);break;case"html":Promise.resolve().then(i.bind(null,258)).then(({importHref:t})=>t(e.url));break;default:console.warn("Unknown resource type specified: ${resource.type}")}})}}),customElements.define("ha-panel-lovelace",class extends a.a{static get template(){return s["a"]`
      <style>
        paper-button {
          color: var(--primary-color);
          font-weight: 500;
        }
      </style>
      <template is='dom-if' if='[[_equal(_state, "loaded")]]' restamp>
        <hui-root
          narrow="[[narrow]]"
          show-menu="[[showMenu]]"
          hass='[[hass]]'
          route="[[route]]"
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
        >
          <paper-button on-click="_fetchConfig">Reload ui-lovelace.yaml</paper-button>
        </hass-error-screen>
      </template>
    `}static get properties(){return{hass:Object,narrow:{type:Boolean,value:!1},showMenu:{type:Boolean,value:!1},route:Object,_columns:{type:Number,value:1},_state:{type:String,value:"loading"},_errorMsg:String,_config:{type:Object,value:null}}}static get observers(){return["_updateColumns(narrow, showMenu)"]}ready(){this._fetchConfig(),this._updateColumns=this._updateColumns.bind(this),this.mqls=[300,600,900,1200].map(e=>{const t=matchMedia(`(min-width: ${e}px)`);return t.addListener(this._updateColumns),t}),this._updateColumns(),super.ready()}_updateColumns(){const e=this.mqls.reduce((e,t)=>e+t.matches,0);this._columns=Math.max(1,e-(!this.narrow&&this.showMenu))}_fetchConfig(){this.hass.connection.sendMessagePromise({type:"frontend/lovelace_config"}).then(e=>this.setProperties({_config:e.result,_state:"loaded"}),e=>this.setProperties({_state:"error",_errorMsg:e.message}))}_equal(e,t){return e===t}})},70:function(e,t,i){"use strict";function s(e,t,i){return new Promise(function(s,a){const r=document.createElement(e);let n="src",o="body";switch(r.onload=(()=>s(t)),r.onerror=(()=>a(t)),e){case"script":r.async=!0,i&&(r.type=i);break;case"link":r.type="text/css",r.rel="stylesheet",n="href",o="head"}r[n]=t,document[o].appendChild(r)})}i.d(t,"a",function(){return a}),i.d(t,"b",function(){return r});const a=e=>s("script",e),r=e=>s("script",e,"module")}}]);
//# sourceMappingURL=6c272362834790742af2.chunk.js.map