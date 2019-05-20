import Vue from 'vue'
import BootstrapVue from 'bootstrap-vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from 'axios'

Vue.config.productionTip = false
Vue.prototype.$http = axios

Vue.mixin({
    methods: {
        paramsToUrl: function(formValues) {
            var queryParams = []
            for (var param in formValues) {
                queryParams.push(`${param}=${encodeURIComponent(formValues[param])}`)
            }
            return queryParams.join('&')
        }
    }
})

Vue.use(BootstrapVue)

axios
    .get('http://anomander.uchicago.edu/philologic/test/scripts/get_web_config.py')
    .then((response) => {
        Vue.prototype.$philoConfig = response.data
        new Vue({
            el: '#app',
            router,
            store,
            template: '<App/>',
            components: {
                App
            }
        })
    })
    .catch((error) => {
        this.loading = false
        this.error = error.toString()
        console.log(error)
    })