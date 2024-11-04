<template>
	<view class="container">
		<!-- 手机号码登录区域 -->
		<view class="login-section">
			<input type="text" placeholder="请输入手机号码" v-model="phoneNumber" />
			<input type="password" placeholder="请输入密码" v-model="password" />
			<button @click="loginByPhone">登录</button>
		</view>

		<!-- 微信登录区域 -->
		<view class="wechat-login-section">
			<button @click="loginByWechat">微信登录</button>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				phoneNumber: '',
				password: ''
			};
		},
		methods: {
			async loginByPhone() {
				if (!this.phoneNumber || !this.password) {
					uni.showToast({
						title: '手机号和密码不能为空',
						icon: 'none'
					});
					return;
				}
				try {
					const response = await uni.request({
						url: '/api/login',
						method: 'POST',
						data: {
							login_type: 'phone',
							phone_number: this.phoneNumber,
							password: this.password
						}
					});
					if (response[1].data.success) {
						uni.showToast({
							title: '登录成功',
							icon: 'success'
						});
						// 存储token等操作，然后跳转到产品主界面
						uni.switchTab({
							url: '/pages/listingform/listingform'
						});
					} else {
						uni.showToast({
							title: response[1].data.message,
							icon: 'none'
						});
					}
				} catch (error) {
					uni.showToast({
						title: '登录失败，请稍后再试',
						icon: 'none'
					});
				}
			},
			loginByWechat() {
				// 这里需要调用微信登录API，通常是使用uni.login()获取code
				// 然后将code发送到后端进行登录或注册
				uni.switchTab({
					url: '/pages/listingform/listingform'
				});

				// uni.login({
				// 	provider: 'weixin',
				// 	success: async (loginRes) => {
				// 		try {
				// 			const response = await uni.request({
				// 				url: '/api/login',
				// 				method: 'POST',
				// 				data: {
				// 					login_type: 'wechat',
				// 					wechat_code: loginRes.code
				// 				}
				// 			});
				// 			if (response[1].data.success) {
				// 				uni.showToast({
				// 					title: '微信登录成功',
				// 					icon: 'success'
				// 				});
				// 				// 存储token等操作，然后跳转到产品主界面
				// 				uni.navigateTo({
				// 					url: '/pages/listingform/listingform'
				// 				});
				// 			} else {
				// 				uni.showToast({
				// 					title: response[1].data.message,
				// 					icon: 'none'
				// 				});
				// 			}
				// 		} catch (error) {
				// 			uni.showToast({
				// 				title: '微信登录失败，请稍后再试',
				// 				icon: 'none'
				// 			});
				// 		}
				// 	},
				// 	fail: (error) => {
				// 		uni.showToast({
				// 			title: '微信登录失败，请稍后再试',
				// 			icon: 'none'
				// 		});
				// 	}
				// });
			}
		}
	};
</script>

<style>
	.container {
		padding: 20px;
	}

	.login-section,
	.wechat-login-section {
		margin-bottom: 20px;
	}

	input {
		width: 100%;
		height: 40px;
		margin-bottom: 10px;
		padding: 10px;
		border: 1px solid #ccc;
		border-radius: 5px;
	}

	button {
		width: 100%;
		height: 40px;
		background-color: #007aff;
		color: white;
		border: none;
		border-radius: 5px;
	}
</style>