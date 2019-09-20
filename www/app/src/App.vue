<template>
    <div id="app">
        <Header />
        <SearchForm />
        <router-view :key="$route.fullPath"></router-view>
    </div>
</template>

<script>
import Header from "./components/Header.vue";
import SearchForm from "./components/SearchForm.vue";
import { EventBus } from "./main.js";
import { mapFields } from "vuex-map-fields";

export default {
    name: "app",
    components: {
        Header,
        SearchForm
    },
    computed: {
        ...mapFields(["formData.report", "formData.q"]),
        defaultFieldValues() {
            let localFields = {
                report: "concordance",
                q: "",
                method: "proxy",
                arg_proxy: "",
                arg_phrase: "",
                results_per_page: "25",
                start: "",
                end: "",
                colloc_filter_choice: "",
                filter_frequency: 100,
                approximate: "no",
                approximate_ratio: 100,
                start_date: "",
                end_date: "",
                year_interval: "",
                sort_by: "rowid",
                first_kwic_sorting_option: "",
                second_kwic_sorting_option: "",
                third_kwic_sorting_option: "",
                start_byte: "",
                end_byte: ""
            };
            for (let field of this.$philoConfig.metadata) {
                localFields[field] = "";
            }
            return localFields;
        },
        reportValues() {
            let reportValues = {};
            let commonFields = [
                "q",
                "method",
                "arg_proxy",
                "arg_phrase",
                "approximate",
                "approximate_ratio",
                ...this.$philoConfig.metadata
            ];
            reportValues.concordance = new Set([
                ...commonFields,
                "results_per_page",
                "sort_by",
                "hit_num"
            ]);
            reportValues.kwic = new Set([
                ...commonFields,
                "results_per_page",
                "first_kwic_sorting_option",
                "second_kwic_sorting_option",
                "third_kwic_sorting_option"
            ]);
            reportValues.collocation = new Set([
                ...commonFields,
                "start",
                "colloc_filter_choice",
                "filter_frequency"
            ]);
            reportValues.time_series = new Set([
                ...commonFields,
                "start_date",
                "end_date",
                "year_interval",
                "max_time"
            ]);
            return reportValues;
        }
    },
    created() {
        document.title = this.$philoConfig.dbname;
        this.$store.commit("setDefaultFields", this.defaultFieldValues);
        this.$store.commit("setReportValues", this.reportValues);
        this.formDataUpdate();
    },
    watch: {
        // call again the method if the route changes
        $route: "formDataUpdate"
    },
    methods: {
        formDataUpdate() {
            let localParams = this.copyObject(this.defaultFieldValues);
            this.$store.commit("updateFormData", {
                ...localParams,
                ...this.$route.query
            });
            this.evaluateRoute();
            EventBus.$emit("urlUpdate");
        },
        evaluateRoute() {
            console.log(this.$route);
            if (this.$route.name == null) {
                this.$router.push("./");
            } else if (
                this.$route.name != "home" &&
                this.$route.name != "textNavigation" &&
                this.$route.name != "tableOfContents"
            ) {
                if (this.q.length == 0 && this.report != "bibliography") {
                    this.report = "bibliography";
                    this.$router.push(
                        this.paramsToRoute(this.$store.state.formData)
                    );
                } else if (
                    this.q.length > 0 &&
                    this.$route.name == "bibliography"
                ) {
                    this.$store.commit("updateFormDataField", {
                        key: "report",
                        value: "concordance"
                    });
                    this.debug(this, this.report);
                    this.$router.push(
                        this.paramsToRoute(this.$store.state.formData)
                    );
                }
            }
        }
    }
};
</script>

<style>
.highlight {
    color: #ef4500;
    font-weight: 400;
}
.passage-highlight {
    display: inline-block;
    color: royalblue;
}
li {
    list-style-type: none;
}
body {
    font-size: 0.95rem;
    font-family: "Open-Sans", sans-serif;
}
.toc-div1 > a,
.toc-div2 > a,
.toc-div3 > a {
    padding: 5px 5px 5px 0px;
}

.bullet-point-div1,
.bullet-point-div2,
.bullet-point-div3 {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 5px;
}

.bullet-point-div1 {
    border: solid 1px;
}

.bullet-point-div2 {
    border: solid 2px;
}

.bullet-point-div3 {
    border: solid 1px;
}

.toc-div1,
.toc-div2,
.toc-div3 {
    text-indent: -0.9em;
    /*Account for the bullet point*/
    margin-bottom: 5px;
}

.toc-div1 {
    padding-left: 0.9em;
}

.toc-div2 {
    padding-left: 1.9em;
}

.toc-div3 {
    padding-left: 2.9em;
}

.toc-div1:hover,
.toc-div2:hover,
.toc-div3:hover {
    cursor: pointer;
}
br {
    content: " ";
    display: block;
}
</style>
