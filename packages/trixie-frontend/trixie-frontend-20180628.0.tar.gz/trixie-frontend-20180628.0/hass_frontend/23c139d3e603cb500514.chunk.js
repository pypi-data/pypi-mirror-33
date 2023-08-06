(window.webpackJsonp=window.webpackJsonp||[]).push([[19],{197:function(e,t,s){"use strict";var i=s(0),a=s(2),r=(s(205),s(11));customElements.define("ha-call-service-button",class extends(Object(r.a)(a.a)){static get template(){return i["a"]`
    <ha-progress-button id="progress" progress="[[progress]]" on-click="buttonTapped"><slot></slot></ha-progress-button>
`}static get properties(){return{hass:{type:Object},progress:{type:Boolean,value:!1},domain:{type:String},service:{type:String},serviceData:{type:Object,value:{}}}}buttonTapped(){this.progress=!0;var e=this,t={domain:this.domain,service:this.service,serviceData:this.serviceData};this.hass.callService(this.domain,this.service,this.serviceData).then(function(){e.progress=!1,e.$.progress.actionSuccess(),t.success=!0},function(){e.progress=!1,e.$.progress.actionError(),t.success=!1}).then(function(){e.fire("hass-service-called",t)})}})},205:function(e,t,s){"use strict";s(62),s(123);var i=s(0),a=s(2);customElements.define("ha-progress-button",class extends a.a{static get template(){return i["a"]`
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
`}static get properties(){return{hass:{type:Object},progress:{type:Boolean,value:!1},disabled:{type:Boolean,value:!1}}}tempClass(e){var t=this.$.container.classList;t.add(e),setTimeout(()=>{t.remove(e)},1e3)}ready(){super.ready(),this.addEventListener("click",e=>this.buttonTapped(e))}buttonTapped(e){this.progress&&e.stopPropagation()}actionSuccess(){this.tempClass("success")}actionError(){this.tempClass("error")}computeDisabled(e,t){return e||t}})},593:function(e,t,s){"use strict";s.r(t),s(145),s(144),s(103),s(60),s(127),s(155),s(50);var i=s(0),a=s(2);s(160),s(157),s(88);var r=s(11),n=s(68),o=(s(147),s(158),s(70)),c=s(100),l=s(84),h=s(61);function d(e){return"function"==typeof e.getCardSize?e.getCardSize():1}function p(e,t){return{type:"error",error:e,origConfig:t}}s(168),customElements.define("hui-error-card",class extends a.a{static get template(){return i["a"]`
      <style>
        :host {
          display: block;
          background-color: red;
          color: white;
          padding: 8px;
        }
      </style>
      [[config.error]]
      <pre>[[_toStr(config.origConfig)]]</pre>
    `}static get properties(){return{config:Object}}getCardSize(){return 4}_toStr(e){return JSON.stringify(e,null,2)}}),customElements.define("hui-camera-preview-card",class extends a.a{static get properties(){return{hass:{type:Object,observer:"_hassChanged"},config:{type:Object,observer:"_configChanged"}}}getCardSize(){return 4}_configChanged(e){this._entityId=null,this.lastChild&&this.removeChild(this.lastChild);const t=e&&e.entity;if(t&&!(t in this.hass.states))return;let s,i,a=null;t?"camera"===Object(h.a)(t)?(this._entityId=t,i="ha-camera-card",s=e):a='Entity domain must be "camera"':a="Entity not defined in card config",a&&(i="hui-error-card",s={error:a});const r=document.createElement(i);a||(r.stateObj=this.hass.states[t],r.hass=this.hass),r.config=s,this.appendChild(r)}_hassChanged(e){if(this.lastChild&&this._entityId&&this._entityId in e.states){const t=this.lastChild,s=e.states[this._entityId];t.stateObj=s,t.hass=e}else this._configChanged(this.config)}}),customElements.define("hui-column-card",class extends a.a{static get template(){return i["a"]`
      <style>
        #root {
          display: flex;
          flex-direction: column;
          margin-top: -4px
          margin-bottom: -8px;
        }
        #root > * {
          margin: 4px 0 8px 0;
        }
      </style>
      <div id="root"></div>
    `}static get properties(){return{hass:{type:Object,observer:"_hassChanged"},config:{type:Object,observer:"_configChanged"}}}constructor(){super(),this._elements=[]}getCardSize(){let e=0;return this._elements.forEach(t=>{e+=d(t)}),e}_configChanged(e){this._elements=[];const t=this.$.root;for(;t.lastChild;)t.removeChild(t.lastChild);if(!e||!e.cards||!Array.isArray(e.cards)){const s=k(p("Card config incorrect.",e));return void t.appendChild(s)}const s=[];e.cards.forEach(e=>{const i=k(e);i.hass=this.hass,s.push(i),t.appendChild(i)}),this._elements=s}_hassChanged(e){this._elements.forEach(t=>{t.hass=e})}}),s(25);var u=s(135),g=s(33),m=(s(87),s(150),s(94));customElements.define("hui-entities-toggle",class extends a.a{static get template(){return i["a"]`
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
`}static get properties(){return{hass:Object,entities:Array,_toggleEntities:{type:Array,computed:"_computeToggleEntities(hass, entities)"}}}_computeToggleEntities(e,t){return t.filter(t=>t in e.states&&Object(m.a)(e,e.states[t]))}_computeIsChecked(e,t){return t.some(t=>g.h.includes(e.states[t].state))}_callService(e){const t=e.target.checked,s={};this.entities.forEach(e=>{if(g.h.includes(this.hass.states[e].state)!==t){const t=Object(h.a)(e),i="lock"===t||"cover"===t?t:"homeassistant";i in s||(s[i]=[]),s[i].push(e)}}),Object.keys(s).forEach(e=>{let i;switch(e){case"lock":i=t?"unlock":"lock";break;case"cover":i=t?"open_cover":"close_cover";break;default:i=t?"turn_on":"turn_off"}const a=s[e];this.hass.callService(e,i,{entity_id:a})})}}),s(153),customElements.define("hui-entities-card",class extends(Object(r.a)(a.a)){static get template(){return i["a"]`
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
      <div class='header'>
        <div class="name">[[_computeTitle(config)]]</div>
        <template is="dom-if" if="[[_showHeaderToggle(config.show_header_toggle)]]">
          <hui-entities-toggle hass="[[hass]]" entities="[[config.entities]]"></hui-entities-toggle>
        </template>
      </div>
      <div id="states"></div>
    </ha-card>
`}static get properties(){return{hass:{type:Object,observer:"_hassChanged"},config:{type:Object,observer:"_configChanged"}}}constructor(){super(),this._elements=[]}getCardSize(){return 1+(this.config?this.config.entities.length:0)}_computeTitle(e){return e.title}_showHeaderToggle(e){return!1!==e}_configChanged(e){const t=this.$.states;for(;t.lastChild;)t.removeChild(t.lastChild);this._elements=[];for(let s=0;s<e.entities.length;s++){const i=e.entities[s];if(!(i in this.hass.states))continue;const a=this.hass.states[i],r=a?`state-card-${Object(u.a)(this.hass,a)}`:"state-card-display",n=document.createElement(r);g.c.includes(Object(h.a)(i))||(n.classList.add("state-card-dialog"),n.addEventListener("click",()=>this.fire("hass-more-info",{entityId:i}))),n.stateObj=a,n.hass=this.hass,this._elements.push({entityId:i,element:n});const o=document.createElement("div");o.appendChild(n),t.appendChild(o)}}_hassChanged(e){for(let t=0;t<this._elements.length;t++){const{entityId:s,element:i}=this._elements[t],a=e.states[s];i.stateObj=a,i.hass=e}}});var f=s(15);customElements.define("hui-entity-filter-card",class extends a.a{static get properties(){return{hass:{type:Object,observer:"_hassChanged"},config:{type:Object,observer:"_configChanged"}}}getCardSize(){return this.lastChild?this.lastChild.getCardSize():1}_getEntities(e,t){const s=new Set;return t.forEach(t=>{const i=[];t.domain&&i.push(e=>Object(f.a)(e)===t.domain),t.entity_id&&i.push(e=>this._filterEntityId(e,t.entity_id)),t.state&&i.push(e=>e.state===t.state),Object.values(e.states).forEach(e=>{i.every(t=>t(e))&&s.add(e.entity_id)})}),Array.from(s)}_filterEntityId(e,t){if(-1===t.indexOf("*"))return e.entity_id===t;const s=new RegExp(`^${t.replace(/\*/g,".*")}$`);return 0===e.entity_id.search(s)}_configChanged(e){let t,s;this.lastChild&&this.removeChild(this.lastChild),e.filter&&Array.isArray(e.filter)?e.card?e.card.type||(e=Object.assign({},e,{card:Object.assign({},e.card,{type:"entities"})})):e=Object.assign({},e,{card:{type:"entities"}}):t="Incorrect filter config.",t?s=k(p(t,e.card)):((s=k(e.card))._filterRawConfig=e.card,this._updateCardConfig(s),s.hass=this.hass),this.appendChild(s)}_hassChanged(e){const t=this.lastChild;this._updateCardConfig(t),t.hass=e}_updateCardConfig(e){e&&"HUI-ERROR-CARD"!==e.tagName&&(e.config=Object.assign({},e._filterRawConfig,{entities:this._getEntities(this.hass,this.config.filter)}))}});var b=s(91),_=s(16),y=(s(106),s(12));customElements.define("hui-glance-card",class extends(Object(y.a)(Object(r.a)(a.a))){static get template(){return i["a"]`
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
    `}static get properties(){return{hass:Object,config:Object,_entities:{type:Array,computed:"_computeEntities(config)"},_error:String}}getCardSize(){return 3}_computeTitle(e){return e.title}_computeEntities(e){return e&&e.entities&&Array.isArray(e.entities)?(this._error=null,e.entities):(this._error="Error in card configuration.",[])}_showEntity(e,t){return e in t}_computeName(e,t){return Object(_.a)(t[e])}_computeStateObj(e,t){return t[e]}_computeState(e,t){return Object(b.a)(this.localize,t[e])}_openDialog(e){this.fire("hass-more-info",{entityId:e.model.item})}}),s(152),s(154),customElements.define("hui-history-graph-card",class extends a.a{static get properties(){return{hass:Object,config:{type:Object,observer:"_configChanged"},_error:String,stateHistory:Object,stateHistoryLoading:Boolean,cacheConfig:{type:Object,value:{refresh:0,cacheKey:null,hoursToShow:24}}}}getCardSize(){return 4}static get template(){return i["a"]`
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
      </style>

      <template is="dom-if" if="[[!_error]]">
        <ha-card>
          <div class='header'>
            <div class="name">[[config.title]]</div>
          </div>
          <ha-state-history-data
            hass="[[hass]]"
            filter-type="recent-entity"
            entity-id="[[config.entities]]"
            data="{{stateHistory}}"
            is-loading="{{stateHistoryLoading}}"
            cache-config="[[cacheConfig]]"
          ></ha-state-history-data>
          <state-history-charts
            hass="[[hass]]"
            history-data="[[stateHistory]]"
            is-loading-data="[[stateHistoryLoading]]"
            up-to-now
            no-single
          ></state-history-charts>
        </ha-card>
      </template>

      <template is="dom-if" if="[[_error]]">
        <hui-error-card error="[[_error]]" config="[[config]]"></hui-error-card>
      </template>
    `}_configChanged(e){e.entities&&Array.isArray(e.entities)?(this._error=null,this.cacheConfig={refresh:e.refresh||0,cacheKey:e.entities,hoursToShow:e.hours||24}):this._error="No entities configured."}}),customElements.define("hui-iframe-card",class extends a.a{static get properties(){return{config:{type:Object,observer:"_configChanged"}}}static get template(){return i["a"]`
      <style>
        ha-card {
          line-height: 0;
          overflow: hidden;
        }
        .header {
          @apply --paper-font-headline;
          /* overwriting line-height +8 because entity-toggle can be 40px height,
            compensating this with reduced padding */
          line-height: 40px;
          color: var(--primary-text-color);
          padding: 20px 16px 12px 16px;
        }
        .header .name {
          @apply --paper-font-common-nowrap;
        }
        .wrapper {
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
      <ha-card>
        <template is="dom-if" if="[[_computeTitle(config)]]">
          <div class="header">
            <div class="name">[[_computeTitle(config)]]</div>
          </div>
        </template>
        <div class="wrapper">
          <iframe src="[[config.url]]"></iframe>
        </div>
      </ha-card>
    `}_computeTitle(e){return e.url?e.title||"":"Error: URL not configured"}_configChanged(e){this.shadowRoot.querySelector(".wrapper").style.paddingTop=e.aspect_ratio||"50%"}getCardSize(){return 1+this.offsetHeight/50}}),s(149),customElements.define("hui-markdown-card",class extends a.a{static get template(){return i["a"]`
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
      </style>
      <ha-card header="[[config.title]]">
        <ha-markdown content='[[config.content]]'></ha-markdown>
      </ha-card>
    `}static get properties(){return{config:Object,noTitle:{type:Boolean,reflectToAttribute:!0,computed:"_computeNoTitle(config.title)"}}}getCardSize(){return this.config.content.split("\n").length}_computeNoTitle(e){return!e}}),s(163),customElements.define("hui-media-control-card",class extends a.a{static get properties(){return{hass:{type:Object,observer:"_hassChanged"},config:{type:Object,observer:"_configChanged"}}}getCardSize(){return 3}_configChanged(e){this._entityId=null,this.lastChild&&this.removeChild(this.lastChild);const t=e&&e.entity;if(t&&!(t in this.hass.states))return;let s,i,a=null;t?"media_player"===Object(h.a)(t)?(this._entityId=t,i="ha-media_player-card",s=e):a='Entity domain must be "media_player"':a="Entity not defined in card config",a&&(i="hui-error-card",s={error:a});const r=document.createElement(i);a||(r.stateObj=this.hass.states[t],r.hass=this.hass),r.config=s,this.appendChild(r)}_hassChanged(e){if(this.lastChild&&this._entityId&&this._entityId in e.states){const t=this.lastChild,s=e.states[this._entityId];t.stateObj=s,t.hass=e}else this._configChanged(this.config)}});const v=["scene","script","weblink"];customElements.define("hui-entity-picture-card",class extends(Object(y.a)(a.a)){static get template(){return i["a"]`
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
    `}static get properties(){return{hass:Object,config:{type:Object,observer:"_configChanged"},_error:String}}getCardSize(){return 3}_configChanged(e){e&&e.entity&&e.image?this._error=null:this._error="Error in card configuration."}_computeClass(e,t){return v.includes(Object(h.a)(e))||g.h.includes(t[e].state)?"":"state-off"}_computeTitle(e,t){return e&&e in t&&Object(_.a)(t[e])}_computeState(e,t){switch(Object(h.a)(e)){case"scene":return this.localize("ui.card.scene.activate");case"script":return this.localize("ui.card.script.execute");case"weblink":return"Open";default:return Object(b.a)(this.localize,t[e])}}_cardClicked(){const e=this.config.entity,t=Object(h.a)(e);if("weblink"===t)window.open(this.hass.states[e].state);else{const s=!g.h.includes(this.hass.states[e].state);let i;switch(t){case"lock":i=s?"unlock":"lock";break;case"cover":i=s?"open_cover":"close_cover";break;default:i=s?"turn_on":"turn_off"}this.hass.callService(t,i,{entity_id:e})}}}),s(197),customElements.define("hui-picture-elements-card",class extends(Object(y.a)(Object(r.a)(a.a))){static get template(){return i["a"]`
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
        white-space: nowrap;
        position: absolute;
        transform: translate(-50%, -50%);
      }
      .state-text {
        padding: 8px;
      }
      .clickable {
        cursor: pointer;
      }
      ha-call-service-button {
        color: var(--primary-color);
      }
    </style>

    <ha-card header="[[config.title]]">
      <div id="root"></div>
    </ha-card>
`}static get properties(){return{hass:{type:Object,observer:"_hassChanged"},config:{type:Object,observer:"_configChanged"}}}getCardSize(){return 4}_configChanged(e){const t=this.$.root;for(this._requiresStateObj=[],this._requiresTextState=[];t.lastChild;)t.removeChild(t.lastChild);if(e&&e.image&&e.elements){const s=document.createElement("img");s.src=e.image,t.appendChild(s),e.elements.forEach(e=>{let s;if("state-badge"===e.type){const t=e.entity;(s=document.createElement("state-badge")).addEventListener("click",()=>this._handleClick(t,"toggle"===e.action)),s.classList.add("clickable"),this._requiresStateObj.push({el:s,entityId:t})}else if("state-text"===e.type){const t=e.entity;(s=document.createElement("div")).addEventListener("click",()=>this._handleClick(t,!1)),s.classList.add("clickable","state-text"),this._requiresTextState.push({el:s,entityId:t})}else"service-button"===e.type&&((s=document.createElement("ha-call-service-button")).hass=this.hass,s.domain=e.service&&e.domain||"homeassistant",s.service=e.service&&e.service.service||"",s.serviceData=e.service&&e.service.data||{},s.innerText=e.text);s.classList.add("element"),e.style&&Object.keys(e.style).forEach(t=>{s.style.setProperty(t,e.style[t])}),t.appendChild(s)})}}_hassChanged(e){this._requiresStateObj.forEach(t=>{const{el:s,entityId:i}=t,a=e.states[i];s.stateObj=a,s.title=this._computeTooltip(a)}),this._requiresTextState.forEach(t=>{const{el:s,entityId:i}=t,a=e.states[i];s.innerText=Object(b.a)(this.localize,a),s.title=this._computeTooltip(a)})}_computeTooltip(e){return`${Object(_.a)(e)}: ${Object(b.a)(this.localize,e)}`}_handleClick(e,t){if(t){const t=!g.h.includes(this.hass.states[e].state),s=Object(h.a)(e),i="lock"===s||"cover"===s?s:"homeassistant";let a;switch(s){case"lock":a=t?"unlock":"lock";break;case"cover":a=t?"open_cover":"close_cover";break;default:a=t?"turn_on":"turn_off"}this.hass.callService(i,a,{entity_id:e})}else this.fire("hass-more-info",{entityId:e})}});var C=s(97);customElements.define("hui-picture-glance-card",class extends(Object(y.a)(Object(r.a)(a.a))){static get template(){return i["a"]`
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
    `}static get properties(){return{hass:Object,config:{type:Object,observer:"_configChanged"},_entitiesDialog:Array,_entitiesService:Array,_error:String}}getCardSize(){return 3}_configChanged(e){let t=[],s=[],i=null;e&&e.entities&&Array.isArray(e.entities)&&e.image?e.force_dialog?t=e.entities:(s=e.entities.filter(e=>Object(m.a)(this.hass,this.hass.states[e])),t=e.entities.filter(e=>!s.includes(e))):i="Error in card configuration.",this.setProperties({_entitiesDialog:t,_entitiesService:s,_error:i})}_showEntity(e,t){return e in t}_computeIcon(e,t){return Object(C.a)(t[e])}_computeClass(e,t){return g.h.includes(t[e].state)?"state-on":""}_computeTooltip(e,t){return`${Object(_.a)(t[e])}: ${Object(b.a)(this.localize,t[e])}`}_openDialog(e){this.fire("hass-more-info",{entityId:e.model.item})}_callService(e){const t=e.model.item;let s=Object(h.a)(t);const i=!g.h.includes(this.hass.states[t].state);let a;switch(s){case"lock":a=i?"unlock":"lock";break;case"cover":a=i?"open_cover":"close_cover";break;case"group":s="homeassistant",a=i?"turn_on":"turn_off";break;default:a=i?"turn_on":"turn_off"}this.hass.callService(s,a,{entity_id:t})}}),s(162),customElements.define("hui-plant-status-card",class extends a.a{static get properties(){return{hass:{type:Object,observer:"_hassChanged"},config:{type:Object,observer:"_configChanged"}}}getCardSize(){return 3}_configChanged(e){this._entityId=null,this.lastChild&&this.removeChild(this.lastChild);const t=e&&e.entity;if(t&&!(t in this.hass.states))return;let s,i,a=null;t?"plant"===Object(h.a)(t)?(this._entityId=t,i="ha-plant-card",s=e):a='Entity domain must be "plant"':a="Entity not defined in card config",a&&(i="hui-error-card",s={error:a});const r=document.createElement(i);a||(r.stateObj=this.hass.states[t],r.hass=this.hass),r.config=s,this.appendChild(r)}_hassChanged(e){if(this.lastChild&&this._entityId&&this._entityId in e.states){const t=this.lastChild,s=e.states[this._entityId];t.stateObj=s,t.hass=e}else this._configChanged(this.config)}}),customElements.define("hui-row-card",class extends a.a{static get template(){return i["a"]`
      <style>
        #root {
          display: flex;
          margin-left: -4px;
          margin-right: -4px;
        }
        #root > * {
          flex: 1 1 0;
          margin: 0 4px;
        }
      </style>
      <div id="root"></div>
    `}static get properties(){return{hass:{type:Object,observer:"_hassChanged"},config:{type:Object,observer:"_configChanged"}}}constructor(){super(),this._elements=[]}getCardSize(){let e=1;return this._elements.forEach(t=>{const s=d(t);s>e&&(e=s)}),e}_configChanged(e){this._elements=[];const t=this.$.root;for(;t.lastChild;)t.removeChild(t.lastChild);if(!e||!e.cards||!Array.isArray(e.cards)){const s=k(p("Card config incorrect.",e));return void t.appendChild(s)}const s=[];e.cards.forEach(e=>{const i=k(e);i.hass=this.hass,s.push(i),t.appendChild(i)}),this._elements=s}_hassChanged(e){this._elements.forEach(t=>{t.hass=e})}}),s(161),customElements.define("hui-weather-forecast-card",class extends a.a{static get properties(){return{hass:{type:Object,observer:"_hassChanged"},config:{type:Object,observer:"_configChanged"}}}getCardSize(){return 4}_configChanged(e){this._entityId=null,this.lastChild&&this.removeChild(this.lastChild);const t=e&&e.entity;if(t&&!(t in this.hass.states))return;let s,i,a=null;t?"weather"===Object(h.a)(t)?(this._entityId=t,i="ha-weather-card",s=e):a='Entity domain must be "weather"':a="Entity not defined in card config",a&&(i="hui-error-card",s={error:a});const r=document.createElement(i);a||(r.stateObj=this.hass.states[t],r.hass=this.hass),r.config=s,this.appendChild(r)}_hassChanged(e){if(this.lastChild&&this._entityId&&this._entityId in e.states){const t=this.lastChild,s=e.states[this._entityId];t.stateObj=s,t.hass=e}else this._configChanged(this.config)}});const w=["camera-preview","column","entities","entity-filter","entity-picture","error","glance","history-graph","iframe","markdown","media-control","picture-elements","picture-glance","plant-status","row","weather-forecast"],x="custom:";function j(e,t){const s=document.createElement(e);return s.config=t,s}function O(e,t){return j("hui-error-card",p(e,t))}function k(e){let t;if(!e||"object"!=typeof e||!e.type)return O("No card type configured.",e);if(e.type.startsWith(x)){if(t=e.type.substr(x.length),customElements.get(t))return j(t,e);const s=O(`Custom element doesn't exist: ${t}.`,e);return customElements.whenDefined(t).then(()=>Object(l.a)(s,"rebuild-view")),s}return w.includes(e.type)?j(`hui-${e.type}-card`,e):O(`Unknown card type encountered: ${e.type}.`,e)}customElements.define("hui-view",class extends a.a{static get template(){return i["a"]`
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
    `}static get properties(){return{hass:{type:Object,observer:"_hassChanged"},columns:{type:Number,observer:"_configChanged"},config:{type:Object,observer:"_configChanged"}}}constructor(){super(),this._elements=[],this._debouncedConfigChanged=function(e,t,s){let i;return function(...t){const s=this;clearTimeout(i),i=setTimeout(()=>{i=null,e.apply(s,t)},100)}}(this._configChanged)}_configChanged(){const e=this.$.columns,t=this.config;for(;e.lastChild;)e.removeChild(e.lastChild);if(!t)return void(this._elements=[]);const s=t.cards.map(e=>{const t=k(e);return t.hass=this.hass,t});let i=[];const a=[];for(let e=0;e<this.columns;e++)i.push([]),a.push(0);s.forEach(e=>{const t="function"==typeof e.getCardSize?e.getCardSize():1;i[function(e){let t=0;for(let e=0;e<a.length;e++){if(a[e]<5){t=e;break}a[e]<a[t]&&(t=e)}return a[t]+=e,t}(t)].push(e)}),(i=i.filter(e=>e.length>0)).forEach(t=>{const s=document.createElement("div");s.classList.add("column"),t.forEach(e=>s.appendChild(e)),e.appendChild(s)}),this._elements=s,"theme"in t&&Object(c.a)(e,this.hass.themes,t.theme)}_hassChanged(e){for(let t=0;t<this._elements.length;t++)this._elements[t].hass=e}});const E={};customElements.define("hui-root",class extends(Object(n.a)(Object(r.a)(a.a))){static get template(){return i["a"]`
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
    `}static get properties(){return{narrow:Boolean,showMenu:Boolean,hass:{type:Object,observer:"_hassChanged"},config:{type:Object,observer:"_configChanged"},columns:{type:Number,observer:"_columnsChanged"},_curView:{type:Number,value:0},route:{type:Object,observer:"_routeChanged"},routeData:Object}}_routeChanged(e){const t=this.config&&this.config.views;if(""===e.path&&"/lovelace"===e.prefix&&t)this.navigate(`/lovelace/${t[0].id||0}`,!0);else if(this.routeData.view){const e=this.routeData.view;let s=0;for(let i=0;i<t.length;i++)if(t[i].id===e||i===parseInt(e)){s=i;break}s!==this._curView&&this._selectView(s)}}_computeViewId(e,t){return e||t}_computeTitle(e){return e.name||"Home Assistant"}_computeTabsHidden(e){return e.length<2}_computeTabTitle(e){return e.tab_title||e.name||"Unnamed View"}_handleRefresh(){this.fire("config-refresh")}_handleViewSelected(e){const t=e.detail.selected;if(t!==this._curView){const e=this.config.views[t].id||t;this.navigate(`/lovelace/${e}`)}var s,i,a,r,n,o,c;s=this,i=this.$.layout.header.scrollTarget,a=i,r=Math.random(),n=Date.now(),o=a.scrollTop,c=0-o,s._currentAnimationId=r,function e(){var t,i=Date.now()-n;i>200?a.scrollTop=0:s._currentAnimationId===r&&(a.scrollTop=(t=i,-c*(t/=200)*(t-2)+o),requestAnimationFrame(e.bind(s)))}.call(s)}_selectView(e){this._curView=e;const t=this.$.view;t.lastChild&&t.removeChild(t.lastChild);const s=document.createElement("hui-view");s.setProperties({hass:this.hass,config:this.config.views[this._curView],columns:this.columns}),t.appendChild(s)}_hassChanged(e){this.$.view.lastChild&&(this.$.view.lastChild.hass=e)}_configChanged(e){this._loadResources(e.resources||[]),this._selectView(this._curView)}_columnsChanged(e){this.$.view.lastChild&&(this.$.view.lastChild.columns=e)}_loadResources(e){e.forEach(e=>{switch(e.type){case"js":if(e.url in E)break;E[e.url]=Object(o.a)(e.url);break;case"module":Object(o.b)(e.url);break;case"html":Promise.resolve().then(s.bind(null,257)).then(({importHref:t})=>t(e.url));break;default:console.warn("Unknown resource type specified: ${resource.type}")}})}}),customElements.define("ha-panel-lovelace",class extends a.a{static get template(){return i["a"]`
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
        ></hass-error-screen>
      </template>
    `}static get properties(){return{hass:Object,narrow:{type:Boolean,value:!1},showMenu:{type:Boolean,value:!1},route:Object,_columns:{type:Number,value:1},_state:{type:String,value:"loading"},_errorMsg:String,_config:{type:Object,value:null}}}ready(){super.ready(),this._fetchConfig(),this._handleWindowChange=this._handleWindowChange.bind(this),this.mqls=[300,600,900,1200].map(e=>{const t=matchMedia(`(min-width: ${e}px)`);return t.addListener(this._handleWindowChange),t}),this._handleWindowChange()}_handleWindowChange(){const e=this.mqls.reduce((e,t)=>e+t.matches,0);this._columns=Math.max(1,e-(!this.narrow&&this.showMenu))}_fetchConfig(){this.hass.connection.sendMessagePromise({type:"frontend/lovelace_config"}).then(e=>this.setProperties({_config:e.result,_state:"loaded"}),e=>this.setProperties({_state:"error",_errorMsg:e.message}))}_equal(e,t){return e===t}})},70:function(e,t,s){"use strict";function i(e,t,s){return new Promise(function(i,a){const r=document.createElement(e);let n="src",o="body";switch(r.onload=(()=>i(t)),r.onerror=(()=>a(t)),e){case"script":r.async=!0,s&&(r.type=s);break;case"link":r.type="text/css",r.rel="stylesheet",n="href",o="head"}r[n]=t,document[o].appendChild(r)})}s.d(t,"a",function(){return a}),s.d(t,"b",function(){return r});const a=e=>i("script",e),r=e=>i("script",e,"module")}}]);
//# sourceMappingURL=23c139d3e603cb500514.chunk.js.map