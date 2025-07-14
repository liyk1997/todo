<template>
	<view class="content">
		<!-- 顶部导航 -->
		<view class="header">
			<view class="title-row">
				<text class="title">Todo List</text>
				<text class="room-info">房间号：{{ roomToken }}</text>
			</view>
			<view class="header-actions">
				<button class="action-btn" @click="showTrash">垃圾桶({{ trashCount }})</button>
				<button class="action-btn" @click="showSettings">设置</button>
				<button class="exit-btn" @click="exitRoom">退出房间</button>
			</view>
		</view>
		
		<!-- 筛选和排序 -->
		<view class="filter-bar">
			<view class="filter-item">
				<text class="filter-label">优先级:</text>
				<picker @change="onPriorityFilterChange" :value="priorityFilterIndex" :range="priorityFilterOptions">
					<view class="picker">{{ priorityFilterOptions[priorityFilterIndex] }}</view>
				</picker>
			</view>
			<view class="filter-item">
				<text class="filter-label">状态:</text>
				<picker @change="onStatusFilterChange" :value="statusFilterIndex" :range="statusFilterOptions">
					<view class="picker">{{ statusFilterOptions[statusFilterIndex] }}</view>
				</picker>
			</view>
		</view>
		
		<!-- 任务输入区域 -->
		<view class="input-area" v-if="!showTaskForm">
			<input class="task-input" v-model="newTask" placeholder="请输入任务" @confirm="showTaskForm = true" />
			<button class="add-btn" @click="showTaskForm = true">详细添加</button>
		</view>
		
		<!-- 详细任务表单 -->
		<view class="task-form" v-if="showTaskForm">
			<view class="form-row">
				<input class="form-input" v-model="taskForm.text" placeholder="任务标题" />
			</view>
			<view class="form-row">
				<textarea class="form-textarea" v-model="taskForm.description" placeholder="任务描述（可选）" />
			</view>
			<view class="form-row">
				<text class="form-label">优先级:</text>
				<picker @change="onPriorityChange" :value="priorityIndex" :range="priorityOptions">
					<view class="picker priority-{{ taskForm.priority }}">{{ priorityLabels[taskForm.priority] }}</view>
				</picker>
			</view>
			<view class="form-row">
				<text class="form-label">截止日期:</text>
				<picker mode="date" @change="onDateChange" :value="taskForm.due_date">
					<view class="picker">{{ taskForm.due_date || '选择日期' }}</view>
				</picker>
			</view>
			<view class="form-row">
				<input class="form-input" v-model="tagInput" placeholder="添加标签（回车确认）" @confirm="addTag" />
				<view class="tags">
					<view v-for="(tag, index) in taskForm.tags" :key="index" class="tag">
						{{ tag }}
						<text class="tag-remove" @click="removeTag(index)">×</text>
					</view>
				</view>
			</view>
			<view class="form-actions">
				<button class="cancel-btn" @click="cancelTaskForm">取消</button>
				<button class="submit-btn" @click="submitTask">添加任务</button>
			</view>
		</view>
		
		<!-- 任务列表 -->
		<view class="todo-list">
			<view v-for="task in filteredTasks" :key="task.id" class="todo-item" :class="{ 'completed': task.completed, 'overdue': isOverdue(task) }">
				<checkbox :checked="task.completed" @click="quickToggleTask(task.id)" />
				<view class="task-content" @click="showTaskDetail(task)">
					<view class="task-header">
						<text :class="['task-text', task.completed ? 'completed' : '']">{{ task.text }}</text>
						<view class="priority-badge priority-{{ task.priority }}">{{ priorityLabels[task.priority] }}</view>
					</view>
					<view class="task-meta">
						<text class="task-creator">{{ task.creator }}</text>
						<text v-if="task.due_date" class="task-due-date" :class="{ 'overdue': isOverdue(task) }">
							{{ formatDate(task.due_date) }}
						</text>
					</view>
					<view v-if="task.tags && task.tags.length" class="task-tags">
						<view v-for="tag in task.tags" :key="tag" class="task-tag">{{ tag }}</view>
					</view>
					<view v-if="task.description" class="task-description">{{ task.description }}</view>
				</view>
				<view class="task-actions">
					<text class="action-btn edit" @click="editTask(task)">编辑</text>
					<text class="action-btn delete" @click="deleteTask(task.id)">删除</text>
				</view>
			</view>
		</view>
		
		<!-- 垃圾桶弹窗 -->
		<view v-if="showTrashModal" class="modal-overlay" @click="showTrashModal = false">
			<view class="modal-content" @click.stop>
				<view class="modal-header">
					<text class="modal-title">垃圾桶</text>
					<text class="modal-close" @click="showTrashModal = false">×</text>
				</view>
				<view class="trash-list">
					<view v-for="task in trashTasks" :key="task.id" class="trash-item">
						<view class="task-info">
							<text class="task-text">{{ task.text }}</text>
							<text class="delete-time">删除于: {{ formatDate(task.deleted_at) }}</text>
						</view>
						<view class="trash-actions">
							<button class="restore-btn" @click="restoreTaskFromTrash(task.id)">恢复</button>
							<button class="permanent-delete-btn" @click="permanentDeleteTask(task.id)">永久删除</button>
						</view>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 设置弹窗 -->
		<view v-if="showSettingsModal" class="modal-overlay" @click="showSettingsModal = false">
			<view class="modal-content" @click.stop>
				<view class="modal-header">
					<text class="modal-title">设置</text>
					<text class="modal-close" @click="showSettingsModal = false">×</text>
				</view>
				<view class="settings-list">
					<view class="setting-item">
						<text class="setting-label">当前环境:</text>
						<picker @change="onEnvironmentChange" :value="environmentIndex" :range="environmentOptions">
							<view class="picker">{{ environmentOptions[environmentIndex] }}</view>
						</picker>
					</view>
					<view class="setting-item">
						<text class="setting-label">轮询间隔:</text>
						<text class="setting-value">{{ config.pollingInterval }}ms</text>
					</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script lang="ts">
import Vue from 'vue';
import {
	Task,
	TaskCreate,
	TaskUpdate,
	Room,
	startPolling,
	stopPolling,
	getRoomTasks,
	createTask,
	updateTask,
	toggleTask,
	deleteTask,
	getTrashTasks,
	restoreTask
} from '../../api/todo';
import { config } from '../../config';

export default Vue.extend({
	data() {
		return {
			newTask: '',
			tasks: [] as Task[],
			roomToken: '',
			userName: '',
			mode: 'create',
			// 任务表单相关
			showTaskForm: false,
			taskForm: {
				text: '',
				description: '',
				priority: 'medium',
				due_date: '',
				tags: [] as string[]
			},
			tagInput: '',
			// 筛选相关
			priorityFilterIndex: 0,
			priorityFilterOptions: ['全部', '高', '中', '低'],
			statusFilterIndex: 0,
			statusFilterOptions: ['全部', '未完成', '已完成'],
			// 垃圾桶相关
			showTrashModal: false,
			trashTasks: [] as Task[],
			trashCount: 0,
			// 设置相关
			showSettingsModal: false,
			environmentIndex: 0,
			environmentOptions: ['开发环境', '生产环境', '本地环境'],
			// 优先级相关
			priorityIndex: 1,
			priorityOptions: ['high', 'medium', 'low'],
			priorityLabels: {
				high: '高',
				medium: '中',
				low: '低'
			},
			config: config,
			// 编辑任务相关
			editingTaskId: null
		}
	},
		computed: {
			filteredTasks() {
				let filtered = (this as any).tasks.filter((task: Task) => !task.is_deleted);
				
				// 优先级筛选
				if ((this as any).priorityFilterIndex > 0) {
					const priorityMap: any = { 1: 'high', 2: 'medium', 3: 'low' };
					filtered = filtered.filter((task: Task) => task.priority === priorityMap[(this as any).priorityFilterIndex]);
				}
				
				// 状态筛选
				if ((this as any).statusFilterIndex === 1) {
					filtered = filtered.filter((task: Task) => !task.completed);
				} else if ((this as any).statusFilterIndex === 2) {
					filtered = filtered.filter((task: Task) => task.completed);
				}
				
				// 按优先级和截止日期排序
				return filtered.sort((a: Task, b: Task) => {
					// 首先按完成状态排序（未完成在前）
					if (a.completed !== b.completed) {
						return a.completed ? 1 : -1;
					}
					
					// 然后按优先级排序
					const priorityOrder: any = { high: 3, medium: 2, low: 1 };
					const priorityDiff = priorityOrder[b.priority] - priorityOrder[a.priority];
					if (priorityDiff !== 0) return priorityDiff;
					
					// 最后按截止日期排序
					if (a.due_date && b.due_date) {
						return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
					}
					if (a.due_date) return -1;
					if (b.due_date) return 1;
					return 0;
				});
			}
		},
		onLoad(options) {
		console.log('index onLoad 收到参数:', options);
		
		if (options && options.token) {
			console.log('收到有效的 token:', options.token);
			this.roomToken = options.token;
			this.mode = options.mode || 'create';
			console.log('设置 mode:', this.mode);
			this.initRoom();
		} else {
			console.warn('没有收到 token，准备跳转回房间页面');
			uni.redirectTo({ 
				url: '/pages/room/room',
				success: () => {
					console.log('跳转回房间页面成功');
				},
				fail: (err) => {
					console.error('跳转回房间页面失败:', err);
				}
			});
		}
	},
	onUnload() {
			stopPolling();
		},

	async onPullDownRefresh() {
		console.log('开始下拉刷新');
		try {
			this.tasks = await getRoomTasks(this.roomToken);
			console.log('刷新任务列表成功');
		} catch (error) {
			console.error('刷新任务列表失败:', error);
			uni.showToast({
				title: '刷新任务列表失败',
				icon: 'none'
			});
		} finally {
			uni.stopPullDownRefresh();
		}
	},
	methods: {
			async initRoom() {
				// 获取或设置用户名
				this.userName = await this.getUserName();

				// 获取现有任务列表
				try {
					this.tasks = await getRoomTasks(this.roomToken);
					await this.loadTrashCount();
					
					// 开始轮询任务列表
					startPolling(this.roomToken, (tasks) => {
						this.tasks = tasks;
						this.loadTrashCount();
					});
				} catch (error) {
					console.error('获取任务列表失败:', error);
					uni.showToast({
						title: '获取任务列表失败',
						icon: 'none'
					});
				}
			},
			
			async loadTrashCount() {
				try {
					const response = await getTrashTasks(this.roomToken);
					this.trashCount = response.length;
				} catch (error) {
					console.error('获取垃圾桶数量失败:', error);
				}
			},
			
			async loadTasks() {
				try {
					const response = await getRoomTasks(this.roomToken);
					this.tasks = response;
					await this.loadTrashCount();
				} catch (error) {
					console.error('获取任务失败:', error);
					uni.showToast({
						title: '获取任务失败',
						icon: 'none'
					});
				}
			},
		async getUserName() {
			// 从本地存储获取用户名，如果没有则提示输入
			let name = uni.getStorageSync('userName');
			if (!name) {
				await new Promise((resolve) => {
					uni.showModal({
						title: '请输入您的名字',
						editable: true,
						success: (res) => {
							if (res.confirm && res.content) {
								name = res.content;
								uni.setStorageSync('userName', name);
							}
							resolve(null);
						}
					});
				});
			}
			return name || '匿名用户';
		},
		// 任务表单相关方法
		showTaskDetail(task) {
			// 显示任务详情（可以扩展为编辑功能）
			console.log('显示任务详情:', task);
		},
		
		cancelTaskForm() {
				this.showTaskForm = false;
				this.editingTaskId = null;
				this.resetTaskForm();
			},
		
		resetTaskForm() {
			this.taskForm = {
				text: '',
				description: '',
				priority: 'medium',
				due_date: '',
				tags: []
			};
			this.tagInput = '';
			this.priorityIndex = 1;
		},
		
		addTag() {
			if (this.tagInput.trim() && !this.taskForm.tags.includes(this.tagInput.trim())) {
				this.taskForm.tags.push(this.tagInput.trim());
				this.tagInput = '';
			}
		},
		
		removeTag(index) {
			this.taskForm.tags.splice(index, 1);
		},
		
		onPriorityChange(e) {
			this.priorityIndex = e.detail.value;
			this.taskForm.priority = this.priorityOptions[e.detail.value];
		},
		
		onDateChange(e) {
			this.taskForm.due_date = e.detail.value;
		},
		
		async submitTask() {
				if (!this.taskForm.text.trim()) {
					uni.showToast({
						title: '请输入任务标题',
						icon: 'none'
					});
					return;
				}
				
				try {
					if (this.editingTaskId) {
						// 编辑任务
					const updateData: any = {
						text: this.taskForm.text,
						description: this.taskForm.description,
						priority: this.taskForm.priority as 'low' | 'medium' | 'high' | 'urgent',
						tags: this.taskForm.tags
					};
					
					if (this.taskForm.due_date) {
						updateData.due_date = this.taskForm.due_date;
					}
						
						await updateTask(this.editingTaskId, updateData);
						
						uni.showToast({
							title: '更新成功',
							icon: 'success'
						});
					} else {
						// 创建新任务
					const taskData: any = {
						room_id: this.roomToken,
						text: this.taskForm.text,
						creator: this.userName,
						description: this.taskForm.description,
						priority: this.taskForm.priority as 'low' | 'medium' | 'high' | 'urgent',
						tags: this.taskForm.tags
					};
					
					if (this.taskForm.due_date) {
						taskData.due_date = this.taskForm.due_date;
					}
						
						await createTask(taskData);
						
						uni.showToast({
							title: '添加成功',
							icon: 'success'
						});
					}
					
					this.cancelTaskForm();
					await this.loadTasks();
				} catch (error) {
					console.error('操作失败:', error);
					uni.showToast({
						title: this.editingTaskId ? '更新失败' : '添加失败',
						icon: 'none'
					});
				}
			},
		
		async addTask() {
			if (!this.newTask.trim()) {
				this.showTaskForm = true;
				this.taskForm.text = this.newTask;
				return;
			}
			
			try {
				await createTask({
					room_id: this.roomToken,
					text: this.newTask,
					creator: this.userName,
					priority: 'medium' as 'medium'
				});
				
				this.newTask = '';
				
				uni.showToast({
					title: '添加成功',
					icon: 'success'
				});
			} catch (error) {
				console.error('添加任务失败:', error);
				uni.showToast({
					title: '添加任务失败',
					icon: 'none'
				});
			}
		},
		// 任务操作相关方法
		async quickToggleTask(taskId) {
			try {
				await toggleTask(taskId);
				await this.loadTasks();
			} catch (error) {
				console.error('切换任务状态失败:', error);
				uni.showToast({
					title: '操作失败',
					icon: 'none'
				});
			}
		},
		
		async toggleTask(taskId) {
			try {
				const task = this.tasks.find(t => t.id === taskId);
				if (task) {
					await updateTask(taskId, {
						completed: !task.completed
					});
					await this.loadTasks();
				}
			} catch (error) {
				console.error('更新任务状态失败:', error);
				uni.showToast({
					title: '更新任务状态失败',
					icon: 'none'
				});
			}
		},
		
		editTask(task) {
			// 编辑任务功能
			this.taskForm = {
				text: task.text,
				description: task.description || '',
				priority: task.priority || 'medium',
				due_date: task.due_date || '',
				tags: task.tags || []
			};
			this.priorityIndex = this.priorityOptions.indexOf(task.priority || 'medium');
			this.showTaskForm = true;
			this.editingTaskId = task.id;
		},

		async deleteTask(taskId) {
			try {
				await deleteTask(taskId, false); // 软删除
				await this.loadTasks();
				uni.showToast({
					title: '已移至垃圾桶',
					icon: 'success'
				});
			} catch (error) {
				console.error('删除任务失败:', error);
				uni.showToast({
					title: '删除任务失败',
					icon: 'none'
				});
			}
		},
		
		// 垃圾桶相关方法
		async showTrash() {
				try {
					const response = await getTrashTasks(this.roomToken);
					this.trashTasks = response;
					this.showTrashModal = true;
				} catch (error) {
					console.error('获取垃圾桶失败:', error);
					uni.showToast({
						title: '获取垃圾桶失败',
						icon: 'none'
					});
				}
			},
		
		async restoreTaskFromTrash(taskId) {
			try {
				await restoreTask(taskId);
				await this.showTrash(); // 刷新垃圾桶
				await this.loadTasks(); // 刷新任务列表
				uni.showToast({
					title: '任务已恢复',
					icon: 'success'
				});
			} catch (error) {
				console.error('恢复任务失败:', error);
				uni.showToast({
					title: '恢复任务失败',
					icon: 'none'
				});
			}
		},
		
		async permanentDeleteTask(taskId) {
			uni.showModal({
				title: '确认删除',
				content: '此操作将永久删除任务，无法恢复',
				success: async (res) => {
					if (res.confirm) {
						try {
							await deleteTask(taskId, true); // 硬删除
							await this.showTrash(); // 刷新垃圾桶
							uni.showToast({
								title: '任务已永久删除',
								icon: 'success'
							});
						} catch (error) {
							console.error('永久删除任务失败:', error);
							uni.showToast({
								title: '删除失败',
								icon: 'none'
							});
						}
					}
				}
			});
		},
		
		// 筛选相关方法
		onPriorityFilterChange(e) {
			this.priorityFilterIndex = e.detail.value;
		},
		
		onStatusFilterChange(e) {
			this.statusFilterIndex = e.detail.value;
		},
		
		// 设置相关方法
		showSettings() {
			this.showSettingsModal = true;
		},
		
		onEnvironmentChange(e) {
			this.environmentIndex = e.detail.value;
			const environments = ['development', 'production', 'local'];
			const { switchEnvironment } = require('../../config/index.ts');
			switchEnvironment(environments[e.detail.value]);
		},
		
		// 工具方法
		isOverdue(task) {
			if (!task.due_date || task.completed) return false;
			return new Date(task.due_date) < new Date();
		},
		
		formatDate(dateStr) {
			if (!dateStr) return '';
			const date = new Date(dateStr);
			return date.toLocaleDateString('zh-CN');
		},
		async exitRoom() {
			try {
				// 显示加载提示
				uni.showLoading({
					title: '退出房间中...'
				});

				// 停止轮询
				stopPolling();

				// 隐藏加载提示
				uni.hideLoading();

				// 显示成功提示
				await new Promise<void>((resolve) => {
					uni.showToast({
						title: '已退出房间',
						icon: 'success',
						duration: 1500,
						success: () => {
							setTimeout(resolve, 1500);
						}
					});
				});

				// 跳转回房间页面
				console.log('准备跳转回房间页面');
				uni.redirectTo({
					url: '/pages/room/room',
					success: () => {
						console.log('跳转回房间页面成功');
					},
					fail: (err) => {
						console.error('跳转回房间页面失败:', err);
					}
				});
			} catch (error) {
				console.error('退出房间失败:', error);
				uni.showToast({
					title: '退出房间失败',
					icon: 'none'
				});
			}
		}
	}
});
</script>

<style>
	.content {
		display: flex;
		flex-direction: column;
		padding: 40rpx;
		background-color: #f8f9fa;
		min-height: 100vh;
	}

	.header {
		margin-bottom: 50rpx;
		padding: 30rpx;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		border-radius: 16rpx;
		box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
	}

	.title-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 20rpx;
	}

	.title {
		font-size: 44rpx;
		font-weight: bold;
		color: #ffffff;
		letter-spacing: 2rpx;
	}

	.room-info {
		font-size: 28rpx;
		color: rgba(255, 255, 255, 0.9);
		background: rgba(255, 255, 255, 0.2);
		padding: 8rpx 20rpx;
		border-radius: 30rpx;
	}

	.exit-btn {
		background: rgba(255, 255, 255, 0.2);
		color: #ffffff;
		font-size: 28rpx;
		padding: 10rpx 30rpx;
		border-radius: 8rpx;
		border: 2rpx solid rgba(255, 255, 255, 0.3);
	}

	.input-area {
		display: flex;
		margin-bottom: 40rpx;
		box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
		border-radius: 12rpx;
		background: #ffffff;
		padding: 20rpx;
	}

	.task-input {
		flex: 1;
		padding: 24rpx;
		border: none;
		background: #f1f3f5;
		border-radius: 8rpx;
		margin-right: 20rpx;
		font-size: 28rpx;
	}

	.add-btn {
		background: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
		color: white;
		border-radius: 8rpx;
		padding: 0 40rpx;
		font-weight: 600;
		box-shadow: 0 2rpx 6rpx rgba(0, 0, 0, 0.1);
		transition: all 0.3s ease;
	}

	.todo-list {
		width: 100%;
		background: #ffffff;
		border-radius: 16rpx;
		box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
		overflow: hidden;
	}

	.todo-item {
		display: flex;
		align-items: center;
		padding: 30rpx;
		border-bottom: 2rpx solid #f1f3f5;
		transition: all 0.3s ease;
	}

	.todo-item:active {
		background-color: #f8f9fa;
	}

	.task-content {
		flex: 1;
		margin: 0 24rpx;
		display: flex;
		flex-direction: column;
		gap: 8rpx;
	}

	.task-text {
		font-size: 30rpx;
		color: #495057;
	}

	.task-creator {
		font-size: 24rpx;
		color: #868e96;
	}

	.completed {
		text-decoration: line-through;
		color: #adb5bd;
	}

	.delete-btn {
		color: #fa5252;
		font-size: 28rpx;
		padding: 10rpx 20rpx;
	}

	/* 新增样式 */
	.header-actions {
		display: flex;
		gap: 20rpx;
		align-items: center;
	}

	.action-btn {
		background: rgba(255, 255, 255, 0.2);
		color: #ffffff;
		font-size: 24rpx;
		padding: 8rpx 20rpx;
		border-radius: 6rpx;
		border: 1rpx solid rgba(255, 255, 255, 0.3);
	}

	.filter-bar {
		display: flex;
		gap: 30rpx;
		margin-bottom: 30rpx;
		padding: 20rpx;
		background: #ffffff;
		border-radius: 12rpx;
		box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
	}

	.filter-item {
		display: flex;
		align-items: center;
		gap: 10rpx;
	}

	.filter-label {
		font-size: 26rpx;
		color: #495057;
		font-weight: 500;
	}

	.picker {
		padding: 8rpx 16rpx;
		background: #f8f9fa;
		border-radius: 6rpx;
		font-size: 24rpx;
		color: #495057;
		border: 1rpx solid #dee2e6;
	}

	.task-form {
		background: #ffffff;
		border-radius: 16rpx;
		padding: 30rpx;
		margin-bottom: 30rpx;
		box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
	}

	.form-row {
		margin-bottom: 30rpx;
	}

	.form-input {
		width: 100%;
		padding: 20rpx;
		border: 2rpx solid #dee2e6;
		border-radius: 8rpx;
		font-size: 28rpx;
		background: #ffffff;
	}

	.form-textarea {
		width: 100%;
		padding: 20rpx;
		border: 2rpx solid #dee2e6;
		border-radius: 8rpx;
		font-size: 28rpx;
		min-height: 120rpx;
		background: #ffffff;
	}

	.form-label {
		font-size: 26rpx;
		color: #495057;
		font-weight: 500;
		margin-bottom: 10rpx;
		display: block;
	}

	.tags {
		display: flex;
		flex-wrap: wrap;
		gap: 10rpx;
		margin-top: 10rpx;
	}

	.tag {
		background: #e3f2fd;
		color: #1976d2;
		padding: 6rpx 12rpx;
		border-radius: 20rpx;
		font-size: 22rpx;
		display: flex;
		align-items: center;
		gap: 6rpx;
	}

	.tag-remove {
		color: #f44336;
		font-weight: bold;
		cursor: pointer;
	}

	.form-actions {
		display: flex;
		gap: 20rpx;
		justify-content: flex-end;
	}

	.cancel-btn {
		background: #6c757d;
		color: white;
		padding: 16rpx 32rpx;
		border-radius: 8rpx;
		font-size: 26rpx;
	}

	.submit-btn {
		background: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
		color: white;
		padding: 16rpx 32rpx;
		border-radius: 8rpx;
		font-size: 26rpx;
	}

	.task-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 8rpx;
	}

	.priority-badge {
		padding: 4rpx 12rpx;
		border-radius: 12rpx;
		font-size: 20rpx;
		font-weight: 500;
	}

	.priority-high {
		background: #ffebee;
		color: #c62828;
	}

	.priority-medium {
		background: #fff3e0;
		color: #ef6c00;
	}

	.priority-low {
		background: #e8f5e8;
		color: #2e7d32;
	}

	.task-meta {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 8rpx;
	}

	.task-due-date {
		font-size: 22rpx;
		color: #6c757d;
	}

	.task-due-date.overdue {
		color: #dc3545;
		font-weight: 500;
	}

	.task-tags {
		display: flex;
		flex-wrap: wrap;
		gap: 6rpx;
		margin-bottom: 8rpx;
	}

	.task-tag {
		background: #f8f9fa;
		color: #6c757d;
		padding: 2rpx 8rpx;
		border-radius: 10rpx;
		font-size: 20rpx;
	}

	.task-description {
		font-size: 24rpx;
		color: #6c757d;
		line-height: 1.4;
		margin-top: 8rpx;
	}

	.task-actions {
		display: flex;
		gap: 15rpx;
	}

	.task-actions .action-btn {
		background: transparent;
		color: #6c757d;
		font-size: 24rpx;
		padding: 8rpx 12rpx;
		border-radius: 4rpx;
		border: none;
	}

	.task-actions .edit {
		color: #007bff;
	}

	.task-actions .delete {
		color: #dc3545;
	}

	.todo-item.overdue {
		border-left: 4rpx solid #dc3545;
	}

	.modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
	}

	.modal-content {
		background: #ffffff;
		border-radius: 16rpx;
		width: 90%;
		max-width: 600rpx;
		max-height: 80vh;
		overflow: hidden;
		box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.15);
	}

	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 30rpx;
		border-bottom: 2rpx solid #f1f3f5;
	}

	.modal-title {
		font-size: 32rpx;
		font-weight: 600;
		color: #212529;
	}

	.modal-close {
		font-size: 40rpx;
		color: #6c757d;
		cursor: pointer;
	}

	.trash-list {
		max-height: 60vh;
		overflow-y: auto;
		padding: 20rpx;
	}

	.trash-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 20rpx;
		border-bottom: 1rpx solid #f1f3f5;
	}

	.task-info {
		flex: 1;
	}

	.delete-time {
		font-size: 22rpx;
		color: #6c757d;
		margin-top: 4rpx;
	}

	.trash-actions {
		display: flex;
		gap: 10rpx;
	}

	.restore-btn {
		background: #28a745;
		color: white;
		padding: 8rpx 16rpx;
		border-radius: 4rpx;
		font-size: 22rpx;
	}

	.permanent-delete-btn {
		background: #dc3545;
		color: white;
		padding: 8rpx 16rpx;
		border-radius: 4rpx;
		font-size: 22rpx;
	}

	.settings-list {
		padding: 20rpx;
	}

	.setting-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 20rpx 0;
		border-bottom: 1rpx solid #f1f3f5;
	}

	.setting-label {
		font-size: 28rpx;
		color: #495057;
	}

	.setting-value {
		font-size: 26rpx;
		color: #6c757d;
	}
	.delete-btn:active {
		background-color: #ffe3e3;
	}
</style>
