"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const common_vendor = require("./common/vendor.js");
if (!Math) {
  "./pages/listingform/listingform.js";
  "./pages/index/index.js";
  "./pages/video/video.js";
}
const _sfc_main = {
  onLaunch: function() {
    console.log("App Launch");
  },
  onShow: function() {
    console.log("App Show");
  },
  onHide: function() {
    console.log("App Hide");
  }
};
function createApp() {
  const app = common_vendor.createSSRApp(_sfc_main);
  app.component("draggable", common_vendor.draggable);
  return {
    app
  };
}
createApp().app.mount("#app");
exports.createApp = createApp;
