<template>
	<scroll-view scroll-y="true" :show-scrollbar="false" :enhanced="true" class="scroll-main">
		<view class="main">
			<view class="page-space">
				<view v-for="housing in housings" :key="housing.house_id" class="container" @click="toggleMask(housing)">

					<view class="house-card">
						<img :src="housing.images[0]" alt="" class="image">
						<view class="housetitle">
							<h3 class="title-text">{{ housing.community }}</h3>
						</view>
					</view>

					<view class="house-details">
						<view class="house-info">
							<view class="house-area">
								<img src="../../static/area.png" alt="" class="house-info-icon">
								<span>{{ housing.area }}㎡</span>
							</view>
							<view class="house-layout">
								<img src="../../static/layout.png" alt="" class="house-info-icon">
								<span>{{ housing.layout }}</span>
							</view>
							<view class="house-floor">
								<img src="../../static/floor.png" alt="" class="house-info-icon">
								<span>{{ housing.floor }}</span>
							</view>
							<view class="house-price">
								<img src="../../static/price.png" alt="" class="house-info-icon">
								<span>{{ housing.total_price }}万</span>
							</view>
						</view>
					</view>

					<view class="mask" v-if="housing.showMask"></view>

					<!-- 弹出的按钮 -->
					<view v-if="housing.showMask" class="popup-btn">
						<button class="popup-btn1" :disabled="housing.is_video_generated || isGeneratingVideo" @click="generateVideo(housing)">
							{{ isGeneratingVideo ? '生成中...' : '生成视频' }}
						</button>

						<button class="popup-btn2" :disabled="!housing.is_video_generated" @click="viewVideo(housing)">查看视频</button>
					</view>
				</view>
			</view>
		</view>
	</scroll-view>
</template>

<script>
	export default {
		data() {
			return {
				housings: [],
				isRefreshing: false, // 新增：用于标记下拉刷新状态
				isGeneratingVideo: false
			};
		},
		methods: {
			async fetchLatestHousings() {
				try {
					this.isRefreshing = true;
					const response = await uni.request({
						url: 'http://192.168.100.198:8000/get_latest_housings',
						method: 'GET'
					});

					if (response && response.statusCode === 200) {
						let uniqueIdCounter = 0;
						this.housings = response.data.housings.map(housing => {
							return {
								...housing,
								showMask: false,
								_id: housing._id,
								house_id: uniqueIdCounter++,
							};
						});
						console.log('Fetched housings:', this.housings);
					} else {
						console.error('Failed to fetch latest housings', response);
					}
					this.isRefreshing = false;
				} catch (error) {
					console.error('Error fetching latest housings', error);
					this.isRefreshing = false;
				}
			},

			// 在调用生成视频的页面
			// 在调用生成视频的页面
			// 在调用生成视频的页面（如 listingform.js）
			generateVideo(housing) {
				// 验证housing对象
				if (!housing || !housing._id || !housing._id.$oid) {
					uni.showToast({
						title: '无效的房源数据',
						icon: 'none'
					});
					return;
				}

				const housingId = housing._id.$oid;
				console.log('准备生成视频，房源ID:', housingId);
				
				// 先存储状态和房源ID
				uni.setStorageSync('enterSource', 'generate');
				uni.setStorageSync('housingId', housingId);

				// 使用 switchTab 跳转到视频页面
				uni.switchTab({
					url: '/pages/video/video'
				});

				
				uni.request({
					url: 'http://192.168.100.198:8000/generate_video',
					method: 'POST',
					header: {
						'content-type': 'application/json'
					},
					data: {
						house_id: housingId  // 修改参数名为housingId
					},
					success: (res) => {
						if (res.statusCode === 200) {
							// 立即跳转到视频页面
							uni.setStorageSync('enterSource', 'view');
							uni.setStorageSync('videoUrl', housing.video_url);
							
							// 使用 reLaunch 替代 switchTab，强制重新加载页面
							uni.reLaunch({
								url: '/pages/video/video',
								success: () => {
									console.log('页面跳转成功');
								},
								fail: (error) => {
									console.error('页面跳转失败', error);
									// 如果跳转失败，尝试使用 switchTab
									uni.switchTab({
										url: '/pages/video/video'
									});
								}
							});
						} else {
							uni.showToast({
								title: '生成视频请求失败',
								icon: 'none'
							});
						}
					},
					fail: (error) => {
						console.error('请求失败:', error);
						uni.showToast({
							title: '网络请求失败',
							icon: 'none'
						});
					},
					complete: () => {
						uni.hideLoading();
					}
				});
			},


			viewVideo(housing) {
				// 先存储视频URL
				uni.setStorageSync('enterSource', 'view');
				uni.setStorageSync('videoUrl', housing.video_url);
				
				// 使用 reLaunch 替代 switchTab，强制重新加载页面
				uni.reLaunch({
					url: '/pages/video/video',
					success: () => {
						console.log('页面跳转成功');
					},
					fail: (error) => {
						console.error('页面跳转失败', error);
						// 如果跳转失败，尝试使用 switchTab
						uni.switchTab({
							url: '/pages/video/video'
						});
					}
				});
			},


			toggleMask(housing) {
				housing.showMask = !housing.showMask;
			}
		},

		onShow() {
			// 新增：在页面显示时执行获取最新房屋信息的方法
			// console.log('onShow执行获取最新房屋信息的方法');
			// this.fetchLatestHousings();
		},
		onPullDownRefresh() {
			// 新增：处理下拉刷新事件
			console.log('下拉时执行获取最新房屋信息的方法');
			this.fetchLatestHousings().then(() => {
				uni.stopPullDownRefresh();
			});
		},
		mounted() {
			console.log('mounted执行获取最新房屋信息的方法');
			this.fetchLatestHousings();
		}
	};
</script>

<style scoped>
	.scroll-main {
		height: 100vh;
	}

	.main {
		max-width: 512px;
		/* 512px */
		/* 假设这是max-w-lg对应的宽度 */
		margin-left: auto;
		margin-right: auto;
		padding-left: 16px;
		/* 16px */
		padding-right: 16px;
		/* 16px */
		padding-top: 16px;
		/* 16px */
		padding-bottom: 16px;
		/* 16px */

	}

	.page-space {
		margin-top: 0px;
	}

	.container {
		/* 背景白色，圆角边框，添加阴影，超出部分隐藏*/
		background-color: white;
		border-radius: 8px;
		box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
		overflow: hidden;
		margin-top: 8px;
		position: relative;

	}

	.mask {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background-color: rgba(0, 0, 0, 0.6);
		z-index: 10;
	}

	.popup-btn {
		position: absolute;
		top: 50%;
		left: 50%;
		width: 100vw;
		/* 视口的宽度 */
		height: 100vh;
		/* 视口的高度 */
		transform: translate(-50%, -50%);
		z-index: 11;
		border: none;
		/* 取消边框 */
		color: white;
		/* 文字颜色改为白色 */
		background-color: transparent;
		/* 背景颜色设置为透明 */
		padding: 10px 20px;
		/* 根据需要调整内边距 */
		cursor: pointer;
		/* 鼠标悬停时显示指针 */
		/* 可能还需要一些额外的样式来确保按钮在透明背景下可见 */
		outline: none;
		/* 移除点击时的轮廓线 */
		display: flex;
		/* 使用flex布局使按钮内的内容居中 */
		justify-content: center;
		/* 水平居中 */
		align-items: center;
		/* 垂直居中 */
		text-align: center;
		/* 文字居中 */

		padding: 10px 20px;
	}




	.house-card {
		position: relative;
		width: 100%;
		height: 208px;
	}

	.image {
		width: 100%;
		/* 设置宽度为100% */
		height: 100%;
		/* 设置高度为100% */
		object-fit: cover;
		/* 覆盖整个容器，保持宽高比，可能裁剪图片 */
	}

	.housetitle {
		position: absolute;
		bottom: 0;
		left: 0;
		right: 0;
		background-image: linear-gradient(to top, rgba(0, 0, 0, 0.6), transparent);
		padding: 12px;
		/* p-3 等同于 padding: 1rem; */
	}

	.title-text {
		font-size: 18px;
		/* 18px */
		line-height: 28px;
		/* 28px */
		/* text-lg 等同于 font-size: 1.125rem; */
		font-weight: 600;
		/* font-semibold 等同于 font-weight: 600; */
		color: white;
		/* text-white 等同于 color: white; */
	}

	.house-details {
		padding: 16px;
	}

	.house-info {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 12px;
	}

	.house-area,
	.house-layout,
	.house-floor,
	.house-price {
		display: flex;
		align-items: center;
		/* 已经正确设置了垂直居中 */
		color: #1c1c1c;
		font-size: 14px;
		line-height: 20px;
	}

	.house-info-icon {
		width: 16px;
		height: 16px;
		margin-right: 6px;
		flex-shrink: 0;
		color: #758599;
		/* 防止图标被压缩 */
	}
</style>