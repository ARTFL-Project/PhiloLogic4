import Vuex from 'vuex'

import {
    getField,
    updateField
} from 'vuex-map-fields'


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
            termGroups: [],
        },
        aggregationCache: {
            results: [],
            query: {}
        },
        sortedKwicCache: {
            queryParams: {},
            results: [],
            totalResults: 0
        },
        totalResultsDone: false,
        showFacets: true,
        urlUpdate: "",
        metadataUpdate: {},
        accessAuthorized: true
    },
    getters: {
        getField
    },
    mutations: {
        updateField,
        updateFormData(state, payload) {
            state.formData = payload
        },
        setDefaultFields(state, payload) {
            for (let field in payload) {
                state.formData[field] = payload[field]
            }
        },
        updateFormDataField(state, payload) {
            state.formData[payload.key] = payload.value
        },
        updateAllMetadata(state, payload) {
            state.formData = { ...state.formData, ...payload }
        },
        setReportValues(state, payload) {
            state.reportValues = payload
        },
        updateCitation(state, payload) {
            state.textNavigationCitation = payload
        },
        updateDescription(state, payload) {
            state.description = payload
        },
        updateResultsLength(state, payload) {
            state.resultsLength = payload
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