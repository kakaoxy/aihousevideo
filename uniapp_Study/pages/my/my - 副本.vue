<template>
	<view class="container">
		<view class="image-list">
			<view v-for="(image, index) in images" :key="index" class="image-item">
				<image :src="image.path" mode="aspectFill" @tap="previewImage(index)"></image>
				<view class="delete-icon" @tap="deleteImage(index)">×</view>
			</view>
			<view v-if="images.length < maxImages" class="add-image" @tap="chooseImage">
				+
			</view>
		</view>
		<button @tap="uploadImages">确定上传</button>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				images: [], // 已选中的图片列表
				maxImages: 30, // 最大图片数量限制
				selectedImageBase64Set: new Set(), // 用于去重的集合
			};
		},
		methods: {
			// 选择图片
			chooseImage() {
				const maxSelect = this.maxImages - this.images.length;
				uni.chooseImage({
					count: maxSelect,
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
					},
				});
			},

			// 获取图片的 base64 编码
			getBase64(path) {
				return new Promise((resolve, reject) => {
					uni.getFileSystemManager().readFile({
						filePath: path,
						encoding: 'base64',
						success: (res) => {
							resolve(res.data);
						},
						fail: (err) => {
							reject(err);
						},
					});
				});
			},

			// 预览图片
			previewImage(index) {
				uni.previewImage({
					urls: this.images.map(image => image.path),
					current: index,
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
				const uploadTasks = this.images.map(async (image) => {
					const compressedImage = await this.compressImage(image.path);
					return this.uploadImage(compressedImage);
				});

				try {
					await Promise.all(uploadTasks);
					uni.showToast({
						title: '上传成功',
						icon: 'success',
					});
				} catch (error) {
					uni.showToast({
						title: '上传失败',
						icon: 'none',
					});
				}
			},

			// 压缩图片
			compressImage(imagePath) {
				return new Promise((resolve, reject) => {
					uni.compressImage({
						src: imagePath,
						quality: 80, // 压缩质量，范围0-100
						success: (res) => {
							resolve(res.tempFilePath);
						},
						fail: (err) => {
							reject(err);
						},
					});
				});
			},

			// 上传单张图片
			uploadImage(imagePath) {
				return new Promise((resolve, reject) => {
					uni.uploadFile({
						url: 'https://your-server.com/upload', // 替换为你的服务器地址
						filePath: imagePath,
						name: 'file',
						success: (res) => {
							resolve(res);
						},
						fail: (err) => {
							reject(err);
						},
					});
				});
			},
		},
	};
</script>



<style>
	.container {
		padding: 20px;
	}

	.image-list {
		display: flex;
		flex-wrap: wrap;
	}

	.image-item {
		position: relative;
		margin: 5px;
		width: 80px;
		height: 80px;
	}

	.image-item image {
		width: 100%;
		height: 100%;
		border-radius: 5px;
	}

	.delete-icon {
		position: absolute;
		top: -8px;
		right: -8px;
		width: 20px;
		height: 20px;
		background-color: red;
		color: white;
		border-radius: 50%;
		text-align: center;
		line-height: 20px;
		font-size: 16px;
		cursor: pointer;
	}

	.add-image {
		width: 80px;
		height: 80px;
		border: 1px dashed #ccc;
		border-radius: 5px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 24px;
		color: #ccc;
		cursor: pointer;
	}

	button {
		margin-top: 20px;
	}
</style>