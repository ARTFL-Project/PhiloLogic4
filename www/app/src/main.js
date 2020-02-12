import Vue from 'vue'
import BootstrapVue from 'bootstrap-vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import vueScrollTo from 'vue-scrollto'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from 'axios'

import appConfig from "../appConfig.json"

Vue.config.productionTip = false
Vue.prototype.$http = axios
Vue.prototype.$scrollTo = vueScrollTo.scrollTo
Vue.prototype.$dbUrl = appConfig.dbUrl

export const EventBus = new Vue() // To pass messages between components

Vue.mixin({
    methods: {
        paramsFilter: function (formValues) {
            let localFormData = {}
            let validFields = []
            if ("report" in formValues && formValues.report in this.$store.state.reportValues) {
                validFields = this.$store.state.reportValues[formValues.report]
            } else {
                validFields = new Set(Object.keys(formValues))
            }
            for (const field in formValues) {
                let value = formValues[field]
                if (field === 'report') {
                    continue
                }
                if (!validFields.has(field)) {
                    continue
                }
                if (value.length > 0 || field === 'results_per_page') {
                    if (
                        (field === 'method' && value === 'proxy') ||
                        (field === 'approximate' && value == 'no') ||
                        (field === 'sort_by' && value === 'rowid')
                    ) {
                        continue
                    } else if ((field == 'start' && value == 0) || (field == 'end' && value == 0)) {
                        continue
                    } else {
                        localFormData[field] = value
                    }
                } else if (field == 'hit_num') {
                    localFormData[field] = value
                }
            }
            return localFormData
        },
        paramsToRoute: function (formValues) {
            let report = formValues.report
            let localFormData = this.paramsFilter(formValues)
            let routeObject = {
                path: `/${report}`,
                query: localFormData
            }
            return routeObject
        },
        paramsToUrlString: function (params) {
            let filteredParams = this.paramsFilter(params)
            let queryParams = []
            for (let param in filteredParams) {
                queryParams.push(`${param}=${encodeURIComponent(filteredParams[param])}`)
            }
            return queryParams.join('&')
        },
        copyObject: function (objectToCopy) {
            return JSON.parse(JSON.stringify(objectToCopy))
        },
        saveToLocalStorage: function (urlString, results) {
            try {
                sessionStorage[urlString] = JSON.stringify(results)
                console.log('saved results to localStorage')
            } catch (e) {
                sessionStorage.clear()
                console.log('Clearing sessionStorage for space...')
                try {
                    sessionStorage[urlString] = JSON.stringify(results)
                    console.log('saved results to localStorage')
                } catch (e) {
                    sessionStorage.clear()
                    console.log('Quota exceeded error: the JSON object is too big...')
                }
            }
        },
        mergeResults: function (fullResults, newData, sortKey) {
            if (typeof fullResults === 'undefined' || Object.keys(fullResults).length === 0) {
                fullResults = newData
            } else {
                for (let key in newData) {
                    let value = newData[key]
                    if (typeof value.count !== 'undefined') {
                        if (key in fullResults) {
                            fullResults[key].count += value.count
                        } else {
                            fullResults[key] = value
                        }
                    }
                }
            }
            let sortedList = this.sortResults(fullResults, sortKey)
            return {
                sorted: sortedList,
                unsorted: fullResults
            }
        },
        sortResults: function (fullResults, sortKey) {
            let sortedList = []
            for (let key in fullResults) {
                sortedList.push({
                    label: key,
                    count: parseFloat(fullResults[key].count),
                    metadata: fullResults[key].metadata
                })
            }
            if (sortKey === 'label') {
                sortedList.sort(function (a, b) {
                    return a.label - b.label
                })
            } else {
                sortedList.sort(function (a, b) {
                    return b.count - a.count
                })
            }
            return sortedList
        },
        deepEqual: function (x, y) {
            const ok = Object.keys,
                tx = typeof x,
                ty = typeof y;
            return x && y && tx === 'object' && tx === ty ? (
                ok(x).length === ok(y).length &&
                ok(x).every(key => this.deepEqual(x[key], y[key]))
            ) : (x === y);
        },
        dictionaryLookup(event, year) {
            if (event.key === "d") {
                var selection = window.getSelection().toString();
                var century = parseInt(year.slice(0, year.length - 2));
                var range = century.toString() + "00-" + String(century + 1) + "00";
                if (range == "NaN00-NaN00") {
                    range = "";
                }
                var link = this.$philoConfig.dictionary_lookup + "?docyear=" + range + "&strippedhw=" + selection;
                window.open(link);
            }
        },
        debug(component, message) {
            console.log(`MESSAGE FROM ${component.$options.name}:`, message)
        }
    }
})

Vue.directive('scroll', {
    inserted: function (el, binding) {
        el.scrollHandler = function (evt) {
            if (binding.value(evt, el)) {
                window.removeEventListener('scroll', el.scrollHandler)
            }
        }
        window.addEventListener('scroll', el.scrollHandler)
    },
    unbind: function (el) {
        window.removeEventListener("scroll", el.scrollHandler)
    }
})

Vue.use(BootstrapVue)

axios
    .get(`${appConfig.dbUrl}/scripts/get_web_config.py`)
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