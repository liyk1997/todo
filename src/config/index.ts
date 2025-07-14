// 环境配置
export interface Config {
  apiBaseUrl: string;
  wsBaseUrl: string;
  environment: 'development' | 'production' | 'local';
  pollingInterval: number;
  enableNotifications: boolean;
}

// 默认配置
const defaultConfig: Config = {
  apiBaseUrl: 'http://localhost:8000',
  wsBaseUrl: 'ws://localhost:8000',
  environment: 'development',
  pollingInterval: 3000,
  enableNotifications: true
};

// 环境配置映射
const envConfigs: Record<string, Partial<Config>> = {
  development: {
    apiBaseUrl: 'http://localhost:8000',
    wsBaseUrl: 'ws://localhost:8000',
    environment: 'development'
  },
  production: {
    apiBaseUrl: 'http://28k26e2067.wicp.vip',
    wsBaseUrl: 'ws://28k26e2067.wicp.vip',
    environment: 'production'
  },
  local: {
    apiBaseUrl: 'http://127.0.0.1:8000',
    wsBaseUrl: 'ws://127.0.0.1:8000',
    environment: 'local'
  }
};

// 获取当前环境
function getCurrentEnv(): string {
  // 优先从环境变量获取
  if (process.env.NODE_ENV) {
    return process.env.NODE_ENV;
  }
  
  // 从本地存储获取用户设置
  try {
    const savedEnv = uni.getStorageSync('app_environment');
    if (savedEnv && envConfigs[savedEnv]) {
      return savedEnv;
    }
  } catch (error) {
    console.warn('Failed to get environment from storage:', error);
  }
  
  // 默认为开发环境
  return 'development';
}

// 创建配置
function createConfig(): Config {
  const env = getCurrentEnv();
  const envConfig = envConfigs[env] || {};
  
  return {
    ...defaultConfig,
    ...envConfig
  };
}

// 导出配置实例
export const config = createConfig();

// 切换环境的方法
export function switchEnvironment(env: string): void {
  if (envConfigs[env]) {
    try {
      uni.setStorageSync('app_environment', env);
      uni.showToast({
        title: `已切换到${env}环境`,
        icon: 'success'
      });
      
      // 提示用户重启应用
      setTimeout(() => {
        uni.showModal({
          title: '环境切换',
          content: '环境已切换，请重启应用以生效',
          showCancel: false
        });
      }, 1500);
    } catch (error) {
      console.error('Failed to switch environment:', error);
      uni.showToast({
        title: '环境切换失败',
        icon: 'error'
      });
    }
  } else {
    uni.showToast({
      title: '无效的环境配置',
      icon: 'error'
    });
  }
}

// 获取所有可用环境
export function getAvailableEnvironments(): string[] {
  return Object.keys(envConfigs);
}

// 获取当前环境名称
export function getCurrentEnvironment(): string {
  return config.environment;
}