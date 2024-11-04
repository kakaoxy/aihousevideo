// #ifndef VUE3
import Vue from 'vue'
import App from './App'
import './uni.promisify.adaptor'
import draggable from 'vuedraggable'

Vue.config.productionTip = false
App.mpType = 'app'

// 注册 vuedraggable 组件
Vue.component('draggable', draggable)

const app = new Vue({
	...App
})
app.$mount()
// #endif

// #ifdef VUE3
import {
	createSSRApp
} from 'vue'
import App from './App'
import draggable from 'vuedraggable'

export function createApp() {
	const app = createSSRApp(App)
	// 在 Vue 3 中，组件需要在根组件或使用该组件的组件中注册
	app.component('draggable', draggable)
	return {
		app
	}
}
// #endif