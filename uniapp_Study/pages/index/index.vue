<template>
	<scroll-view scroll-y="true" :show-scrollbar="false" :enhanced="true" class="scroll-main">
		<view class="container">
			<view class="promotion-info">
				<view class="introduction-section">
					<textarea placeholder="请输入房源介绍 | 建议包含房源、小区及周边三个角度,尽可能完整地介绍该房源的卖点" v-model="houseDescription"
						class="textarea" maxlength="-1"></textarea>
				</view>

				<view class="image-list">
					<view v-for="(image, index) in images" :key="index" class="image-item">
						<image :src="image.path" mode="aspectFill" @tap="previewImage(index)"></image>
						<view class="delete-icon" @tap="deleteImage(index)">×</view>
					</view>
					<view v-if="images.length < maxImages" class="add-image" @tap="chooseImage">
						+
					</view>
				</view>
			</view>
			<!--  添加房源基本信息 小区名称、面积、户型使用选择器实现格式为x房x厅x卫、楼层（格式为x层/总x层）总价 -->
			<view class="house-info">
				<view class="form-item">
					<text class="label">小区名称:</text>
					<input type="text" v-model="communityName" placeholder="请输入小区名称" />
				</view>

				<view class="form-item">
					<text class="label">面积:</text>
					<input type="number" v-model="area" placeholder="请输入面积（平方米）" />
				</view>

				<view class="form-item">
					<text class="label">户型:</text>
					<picker mode="multiSelector" :range="houseTypeRange" :value="houseTypeIndex"
						@change="onHouseTypeChange">
						<view class="picker">
							{{ houseTypeRange[0][houseTypeIndex[0]] }}{{ houseTypeRange[1][houseTypeIndex[1]] }}{{ houseTypeRange[2][houseTypeIndex[2]] }}
						</view>
					</picker>
				</view>

				<view class="form-item-1">
					<text class="label">楼层:</text>
					<view class="floor-inputs">
						<input type="number" v-model="currentFloor" placeholder="当前楼层" class="half-input"/>
						<text class="floor-divider">/</text>
						<input type="number" v-model="totalFloors" placeholder="总楼层" class="half-input"/>
					</view>
				</view>

				<view class="form-item">
					<text class="label">总价:</text>
					<input type="number" v-model="totalPrice" placeholder="请输入总价（万元）" />
				</view>

				<!-- <button @click="submitForm">提交</button> -->
			</view>
			<button :disabled="isUploading" @tap="uploadImages">
				{{ isUploading? '上传中...' : '发布' }}
			</button>
		</view>
	</scroll-view>
</template>

<script>
	export default {
		data() {
			return {
				houseDescription: '',
				images: [], // 已选中的图片列表
				maxImages: 30, // 最大图片数量限制
				communityName: '',
				area: '',
				houseTypeRange: [
					['1房', '2房', '3房', '4房', '5房', '6房', '7房', '8房', '9房'], // 房
					['0厅','1厅', '2厅', '3厅', '4厅', '5厅', '6厅', '7厅', '8厅', '9厅'], // 厅
					['0卫','1卫', '2卫', '3卫', '4卫', '5卫', '6卫', '7卫', '8卫', '9卫'] // 卫
				],
				houseTypeIndex: [0, 0, 0],
				currentFloor: '',
				totalFloors: '',
				totalPrice: '',
				isUploading: false,
				selectedImageBase64Set: new Set(), // 用于去重的集合
			};
		},
		methods: {
			// 选择图片
			chooseImage() {
				const maxSelect = this.maxImages - this.images.length;
				uni.chooseImage({
					count: maxSelect,
					sizeType: ['compressed'],
					sourceType: ['album'],
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
				this.isUploading = true;
				try {
					// 上传图片并获取图片 URL
					const uploadTasks = this.images.map(async (image) => {
						const compressedImage = await this.compressImage(image.path);
						const uploadResult = await this.uploadImage(compressedImage);
						const imageUrls = JSON.parse(uploadResult.data).imageUrls;
						return imageUrls;
					});

					// 等待所有图片上传完成
					const uploadResults = await Promise.all(uploadTasks);

					// 将所有图片 URL 合并到一个数组中
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

					const response = await uni.request({
						url: 'http://192.168.100.198:8000/add_housing/',
						method: 'POST',
						data: housingData
					});

					

					// 检查返回值
					if (response && response.statusCode === 200) {
						// 跳转到listingform页面
						uni.switchTab({
							url: '/pages/listingform/listingform'
						});
						// 清空表单中填写的内容	
						this.houseDescription = '';
						this.images = [];
						this.communityName = '';
						this.area = '';
						this.houseTypeIndex = [0, 0, 0];
						this.currentFloor = '';
						this.totalFloors = '';
						this.totalPrice = '';
						this.selectedImageBase64Set.clear();
						this.isUploading = false;

						uni.showToast({
							title: '房源添加成功',
							icon: 'success'
						});
					} else {
						uni.showToast({
							title: '房源添加失败',
							icon: 'none'
						});
						console.error('房源添加失败', response);
					}
				} catch (error) {
					uni.showToast({
						title: '上传失败',
						icon: 'none'
					});
					console.error('上传失败', error);
				}
			},

			// 压缩图片
			compressImage(imagePath) {
				return new Promise((resolve, reject) => {
					uni.compressImage({
						src: imagePath,
						quality: 60, // 压缩质量，范围0-100
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
						url: 'http://192.168.100.198:8000/upload/image', // 替换为你的服务器地址
						filePath: imagePath,
						name: 'files',  // 注意这里应该是 'files'
						success: (res) => {
							resolve(res);
						},
						fail: (err) => {
							reject(err);
						},
					});
				});
			},
			
			onHouseTypeChange(e) {
				this.houseTypeIndex = e.detail.value;
			},
		},
	};
</script>

<style>
	.scroll-main {
		height: 100vh;
	}

	.container {
		padding: 20px;
		border-width: 0;
		border-style: none;
		border-color: transparent;
	}


	.textarea {
		width: 100%;
		height: 168px;
		border: 1px solid #eee;
		padding: 10px;
	}

	.introduction-section .textarea {
		border: none !important;
		outline: none !important;
	}

	.image-list {
		display: flex;
		flex-wrap: wrap;
		justify-content: flex-start;
		/* 使图片从左到右依次排列 */
		align-items: center;
		/* 垂直居中 */
	}

	.image-item {
		position: relative;
		margin: 5px;
		width: 100px;
		height: 100px;
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
		width: 100px;
		height: 100px;
		border: 1px dashed #ccc;
		border-radius: 5px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 24px;
		color: #ccc;
		cursor: pointer;
		margin: 5px;
	}



	.house-info {
	display: flex;
	flex-direction: column;
	border: 1px solid #ccc;
	border-radius: 5px;
 	padding: 0 15px;
	}

	.form-item, .form-item-1 {
	display: flex;
	align-items: center;
	margin-bottom: 10px;
	padding: 5px;
	}

	.label {
	width: 100px;
	text-align: left;
	margin-right: 10px;
	}

	.input {
	flex-grow: 1;
	width: 200px; 
	}	

	.picker {
	width: 100%;
	}

	.floor-inputs {
	display: flex;
	align-items: center;
	}

	.half-input {
	width: 68px; 
	}

	.floor-divider {
	margin: 0 5px;
	} 
	








	button {
		background-color: #3a3f3a;
		color: white;
		/* padding: 10px 10px; */
		border: none;
		border-radius: 5px;
		margin-top: 5px;
	}
</style>