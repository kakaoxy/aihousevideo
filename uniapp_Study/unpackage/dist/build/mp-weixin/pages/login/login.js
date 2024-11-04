"use strict";const o=require("../../common/vendor.js"),e={data:()=>({isLoggedIn:!1,userInfo:{}}),onLoad(){const e=o.index.getStorageSync("userInfo");e&&(this.isLoggedIn=!0,this.userInfo=e,this.navigateToListingForm())},methods:{login(){o.index.getUserProfile({desc:"用于完善会员资料",success:e=>{this.userInfo=e.userInfo,this.isLoggedIn=!0,o.index.setStorageSync("userInfo",e.userInfo),this.navigateToListingForm()},fail:e=>{console.error("授权失败",e),o.index.showToast({title:"授权失败，请重试",icon:"none"})}})},navigateToListingForm(){o.index.switchTab({url:"/pages/listingform/listingform",success:()=>{console.log("跳转到 listingform 页面成功")},fail:o=>{console.error("跳转到 listingform 页面失败",o)}})}}};const n=o._export_sfc(e,[["render",function(e,n,s,i,r,t){return o.e({a:!r.isLoggedIn},r.isLoggedIn?{c:r.userInfo.avatarUrl,d:o.t(r.userInfo.nickName)}:{b:o.o(((...o)=>t.login&&t.login(...o)))})}]]);wx.createPage(n);
