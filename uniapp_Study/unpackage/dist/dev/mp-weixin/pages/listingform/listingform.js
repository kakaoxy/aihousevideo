"use strict";
const common_vendor = require("../../common/vendor.js");
const common_assets = require("../../common/assets.js");
const _sfc_main = {
  data() {
    return {
      housings: [],
      isRefreshing: false,
      // 新增：用于标记下拉刷新状态
      isGeneratingVideo: false
    };
  },
  methods: {
    async fetchLatestHousings() {
      try {
        this.isRefreshing = true;
        const response = await common_vendor.index.request({
          url: "http://101.126.149.86:8000/get_latest_housings",
          method: "GET"
        });
        if (response && response.statusCode === 200) {
          let uniqueIdCounter = 0;
          this.housings = response.data.housings.map((housing) => {
            return {
              ...housing,
              showMask: false,
              _id: housing._id,
              house_id: uniqueIdCounter++
            };
          });
          console.log("Fetched housings:", this.housings);
        } else {
          console.error("Failed to fetch latest housings", response);
        }
        this.isRefreshing = false;
      } catch (error) {
        console.error("Error fetching latest housings", error);
        this.isRefreshing = false;
      }
    },
    // 在调用生成视频的页面
    // 在调用生成视频的页面
    // 在调用生成视频的页面（如 listingform.js）
    generateVideo(housing) {
      if (!housing || !housing._id || !housing._id.$oid) {
        common_vendor.index.showToast({
          title: "无效的房源数据",
          icon: "none"
        });
        return;
      }
      const housingId = housing._id.$oid;
      console.log("准备生成视频，房源ID:", housingId);
      common_vendor.index.setStorageSync("enterSource", "generate");
      common_vendor.index.setStorageSync("housingId", housingId);
      common_vendor.index.switchTab({
        url: "/pages/video/video"
      });
      common_vendor.index.request({
        url: "http://101.126.149.86:8000/generate_video",
        method: "POST",
        header: {
          "content-type": "application/json"
        },
        data: {
          house_id: housingId
          // 修改参数名为housingId
        },
        success: (res) => {
          if (res.statusCode === 200) {
            common_vendor.index.setStorageSync("enterSource", "view");
            common_vendor.index.setStorageSync("videoUrl", housing.video_url);
            common_vendor.index.reLaunch({
              url: "/pages/video/video",
              success: () => {
                console.log("页面跳转成功");
              },
              fail: (error) => {
                console.error("页面跳转失败", error);
                common_vendor.index.switchTab({
                  url: "/pages/video/video"
                });
              }
            });
          } else {
            common_vendor.index.showToast({
              title: "生成视频请求失败",
              icon: "none"
            });
          }
        },
        fail: (error) => {
          console.error("请求失败:", error);
          common_vendor.index.showToast({
            title: "网络请求失败",
            icon: "none"
          });
        },
        complete: () => {
          common_vendor.index.hideLoading();
        }
      });
    },
    viewVideo(housing) {
      common_vendor.index.setStorageSync("enterSource", "view");
      common_vendor.index.setStorageSync("videoUrl", housing.video_url);
      common_vendor.index.reLaunch({
        url: "/pages/video/video",
        success: () => {
          console.log("页面跳转成功");
        },
        fail: (error) => {
          console.error("页面跳转失败", error);
          common_vendor.index.switchTab({
            url: "/pages/video/video"
          });
        }
      });
    },
    toggleMask(housing) {
      housing.showMask = !housing.showMask;
    }
  },
  onShow() {
  },
  onPullDownRefresh() {
    console.log("下拉时执行获取最新房屋信息的方法");
    this.fetchLatestHousings().then(() => {
      common_vendor.index.stopPullDownRefresh();
    });
  },
  mounted() {
    console.log("mounted执行获取最新房屋信息的方法");
    this.fetchLatestHousings();
  }
};
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return {
    a: common_vendor.f($data.housings, (housing, k0, i0) => {
      return common_vendor.e({
        a: housing.images[0],
        b: common_vendor.t(housing.community),
        c: common_vendor.t(housing.area),
        d: common_vendor.t(housing.layout),
        e: common_vendor.t(housing.floor),
        f: common_vendor.t(housing.total_price),
        g: housing.showMask
      }, housing.showMask ? {} : {}, {
        h: housing.showMask
      }, housing.showMask ? {
        i: common_vendor.t($data.isGeneratingVideo ? "生成中..." : "生成视频"),
        j: housing.is_video_generated || $data.isGeneratingVideo,
        k: common_vendor.o(($event) => $options.generateVideo(housing), housing.house_id),
        l: !housing.is_video_generated,
        m: common_vendor.o(($event) => $options.viewVideo(housing), housing.house_id)
      } : {}, {
        n: housing.house_id,
        o: common_vendor.o(($event) => $options.toggleMask(housing), housing.house_id)
      });
    }),
    b: common_assets._imports_0,
    c: common_assets._imports_1,
    d: common_assets._imports_2,
    e: common_assets._imports_3
  };
}
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["render", _sfc_render], ["__scopeId", "data-v-80bcded7"]]);
wx.createPage(MiniProgramPage);
