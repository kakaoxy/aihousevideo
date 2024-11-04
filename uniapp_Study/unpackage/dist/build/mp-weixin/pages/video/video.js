"use strict";const e=require("../../common/vendor.js"),o={data:()=>({videoUrl:"",logs:[],isVideo:!1,scrollTop:0,isLoading:!1,error:null,pollingTimer:null,enterSource:"",housingId:null,isGeneratingVideo:!1}),onShow(){this.initializePage()},onLoad(){this.initializePage()},onHide(){this.clearPolling()},onUnload(){this.clearPolling()},methods:{initializePage(){try{const o=e.index.getStorageSync("enterSource");if(console.log("启动来源enterSource:",o),"view"===o)this.handleViewVideo();else if("generate"===o){const o=e.index.getStorageSync("housingId");console.log("进入来源为 generate，房源ID:",o),o?(this.housingId=o,this.isGeneratingVideo=!0,this.handleGenerateVideo()):this.handleVideoError("未找到有效的房源ID")}}catch(o){console.error("初始化页面错误:",o),this.handleVideoError("页面初始化失败")}},handleViewVideo(){const o=e.index.getStorageSync("videoUrl");if(console.log("启动了handleViewVideo，videoUrl:",o),o){const i="http://101.126.149.86:8000",t=o.replace(/^\./,"").replace(/\\/g,"/"),n=encodeURI(t);this.videoUrl=i+n,this.isVideo=!0,e.index.removeStorageSync("videoUrl"),console.log("设置的视频URL:",this.videoUrl),this.preloadVideo()}},async pollLogs(){if(this.housingId)try{const o=await e.index.request({url:"http://101.126.149.86:8000/get_log",method:"GET"});if(console.log("轮询日志响应:",o),200===o.statusCode&&o.data&&this.logs.push(o.data.log),200===o.statusCode&&o.data){const i=o.data;this.logs=i.logs||[],this.scrollTop=1e4,"completed"===i.status&&i.video_url?(this.clearPolling(),this.isGeneratingVideo=!1,video_Url=`http://101.126.149.86:8000${i.video_url}`,this.videoUrl=encodeURI(video_Url),console.log("videoUrl:",this.videoUrl),this.isVideo=!0,this.preloadVideo(),e.index.removeStorageSync("enterSource"),e.index.removeStorageSync("housingId")):"failed"===i.status&&(this.clearPolling(),this.isGeneratingVideo=!1,this.handleVideoError("视频生成失败"),e.index.removeStorageSync("enterSource"),e.index.removeStorageSync("housingId"))}else console.error("获取日志响应异常:",o)}catch(o){console.error("轮询日志失败:",o),o.errMsg&&o.errMsg.includes("request:fail")?console.log("网络错误，继续轮询"):(this.clearPolling(),this.isGeneratingVideo=!1,this.handleVideoError("获取生成状态失败"))}else console.error("没有找到房源ID")},handleGenerateVideo(){console.log("handleGenerateVideo执行生成视频请求"),this.housingId?(this.isVideo=!1,this.logs=[],this.error=null,this.isGeneratingVideo=!0,this.startPollingLogs()):this.handleVideoError("无效的房源ID")},startPollingLogs(){console.log("startPollingLogs执行轮询日志请求"),this.housingId?(this.clearPolling(),this.pollLogs(),this.pollingTimer=setInterval((()=>{this.pollLogs()}),3e3)):console.error("没有找到房源ID")},clearPolling(){this.pollingTimer&&(clearInterval(this.pollingTimer),this.pollingTimer=null)},preloadVideo(){if(!this.videoUrl)return;e.index.showLoading({title:"加载中..."});const o=e.index.createVideoContext("myVideo");o&&(o.stop(),o.seek(0)),e.index.request({url:this.videoUrl,method:"HEAD",success:e=>{200===e.statusCode?this.isVideo=!0:this.handleVideoError("视频资源不可用")},fail:e=>{this.handleVideoError("视频加载失败")},complete:()=>{e.index.hideLoading()}})},downloadVideo(){this.videoUrl?(e.index.showLoading({title:"下载中..."}),e.index.downloadFile({url:this.videoUrl,success:o=>{200===o.statusCode?e.index.saveVideoToPhotosAlbum({filePath:o.tempFilePath,success:()=>{e.index.hideLoading(),e.index.showToast({title:"视频已保存到相册",icon:"success",duration:2e3})},fail:o=>{e.index.hideLoading(),e.index.showToast({title:"保存失败，请重试",icon:"none",duration:2e3})}}):(e.index.hideLoading(),e.index.showToast({title:"下载失败，请重试",icon:"none",duration:2e3}))},fail:o=>{e.index.hideLoading(),e.index.showToast({title:"下载失败，请重试",icon:"none",duration:2e3})}})):e.index.showToast({title:"视频地址无效",icon:"none",duration:2e3})},handleVideoError(o){console.error(o),this.error=o,this.isVideo=!1,e.index.showToast({title:o,icon:"none",duration:2e3})}}};const i=e._export_sfc(o,[["render",function(o,i,t,n,s,r){return e.e({a:s.isVideo&&s.videoUrl},s.isVideo&&s.videoUrl?{b:s.videoUrl,c:e.o(((...e)=>r.handleVideoError&&r.handleVideoError(...e)))}:{},{d:e.o(((...e)=>r.downloadVideo&&r.downloadVideo(...e))),e:s.error},s.error?{f:e.t(s.error)}:{},{g:s.isGeneratingVideo},(s.isGeneratingVideo,{}),{h:s.logs.length>0},s.logs.length>0?{i:e.f(s.logs,((o,i,t)=>({a:e.t(o),b:i}))),j:s.scrollTop}:{})}]]);wx.createPage(i);
