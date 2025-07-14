module.exports = {
  presets: [
    ['@vue/app', {
      useBuiltIns: 'entry'
    }]
  ],
  plugins: [
    '@babel/plugin-transform-runtime',
    ['import', {
      'libraryName': '@dcloudio/uni-ui',
      'customName': (name) => `@dcloudio/uni-ui/lib/${name}/${name}`
    }]
  ]
}
