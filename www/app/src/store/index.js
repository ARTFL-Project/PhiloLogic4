import Vue from 'vue'
import Vuex from 'vuex'

import {
    getField,
    updateField
} from 'vuex-map-fields'

Vue.use(Vuex)

export default new Vuex.Store({
    strict: true,
    state: {
        formData: {},
        reportValues: {},
        resultsLength: 0,
        textNavigationCitation: {},
        textObject: '',
        navBar: '',
        tocElements: {},
        byte: '',
        searching: false,
        currentReport: "concordance",
        description: {
            start: 0,
            end: 0,
            results_per_page: 25,
            termGroups: []
        },
        aggregationCache: {
            results: [],
            query: {}
        },
        sortedKwicCache: {
            queryParams: {},
            results: [],
            totalResults: 0
        }
    },
    getters: {
        getField
    },
    mutations: {
        updateField,
        updateFormData(state, payload) {
            Vue.set(state, 'formData', payload)
        },
        setDefaultFields(state, payload) {
            for (let field in payload) {
                Vue.set(state.formData, field, payload[field])
            }
        },
        updateFormDataField(state, payload) {
            Vue.set(state.formData, payload.key, payload.value)
        },
        setReportValues(state, payload) {
            Vue.set(state, "reportValues", payload)
        },
        updateCitation(state, payload) {
            Vue.set(state, 'textNavigationCitation', payload)
        },
        updateDescription(state, payload) {
            Vue.set(state, "description", payload)
        }
    },
    actions: {
        updateStartEndDate(context, payload) {
            context.commit("updateFormData", {
                ...context.state.formData,
                start_date: payload.startDate,
                end_date: payload.endDate
            })
        },
    }
})