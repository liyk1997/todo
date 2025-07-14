<template>
	<view class="container">
		<view class="room-form">
			<view class="form-header">
				<text class="title">房间管理</text>
			</view>
			
			<view class="form-content">
				<view class="input-group">
					<input class="input" v-model="roomToken" placeholder="请输入房间令牌" />
					<button class="btn join-btn" @click="joinRoom">加入房间</button>
				</view>
				<view class="divider">
					<text class="divider-text">或者</text>
				</view>
				<button class="btn create-btn" @click="createRoom">创建新房间</button>
			</view>
		</view>
	</view>
</template>

<script lang="ts">
import Vue, { ComponentOptions } from 'vue';
import { createRoom as apiCreateRoom, joinRoom as apiJoinRoom } from '../../api/todo';

export default Vue.extend({
	data() {
		return {
			roomToken: ''
		}
	},
	methods: {
		async createRoom() {
			try {
				// 显示加载提示
				uni.showLoading({
					title: '创建房间中...'
				});

				const room = await apiCreateRoom();
				console.log('房间创建成功，token:', room.token);

				// 隐藏加载提示
				uni.hideLoading();

				// 显示成功提示
				await new Promise<void>((resolve) => {
					uni.showToast({
						title: '房间创建成功，令牌：' + room.token,
						icon: 'none',
						duration: 1500,
						success: () => {
							setTimeout(resolve, 1500);
						}
					});
				});

				// 跳转到Todo列表页面
				const url = `/pages/index/index?token=${room.token}&mode=create`;
				console.log('准备跳转到:', url);
				uni.redirectTo({
					url,
					success: () => {
						console.log('跳转成功');
					},
					fail: (err) => {
						console.error('跳转失败:', err);
					}
				});
			} catch (error) {
				console.error('创建房间失败:', error);
				uni.showToast({
					title: '创建房间失败',
					icon: 'none'
				});
			}
		},
		async joinRoom() {
			if (!this.roomToken.trim()) {
				uni.showToast({
					title: '请输入房间令牌',
					icon: 'none'
				});
				return;
			}

			try {
				// 显示加载提示
				uni.showLoading({
					title: '加入房间中...'
				});

				const room = await apiJoinRoom(this.roomToken);
				console.log('加入房间成功，token:', room.token);

				// 隐藏加载提示
				uni.hideLoading();

				// 显示成功提示
				await new Promise<void>((resolve) => {
					uni.showToast({
						title: '加入房间成功',
						icon: 'success',
						duration: 1500,
						success: () => {
							setTimeout(resolve, 1500);
						}
					});
				});

				// 跳转到Todo列表页面
				const url = `/pages/index/index?token=${room.token}&mode=join`;
				console.log('准备跳转到:', url);
				uni.redirectTo({
					url,
					success: () => {
						console.log('跳转成功');
					},
					fail: (err) => {
						console.error('跳转失败:', err);
					}
				});
			} catch (error) {
				console.error('加入房间失败:', error);
				uni.showToast({
					title: '房间不存在或已关闭',
					icon: 'none'
				});
			}
		}
	}
});
</script>

<style>
.container {
	padding: 40rpx;
	min-height: 100vh;
	background-color: #f8f9fa;
	display: flex;
	justify-content: center;
	align-items: center;
}

.room-form {
	width: 100%;
	background: #ffffff;
	border-radius: 20rpx;
	padding: 40rpx;
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
}

.form-header {
	text-align: center;
	margin-bottom: 50rpx;
}

.title {
	font-size: 44rpx;
	font-weight: bold;
	color: #333;
	letter-spacing: 2rpx;
}

.form-content {
	display: flex;
	flex-direction: column;
	gap: 30rpx;
}

.input-group {
	display: flex;
	gap: 20rpx;
}

.input {
	flex: 1;
	padding: 20rpx;
	border: 2rpx solid #e9ecef;
	border-radius: 10rpx;
	font-size: 28rpx;
	background: #f8f9fa;
}

.btn {
	padding: 20rpx 40rpx;
	border-radius: 10rpx;
	font-size: 28rpx;
	font-weight: bold;
	text-align: center;
	transition: all 0.3s ease;
}

.join-btn {
	background: #4facfe;
	color: white;
}

.create-btn {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	color: white;
}

.divider {
	display: flex;
	align-items: center;
	text-align: center;
	margin: 20rpx 0;
}

.divider::before,
.divider::after {
	content: '';
	flex: 1;
	border-bottom: 2rpx solid #e9ecef;
}

.divider-text {
	color: #868e96;
	padding: 0 20rpx;
	font-size: 24rpx;
}
</style>