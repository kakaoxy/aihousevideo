<template>
	<view class="container">
		<form @submit="register">
			<view class="input-group">
				<input type="text" placeholder="请输入手机号码" v-model="phoneNumber" @input="validatePhoneNumber" />
				<text v-if="phoneError">{{ phoneError }}</text>
			</view>
			<view class="input-group">
				<input type="password" placeholder="密码需包含数字和字母，长度不少于8位" v-model="password" />
			</view>
			<view class="input-group">
				<input type="text" placeholder="邀请码（可选）" v-model="invitationCode" />
			</view>
			<button form-type="submit" :disabled="isRegistering">注册</button>
		</form>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				phoneNumber: '',
				password: '',
				invitationCode: '',
				phoneError: '',
				isRegistering: false
			};
		},
		methods: {
			validatePhoneNumber() {
				const regex = /^1[3-9]\d{9}$/;
				if (!regex.test(this.phoneNumber)) {
					this.phoneError = '手机号码格式不正确';
				} else {
					this.phoneError = '';
				}
			},
			async register(e) {
				e.preventDefault();
				if (this.phoneError || !this.phoneNumber || !this.password) {
					uni.showToast({
						title: '请填写正确的信息',
						icon: 'none'
					});
					return;
				}
				if (this.password.length < 8 || !/\d/.test(this.password) || !/[a-zA-Z]/.test(this.password)) {
					uni.showToast({
						title: '密码不符合要求',
						icon: 'none'
					});
					return;
				}
				this.isRegistering = true;
				try {
					const response = await uni.request({
						url: '/api/register',
						method: 'POST',
						data: {
							phone_number: this.phoneNumber,
							password: this.password,
							invitation_code: this.invitationCode
						}
					});
					if (response[1].data.success) {
						uni.showToast({
							title: '注册成功',
							icon: 'success'
						});
						// 这里可以调用登录接口并跳转到listingform页面
						// this.login();
						uni.navigateTo({
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
						title: '注册失败，请稍后再试',
						icon: 'none'
					});
				} finally {
					this.isRegistering = false;
				}
			},
			// login() {
			//   // 登录逻辑，可以调用登录接口
			// }
		}
	};
</script>

<style>
	.container {
		padding: 20px;
	}

	.input-group {
		margin-bottom: 20px;
	}

	.input-group text {
		color: red;
	}

	button {
		background-color: #007aff;
		color: white;
		border: none;
		padding: 10px 20px;
		border-radius: 5px;
	}

	button:disabled {
		background-color: #ccc;
	}
</style>