import { createApp, configureCompat } from 'vue'
import vueScrollTo from 'vue-scrollto'
import App from './App.vue'
import router from './router'
import store from './store'
import { paramsFilter, paramsToRoute, paramsToUrlString, copyObject, saveToLocalStorage, mergeResults, sortResults, deepEqual, dictionaryLookup, debug } from './mixins.js'
import axios from 'axios'
import "bootstrap"
import { createNanoEvents } from 'nanoevents'

import appConfig from "../appConfig.json"

configureCompat({
    MODE: 3
})

export const emitter = createNanoEvents()

axios
    .get(`${appConfig.dbUrl}/scripts/get_web_config.py`, {
    })
    .then((response) => {
        const app = createApp(App)
        app.config.globalProperties.$philoConfig = response.data
        app.config.globalProperties.$scrollTo = vueScrollTo.scrollTo
        app.config.globalProperties.$dbUrl = appConfig.dbUrl
        app.provide("$http", axios)
        app.use(router)
        app.use(store)
        app.mixin({
            methods: {
                paramsFilter, paramsToRoute, paramsToUrlString, copyObject, saveToLocalStorage, mergeResults, sortResults, deepEqual, dictionaryLookup, debug
            }
        })
        app.directive('scroll', {
            mounted: function (el, binding) {
                el.scrollHandler = function (evt) {
                    if (binding.value(evt, el)) {
                        window.removeEventListener('scroll', el.scrollHandler)
                    }
                }
                window.addEventListener('scroll', el.scrollHandler)
            },
            unmounted: function (el) {
                window.removeEventListener("scroll", el.scrollHandler)
            }
        })

        router.isReady().then(() => app.mount('#app'))
    })
    .catch((error) => {
        // this.loading = false
        console.log(error.toString())
    })