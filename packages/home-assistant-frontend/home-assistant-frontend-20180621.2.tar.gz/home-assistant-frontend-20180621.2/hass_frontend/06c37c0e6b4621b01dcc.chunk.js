(window.webpackJsonp=window.webpackJsonp||[]).push([[17],{598:function(e,a,l){"use strict";l.r(a),l(103);var t=l(0),o=l(2);l(122),l(141),customElements.define("ha-panel-iframe",class extends o.a{static get template(){return t["a"]`
    <style include='ha-style'>
      iframe {
        border: 0;
        width: 100%;
        height: calc(100% - 64px);
      }
    </style>
    <app-toolbar>
      <ha-menu-button narrow='[[narrow]]' show-menu='[[showMenu]]'></ha-menu-button>
      <div main-title>[[panel.title]]</div>
    </app-toolbar>

    <iframe
      src='[[panel.config.url]]'
      sandbox="allow-forms allow-popups allow-pointer-lock allow-same-origin allow-scripts"
      allowfullscreen="true" webkitallowfullscreen="true" mozallowfullscreen="true"
    ></iframe>
    `}static get properties(){return{panel:{type:Object},narrow:{type:Boolean},showMenu:{type:Boolean}}}})}}]);
//# sourceMappingURL=06c37c0e6b4621b01dcc.chunk.js.map