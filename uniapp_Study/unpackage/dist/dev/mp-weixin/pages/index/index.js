"use strict";
const common_vendor = require("../../common/vendor.js");
const _sfc_main = {
  data() {
    return {
      houseDescription: "",
      images: [],
      // 已选中的图片列表
      maxImages: 30,
      // 最大图片数量限制
      communityName: "",
      area: "",
      houseTypeRange: [
        ["1房", "2房", "3房", "4房", "5房", "6房", "7房", "8房", "9房"],
        // 房
        ["0厅", "1厅", "2厅", "3厅", "4厅", "5厅", "6厅", "7厅", "8厅", "9厅"],
        // 厅
        ["0卫", "1卫", "2卫", "3卫", "4卫", "5卫", "6卫", "7卫", "8卫", "9卫"]
        // 卫
      ],
      houseTypeIndex: [0, 0, 0],
      currentFloor: "",
      totalFloors: "",
      totalPrice: "",
      isUploading: false,
      selectedImageBase64Set: /* @__PURE__ */ new Set()
      // 用于去重的集合
    };
  },
  methods: {
    // 选择图片
    chooseImage() {
      const maxSelect = this.maxImages - this.images.length;
      common_vendor.index.chooseImage({
        count: maxSelect,
        sizeType: ["compressed"],
        sourceType: ["album"],
        success: async (res) => {
          for (const path of res.tempFilePaths) {
            const base64 = await this.getBase64(path);
            if (!this.selectedImageBase64Set.has(base64)) {
              this.selectedImageBase64Set.add(base64);
              this.images.push({
                path,
                base64
              });
            }
          }
        }
      });
    },
    // 获取图片的 base64 编码
    getBase64(path) {
      return new Promise((resolve, reject) => {
        common_vendor.index.getFileSystemManager().readFile({
          filePath: path,
          encoding: "base64",
          success: (res) => {
            resolve(res.data);
          },
          fail: (err) => {
            reject(err);
          }
        });
      });
    },
    // 预览图片
    previewImage(index) {
      common_vendor.index.previewImage({
        urls: this.images.map((image) => image.path),
        current: index
      });
    },
    // 删除图片
    deleteImage(index) {
      const deletedImage = this.images[index];
      this.images.splice(index, 1);
      this.selectedImageBase64Set.delete(deletedImage.base64);
    },
    // 上传图片
    async uploadImages() {
      this.isUploading = true;
      try {
        const uploadTasks = this.images.map(async (image) => {
          const compressedImage = await this.compressImage(image.path);
          const uploadResult = await this.uploadImage(compressedImage);
          const imageUrls2 = JSON.parse(uploadResult.data).imageUrls;
          return imageUrls2;
        });
        const uploadResults = await Promise.all(uploadTasks);
        const imageUrls = uploadResults.flat();
        const housingData = {
          description: this.houseDescription,
          community: this.communityName,
          area: this.area,
          // layout: `${this.houseTypeRange[0][this.houseTypeIndex[0]]}${this.houseTypeRange[1][this.houseTypeIndex[1]]}${this.houseTypeRange[2][this.houseTypeIndex[2]]}`,
          layout: `${this.houseTypeRange[0][this.houseTypeIndex[0]]}${this.houseTypeRange[1][this.houseTypeIndex[1]]}${this.houseTypeRange[2][this.houseTypeIndex[2]]}`,
          floor: `${this.currentFloor}层/共${this.totalFloors}层`,
          total_price: this.totalPrice,
          images: imageUrls,
          is_video_generated: false
        };
        console.log(housingData.layout);
        const response = await common_vendor.index.request({
          url: "http://192.168.100.198:8000/add_housing/",
          method: "POST",
          data: housingData
        });
        if (response && response.statusCode === 200) {
          common_vendor.index.switchTab({
            url: "/pages/listingform/listingform"
          });
          this.houseDescription = "";
          this.images = [];
          this.communityName = "";
          this.area = "";
          this.houseTypeIndex = [0, 0, 0];
          this.currentFloor = "";
          this.totalFloors = "";
          this.totalPrice = "";
          this.selectedImageBase64Set.clear();
          this.isUploading = false;
          common_vendor.index.showToast({
            title: "房源添加成功",
            icon: "success"
          });
        } else {
          common_vendor.index.showToast({
            title: "房源添加失败",
            icon: "none"
          });
          console.error("房源添加失败", response);
        }
      } catch (error) {
        common_vendor.index.showToast({
          title: "上传失败",
          icon: "none"
        });
        console.error("上传失败", error);
      }
    },
    // 压缩图片
    compressImage(imagePath) {
      return new Promise((resolve, reject) => {
        common_vendor.index.compressImage({
          src: imagePath,
          quality: 60,
          // 压缩质量，范围0-100
          success: (res) => {
            resolve(res.tempFilePath);
          },
          fail: (err) => {
            reject(err);
          }
        });
      });
    },
    // 上传单张图片
    uploadImage(imagePath) {
      return new Promise((resolve, reject) => {
        common_vendor.index.uploadFile({
          url: "http://192.168.100.198:8000/upload/image",
          // 替换为你的服务器地址
          filePath: imagePath,
          name: "files",
          // 注意这里应该是 'files'
          success: (res) => {
            resolve(res);
          },
          fail: (err) => {
            reject(err);
          }
        });
      });
    },
    onHouseTypeChange(e) {
      this.houseTypeIndex = e.detail.value;
    }
  }
};
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return common_vendor.e({
    a: $data.houseDescription,
    b: common_vendor.o(($event) => $data.houseDescription = $event.detail.value),
    c: common_vendor.f($data.images, (image, index, i0) => {
      return {
        a: image.path,
        b: common_vendor.o(($event) => $options.previewImage(index), index),
        c: common_vendor.o(($event) => $options.deleteImage(index), index),
        d: index
      };
    }),
    d: $data.images.length < $data.maxImages
  }, $data.images.length < $data.maxImages ? {
    e: common_vendor.o((...args) => $options.chooseImage && $options.chooseImage(...args))
  } : {}, {
    f: $data.communityName,
    g: common_vendor.o(($event) => $data.communityName = $event.detail.value),
    h: $data.area,
    i: common_vendor.o(($event) => $data.area = $event.detail.value),
    j: common_vendor.t($data.houseTypeRange[0][$data.houseTypeIndex[0]]),
    k: common_vendor.t($data.houseTypeRange[1][$data.houseTypeIndex[1]]),
    l: common_vendor.t($data.houseTypeRange[2][$data.houseTypeIndex[2]]),
    m: $data.houseTypeRange,
    n: $data.houseTypeIndex,
    o: common_vendor.o((...args) => $options.onHouseTypeChange && $options.onHouseTypeChange(...args)),
    p: $data.currentFloor,
    q: common_vendor.o(($event) => $data.currentFloor = $event.detail.value),
    r: $data.totalFloors,
    s: common_vendor.o(($event) => $data.totalFloors = $event.detail.value),
    t: $data.totalPrice,
    v: common_vendor.o(($event) => $data.totalPrice = $event.detail.value),
    w: common_vendor.t($data.isUploading ? "上传中..." : "发布"),
    x: $data.isUploading,
    y: common_vendor.o((...args) => $options.uploadImages && $options.uploadImages(...args))
  });
}
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["render", _sfc_render]]);
wx.createPage(MiniProgramPage);
