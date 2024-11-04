<template>
	<view class="video-container">
		<!-- 视频播放部分 -->
		<view class="video-player">
			<video v-if="isVideo && videoUrl" id="myVideo" :src="videoUrl" controls preload="metadata"
				@error="handleVideoError" style="width: 100%;"></video>

			<view class="download-btn" @click="downloadVideo">下载视频</view>
		</view>

		<!-- 错误提示 -->
		<view v-if="error" class="error-message">
			{{ error }}
		</view>

		<!-- 生成状态提示 -->
		<view v-if="isGeneratingVideo" class="generating-message">
			正在生成视频，请耐心等待...
		</view>

		<!-- 日志显示部分 -->
		<scroll-view v-if="logs.length > 0" class="log-container" scroll-y :scroll-top="scrollTop">
			<view v-for="(log, index) in logs" :key="index" class="log-item">
				{{ log }}
			</view>
		</scroll-view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				videoUrl: '',
				logs: [],
				isVideo: false,
				scrollTop: 0,
				isLoading: false,
				error: null,
				pollingTimer: null,
				enterSource: '',
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
					const enterSource = uni.getStorageSync('enterSource');
					console.log('启动来源enterSource:', enterSource);

					if (enterSource === 'view') {
						this.handleViewVideo();
					} else if (enterSource === 'generate') {
						const housingId = uni.getStorageSync('housingId');
						console.log('进入来源为 generate，房源ID:', housingId);
						if (housingId) {
							this.housingId = housingId;
							this.isGeneratingVideo = true;
							this.handleGenerateVideo();
							// 确保清除存储在正确的时机
						} else {
							this.handleVideoError('未找到有效的房源ID');
						}
					}
				} catch (error) {
					console.error('初始化页面错误:', error);
					this.handleVideoError('页面初始化失败');
				}
			},

			handleViewVideo() {
				const videoUrl = uni.getStorageSync('videoUrl');
				console.log('启动了handleViewVideo，videoUrl:', videoUrl)
				if (videoUrl) {
					const baseUrl = 'http://101.126.149.86:8000';
					const processedUrl = videoUrl.replace(/^\./, '').replace(/\\/g, '/');
					const endUrl = encodeURI(processedUrl);
					this.videoUrl = baseUrl + endUrl;
					// console.log('processedUrl:',this.videoUrl)
					this.isVideo = true;

					// 清除视频URL存储
					uni.removeStorageSync('videoUrl');

					console.log('设置的视频URL:', this.videoUrl);

					// 预加载视频
					this.preloadVideo();
				}
			},

			async pollLogs() {
				if (!this.housingId) {
					console.error('没有找到房源ID');
					return;
				}

				try {
					const res = await uni.request({
						url: `http://101.126.149.86:8000/get_log`,
						method: 'GET'
					});

					console.log('轮询日志响应:', res);
					if (res.statusCode === 200 && res.data) {
						// 将返回的信息显示在页面上
						this.logs.push(res.data.log);
					}

					if (res.statusCode === 200 && res.data) {
						const data = res.data;
						this.logs = data.logs || [];
						this.scrollTop = 10000; // 自动滚动到底部

						// 检查视频是否生成完成
						if (data.status === 'completed' && data.video_url) {
							this.clearPolling();
							this.isGeneratingVideo = false;
							video_Url = `http://101.126.149.86:8000${data.video_url}`;
							this.videoUrl = encodeURI(video_Url)
							console.log('videoUrl:', this.videoUrl)
							this.isVideo = true;
							this.preloadVideo();
							uni.removeStorageSync('enterSource');
							uni.removeStorageSync('housingId');
						} else if (data.status === 'failed') {
							this.clearPolling();
							this.isGeneratingVideo = false;
							this.handleVideoError('视频生成失败');
							uni.removeStorageSync('enterSource');
							uni.removeStorageSync('housingId');
						}
						// 如果状态是 processing，继续轮询
					} else {
						console.error('获取日志响应异常:', res);
					}
				} catch (error) {
					console.error('轮询日志失败:', error);
					// 如果是网络错误，可以继续轮询
					// 如果是其他错误，可能需要停止轮询
					if (error.errMsg && error.errMsg.includes('request:fail')) {
						// 网络错误，继续轮询
						console.log('网络错误，继续轮询');
					} else {
						this.clearPolling();
						this.isGeneratingVideo = false;
						this.handleVideoError('获取生成状态失败');
					}
				}
			},

			handleGenerateVideo() {
				console.log('handleGenerateVideo执行生成视频请求');
				if (!this.housingId) {
					this.handleVideoError('无效的房源ID');
					return;
				}

				this.isVideo = false;
				this.logs = [];
				this.error = null;
				this.isGeneratingVideo = true;
				this.startPollingLogs();
			},

			startPollingLogs() {
				console.log('startPollingLogs执行轮询日志请求');
				if (!this.housingId) {
					console.error('没有找到房源ID');
					return;
				}

				// 清除之前的轮询
				this.clearPolling();

				// 开始新的轮询
				this.pollLogs();
				this.pollingTimer = setInterval(() => {
					this.pollLogs();
				}, 3000); // 每3秒轮询一次
			},

			clearPolling() {
				if (this.pollingTimer) {
					clearInterval(this.pollingTimer);
					this.pollingTimer = null;
				}
			},


			preloadVideo() {
				if (!this.videoUrl) return;

				uni.showLoading({
					title: '加载中...'
				});

				const videoContext = uni.createVideoContext('myVideo');
				if (videoContext) {
					videoContext.stop();
					videoContext.seek(0);
				}

				uni.request({
					url: this.videoUrl,
					method: 'HEAD',
					success: (res) => {
						if (res.statusCode === 200) {
							this.isVideo = true;
						} else {
							this.handleVideoError('视频资源不可用');
						}
					},
					fail: (error) => {
						this.handleVideoError('视频加载失败');
					},
					complete: () => {
						uni.hideLoading();
					}
				});
			},

			downloadVideo() {
				if (!this.videoUrl) {
					uni.showToast({
						title: '视频地址无效',
						icon: 'none',
						duration: 2000
					});
					return;
				}

				uni.showLoading({
					title: '下载中...'
				});

				uni.downloadFile({
					url: this.videoUrl,
					success: (res) => {
						if (res.statusCode === 200) {
							uni.saveVideoToPhotosAlbum({
								filePath: res.tempFilePath,
								success: () => {
									uni.hideLoading();
									uni.showToast({
										title: '视频已保存到相册',
										icon: 'success',
										duration: 2000
									});
								},
								fail: (err) => {
									uni.hideLoading();
									uni.showToast({
										title: '保存失败，请重试',
										icon: 'none',
										duration: 2000
									});
								}
							});
						} else {
							uni.hideLoading();
							uni.showToast({
								title: '下载失败，请重试',
								icon: 'none',
								duration: 2000
							});
						}
					},
					fail: (err) => {
						uni.hideLoading();
						uni.showToast({
							title: '下载失败，请重试',
							icon: 'none',
							duration: 2000
						});
					}
				});
			},



			handleVideoError(errorMsg) {
				console.error(errorMsg);
				this.error = errorMsg;
				this.isVideo = false;

				uni.showToast({
					title: errorMsg,
					icon: 'none',
					duration: 2000
				});
			}
		}
	};
</script>

<style>
	.container {
		height: 100vh;
		display: flex;
		flex-direction: column;
	}


	.video-player {
		position: relative;
		align-items: center;
		justify-content: center;
		background-color: #000;
	}

	.download-btn {
		position: absolute;
		right: 20rpx;
		bottom: 20rpx;
		background-color: rgba(0, 0, 0, 0.6);
		color: #fff;
		padding: 10rpx 20rpx;
		border-radius: 10rpx;
		font-size: 28rpx;
	}

	.log-section {
		flex: 1;
		background-color: #f5f5f5;
		padding: 20rpx;
	}

	.log-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 20rpx 0;
	}

	.log-title {
		font-size: 32rpx;
		font-weight: bold;
	}

	.refresh-text {
		color: #007AFF;
		font-size: 28rpx;
	}

	.log-content {
		height: calc(50vh - 100rpx);
		background-color: #fff;
		border-radius: 10rpx;
		padding: 20rpx;
	}

	.log-item {
		font-size: 28rpx;
		line-height: 1.5;
		padding: 10rpx 0;
		border-bottom: 1rpx solid #eee;
	}
</style>