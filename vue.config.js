const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: ['@dcloudio/uni-ui'],
  parallel: false,
  lintOnSave: false
})