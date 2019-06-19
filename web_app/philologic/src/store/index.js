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
        formData: {
            report: 'concordance',
            q: '',
            method: 'proxy',
            arg_proxy: '',
            arg_phrase: '',
            results_per_page: '25',
            method: 'proxy',
            start: '',
            end: '',
            colloc_filter_choice: '',
            filter_frequency: 100,
            approximate: 'no',
            approximate_ratio: 100,
            metadataFields: {},
            start_date: '',
            end_date: '',
            year_interval: '',
            sort_by: 'rowid',
            first_kwic_sorting_option: '',
            second_kwic_sorting_option: '',
            third_kwic_sorting_option: '',
            start_byte: '',
            end_byte: ''
        },
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
        }
    },
    getters: {
        getField
    },
    mutations: {
        updateField,
        updateStore(state, payload) {
            let metadataFields = {}
            for (let field of payload.metadata) {
                if (field in payload.routeQuery) {
                    metadataFields[field] = payload.routeQuery[field]
                    delete payload.routeQuery[field]
                } else {
                    metadataFields[field] = ''
                }
            }
            state.formData.metadataFields = {
                ...state.formData.metadataFields,
                ...metadataFields
            }
            let localStore = JSON.parse(JSON.stringify(state.formData))
            if (Object.keys(payload.routeQuery).length > 0) {
                for (let field in payload.routeQuery) {
                    localStore[field] = payload.routeQuery[field]
                }
                Vue.set(state, 'formData', localStore)
            }
            console.log('STORE', state.formData)
            console.log('METADATA', state.formData.metadataFields)
        },
        updateMethod(state, payload) {
            // method must be reserved, so we create our custom handler
            Vue.set(state.formData, 'method', payload)
        },
        replaceStore(state, payload) {
            Vue.set(state, 'formData', payload)
        },
        updateMetadata(state, payload) {
            state.formData.metadataFields = {
                ...state.formData.metadataFields,
                ...payload
            }
        },
        removeMetadata(state, payload) {
            state.formData.metadataFields[payload] = ''
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
            context.commit("replaceStore", {
                ...context.state.formData,
                start_date: payload.startDate,
                end_date: payload.endDate
            })
        },
    }
})