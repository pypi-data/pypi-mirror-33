(window.webpackJsonp=window.webpackJsonp||[]).push([[27],{129:function(e,t,n){"use strict";function s(e,t){"setProperties"in e?e.setProperties(t):Object.keys(t).forEach(n=>{e[n]=t[n]})}n.d(t,"a",function(){return s})},130:function(e,t,n){"use strict";function s(e){const t="html_url"in e?`ha-panel-${e.name}`:e.name;return document.createElement(t)}n.d(t,"a",function(){return s})},131:function(e,t,n){"use strict";n.d(t,"a",function(){return o});var s=n(82);const r={};function o(e){return"html_url"in e?Promise.all([Promise.all([n.e(9),n.e(38)]).then(n.bind(null,126)),n.e(37).then(n.bind(null,114))]).then(([{},{importHrefPromise:t}])=>t(e.html_url)):e.js_url?(e.js_url in r||(r[e.js_url]=Object(s.a)(e.js_url)),r[e.js_url]):Promise.reject("No valid url found in panel config.")}},597:function(e,t,n){"use strict";n.r(t);var s=n(3),r=n(11),o=n(68),a=n(131),i=n(130),c=n(129);customElements.define("ha-panel-custom",class extends(Object(o.a)(Object(r.a)(s.a))){static get properties(){return{hass:Object,narrow:Boolean,showMenu:Boolean,route:Object,panel:{type:Object,observer:"_panelChanged"}}}static get observers(){return["_dataChanged(hass, narrow, showMenu, route)"]}constructor(){super(),this._setProperties=null}_panelChanged(e){for(delete window.customPanel,this._setProperties=null;this.lastChild;)this.remove(this.lastChild);const t=e.config._panel_custom,n=document.createElement("a");if(n.href=t.html_url||t.js_url,!t.trust_external&&!["localhost","127.0.0.1",location.hostname].includes(n.hostname)&&!confirm(`Do you trust the external panel "${t.name}" at "${n.href}"?\n\nIt will have access to all data in Home Assistant.\n\n(Check docs for the panel_custom component to hide this message)`))return;if(!t.embed_iframe)return void Object(a.a)(t).then(()=>{const n=Object(i.a)(t);this._setProperties=(e=>Object(c.a)(n,e)),Object(c.a)(n,{panel:e,hass:this.hass,narrow:this.narrow,showMenu:this.showMenu,route:this.route}),this.appendChild(n)},()=>{alert(`Unable to load custom panel from ${n.href}`)});window.customPanel=this,this.innerHTML="\n    <style>\n      iframe {\n        border: 0;\n        width: 100%;\n        height: 100%;\n        display: block;\n      }\n    </style>\n    <iframe></iframe>\n    ";const s=this.querySelector("iframe").contentWindow.document;s.open(),s.write("<script src='/frontend_latest/custom-panel.js'><\/script>"),s.close()}disconnectedCallback(){super.disconnectedCallback(),delete window.customPanel}_dataChanged(e,t,n,s){this._setProperties&&this._setProperties({hass:e,narrow:t,showMenu:n,route:s})}registerIframe(e,t){e(this.panel,{hass:this.hass,narrow:this.narrow,showMenu:this.showMenu,route:this.route}),this._setProperties=t}})},82:function(e,t,n){"use strict";n.d(t,"a",function(){return s});const s=e=>(r="script",e=e,new Promise(function(t,n){const s=document.createElement(r);let o="src",a="body";switch(s.onload=(()=>t(e)),s.onerror=(()=>n(e)),r){case"script":s.async=!0;break;case"link":s.type="text/css",s.rel="stylesheet",o="href",a="head"}s[o]=e,document[a].appendChild(s)}));var r,o}}]);
//# sourceMappingURL=38a8c7fce5d876e79007.chunk.js.map