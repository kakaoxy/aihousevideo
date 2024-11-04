"use strict";
const common_vendor = require("../../common/vendor.js");
const _sfc_main = {
  data() {
    return {
      videoUrl: "",
      logs: [],
      isVideo: false,
      scrollTop: 0,
      isLoading: false,
      error: null,
      pollingTimer: null,
      enterSource: "",
      housingId: null,
      isGeneratingVideo: false
    };
  },
  onShow() {
    this.initializePage();
  },
  onLoad() {
    this.initializePage();
  },
  onHide() {
    this.clearPolling();
  },
  onUnload() {
    this.clearPolling();
  },
  methods: {
    initializePage() {
      try {
        const enterSource = common_vendor.index.getStorageSync("enterSource");
        console.log("启动来源enterSource:", enterSource);
        if (enterSource === "view") {
          this.handleViewVideo();
        } else if (enterSource === "generate") {
          const housingId = common_vendor.index.getStorageSync("housingId");
          console.log("进入来源为 generate，房源ID:", housingId);
          if (housingId) {
            this.housingId = housingId;
            this.isGeneratingVideo = true;
            this.handleGenerateVideo();
          } else {
            this.handleVideoError("未找到有效的房源ID");
          }
        }
      } catch (error) {
        console.error("初始化页面错误:", error);
        this.handleVideoError("页面初始化失败");
      }
    },
    handleViewVideo() {
      const videoUrl = common_vendor.index.getStorageSync("videoUrl");
      console.log("启动了handleViewVideo，videoUrl:", videoUrl);
      if (videoUrl) {
        const baseUrl = "http://192.168.100.198:8000";
        const processedUrl = videoUrl.replace(/^\./, "").replace(/\\/g, "/");
        const endUrl = encodeURI(processedUrl);
        this.videoUrl = baseUrl + endUrl;
        this.isVideo = true;
        common_vendor.index.removeStorageSync("videoUrl");
        console.log("设置的视频URL:", this.videoUrl);
        this.preloadVideo();
      }
    },
    async pollLogs() {
      if (!this.housingId) {
        console.error("没有找到房源ID");
        return;
      }
      try {
        const res = await common_vendor.index.request({
          url: `http://192.168.100.198:8000/get_log`,
          method: "GET"
        });
        console.log("轮询日志响应:", res);
        if (res.statusCode === 200 && res.data) {
          this.logs.push(res.data.log);
        }
        if (res.statusCode === 200 && res.data) {
          const data = res.data;
          this.logs = data.logs || [];
          this.scrollTop = 1e4;
          if (data.status === "completed" && data.video_url) {
            this.clearPolling();
            this.isGeneratingVideo = false;
            video_Url = `http://192.168.100.198:8000${data.video_url}`;
            this.videoUrl = encodeURI(video_Url);
            console.log("videoUrl:", this.videoUrl);
            this.isVideo = true;
            this.preloadVideo();
            common_vendor.index.removeStorageSync("enterSource");
            common_vendor.index.removeStorageSync("housingId");
          } else if (data.status === "failed") {
            this.clearPolling();
            this.isGeneratingVideo = false;
            this.handleVideoError("视频生成失败");
            common_vendor.index.removeStorageSync("enterSource");
            common_vendor.index.removeStorageSync("housingId");
          }
        } else {
          console.error("获取日志响应异常:", res);
        }
      } catch (error) {
        console.error("轮询日志失败:", error);
        if (error.errMsg && error.errMsg.includes("request:fail")) {
          console.log("网络错误，继续轮询");
        } else {
          this.clearPolling();
          this.isGeneratingVideo = false;
          this.handleVideoError("获取生成状态失败");
        }
      }
    },
    handleGenerateVideo() {
      console.log("handleGenerateVideo执行生成视频请求");
      if (!this.housingId) {
        this.handleVideoError("无效的房源ID");
        return;
      }
      this.isVideo = false;
      this.logs = [];
      this.error = null;
      this.isGeneratingVideo = true;
      this.startPollingLogs();
    },
    startPollingLogs() {
      console.log("startPollingLogs执行轮询日志请求");
      if (!this.housingId) {
        console.error("没有找到房源ID");
        return;
      }
      this.clearPolling();
      this.pollLogs();
      this.pollingTimer = setInterval(() => {
        this.pollLogs();
      }, 3e3);
    },
    clearPolling() {
      if (this.pollingTimer) {
        clearInterval(this.pollingTimer);
        this.pollingTimer = null;
      }
    },
    preloadVideo() {
      if (!this.videoUrl)
        return;
      common_vendor.index.showLoading({
        title: "加载中..."
      });
      const videoContext = common_vendor.index.createVideoContext("myVideo");
      if (videoContext) {
        videoContext.stop();
        videoContext.seek(0);
      }
      common_vendor.index.request({
        url: this.videoUrl,
        method: "HEAD",
        success: (res) => {
          if (res.statusCode === 200) {
            this.isVideo = true;
          } else {
            this.handleVideoError("视频资源不可用");
          }
        },
        fail: (error) => {
          this.handleVideoError("视频加载失败");
        },
        complete: () => {
          common_vendor.index.hideLoading();
        }
      });
    },
    downloadVideo() {
      if (!this.videoUrl) {
        common_vendor.index.showToast({
          title: "视频地址无效",
          icon: "none",
          duration: 2e3
        });
        return;
      }
      common_vendor.index.showLoading({
        title: "下载中..."
      });
      common_vendor.index.downloadFile({
        url: this.videoUrl,
        success: (res) => {
          if (res.statusCode === 200) {
            common_vendor.index.saveVideoToPhotosAlbum({
              filePath: res.tempFilePath,
              success: () => {
                common_vendor.index.hideLoading();
                common_vendor.index.showToast({
                  title: "视频已保存到相册",
                  icon: "success",
                  duration: 2e3
                });
              },
              fail: (err) => {
                common_vendor.index.hideLoading();
                common_vendor.index.showToast({
                  title: "保存失败，请重试",
                  icon: "none",
                  duration: 2e3
                });
              }
            });
          } else {
            common_vendor.index.hideLoading();
            common_vendor.index.showToast({
              title: "下载失败，请重试",
              icon: "none",
              duration: 2e3
            });
          }
        },
        fail: (err) => {
          common_vendor.index.hideLoading();
          common_vendor.index.showToast({
            title: "下载失败，请重试",
            icon: "none",
            duration: 2e3
          });
        }
      });
    },
    handleVideoError(errorMsg) {
      console.error(errorMsg);
      this.error = errorMsg;
      this.isVideo = false;
      common_vendor.index.showToast({
        title: errorMsg,
        icon: "none",
        duration: 2e3
      });
    }
  }
};
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return common_vendor.e({
    a: $data.isVideo && $data.videoUrl
  }, $data.isVideo && $data.videoUrl ? {
    b: $data.videoUrl,
    c: common_vendor.o((...args) => $options.handleVideoError && $options.handleVideoError(...args))
  } : {}, {
    d: common_vendor.o((...args) => $options.downloadVideo && $options.downloadVideo(...args)),
    e: $data.error
  }, $data.error ? {
    f: common_vendor.t($data.error)
  } : {}, {
    g: $data.isGeneratingVideo
  }, $data.isGeneratingVideo ? {} : {}, {
    h: $data.logs.length > 0
  }, $data.logs.length > 0 ? {
    i: common_vendor.f($data.logs, (log, index, i0) => {
      return {
        a: common_vendor.t(log),
        b: index
      };
    }),
    j: $data.scrollTop
  } : {});
}
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["render", _sfc_render]]);
wx.createPage(MiniProgramPage);
