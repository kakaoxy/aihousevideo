<template>
	<view class="container">
		<!-- 个人信息区域 -->
		<view class="profile-section">
			<view class="avatar" @click="changeAvatar">
				<image :src="userAvatar" mode="aspectFill"></image>
			</view>
			<input type="text" placeholder="昵称" v-model="nickname" />
			<input type="text" placeholder="手机号码" v-model="phoneNumber" @click="showVerificationCodeInput = true" />
			<input v-if="showVerificationCodeInput" type="text" placeholder="验证码" v-model="verificationCode" />
			<button @click="saveProfile">保存</button>
		</view>

		<!-- 账户余额区域 -->
		<view class="balance-section">
			<text>账户余额：{{ balance }}</text>
		</view>

		<!-- 账户充值区域 -->
		<view class="recharge-section">
			<input type="number" placeholder="充值金额" v-model="rechargeAmount" />
			<picker mode="selector" :range="paymentMethods" @change="selectPaymentMethod">
				<view>{{ selectedPaymentMethod }}</view>
			</picker>
			<button @click="recharge">充值</button>
		</view>

		<!-- 邀请码区域 -->
		<view class="invitation-code-section">
			<text>邀请码：{{ invitationCode }}</text>
			<button @click="copyInvitationCode">复制</button>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				userAvatar: '', // 用户头像URL
				nickname: '',
				phoneNumber: '',
				verificationCode: '',
				showVerificationCodeInput: false,
				balance: 0,
				rechargeAmount: 0,
				paymentMethods: ['微信支付', '支付宝'],
				selectedPaymentMethod: '微信支付',
				invitationCode: ''
			};
		},
		methods: {
			changeAvatar() {
				// 弹出选择框让用户选择从相册上传或拍照更换头像
				uni.chooseImage({
					count: 1, // 默认9
					sizeType: ['original', 'compressed'], // 可以指定是原图还是压缩图，默认二者都有
					sourceType: ['album', 'camera'], // 可以指定来源是相册还是相机，默认二者都有
					success: (res) => {
						// 将选择的图片上传到服务器
						this.uploadAvatar(res.tempFilePaths[0]);
					}
				});
			},
			uploadAvatar(avatarPath) {
				// 这里需要实现上传头像到服务器的逻辑
			},
			saveProfile() {
				// 发送请求到后端保存个人信息
			},
			recharge() {
				// 发送请求到后端进行充值操作
			},
			copyInvitationCode() {
				// 复制邀请码到剪贴板
				uni.setClipboardData({
					data: this.invitationCode,
					success: () => {
						uni.showToast({
							title: '复制成功'
						});
					}
				});
			},
			selectPaymentMethod(e) {
				this.selectedPaymentMethod = this.paymentMethods[e.target.value];
			}
		},
		onShow() {
			// 页面显示时获取用户信息和余额
			this.getUserInfo();
			this.getBalance();
			this.getInvitationCode();
		},
		methods: {
			async getUserInfo() {
				// 获取用户信息的逻辑
			},
			async getBalance() {
				// 获取用户余额的逻辑
			},
			async getInvitationCode() {
				// 获取用户邀请码的逻辑
			}
		}
	};
</script>

<style>
	.container {
		padding: 20px;
	}

	.profile-section,
	.balance-section,
	.recharge-section,
	.invitation-code-section {
		margin-bottom: 20px;
	}

	.avatar {
		width: 100px;
		height: 100px;
		margin-bottom: 10px;
	}

	.avatar image {
		width: 100%;
		height: 100%;
		border-radius: 50%;
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