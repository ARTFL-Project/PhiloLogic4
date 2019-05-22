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

export const EventBus = new Vue(); // To pass messages between components

Vue.mixin({
    methods: {
        paramsFilter: function(formValues) {
            let localFormData = {}
            for (const field in formValues) {
                let value = formValues[field]
                if (field === "report") {
                    continue
                }
                if (field === "metadataFields") {
                    for (let metadataField in value) {
                        if (value[metadataField].length > 0) {
                            localFormData[metadataField] = value[metadataField]
                        }
                    }
                } else if (value.length > 0 || field === "results_per_page") {
                    if (field === "method" && value === "proxy" || field === "approximate" && value == "no" || field === "sort_by" && value === "rowid") {
                        continue
                    } else if (field == "start" && value == 0 || field == "end" && value == 0) {
                        continue
                    } else {
                        localFormData[field] = value
                    }
                } else if (field == "hit_num") {
                    localFormData[field] = value
                }
            }
            return localFormData
        },
        paramsToRoute: function(formValues) {
            let report = formValues.report
            let localFormData = this.paramsFilter(formValues)
            let routeObject = {
                path: report,
                query: localFormData
            }
            return routeObject
        },
        paramsToUrlString: function(params) {
            let filteredParams = this.paramsFilter(params)
            let queryParams = [];
            for (let param in filteredParams) {
                queryParams.push(
                    `${param}=${encodeURIComponent(filteredParams[param])}`
                );
            }
            return queryParams.join("&");
        },
        copyObject: function(objectToCopy) {
            return JSON.parse(JSON.stringify(objectToCopy))
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