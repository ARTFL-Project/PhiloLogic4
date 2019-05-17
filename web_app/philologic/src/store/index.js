import Vue from 'vue/dist/vue.js'
import Vuex from 'vuex'

import { getField, updateField } from 'vuex-map-fields'

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
			approximate: 'yes',
			approximate_ratio: 100,
			metadataFields: {},
			start_date: '',
			end_date: '',
			year_interval: ''
		}
	},
	getters: {
		getField
	},
	mutations: {
		updateField
	}
})
