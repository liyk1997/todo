import Vue from 'vue'
import VueCompositionAPI from '@vue/composition-api'
import App from './App.vue'
import './uni.promisify.adaptor'

Vue.use(VueCompositionAPI)

Vue.config.productionTip = false

const app = new (typeof App === 'function' ? App : Vue.extend(Object.assign({ mpType: 'app' }, App)))
app.$mount();
