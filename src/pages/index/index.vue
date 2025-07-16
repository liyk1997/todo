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
					<view class="setting-item" @click="switchUser">
						<text class="setting-label">当前用户:</text>
						<text class="setting-value">{{ userName }}</text>
						<text class="setting-action">点击切换</text>
					</view>
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

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
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

const config = { pollingInterval: 3000 }; // Temporary config

const newTask = ref('');
const tasks = ref<Task[]>([]);
const roomToken = ref('');
const userName = ref('');
const mode = ref('create');
const showTaskForm = ref(false);
const taskForm = ref({
  text: '',
  description: '',
  priority: 'medium',
  due_date: '',
  tags: [] as string[],
});
const tagInput = ref('');
const priorityFilterIndex = ref(0);
const priorityFilterOptions = ['全部', '高', '中', '低'];
const statusFilterIndex = ref(0);
const statusFilterOptions = ['全部', '未完成', '已完成'];
const showTrashModal = ref(false);
const trashTasks = ref<Task[]>([]);
const trashCount = ref(0);
const showSettingsModal = ref(false);
const environmentIndex = ref(0);
const environmentOptions = ['开发环境', '生产环境', '本地环境'];
const priorityIndex = ref(1);
const priorityOptions = ['high', 'medium', 'low'];
const priorityLabels = {
  high: '高',
  medium: '中',
  low: '低',
};
const editingTaskId = ref(null);

const filteredTasks = computed(() => {
  let filtered = tasks.value.filter((task: Task) => !task.is_deleted);

  // 优先级筛选
  if (priorityFilterIndex.value > 0) {
    const priorityMap: any = { 1: 'high', 2: 'medium', 3: 'low' };
    filtered = filtered.filter((task: Task) => task.priority === priorityMap[priorityFilterIndex.value]);
  }

  // 状态筛选
  if (statusFilterIndex.value === 1) {
    filtered = filtered.filter((task: Task) => !task.completed);
  } else if (statusFilterIndex.value === 2) {
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
});

onLoad((options: any) => {
  console.log('index onLoad 收到参数:', options);

  if (options && options.token) {
    console.log('收到有效的 token:', options.token);
    roomToken.value = options.token;
    mode.value = options.mode || 'create';
    console.log('设置 mode:', mode.value);
    initRoom();
  } else {
    console.warn('没有收到 token，准备跳转回房间页面');
    uni.redirectTo({
      url: '/pages/room/room',
      success: () => {
        console.log('跳转回房间页面成功');
      },
      fail: (err) => {
        console.error('跳转回房间页面失败:', err);
      },
    });
  }
});

onUnmounted(() => {
  stopPolling();
});

onPullDownRefresh(async () => {
  console.log('开始下拉刷新');
  try {
    tasks.value = await getRoomTasks(roomToken.value);
    console.log('刷新任务列表成功');
  } catch (error) {
    console.error('刷新任务列表失败:', error);
    uni.showToast({
      title: '刷新任务列表失败',
      icon: 'none',
    });
  } finally {
    uni.stopPullDownRefresh();
  }
});

async function initRoom() {
  // 获取或设置用户名
  userName.value = await getUserName();

  // 获取现有任务列表
  try {
    tasks.value = await getRoomTasks(roomToken.value);
    await loadTrashCount();

    // 开始轮询任务列表
    startPolling(roomToken.value, (newTasks) => {
      tasks.value = newTasks;
      loadTrashCount();
    });
  } catch (error) {
    console.error('获取任务列表失败:', error);
    uni.showToast({
      title: '获取任务列表失败',
      icon: 'none',
    });
  }
}
			
async function loadTrashCount() {
  try {
    const response = await getTrashTasks(roomToken.value);
    trashCount.value = response.length;
  } catch (error) {
    console.error('获取垃圾桶数量失败:', error);
  }
}
			
async function loadTasks() {
  try {
    const response = await getRoomTasks(roomToken.value);
    tasks.value = response;
    await loadTrashCount();
  } catch (error) {
    console.error('获取任务失败:', error);
    uni.showToast({
      title: '获取任务失败',
      icon: 'none',
    });
  }
}
async function getUserName() {
  // 从本地存储获取用户名，如果没有则提示输入
  let name = uni.getStorageSync('todoAppUser');
  if (!name) {
    await new Promise((resolve) => {
      uni.showModal({
        title: '欢迎使用Todo应用',
        content: '请输入您的姓名开始使用',
        editable: true,
        placeholderText: '请输入您的姓名',
        success: (res) => {
          if (res.confirm && res.content && res.content.trim()) {
            name = res.content.trim();
            uni.setStorageSync('todoAppUser', name);
            uni.showToast({
              title: `欢迎，${name}！`,
              icon: 'success',
            });
          } else {
            name = '匿名用户';
          }
          resolve(null);
        },
      });
    });
  }
  return name || '匿名用户';
}
// 任务表单相关方法
function showTaskDetail(task: Task) {
  // 显示任务详情（可以扩展为编辑功能）
  console.log('显示任务详情:', task);
}
		
function cancelTaskForm() {
  showTaskForm.value = false;
  editingTaskId.value = null;
  resetTaskForm();
}
		
function resetTaskForm() {
  taskForm.value = {
    text: '',
    description: '',
    priority: 'medium',
    due_date: '',
    tags: [],
  };
  tagInput.value = '';
  priorityIndex.value = 1;
}
		
function addTag() {
  if (tagInput.value.trim() && !taskForm.value.tags.includes(tagInput.value.trim())) {
    taskForm.value.tags.push(tagInput.value.trim());
    tagInput.value = '';
  }
}
		
function removeTag(index: number) {
  taskForm.value.tags.splice(index, 1);
}
		
function onPriorityChange(e: any) {
  priorityIndex.value = e.detail.value;
  taskForm.value.priority = priorityOptions[e.detail.value];
}
		
function onDateChange(e: any) {
  taskForm.value.due_date = e.detail.value;
}
		
async function submitTask() {
  if (!taskForm.value.text.trim()) {
    uni.showToast({
      title: '请输入任务标题',
      icon: 'none',
    });
    return;
  }

  try {
    if (editingTaskId.value) {
      // 编辑任务
      const updateData: any = {
        text: taskForm.value.text,
        description: taskForm.value.description,
        priority: taskForm.value.priority as 'low' | 'medium' | 'high' | 'urgent',
        tags: taskForm.value.tags,
      };

      if (taskForm.value.due_date) {
        updateData.due_date = taskForm.value.due_date;
      }

      await updateTask(editingTaskId.value, updateData);

      uni.showToast({
        title: '更新成功',
        icon: 'success',
      });
    } else {
      // 创建新任务
      const taskData: any = {
        room_id: roomToken.value,
        text: taskForm.value.text,
        creator: userName.value,
        description: taskForm.value.description,
        priority: taskForm.value.priority as 'low' | 'medium' | 'high' | 'urgent',
        tags: taskForm.value.tags,
      };

      if (taskForm.value.due_date) {
        taskData.due_date = taskForm.value.due_date;
      }

      await createTask(taskData);

      uni.showToast({
        title: '添加成功',
        icon: 'success',
      });
    }

    cancelTaskForm();
    await loadTasks();
  } catch (error) {
    console.error('操作失败:', error);
    uni.showToast({
      title: editingTaskId.value ? '更新失败' : '添加失败',
      icon: 'none',
    });
  }
}
		
async function addTask() {
  if (!newTask.value.trim()) {
    showTaskForm.value = true;
    taskForm.value.text = newTask.value;
    return;
  }

  try {
    await createTask({
      room_id: roomToken.value,
      text: newTask.value,
      creator: userName.value,
      priority: 'medium' as 'medium',
    });

    newTask.value = '';

    uni.showToast({
      title: '添加成功',
      icon: 'success',
    });
  } catch (error) {
    console.error('添加任务失败:', error);
    uni.showToast({
      title: '添加任务失败',
      icon: 'none',
    });
  }
}
// 任务操作相关方法
async function quickToggleTask(taskId: string) {
  try {
    await toggleTask(taskId);
    await loadTasks();
  } catch (error) {
    console.error('切换任务状态失败:', error);
    uni.showToast({
      title: '操作失败',
      icon: 'none',
    });
  }
}
		
async function toggleTask(taskId: string) {
  try {
    const task = tasks.value.find(t => t.id === taskId);
    if (task) {
      await updateTask(taskId, {
        completed: !task.completed,
      });
      await loadTasks();
    }
  } catch (error) {
    console.error('更新任务状态失败:', error);
    uni.showToast({
      title: '更新任务状态失败',
      icon: 'none',
    });
  }
}
		
function editTask(task: Task) {
  // 编辑任务功能
  taskForm.value = {
    text: task.text,
    description: task.description || '',
    priority: task.priority || 'medium',
    due_date: task.due_date || '',
    tags: task.tags || [],
  };
  priorityIndex.value = priorityOptions.indexOf(task.priority || 'medium');
  showTaskForm.value = true;
  editingTaskId.value = task.id;
}

async function deleteTask(taskId: string) {
  try {
    await deleteTask(taskId, false); // 软删除
    await loadTasks();
    uni.showToast({
      title: '已移至垃圾桶',
      icon: 'success',
    });
  } catch (error) {
    console.error('删除任务失败:', error);
    uni.showToast({
      title: '删除任务失败',
      icon: 'none',
    });
  }
}
		
// 垃圾桶相关方法
async function showTrash() {
  try {
    const response = await getTrashTasks(roomToken.value);
    trashTasks.value = response;
    showTrashModal.value = true;
  } catch (error) {
    console.error('获取垃圾桶失败:', error);
    uni.showToast({
      title: '获取垃圾桶失败',
      icon: 'none',
    });
  }
}
		
async function restoreTaskFromTrash(taskId: string) {
  try {
    await restoreTask(taskId);
    await showTrash(); // 刷新垃圾桶
    await loadTasks(); // 刷新任务列表
    uni.showToast({
      title: '任务已恢复',
      icon: 'success',
    });
  } catch (error) {
    console.error('恢复任务失败:', error);
    uni.showToast({
      title: '恢复任务失败',
      icon: 'none',
    });
  }
}
		
async function permanentDeleteTask(taskId: string) {
  uni.showModal({
    title: '确认删除',
    content: '此操作将永久删除任务，无法恢复',
    success: async (res) => {
      if (res.confirm) {
        try {
          await deleteTask(taskId, true); // 硬删除
          await showTrash(); // 刷新垃圾桶
          uni.showToast({
            title: '任务已永久删除',
            icon: 'success',
          });
        } catch (error) {
          console.error('永久删除任务失败:', error);
          uni.showToast({
            title: '删除失败',
            icon: 'none',
          });
        }
      }
    },
  });
}
		
// 筛选相关方法
function onPriorityFilterChange(e: any) {
  priorityFilterIndex.value = e.detail.value;
}
		
function onStatusFilterChange(e: any) {
  statusFilterIndex.value = e.detail.value;
}
		
// 设置相关方法
function showSettings() {
  showSettingsModal.value = true;
}
		
function onEnvironmentChange(e: any) {
  environmentIndex.value = e.detail.value;
  const environments = ['development', 'production', 'local'];
  const { switchEnvironment } = require('../../config/index.ts');
  switchEnvironment(environments[e.detail.value]);
}
		
// 用户切换方法
async function switchUser() {
  uni.showModal({
    title: '切换用户',
    content: '请输入新的用户名',
    editable: true,
    placeholderText: '请输入您的姓名',
    success: (res) => {
      if (res.confirm && res.content && res.content.trim()) {
        const newName = res.content.trim();
        uni.setStorageSync('todoAppUser', newName);
        userName.value = newName;
        showSettingsModal.value = false;
        uni.showToast({
          title: `已切换到用户：${newName}`,
          icon: 'success',
        });
      }
    },
  });
}
		
// 工具方法
function isOverdue(task: Task) {
  if (!task.due_date || task.completed) return false;
  return new Date(task.due_date) < new Date();
}
		
function formatDate(dateStr: string) {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString('zh-CN');
}
async function exitRoom() {
  try {
    // 显示加载提示
    uni.showLoading({
      title: '退出房间中...',
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
        },
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
      },
    });
  } catch (error) {
    console.error('退出房间失败:', error);
    uni.showToast({
      title: '退出房间失败',
      icon: 'none',
    });
  }
}
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
	
	.setting-action {
		font-size: 24rpx;
		color: #007bff;
		margin-left: 10rpx;
	}
	
	.setting-item:active {
		background-color: #f8f9fa;
	}
	
	.delete-btn:active {
		background-color: #ffe3e3;
	}
</style>
