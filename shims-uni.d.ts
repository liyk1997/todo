/// <reference types='@dcloudio/types' />
import Vue from 'vue'

declare module "vue/types/options" {
  type Hooks = App.AppInstance & Page.PageInstance;
  interface ComponentOptions<V extends Vue> extends Hooks {
    /**
     * 组件类型
     */
    mpType?: string;
  }
}

declare module "vue/types/vue" {
  interface Vue {
    $mp: {
      page: {
        route: string;
        options: Record<string, any>;
      };
    };
  }
}

declare module "@vue/runtime-core" {
  interface ComponentCustomProperties {
    $mp: {
      page: {
        route: string;
        options: Record<string, any>;
      };
    };
  }
}
