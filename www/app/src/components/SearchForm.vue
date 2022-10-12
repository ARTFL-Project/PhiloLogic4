<template>
    <div>
        <div class="card shadow" style="border: transparent">
            <form @submit.prevent @reset="onReset" @keyup.enter="onSubmit()">
                <div id="form-body">
                    <div id="initial-form">
                        <div class="btn-group" role="group" id="report" style="width: 100%; top: -1px">
                            <button
                                type="button"
                                :id="report"
                                v-for="searchReport in reports"
                                @click="reportChange(searchReport)"
                                :key="searchReport"
                                class="btn btn-secondary rounded-0"
                                :class="{ active: currentReport == searchReport }"
                            >
                                <span v-if="searchReport != 'kwic'">{{ $t(`searchForm.${searchReport}`) }}</span>
                                <span v-else
                                    ><span class="d-md-inline d-sm-none">{{ $t(`searchForm.${searchReport}`) }}</span
                                    ><span class="d-md-none">{{ $t("searchForm.shortKwic") }}</span></span
                                >
                            </button>
                        </div>
                        <div id="search_terms_container" class="p-3">
                            <div class="row" id="search_terms">
                                <div class="cols-12 cols-md-8">
                                    <div class="input-group" id="q-group">
                                        <button class="btn btn-outline-secondary" type="button">
                                            <label for="query-term-input">{{ $t("searchForm.searchTerms") }}</label>
                                        </button>
                                        <button
                                            class="btn btn-outline-info"
                                            type="button"
                                            data-bs-toggle="modal"
                                            data-bs-target="#search-tips"
                                            @mouseover="showTips = true"
                                            @mouseleave="showTips = false"
                                        >
                                            <span v-if="!showTips">?</span>
                                            <span v-if="showTips">{{ $t("searchForm.tips") }}</span>
                                        </button>
                                        <input
                                            type="text"
                                            class="form-control"
                                            id="query-term-input"
                                            v-model="queryTermTyped"
                                            @input="onChange('q')"
                                            @keyup.down="onArrowDown('q')"
                                            @keyup.up="onArrowUp('q')"
                                            @keyup.enter="onEnter('q')"
                                        />

                                        <ul
                                            id="autocomplete-q"
                                            class="autocomplete-results shadow"
                                            :style="autoCompletePosition('q')"
                                            v-if="autoCompleteResults.q.length > 0"
                                        >
                                            <li
                                                tabindex="-1"
                                                v-for="(result, i) in autoCompleteResults.q"
                                                :key="result"
                                                @click="setResult(result, 'q')"
                                                class="autocomplete-result"
                                                :class="{ 'is-active': i === arrowCounters.q }"
                                                v-html="result"
                                            ></li>
                                        </ul>
                                        <button class="btn btn-secondary" id="button-search" @click="onSubmit()">
                                            {{ $t("searchForm.search") }}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div id="head-search-container" class="px-3 pt-1 pb-3" v-if="dictionary">
                            <div class="input-group" id="head-group">
                                <button type="button" class="btn btn-outline-secondary">
                                    <label :for="metadataDisplay[headIndex].value + '-input'">{{
                                        metadataDisplay[headIndex].label
                                    }}</label>
                                </button>
                                <input
                                    type="text"
                                    class="form-control"
                                    :id="metadataDisplay[headIndex].value + '-input'"
                                    :name="metadataDisplay[headIndex].value"
                                    :placeholder="metadataDisplay[headIndex].example"
                                    v-model="metadataValues.head"
                                    @input="onChange('head')"
                                    @keydown.down="onArrowDown(metadataDisplay[headIndex].value)"
                                    @keydown.up="onArrowUp(metadataDisplay[headIndex].value)"
                                    @keyup.enter="onEnter(metadataDisplay[headIndex].value)"
                                />
                                <ul
                                    :id="'autocomplete-' + metadataDisplay[headIndex].value"
                                    class="autocomplete-results shadow"
                                    :style="autoCompletePosition(metadataDisplay[headIndex].value)"
                                    v-if="autoCompleteResults[metadataDisplay[headIndex].value].length > 0"
                                >
                                    <li
                                        tabindex="-1"
                                        v-for="(result, i) in autoCompleteResults[metadataDisplay[headIndex].value]"
                                        :key="result"
                                        @click="setResult(result, metadataDisplay[headIndex].value)"
                                        class="autocomplete-result"
                                        :class="{
                                            'is-active': i === arrowCounters[metadataDisplay[headIndex].value],
                                        }"
                                        v-html="result"
                                    ></li>
                                </ul>
                            </div>
                        </div>
                        <div id="search-buttons">
                            <div class="input-group">
                                <button type="reset" id="reset_form" class="btn btn-outline-secondary">
                                    {{ $t("searchForm.clear") }}
                                </button>
                                <button
                                    type="button"
                                    id="show-search-form"
                                    class="btn btn-secondary"
                                    @click="toggleForm()"
                                >
                                    <span v-if="!formOpen">{{ $t("searchForm.showSearchOptions") }}</span>
                                    <span v-else>{{ $t("searchForm.hideSearchOptions") }}</span>
                                </button>
                            </div>
                        </div>
                    </div>
                    <transition name="slide-fade">
                        <div id="search-elements" v-if="formOpen" class="ps-3 pe-3 pb-3 shadow">
                            <div class="mt-1">
                                <h6>{{ $t("searchForm.searchTermsParameters") }}:</h6>
                                <div
                                    class="form-check form-switch form-check-inline"
                                    id="approximate"
                                    style="height: 31px"
                                >
                                    <input
                                        class="form-check-input"
                                        type="checkbox"
                                        id="approximate-input"
                                        v-model="approximateSelected"
                                        @change="approximateChange(approximateSelected)"
                                    />
                                    <label class="form-check-label" for="approximate-input"
                                        >{{ $t("searchForm.approximateMatch") }}
                                    </label>
                                </div>
                                <select
                                    class="form-select form-select-sm d-inline-block"
                                    style="max-width: fit-content; margin-left: 0.5rem"
                                    v-model="approximate_ratio"
                                    :disabled="!approximateSelected"
                                    aria-label=".form-select-sm"
                                >
                                    <option v-for="value in approximateValues" :key="value.value" :value="value.value">
                                        {{ value.text }}
                                    </option>
                                    >
                                </select>
                                <div class="input-group mb-4" v-if="currentReport != 'collocation'">
                                    <button class="btn btn-outline-secondary" type="button">
                                        {{ $t("searchForm.searchCoOccurrences") }}</button
                                    ><select
                                        class="form-select"
                                        style="width: fit-content; max-width: fit-content"
                                        v-model="method"
                                    >
                                        <option v-for="value in methodOptions" :key="value.value" :value="value.value">
                                            {{ value.text }}
                                        </option>
                                    </select>
                                    <button
                                        class="btn btn-outline-secondary"
                                        type="button"
                                        v-if="method == 'proxy' || method == 'phrase'"
                                    >
                                        <label for="arg-proxy" v-if="method == 'proxy'"
                                            >{{ $t("searchForm.howMany") }}?</label
                                        >
                                        <label for="arg-phrase" v-if="method == 'phrase'"
                                            >{{ $t("searchForm.howMany") }}?</label
                                        >
                                    </button>
                                    <input
                                        class="form-control"
                                        type="text"
                                        name="arg_proxy"
                                        id="arg-proxy"
                                        v-model="arg_proxy"
                                        v-if="method == 'proxy'"
                                    />
                                    <input
                                        class="form-control"
                                        type="text"
                                        name="arg_phrase"
                                        id="arg-phrase"
                                        v-model="arg_phrase"
                                        v-if="method == 'phrase'"
                                    />
                                    <span
                                        class="input-group-text ms-0"
                                        v-if="method == 'proxy' || method == 'phrase'"
                                        >{{ $t("searchForm.wordsSentence") }}</span
                                    >
                                </div>
                                <h6>{{ $t("searchForm.filterByField") }}:</h6>
                                <div
                                    class="input-group pb-2"
                                    v-for="localField in metadataDisplayFiltered"
                                    :key="localField.value"
                                >
                                    <div
                                        class="input-group pb-2"
                                        :id="localField.value + '-group'"
                                        v-if="metadataInputStyle[localField.value] == 'text'"
                                    >
                                        <button type="button" class="btn btn-outline-secondary">
                                            <label :for="localField.value + 'input-filter'">{{
                                                localField.label
                                            }}</label></button
                                        ><input
                                            type="text"
                                            class="form-control"
                                            :id="localField.value + 'input-filter'"
                                            :name="localField.value"
                                            :placeholder="localField.example"
                                            v-model="metadataValues[localField.value]"
                                            @input="onChange(localField.value)"
                                            @keydown.down="onArrowDown(localField.value)"
                                            @keydown.up="onArrowUp(localField.value)"
                                            @keyup.enter="onEnter(localField.value)"
                                            v-if="
                                                metadataInputStyle[localField.value] == 'text' &&
                                                metadataInputStyle[localField.value] != 'date'
                                            "
                                        />
                                        <ul
                                            :id="'autocomplete-' + localField.value"
                                            class="autocomplete-results shadow"
                                            :style="autoCompletePosition(localField.value)"
                                            v-if="
                                                autoCompleteResults[localField.value].length > 0 &&
                                                metadataInputStyle[localField.value] != 'date'
                                            "
                                        >
                                            <li
                                                tabindex="-1"
                                                v-for="(result, i) in autoCompleteResults[localField.value]"
                                                :key="result"
                                                @click="setResult(result, localField.value)"
                                                class="autocomplete-result"
                                                :class="{ 'is-active': i === arrowCounters[localField.value] }"
                                                v-html="result"
                                            ></li>
                                        </ul>
                                    </div>
                                    <div
                                        class="input-group pb-2"
                                        :id="localField.value + '-group'"
                                        v-if="metadataInputStyle[localField.value] == 'checkbox'"
                                    >
                                        <button
                                            style="border-top-right-radius: 0; border-bottom-right-radius: 0"
                                            class="btn btn-outline-secondary me-2"
                                        >
                                            {{ localField.label }}
                                        </button>
                                        <div class="d-inline-block">
                                            <div
                                                class="form-check d-inline-block ms-3"
                                                style="padding-top: 0.35rem"
                                                :id="localField.value"
                                                :options="metadataChoiceValues[localField.value]"
                                                v-for="metadataChoice in metadataChoiceValues[localField.value]"
                                                :key="metadataChoice.value"
                                                v-once
                                            >
                                                <input
                                                    class="form-check-input"
                                                    type="checkbox"
                                                    :id="metadataChoice.value"
                                                    v-model="metadataChoiceChecked[metadataChoice.value]"
                                                />
                                                <label class="form-check-label" :for="metadataChoice.value">{{
                                                    metadataChoice.text
                                                }}</label>
                                            </div>
                                        </div>
                                    </div>
                                    <div
                                        class="input-group pb-2"
                                        :id="localField.value + '-group'"
                                        v-if="metadataInputStyle[localField.value] == 'dropdown'"
                                    >
                                        <button type="button" class="btn btn-outline-secondary">
                                            <label :for="localField.value + '-input-filter'">{{
                                                localField.label
                                            }}</label>
                                        </button>
                                        <select
                                            class="form-select"
                                            :id="localField.value + '-select'"
                                            v-model="metadataChoiceSelected[localField.value]"
                                        >
                                            <option
                                                v-for="innerValue in metadataChoiceValues[localField.value]"
                                                :key="innerValue.value"
                                                :value="innerValue.value"
                                                :id="innerValue.value + '-select-option'"
                                            >
                                                {{ innerValue.text }}
                                            </option>
                                        </select>
                                    </div>
                                    <div
                                        class="input-group pb-2"
                                        :id="localField.value + '-group'"
                                        v-if="['date', 'int'].includes(metadataInputStyle[localField.value])"
                                    >
                                        <button
                                            type="button"
                                            class="btn btn-outline-secondary"
                                            style="border-top-right-radius: 0; border-bottom-right-radius: 0"
                                        >
                                            <label :for="localField.value + '-date'">{{ localField.label }}</label>
                                        </button>
                                        <div class="btn-group" role="group">
                                            <button
                                                class="btn btn-secondary dropdown-toggle"
                                                style="border-top-left-radius: 0; border-bottom-left-radius: 0"
                                                type="button"
                                                :id="localField.value + '-selector'"
                                                data-bs-toggle="dropdown"
                                                aria-expanded="false"
                                            >
                                                {{ $t(`searchForm.${dateType[localField.value]}Date`) }}
                                            </button>
                                            <ul class="dropdown-menu" :aria-labelledby="localField.value + '-selector'">
                                                <li @click="dateTypeToggle(localField.value, 'exact')">
                                                    <a class="dropdown-item">{{ $t("searchForm.exactDate") }}</a>
                                                </li>
                                                <li @click="dateTypeToggle(localField.value, 'range')">
                                                    <a class="dropdown-item">{{ $t("searchForm.rangeDate") }}</a>
                                                </li>
                                            </ul>
                                        </div>
                                        <input
                                            type="text"
                                            class="form-control"
                                            :id="localField.value + 'input-filter'"
                                            :name="localField.value"
                                            :placeholder="localField.example"
                                            v-model="metadataValues[localField.value]"
                                            v-if="dateType[localField.value] == 'exact'"
                                        />
                                        <span class="d-inline-block" v-if="dateType[localField.value] == 'range'">
                                            <div class="input-group ms-3">
                                                <button class="btn btn-outline-secondary" type="button">
                                                    <label for="query-term-input">{{
                                                        $t("searchForm.dateFrom")
                                                    }}</label>
                                                </button>
                                                <input
                                                    type="text"
                                                    class="form-control date-range"
                                                    :id="localField.value + '-start-input-filter'"
                                                    :name="localField.value + '-start'"
                                                    :placeholder="localField.example"
                                                    v-model="dateRange[localField.value].start"
                                                />
                                                <button class="btn btn-outline-secondary ms-3" type="button">
                                                    <label for="query-term-input">{{
                                                        $t("searchForm.dateTo")
                                                    }}</label></button
                                                ><input
                                                    type="text"
                                                    class="form-control date-range"
                                                    :id="localField.value + 'end-input-filter'"
                                                    :name="localField.value + '-end'"
                                                    :placeholder="localField.example"
                                                    v-model="dateRange[localField.value].end"
                                                />
                                            </div>
                                        </span>
                                    </div>
                                </div>
                            </div>
                            <div class="d-flex mt-4" v-if="currentReport === 'collocation'">
                                <div class="input-group d-inline" style="width: fit-content">
                                    <button class="btn btn-outline-secondary" style="height: fit-content">
                                        <label for="filter-frequency">{{ $t("searchForm.wordFiltering") }}</label>
                                    </button>
                                    <input
                                        type="text"
                                        class="form-control d-inline-block"
                                        id="filter-frequency"
                                        name="filter_frequency"
                                        placeholder="100"
                                        v-model="filter_frequency"
                                        style="width: 60px; text-align: center"
                                    />
                                </div>
                                <div>
                                    <div
                                        class="form-check"
                                        v-for="collocFilter in collocationOptions"
                                        :key="collocFilter.value"
                                    >
                                        <input
                                            class="btn-check"
                                            type="radio"
                                            name="colloc_filter_choice"
                                            v-model="colloc_filter_choice"
                                            :value="collocFilter.value"
                                            :id="collocFilter.value"
                                        />
                                        <label class="btn btn-secondary" :for="collocFilter.value">{{
                                            collocFilter.text
                                        }}</label
                                        ><br />
                                    </div>
                                </div>
                            </div>
                            <div class="input-group mt-4 pt-1 pb-2" v-if="currentReport === 'time_series'">
                                <button class="btn btn-outline-secondary">{{ $t("searchForm.dateRange") }}</button>
                                <span class="d-inline-flex align-self-center mx-2"
                                    ><label for="start_date">{{ $t("searchForm.dateFrom") }}</label></span
                                >
                                <input
                                    type="text"
                                    class="form-control"
                                    name="start_date"
                                    id="start_date"
                                    style="max-width: 65px; text-align: center"
                                    v-model="start_date"
                                />
                                <span class="d-inline-flex align-self-center mx-2"
                                    ><label for="end_date">{{ $t("searchForm.dateTo") }}</label></span
                                >
                                <input
                                    type="text"
                                    class="form-control"
                                    name="end_date"
                                    id="end_date"
                                    style="max-width: 65px; text-align: center"
                                    v-model="end_date"
                                />
                            </div>
                            <div class="input-group" v-if="currentReport == 'time_series'">
                                <button class="btn btn-outline-secondary">
                                    <label for="year_interval">{{ $t("searchForm.yearInterval") }}</label>
                                </button>
                                <span class="d-inline-flex align-self-center mx-2">{{ $t("searchForm.every") }}</span>
                                <input
                                    type="text"
                                    class="form-control"
                                    name="year_interval"
                                    id="year_interval"
                                    style="max-width: 50px; text-align: center"
                                    v-model="year_interval"
                                />
                                <span class="d-inline-flex align-self-center mx-2">{{ $t("searchForm.years") }}</span>
                            </div>
                            <div class="input-group mt-4" v-if="currentReport === 'aggregation'">
                                <button class="btn btn-outline-secondary">{{ $t("searchForm.groupResultsBy") }}</button>
                                <select
                                    v-once
                                    class="form-select"
                                    :aria-label="aggregationOptions[0].text"
                                    style="max-width: fit-content"
                                    v-model="group_by"
                                >
                                    <option
                                        v-for="aggregationOption in aggregationOptions"
                                        :key="aggregationOption.text"
                                        :value="aggregationOption.value"
                                    >
                                        {{ aggregationOption.text }}
                                    </option>
                                </select>
                            </div>
                            <h6 class="mt-3" v-if="['concordance', 'kwic', 'bibliography'].includes(currentReport)">
                                {{ $t("searchForm.displayOptions") }}:
                            </h6>
                            <div
                                class="input-group pb-2"
                                v-if="['concordance', 'bibliography'].includes(currentReport)"
                            >
                                <button class="btn btn-outline-secondary">{{ $t("searchForm.sortResultsBy") }}</button>
                                <select
                                    v-once
                                    class="form-select"
                                    style="max-width: fit-content"
                                    aria-label="select fields"
                                    v-model="sort_by"
                                >
                                    <option
                                        v-for="sortValue in sortValues"
                                        :key="sortValue.value"
                                        :value="sortValue.value"
                                    >
                                        {{ sortValue.text }}
                                    </option>
                                </select>
                            </div>
                            <div
                                class="btn-group radio-btn-group"
                                role="group"
                                v-if="
                                    currentReport != 'collocation' &&
                                    currentReport != 'time_series' &&
                                    currentReport != 'aggregation'
                                "
                            >
                                <button class="btn btn-outline-secondary">{{ $t("searchForm.resultsPerPage") }}</button>
                                <span v-for="resultsPerPage in resultsPerPageOptions" :key="resultsPerPage" v-once>
                                    <input
                                        type="radio"
                                        class="btn-check"
                                        :id="`page-${resultsPerPage}`"
                                        :value="`${resultsPerPage}`"
                                        v-model="results_per_page"
                                    />
                                    <label class="btn btn-secondary radio-group" :for="`page-${resultsPerPage}`">{{
                                        resultsPerPage
                                    }}</label>
                                </span>
                            </div>
                        </div>
                    </transition>
                </div>
            </form>
        </div>
        <div class="d-flex justify-content-center position-relative" v-if="searching">
            <div
                class="spinner-border"
                style="width: 8rem; height: 8rem; position: absolute; z-index: 50; top: 30px"
                role="status"
            >
                <span class="visually-hidden">{{ $t("common.loading") }}</span>
            </div>
        </div>
        <div class="modal fade" id="search-tips" tabindex="-1">
            <SearchTips></SearchTips>
        </div>
    </div>
</template>

<script>
import { mapFields } from "vuex-map-fields";
import SearchTips from "./SearchTips";
export default {
    name: "SearchForm",
    components: {
        SearchTips,
    },
    inject: ["$http"],
    computed: {
        ...mapFields([
            "formData.report",
            "formData.q",
            "formData.colloc_filter_choice",
            "formData.filter_frequency",
            "formData.approximate",
            "formData.approximate_ratio",
            "formData.method",
            "formData.arg_proxy",
            "formData.arg_phrase",
            "formData.start_date",
            "formData.end_date",
            "formData.year_interval",
            "formData.sort_by",
            "formData.results_per_page",
            "formData.start",
            "formData.end",
            "formData.byte",
            "formData.group_by",
            "searching",
            "currentReport",
            "metadataUpdate",
        ]),
        formData() {
            return this.$store.state.formData;
        },
        sortValues() {
            let sortValues = [
                {
                    value: "rowid",
                    text: "select",
                },
            ];
            for (let fields of this.$philoConfig.concordance_biblio_sorting) {
                let label = [];
                for (let field of fields) {
                    if (field in this.$philoConfig.metadata_aliases) {
                        label.push(this.$philoConfig.metadata_aliases[field]);
                    } else {
                        label.push(field);
                    }
                }
                sortValues.push({ text: label.join(", "), value: fields });
            }
            return sortValues;
        },
        metadataDisplayFiltered() {
            let metadataInForm = [];
            if (this.currentReport == "time_series") {
                for (let metadataField of this.metadataDisplay) {
                    if (this.$philoConfig.time_series_year_field !== metadataField.value) {
                        metadataInForm.push(metadataField);
                    }
                }
            } else {
                metadataInForm = this.copyObject(this.metadataDisplay);
            }
            if (!this.dictionary) {
                return metadataInForm;
            } else {
                let localMetadataDisplay = this.copyObject(metadataInForm);
                localMetadataDisplay.splice(this.headIndex, 1);
                return localMetadataDisplay;
            }
        },
    },
    data() {
        return {
            dictionary: this.$philoConfig.dictionary,
            metadataInputStyle: this.$philoConfig.metadata_input_style,
            headIndex: 0,
            formOpen: false,
            approximateValues: [
                { text: this.$t("searchForm.similarity", { n: 90 }), value: "90" },
                { text: this.$t("searchForm.similarity", { n: 80 }), value: "80" },
            ],
            approximateSelected: false,
            methodOptions: [
                { text: this.$t("searchForm.within"), value: "proxy" },
                { text: this.$t("searchForm.withinExactly"), value: "phrase" },
                { text: this.$t("common.sameSentence"), value: "cooc" },
            ],
            metadataDisplay: [],
            metadataValues: {},
            metadataChoiceValues: {},
            metadataChoiceChecked: {},
            metadataChoiceSelected: {},
            collocationOptions: [
                { text: this.$t("searchForm.mostFrequentTerms"), value: "frequency" },
                { text: this.$t("searchForm.stopwords"), value: "stopwords" },
                { text: this.$t("searchForm.noFiltering"), value: "nofilter" },
            ],
            selectedSortValues: "rowid",
            resultsPerPageOptions: [25, 100, 500, 1000],
            aggregationOptions: this.$philoConfig.aggregation_config.map((f) => ({
                text: this.$philoConfig.metadata_aliases[f.field] || f.field.charAt(0).toUpperCase() + f.field.slice(1),
                value: f.field,
            })),
            statFieldSelected: this.getLoadedStatField(),
            autoCompleteResults: {
                q: "",
                ...Object.fromEntries(this.$philoConfig.metadata.map((field) => [field, []])),
            },
            arrowCounters: { q: -1 },
            isOpen: false,
            showTips: false,
            queryTermTyped: this.$route.query.q || this.q || "",
            metadataTyped: {},
            dateType: {},
            dateRange: {},
            reports: this.$philoConfig.search_reports,
        };
    },
    watch: {
        // call again the method if the route changes
        $route: "updateInputData",
        metadataUpdate(metadata) {
            for (let field of metadata) {
                if (this.$philoConfig.metadata_input_style[field] == "text") {
                    this.metadataValues[field] = metadata[field];
                } else if (this.$philoConfig.metadata_input_style[field] == "dropdown") {
                    this.metadataChoiceSelected[field] = metadata[field];
                } else if (this.$philoConfig.metadata_input_style[field] == "checkbox") {
                    this.metadataChoiceChecked[field] = metadata[field].split(" | ");
                }
            }
            for (let metadataField of this.$philoConfig.metadata) {
                this.autoCompleteResults[metadataField] = [];
                this.arrowCounters[metadataField] = -1;
            }
        },
    },
    created() {
        for (let metadataField of this.$philoConfig.metadata) {
            let metadataObj = {
                label: metadataField[0].toUpperCase() + metadataField.slice(1),
                value: metadataField,
                example: this.$philoConfig.search_examples[metadataField],
            };
            if (metadataField in this.$philoConfig.metadata_aliases) {
                metadataObj.label = this.$philoConfig.metadata_aliases[metadataField];
            }
            this.metadataDisplay.push(metadataObj);
            if (this.formData[metadataField] != "") {
                if (this.$philoConfig.metadata_input_style[metadataField] == "text") {
                    this.metadataValues[metadataField] = this.formData[metadataField];
                } else if (this.$philoConfig.metadata_input_style[metadataField] == "checkbox") {
                    this.metadataChoiceChecked[metadataField] = this.formData[metadataField].split(" | ");
                }
            }
            this.arrowCounters[metadataField] = -1;
            if (metadataField == "head") {
                this.headIndex = this.metadataDisplay.length - 1;
            }
            if (this.$philoConfig.metadata_input_style[metadataField] == "dropdown") {
                this.metadataChoiceSelected[metadataField] = this.formData[metadataField] || "";
            }
        }
        for (let metadata in this.$philoConfig.metadata_choice_values) {
            this.metadataChoiceValues[metadata] = [];
            let choiceValue = this.$philoConfig.metadata_choice_values[metadata];
            for (let i = 0; i < choiceValue.length; i++) {
                let quotedValue = choiceValue[i].value;
                this.metadataChoiceValues[metadata].push({
                    text: choiceValue[i].label,
                    value: quotedValue,
                });
            }
        }
        for (let metadata in this.metadataInputStyle) {
            this.dateType[metadata] = "exact";
            this.dateRange[metadata] = { start: "", end: "" };
        }
        for (let metadata in this.metadataInputStyle) {
            if (metadata in this.formData) {
                if (this.metadataInputStyle[metadata] == "date" && this.formData[metadata].search(/<=>/) != -1) {
                    this.dateType[metadata] = "range";
                    let dateRanges = this.formData[metadata].split(/<=>/);
                    this.dateRange[metadata] = { start: dateRanges[0], end: dateRanges[1] };
                } else if (this.metadataInputStyle[metadata] == "int" && this.formData[metadata].search(/-/) != -1) {
                    this.dateType[metadata] = "range";
                    let dateRanges = this.formData[metadata].split(/-/);
                    this.dateRange[metadata] = { start: dateRanges[0], end: dateRanges[1] };
                }
            }
        }
    },
    mounted() {
        this.$nextTick(() => {
            document.getElementById("form-body").addEventListener("change", (event) => {
                if (event.target.id in this.$philoConfig.metadata_choice_values) {
                    let value = event.target.options[document.getElementById(event.target.id).selectedIndex].value;
                    this.$store.commit("updateFormDataField", {
                        key: event.target.id,
                        value: value,
                    });
                }
            });
            document.addEventListener("click", () => {
                this.clearAutoCompletePopup();
            });
        });
    },
    methods: {
        approximateChange(val) {
            if (val) {
                this.approximate_ratio = "90";
            } else {
                this.approximate_ratio = "";
            }
        },
        updateInputData() {
            this.queryTermTyped = this.q;
            for (let field of this.$philoConfig.metadata) {
                if (this.$philoConfig.metadata_input_style[field] == "text") {
                    this.metadataValues[field] = this.formData[field];
                } else if (this.$philoConfig.metadata_input_style[field] == "dropdown") {
                    this.metadataChoiceSelected[field] = this.formData[field];
                } else if (this.$philoConfig.metadata_input_style[field] == "checkbox") {
                    this.metadataChoiceChecked[field] = this.formData[field].split(" | ");
                }
            }
        },
        buildMetadataFieldDisplay() {
            for (let metadataField of this.$philoConfig.metadata) {
                let metadataObj = {
                    label: metadataField[0].toUpperCase() + metadataField.slice(1),
                    value: metadataField,
                    example: this.$philoConfig.search_examples[metadataField],
                };
                if (metadataField in this.$philoConfig.metadata_aliases) {
                    metadataObj.label = this.$philoConfig.metadata_aliases[metadataField];
                }
                this.metadataValues[metadataField] = "";
                this.metadataDisplay.push(metadataObj);
            }
        },
        getLoadedStatField() {
            let queryParam = this.$store.state.formData.group_by;
            if (queryParam) {
                return (
                    this.$philoConfig.metadata_aliases[queryParam] ||
                    queryParam.charAt(0).toUpperCase() + queryParam.slice(1)
                );
            }
        },
        dateRangeHandler() {
            for (let metadata in this.metadataInputStyle) {
                if (["date", "int"].includes(this.metadataInputStyle[metadata]) && this.dateType[metadata] != "exact") {
                    let separator = "-";
                    if (this.metadataInputStyle[metadata] == "date") {
                        separator = "<=>";
                    }
                    if (this.dateRange[metadata].start.length > 0 && this.dateRange[metadata].end.length > 0) {
                        this.metadataValues[
                            metadata
                        ] = `${this.dateRange[metadata].start}${separator}${this.dateRange[metadata].end}`;
                    } else if (this.dateRange[metadata].start.length > 0 && this.dateRange[metadata].end.length == 0) {
                        this.metadataValues[metadata] = `${this.dateRange[metadata].start}${separator}`;
                    } else if (this.dateRange[metadata].start.length == 0 && this.dateRange[metadata].end.length > 0) {
                        this.metadataValues[metadata] = `${separator}${this.dateRange[metadata].end}`;
                    }
                }
            }
        },
        onSubmit() {
            this.report = this.currentReport;
            this.formOpen = false;
            let metadataChoices = Object.fromEntries(
                Object.entries(this.metadataChoiceChecked).map(([key, val]) => [key, val.join(" | ")])
            );
            let metadataSelected = Object.fromEntries(
                Object.entries(this.metadataChoiceSelected).map(([key, val]) => [key, val])
            );
            this.dateRangeHandler();
            this.clearAutoCompletePopup();
            this.$router.push(
                this.paramsToRoute({
                    ...this.$store.state.formData,
                    ...this.metadataValues,
                    ...metadataChoices,
                    ...metadataSelected,
                    approximate: this.approximateSelected ? "yes" : "no",
                    q: this.queryTermTyped.trim(),
                    start: "",
                    end: "",
                    byte: "",
                    start_date: this.start_date,
                    end_date: this.end_date,
                })
            );
        },
        onReset() {
            this.$store.commit("setDefaultFields", this.$parent.defaultFieldValues);
            for (let field of this.$philoConfig.metadata) {
                this.metadataValues[field] = "";
            }
            this.queryTermTyped = "";
            for (let metadata in this.metadataInputStyle) {
                if (this.metadataInputStyle[metadata] == "date" || this.metadataInputStyle[metadata] == "int") {
                    this.dateType[metadata] = "exact";
                    this.dateRange[metadata] = { start: "", end: "" };
                }
            }
            this.$nextTick(() => {
                this.show = true;
            });
        },
        reportChange(report) {
            if (report === "landing_page") {
                this.report = this.$philoConfig.search_reports[0];
            } else if (report === "collocation") {
                if (this.$philoConfig.stopwords.length > 0) {
                    this.colloc_filter_choice = "stopwords";
                } else {
                    this.colloc_filter_choice = "frequency";
                }
            }
            this.currentReport = report;
            if (!this.formOpen) {
                this.toggleForm();
            }
        },
        toggleForm() {
            if (!this.formOpen) {
                this.formOpen = true;
            } else {
                this.formOpen = false;
            }
        },
        clearFormData() {},
        selectApproximate(approximateValue) {
            this.approximate_ratio = approximateValue;
        },
        onChange(field) {
            if (this.$philoConfig.autocomplete.includes(field)) {
                if (this.timeout) clearTimeout(this.timeout);
                this.timeout = setTimeout(() => {
                    if (field == "q") {
                        let currentQueryTerm = this.$route.query.q;
                        if (
                            this.queryTermTyped.replace('"', "").length > 1 &&
                            this.queryTermTyped != currentQueryTerm
                        ) {
                            this.$http
                                .get(`${this.$dbUrl}/scripts/autocomplete_term.py`, {
                                    params: { term: this.queryTermTyped },
                                })
                                .then((response) => {
                                    this.autoCompleteResults.q = response.data;
                                    this.isLoading = false;
                                });
                        }
                    } else {
                        let currentFieldValue = this.$route.query[field];
                        if (this.metadataValues[field].length > 1 && this.metadataValues[field] != currentFieldValue) {
                            this.$http
                                .get(`${this.$dbUrl}/scripts/autocomplete_metadata.py`, {
                                    params: {
                                        term: this.metadataValues[field],
                                        field: field,
                                    },
                                })
                                .then((response) => {
                                    this.autoCompleteResults[field] = response.data.map((result) =>
                                        result.replace(/CUTHERE/, "<last/>")
                                    );
                                })
                                .catch((error) => {
                                    this.debug(this, error);
                                });
                        }
                    }
                }, 200);
            }
        },
        onArrowDown(field) {
            if (this.arrowCounters[field] < this.autoCompleteResults[field].length) {
                this.arrowCounters[field] = this.arrowCounters[field] + 1;
            }
            if (this.arrowCounters[field] > 5) {
                let container = document.getElementById(`autocomplete-${field}`);
                let topOffset = container.scrollTop;
                container.scrollTop = topOffset + 36;
            }
        },
        onArrowUp(field) {
            if (this.arrowCounters[field] > 0) {
                this.arrowCounters[field] = this.arrowCounters[field] - 1;
            }
            let container = document.getElementById(`autocomplete-${field}`);
            let topOffset = container.scrollTop;
            container.scrollTop = topOffset - 36;
        },
        onEnter(field) {
            let result = this.autoCompleteResults[field][this.arrowCounters[field]];
            this.setResult(result, field);
        },
        clearAutoCompletePopup() {
            this.autoCompleteResults = {
                q: "",
                ...Object.fromEntries(this.$philoConfig.metadata.map((field) => [field, []])),
            };
        },
        closeAutoComplete() {},
        setResult(inputString, field) {
            if (typeof inputString != "undefined") {
                let inputGroup, lastInput;
                if (field == "q") {
                    inputGroup = inputString.replace(/<[^>]+>/g, "").split(/(\s*\|\s*|\s*OR\s*|\s+|\s*NOT\s*)/);
                    lastInput = inputGroup.pop();
                    if (lastInput.match(/"/)) {
                        if (lastInput.startsWith('"')) {
                            lastInput = lastInput.slice(1);
                        }
                        if (lastInput.endsWith('"')) {
                            lastInput = lastInput.slice(0, lastInput.length - 1);
                        }
                    }
                    this.queryTermTyped = `${inputGroup.join("")}"${lastInput.trim()}"`;
                } else {
                    let prefix = "";
                    if (inputString.match(/<last\/>/)) {
                        inputGroup = inputString.split(/<last\/>/);
                        lastInput = inputGroup.pop();
                        lastInput = lastInput.trim().replace(/<[^>]+>/g, "");
                        prefix = inputGroup.join("");
                    } else {
                        lastInput = inputString.replace(/<[^>]+>/g, "").trim();
                    }
                    if (lastInput.match(/"/)) {
                        if (lastInput.startsWith('"')) {
                            lastInput = lastInput.slice(1);
                        }
                        if (lastInput.endsWith('"')) {
                            lastInput = lastInput.slice(0, lastInput.length - 1);
                        }
                    }
                    let finalInput = `${prefix}"${lastInput}"`;
                    this.metadataValues[field] = finalInput;
                    this.$store.commit("updateFormDataField", {
                        key: field,
                        value: finalInput,
                    });
                }
            }
            this.autoCompleteResults[field] = [];
            this.arrowCounters[field] = -1;
        },
        autoCompletePosition(field) {
            let parent = document.getElementById(`${field}-group`);
            if (parent) {
                let input = parent.querySelector("input");
                let childOffset = input.offsetLeft;
                return `left: ${childOffset}px; width: ${input.offsetWidth}px`;
            }
        },
        dateTypeToggle(metadata, dateType) {
            this.dateRange[metadata] = { start: "", end: "" };
            this.metadataValues[metadata] = "";
            this.dateType[metadata] = dateType;
        },
    },
};
</script>

<style scoped>
input[type="text"] {
    opacity: 1;
}
.input-group,
#search-elements h6 {
    width: fit-content;
}
#report .btn {
    font-variant: small-caps;
    font-size: 1rem !important;
}
.dico-margin {
    margin-top: 210px !important;
}
#search-elements {
    position: absolute;
    z-index: 50;
    background-color: #fff;
    width: 100%;
    left: 0;
}
#search-elements.dico {
    margin-top: 168px;
}

#search-elements > h5 {
    margin-top: 15px;
    margin-bottom: 15px;
}

#search-elements .btn-outline-secondary,
#q-group .btn-outline-secondary,
#head-group .btn {
    pointer-events: none; /*disable hover effect*/
}
#search_terms .input-group,
#search-elements .input-group {
    max-width: 700px;
    width: 100%;
}

#report label {
    font-size: 1.1em;
    font-variant: small-caps;
    text-transform: capitalize;
}

.search_box {
    width: 250px;
    vertical-align: middle;
}

#search_field {
    font-weight: 400;
}

#more_options {
    width: 200px;
}

#more_options:hover {
    cursor: pointer;
}

#search_terms_container {
    padding-top: 15px;
    padding-bottom: 15px;
}

#search_terms,
#head-search-container {
    text-align: center;
}

#head-search-container {
    margin-top: -10px;
    padding-bottom: 15px;
}

.no-example {
    display: none;
}

#method,
.metadata_fields,
#collocation-options > div,
#time-series-options > div {
    margin-top: 10px;
}

#initial-form .btn-primary.active {
    box-shadow: 0px 0px;
    border-top: 0px;
}

#tip-text {
    display: none;
}

#tip-btn:hover #tip-text {
    display: inline;
}

#tip-btn:hover #tip {
    display: none;
}

#search_terms .row {
    text-align: left;
    padding-left: 20px;
    padding-right: 20px;
}
#search-buttons {
    position: absolute;
    top: 3rem;
    right: 1rem;
    z-index: 51;
}

.radio-group {
    border-radius: 0;
}
.radio-btn-group span:last-of-type label {
    border-top-right-radius: 0.25rem;
    border-bottom-right-radius: 0.25rem;
}

@media (max-width: 992px) {
    #search-buttons {
        position: initial;
        margin-bottom: 1rem;
        margin-left: 0;
        margin-right: 0;
        text-align: center;
    }
    #search-elements {
        margin-top: -1rem;
    }
}

@media (max-width: 768px) {
    #collocation-options .row {
        margin-left: -15px;
    }
}

/*Dico layout changes*/

#search_elements {
    border-top-width: 0px;
}

.select {
    font-size: inherit;
    position: relative;
    display: inline-block;
    width: 100%;
    text-align: center;
}

.select select {
    outline: none;
    -webkit-appearance: none;
    display: block;
    padding: 6px 12px;
    margin: 0;
    transition: border-color 0.2s;
    border: 1px solid #ccc;
    border-radius: 0px;
    background: #fff;
    color: #555;
    line-height: normal;
    font-family: inherit;
    font-size: inherit;
    line-height: inherit;
    width: 100%;
}

.autocomplete {
    position: relative;
}
.autocomplete-results {
    padding: 0;
    margin: 3px 0 0 15px;
    border: 1px solid #eeeeee;
    border-top-width: 0px;
    max-height: 216px;
    overflow-y: scroll;
    width: 267px;
    position: absolute;
    left: 0;
    background-color: #fff;
    z-index: 100;
    top: 34px;
    font-size: 1.2rem;
}
.autocomplete-result {
    list-style: none;
    text-align: left;
    padding: 4px 12px;
    cursor: pointer;
    font-size: 1.2rem;
}
.autocomplete-result:hover,
.is-active {
    background-color: #ddd;
    color: black;
}
::placeholder {
    opacity: 0.4;
}

input:focus::placeholder {
    opacity: 0;
}
.code-block {
    font-family: monospace;
    font-size: 120%;
    background-color: #ededed;
    padding: 0px 4px;
}
.date-range {
    display: inline-block;
    width: auto;
}
.slide-fade-enter-active,
.slide-fade-leave-active {
    transition: all 0.3s ease-out;
}
.slide-fade-enter-from,
.slide-fade-leave-to {
    transform: translateY(-30px);
    opacity: 0;
}
h6 {
    font-variant: small-caps;
    font-weight: 700;
    font-size: 1.05rem;
}
</style>