declare module "*.vue" {
  import Vue from 'vue'
  export type VueComponent = Vue & {
    $mp: {
      page: {
        route: string
        options: Record<string, any>
      }
    }
  }
  export default Vue
}
