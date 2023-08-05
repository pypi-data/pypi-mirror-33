!function(e){var n={};function t(s){if(n[s])return n[s].exports;var o=n[s]={i:s,l:!1,exports:{}};return e[s].call(o.exports,o,o.exports,t),o.l=!0,o.exports}t.m=e,t.c=n,t.d=function(e,n,s){t.o(e,n)||Object.defineProperty(e,n,{configurable:!1,enumerable:!0,get:s})},t.r=function(e){Object.defineProperty(e,"__esModule",{value:!0})},t.n=function(e){var n=e&&e.__esModule?function(){return e.default}:function(){return e};return t.d(n,"a",n),n},t.o=function(e,n){return Object.prototype.hasOwnProperty.call(e,n)},t.p="/frontend_latest/",t(t.s=161)}({161:function(e,n,t){"use strict";t.r(n);var s=t(61);const o=window.createHassConnection=function(e,n){const t=`${"https:"===window.location.protocol?"wss":"ws"}://${window.location.host}/api/websocket?latest`,o={setupRetry:10};return e?o.authToken=e:n&&(o.accessToken=n),Object(s.c)(t,o).then(function(e){return Object(s.e)(e),Object(s.d)(e),e})};function r(){document.location=`/frontend_latest/authorize.html?response_type=code&client_id=${window.clientId}&redirect_uri=/`}window.refreshToken=(()=>(function(e,n){const t=new FormData;return t.append("grant_type","refresh_token"),t.append("refresh_token",n),fetch("/auth/token",{method:"POST",headers:{authorization:`Basic ${btoa(e)}`},body:t}).then(e=>{if(!e.ok)throw new Error("Unable to fetch tokens");return e.json()})})(window.clientId,window.tokens.refresh_token).then(e=>(window.tokens.access_token=e.access_token,localStorage.tokens=JSON.stringify(window.tokens),e.access_token),()=>r())),window.clientId?function(){if(location.search){const n=function(e){const n={},t=location.search.substr(1).split("&");for(let e=0;e<t.length;e++){const s=t[e].split("="),o=decodeURIComponent(s[0]),r=s.length>1?decodeURIComponent(s[1]):void 0;n[o]=r}return n}();if(n.code)return e=n.code,void function(e,n){const t=new FormData;return t.append("grant_type","authorization_code"),t.append("code",n),fetch("/auth/token",{method:"POST",headers:{authorization:`Basic ${btoa(e)}`},body:t}).then(e=>{if(!e.ok)throw new Error("Unable to fetch tokens");return e.json()})}(window.clientId,e).then(e=>{localStorage.tokens=JSON.stringify(e),document.location=location.pathname},e=>{console.error("Resolve token failed",e),alert("Unable to fetch tokens"),r()})}var e;if(localStorage.tokens)return window.tokens=JSON.parse(localStorage.tokens),void(window.hassConnection=o(null,window.tokens.access_token).catch(e=>{if(e!==s.b)throw e;return window.refreshToken().then(e=>o(null,e))}));r()}():"1"===window.noAuth?window.hassConnection=o():window.localStorage.authToken?window.hassConnection=o(window.localStorage.authToken):window.hassConnection=null,window.addEventListener("error",e=>{const n=document.querySelector("home-assistant");n&&n.hass&&n.hass.callService&&n.hass.callService("system_log","write",{logger:`frontend.js.latest.${"20180616.0".replace(".","")}`,message:`${e.filename}:${e.lineno}:${e.colno} ${e.message}`})})},61:function(e,n,t){"use strict";t.d(n,"a",function(){return s}),t.d(n,"b",function(){return o}),t.d(n,"c",function(){return l}),t.d(n,"d",function(){return f}),t.d(n,"e",function(){return h});var s=1,o=2,r="auth_required",i="auth_invalid",c="auth_ok";function a(e,n){function t(a,u,d){var l=new WebSocket(e),f=!1,h=function(){if(l.removeEventListener("close",h),f)d(o);else if(0!==a){var e=-1===a?-1:a-1;setTimeout(function(){return t(e,u,d)},1e3)}else d(s)},v=function(e){switch(JSON.parse(e.data).type){case r:n.authToken?l.send(JSON.stringify({type:"auth",api_password:n.authToken})):n.accessToken?l.send(JSON.stringify({type:"auth",access_token:n.accessToken})):(f=!0,l.close());break;case i:f=!0,l.close();break;case c:l.removeEventListener("message",v),l.removeEventListener("close",h),l.removeEventListener("error",h),u(l)}};l.addEventListener("message",v),l.addEventListener("close",h),l.addEventListener("error",h)}return new Promise(function(e,s){return t(n.setupRetry||0,e,s)})}function u(e){return e.result}var d=function(e,n){this.url=e,this.options=n||{},this.commandId=1,this.commands={},this.eventListeners={},this.closeRequested=!1,this._handleMessage=this._handleMessage.bind(this),this._handleClose=this._handleClose.bind(this)};function l(e,n){return void 0===n&&(n={}),a(e,n).then(function(t){var s=new d(e,n);return s.setSocket(t),s})}function f(e,n){return e._subscribeConfig?e._subscribeConfig(n):new Promise(function(t,s){var o=null,r=null,i=[],c=null;n&&i.push(n);var a=function(e){o=Object.assign({},o,e);for(var n=0;n<i.length;n++)i[n](o)},u=function(e,n){var t;return a({services:Object.assign({},o.services,(t={},t[e]=n,t))})},d=function(){return Promise.all([e.getConfig(),e.getPanels(),e.getServices()]).then(function(e){var n=e[0],t=e[1],s=e[2];a({core:n,panels:t,services:s})})},l=function(e){e&&i.splice(i.indexOf(e),1),0===i.length&&r()};e._subscribeConfig=function(e){return e&&(i.push(e),null!==o&&e(o)),c.then(function(){return function(){return l(e)}})},(c=Promise.all([e.subscribeEvents(function(e){if(null!==o){var n=Object.assign({},o.core,{components:o.core.components.concat(e.data.component)});a({core:n})}},"component_loaded"),e.subscribeEvents(function(e){var n;if(null!==o){var t=e.data,s=t.domain,r=t.service,i=Object.assign({},o.services[s]||{},((n={})[r]={description:"",fields:{}},n));u(s,i)}},"service_registered"),e.subscribeEvents(function(e){if(null!==o){var n=e.data,t=n.domain,s=n.service,r=o.services[t];if(r&&s in r){var i={};Object.keys(r).forEach(function(e){e!==s&&(i[e]=r[e])}),u(t,i)}}},"service_removed"),d()])).then(function(s){var o=s[0],i=s[1],c=s[2];r=function(){e.removeEventListener("ready",d),o(),i(),c()},e.addEventListener("ready",d),t(function(){return l(n)})},function(){return s()})})}function h(e,n){return e._subscribeEntities?e._subscribeEntities(n):new Promise(function(t,s){function o(){return e.getStates().then(function(e){i=function(e){for(var n,t={},s=0;s<e.length;s++)t[(n=e[s]).entity_id]=n;return t}(e);for(var n=0;n<a.length;n++)a[n](i)})}function r(n){n&&a.splice(a.indexOf(n),1),0===a.length&&(c(),e.removeEventListener("ready",o),e._subscribeEntities=null)}var i=null,c=null,a=[],u=null;n&&a.push(n),e._subscribeEntities=function(e){return e&&(a.push(e),null!==i&&e(i)),u.then(function(){return function(){return r(e)}})},(u=Promise.all([e.subscribeEvents(function(e){if(null!==i){var n=e.data,t=n.entity_id,s=n.new_state;i=s?function(e,n){var t=Object.assign({},e);return t[n.entity_id]=n,t}(i,s):function(e,n){var t=Object.assign({},e);return delete t[n],t}(i,t);for(var o=0;o<a.length;o++)a[o](i)}},"state_changed"),o()])).then(function(s){var i=s[0];c=i,e.addEventListener("ready",o),t(function(){return r(n)})},function(){return s()})})}d.prototype.setSocket=function(e){var n=this,t=this.socket;if(this.socket=e,e.addEventListener("message",this._handleMessage),e.addEventListener("close",this._handleClose),t){var s=this.commands;this.commandId=1,this.commands={},Object.keys(s).forEach(function(e){var t=s[e];t.eventType&&n.subscribeEvents(t.eventCallback,t.eventType).then(function(e){t.unsubscribe=e})}),this.fireEvent("ready")}},d.prototype.addEventListener=function(e,n){var t=this.eventListeners[e];t||(t=this.eventListeners[e]=[]),t.push(n)},d.prototype.removeEventListener=function(e,n){var t=this.eventListeners[e];if(t){var s=t.indexOf(n);-1!==s&&t.splice(s,1)}},d.prototype.fireEvent=function(e,n){var t=this;(this.eventListeners[e]||[]).forEach(function(e){return e(t,n)})},d.prototype.close=function(){this.closeRequested=!0,this.socket.close()},d.prototype.getStates=function(){return this.sendMessagePromise({type:"get_states"}).then(u)},d.prototype.getServices=function(){return this.sendMessagePromise({type:"get_services"}).then(u)},d.prototype.getPanels=function(){return this.sendMessagePromise({type:"get_panels"}).then(u)},d.prototype.getConfig=function(){return this.sendMessagePromise({type:"get_config"}).then(u)},d.prototype.callService=function(e,n,t){return this.sendMessagePromise(function(e,n,t){var s={type:"call_service",domain:e,service:n};return t&&(s.service_data=t),s}(e,n,t))},d.prototype.subscribeEvents=function(e,n){var t=this;return this.sendMessagePromise(function(e){var n={type:"subscribe_events"};return e&&(n.event_type=e),n}(n)).then(function(s){var o={eventCallback:e,eventType:n,unsubscribe:function(){return t.sendMessagePromise((e=s.id,{type:"unsubscribe_events",subscription:e})).then(function(){delete t.commands[s.id]});var e}};return t.commands[s.id]=o,function(){return o.unsubscribe()}})},d.prototype.ping=function(){return this.sendMessagePromise({type:"ping"})},d.prototype.sendMessage=function(e){this.socket.send(JSON.stringify(e))},d.prototype.sendMessagePromise=function(e){var n=this;return new Promise(function(t,s){n.commandId+=1;var o=n.commandId;e.id=o,n.commands[o]={resolve:t,reject:s},n.sendMessage(e)})},d.prototype._handleMessage=function(e){var n=JSON.parse(e.data);switch(n.type){case"event":this.commands[n.id].eventCallback(n.event);break;case"result":n.success?this.commands[n.id].resolve(n):this.commands[n.id].reject(n.error),delete this.commands[n.id]}},d.prototype._handleClose=function(){var e=this;if(Object.keys(this.commands).forEach(function(n){var t=e.commands[n].reject;t&&t({type:"result",success:!1,error:{code:3,message:"Connection lost"}})}),!this.closeRequested){this.fireEvent("disconnected");var n=Object.assign({},this.options,{setupRetry:0}),t=function(s){setTimeout(function(){a(e.url,n).then(function(n){return e.setSocket(n)},function(n){return n===o?e.fireEvent("reconnect-error",n):t(s+1)})},1e3*Math.min(s,5))};t(0)}}}});
//# sourceMappingURL=core.js.map