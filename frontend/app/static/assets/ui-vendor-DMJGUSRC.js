import{r as l}from"./react-vendor-nf7bT_Uh.js";var k={exports:{}},f={};/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var x=l,w=Symbol.for("react.element"),v=Symbol.for("react.fragment"),E=Object.prototype.hasOwnProperty,b=x.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner,R={key:!0,ref:!0,__self:!0,__source:!0};function g(t,e,o){var r,n={},s=null,i=null;o!==void 0&&(s=""+o),e.key!==void 0&&(s=""+e.key),e.ref!==void 0&&(i=e.ref);for(r in e)E.call(e,r)&&!R.hasOwnProperty(r)&&(n[r]=e[r]);if(t&&t.defaultProps)for(r in e=t.defaultProps,e)n[r]===void 0&&(n[r]=e[r]);return{$$typeof:w,type:t,key:s,ref:i,props:n,_owner:b.current}}f.Fragment=v;f.jsx=g;f.jsxs=g;k.exports=f;var m=k.exports;function h(t,e){if(typeof t=="function")return t(e);t!=null&&(t.current=e)}function A(...t){return e=>{let o=!1;const r=t.map(n=>{const s=h(n,e);return!o&&typeof s=="function"&&(o=!0),s});if(o)return()=>{for(let n=0;n<r.length;n++){const s=r[n];typeof s=="function"?s():h(t[n],null)}}}}function S(t){const e=N(t),o=l.forwardRef((r,n)=>{const{children:s,...i}=r,c=l.Children.toArray(s),a=c.find(O);if(a){const p=a.props.children,d=c.map(y=>y===a?l.Children.count(p)>1?l.Children.only(null):l.isValidElement(p)?p.props.children:null:y);return m.jsx(e,{...i,ref:n,children:l.isValidElement(p)?l.cloneElement(p,void 0,d):null})}return m.jsx(e,{...i,ref:n,children:s})});return o.displayName=`${t}.Slot`,o}var H=S("Slot");function N(t){const e=l.forwardRef((o,r)=>{const{children:n,...s}=o;if(l.isValidElement(n)){const i=L(n),c=$(s,n.props);return n.type!==l.Fragment&&(c.ref=r?A(r,i):i),l.cloneElement(n,c)}return l.Children.count(n)>1?l.Children.only(null):null});return e.displayName=`${t}.SlotClone`,e}var j=Symbol("radix.slottable");function O(t){return l.isValidElement(t)&&typeof t.type=="function"&&"__radixId"in t.type&&t.type.__radixId===j}function $(t,e){const o={...e};for(const r in e){const n=t[r],s=e[r];/^on[A-Z]/.test(r)?n&&s?o[r]=(...c)=>{const a=s(...c);return n(...c),a}:n&&(o[r]=n):r==="style"?o[r]={...n,...s}:r==="className"&&(o[r]=[n,s].filter(Boolean).join(" "))}return{...t,...o}}function L(t){var r,n;let e=(r=Object.getOwnPropertyDescriptor(t.props,"ref"))==null?void 0:r.get,o=e&&"isReactWarning"in e&&e.isReactWarning;return o?t.ref:(e=(n=Object.getOwnPropertyDescriptor(t,"ref"))==null?void 0:n.get,o=e&&"isReactWarning"in e&&e.isReactWarning,o?t.props.ref:t.props.ref||t.ref)}/**
 * @license lucide-react v0.544.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const P=t=>t.replace(/([a-z0-9])([A-Z])/g,"$1-$2").toLowerCase(),I=t=>t.replace(/^([A-Z])|[\s-_]+(\w)/g,(e,o,r)=>r?r.toUpperCase():o.toLowerCase()),_=t=>{const e=I(t);return e.charAt(0).toUpperCase()+e.slice(1)},C=(...t)=>t.filter((e,o,r)=>!!e&&e.trim()!==""&&r.indexOf(e)===o).join(" ").trim(),T=t=>{for(const e in t)if(e.startsWith("aria-")||e==="role"||e==="title")return!0};/**
 * @license lucide-react v0.544.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */var W={xmlns:"http://www.w3.org/2000/svg",width:24,height:24,viewBox:"0 0 24 24",fill:"none",stroke:"currentColor",strokeWidth:2,strokeLinecap:"round",strokeLinejoin:"round"};/**
 * @license lucide-react v0.544.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const D=l.forwardRef(({color:t="currentColor",size:e=24,strokeWidth:o=2,absoluteStrokeWidth:r,className:n="",children:s,iconNode:i,...c},a)=>l.createElement("svg",{ref:a,...W,width:e,height:e,stroke:t,strokeWidth:r?Number(o)*24/Number(e):o,className:C("lucide",n),...!s&&!T(c)&&{"aria-hidden":"true"},...c},[...i.map(([p,d])=>l.createElement(p,d)),...Array.isArray(s)?s:[s]]));/**
 * @license lucide-react v0.544.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const u=(t,e)=>{const o=l.forwardRef(({className:r,...n},s)=>l.createElement(D,{ref:s,iconNode:e,className:C(`lucide-${P(_(t))}`,`lucide-${t}`,r),...n}));return o.displayName=_(t),o};/**
 * @license lucide-react v0.544.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const M=[["path",{d:"m21 16-4 4-4-4",key:"f6ql7i"}],["path",{d:"M17 20V4",key:"1ejh1v"}],["path",{d:"m3 8 4-4 4 4",key:"11wl7u"}],["path",{d:"M7 4v16",key:"1glfcx"}]],J=u("arrow-up-down",M);/**
 * @license lucide-react v0.544.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const V=[["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}],["line",{x1:"12",x2:"12",y1:"8",y2:"12",key:"1pkeuh"}],["line",{x1:"12",x2:"12.01",y1:"16",y2:"16",key:"4dfq90"}]],K=u("circle-alert",V);/**
 * @license lucide-react v0.544.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const B=[["path",{d:"M21.801 10A10 10 0 1 1 17 3.335",key:"yps3ct"}],["path",{d:"m9 11 3 3L22 4",key:"1pflzl"}]],Y=u("circle-check-big",B);/**
 * @license lucide-react v0.544.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const U=[["path",{d:"M12 6v6l4 2",key:"mmk7yg"}],["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}]],G=u("clock",U);/**
 * @license lucide-react v0.544.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Z=[["path",{d:"M16 17h6v-6",key:"t6n2it"}],["path",{d:"m22 17-8.5-8.5-5 5L2 7",key:"x473p"}]],Q=u("trending-down",Z);/**
 * @license lucide-react v0.544.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const q=[["path",{d:"M16 7h6v6",key:"box55l"}],["path",{d:"m22 7-8.5 8.5-5-5L2 17",key:"1t1m79"}]],X=u("trending-up",q);/**
 * @license lucide-react v0.544.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const F=[["path",{d:"M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z",key:"1xq2db"}]],ee=u("zap",F);export{J as A,G as C,H as S,X as T,ee as Z,Y as a,K as b,Q as c,m as j};
