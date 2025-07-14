import { ref } from '@vue/composition-api';
import { config } from '../config';

const API_BASE = config.apiBaseUrl;
let ws: WebSocket | null = null;

export interface Task {
    id: number;
    text: string;
    completed: boolean;
    creator: string;
    room_id: string;
    priority: 'low' | 'medium' | 'high' | 'urgent';
    due_date?: string;
    tags: string[];
    description?: string;
    is_deleted: boolean;
    created_at: string;
    updated_at?: string;
    deleted_at?: string;
}

export interface TaskCreate {
    text: string;
    creator: string;
    room_id: string;
    priority?: 'low' | 'medium' | 'high' | 'urgent';
    due_date?: string;
    tags?: string[];
    description?: string;
}

export interface TaskUpdate {
    text?: string;
    completed?: boolean;
    priority?: 'low' | 'medium' | 'high' | 'urgent';
    due_date?: string;
    tags?: string[];
    description?: string;
}

export interface Room {
    id: number;
    token: string;
    created_at: string;
    active_users: string[];
}

// 轮询间隔（毫秒）
const POLLING_INTERVAL = config.pollingInterval;

// 轮询状态
let pollingTimer: number | null = null;
let isPolling = false;

// 通用请求处理函数
async function request<T>(options: UniApp.RequestOptions): Promise<T> {
    return new Promise((resolve, reject) => {
        uni.request({
            ...options,
            success: (res) => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    resolve(res.data as T);
                } else {
                    reject(new Error(`请求失败: ${res.statusCode}`));
                }
            },
            fail: (err) => {
                reject(new Error(`网络请求失败: ${err.errMsg}`));
            }
        });
    });
}

// 创建新房间
export async function createRoom(): Promise<Room> {
    return request<Room>({
        url: `${API_BASE}/rooms/create`,
        method: 'POST'
    });
}

// 加入房间
export async function joinRoom(token: string): Promise<Room> {
    return request<Room>({
        url: `${API_BASE}/rooms/${token}`,
        method: 'GET'
    });
}

// 获取房间任务列表
export async function getRoomTasks(roomId: string): Promise<Task[]> {
    return request<Task[]>({
        url: `${API_BASE}/rooms/${roomId}/tasks`,
        method: 'GET'
    });
}

// 创建新任务
export async function createTask(task: TaskCreate): Promise<Task> {
    return request<Task>({
        url: `${API_BASE}/tasks`,
        method: 'POST',
        data: task
    });
}

// 更新任务状态
export async function updateTask(taskId: number, updates: TaskUpdate): Promise<Task> {
    return request<Task>({
        url: `${API_BASE}/tasks/${taskId}`,
        method: 'PUT',
        data: updates
    });
}

export async function toggleTask(taskId: number): Promise<Task> {
    return request<Task>({
        url: `${API_BASE}/tasks/${taskId}/toggle`,
        method: 'PUT'
    });
}

// 删除任务
export async function deleteTask(taskId: number, permanent: boolean = false): Promise<void> {
    return request<void>({
        url: `${API_BASE}/tasks/${taskId}?permanent=${permanent}`,
        method: 'DELETE'
    });
}

export async function getTrashTasks(roomId: string): Promise<Task[]> {
    return request<Task[]>({
        url: `${API_BASE}/rooms/${roomId}/trash`,
        method: 'GET'
    });
}

export async function restoreTask(taskId: number): Promise<void> {
    return request<void>({
        url: `${API_BASE}/tasks/${taskId}/restore`,
        method: 'POST'
    });
}

// 轮询状态
const pollingStatus = ref<'polling' | 'stopped'>('stopped');

// 开始轮询
export function startPolling(roomId: string, onUpdate: (tasks: Task[]) => void) {
    if (isPolling) {
        console.log('已经在轮询中');
        return;
    }

    isPolling = true;
    pollingStatus.value = 'polling';
    console.log('开始轮询任务列表');

    async function poll() {
        if (!isPolling) return;

        try {
            const tasks = await getRoomTasks(roomId);
            onUpdate(tasks);
        } catch (error) {
            console.error('轮询任务列表失败:', error);
            uni.showToast({
                title: '获取任务列表失败',
                icon: 'none',
                duration: 2000
            });
        }

        pollingTimer = setTimeout(poll, POLLING_INTERVAL);
    }

    poll();
}

// 停止轮询
export function stopPolling() {
    console.log('停止轮询任务列表');
    isPolling = false;
    pollingStatus.value = 'stopped';
    
    if (pollingTimer) {
        clearTimeout(pollingTimer);
        pollingTimer = null;
    }
}