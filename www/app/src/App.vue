<template>
    <div id="philologic-app">
        <Header />
        <SearchForm v-if="accessAuthorized" />
        <router-view v-if="accessAuthorized" />
        <access-control :client-ip="clientIp" :domain-name="domainName" v-if="!accessAuthorized" />
        <div class="container-fluid" role="complementary" aria-label="Footer" v-if="accessAuthorized">
            <div class="text-center mb-4">
                <hr class="mb-3" style="width:20%; margin: auto" />
                Powered by
                <br />
                <a href="https://artfl-project.uchicago.edu/"
                    title="Philologic 4: Open Source ARTFL Search and Retrieval Engine">
                    <img src="./assets/philo.png" alt="PhiloLogic" height="40" width="110" />
                </a>
            </div>
        </div>
    </div>
</template>

<script>
import { defineAsyncComponent } from "vue";
import { mapFields } from "vuex-map-fields";
import Header from "./components/Header.vue";
const SearchForm = defineAsyncComponent(() => import("./components/SearchForm.vue"));
const AccessControl = defineAsyncComponent(() => import("./components/AccessControl.vue"));

export default {
    name: "app",
    components: {
        Header,
        SearchForm,
        AccessControl,
    },
    inject: ["$http"],
    data() {
        return {
            initialLoad: true,
            clientIp: "",
            domainName: "",
            accessAuthorized: true,
        };
    },
    computed: {
        ...mapFields(["formData.report", "formData.q", "urlUpdate", "showFacets"]),
        defaultFieldValues() {
            let localFields = {
                report: "home",
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
                year_interval: this.$philoConfig.time_series_interval,
                sort_by: "rowid",
                first_kwic_sorting_option: "",
                second_kwic_sorting_option: "",
                third_kwic_sorting_option: "",
                start_byte: "",
                end_byte: "",
                group_by: this.$philoConfig.aggregation_config[0].field,
            };
            for (let field of this.$philoConfig.metadata) {
                localFields[field] = "";
            }
            return localFields;
        },
        reportValues() {
            let reportValues = {};
            let commonFields = ["q", "approximate", "approximate_ratio", ...this.$philoConfig.metadata];
            reportValues.concordance = new Set([
                ...commonFields,
                "method",
                "arg_proxy",
                "arg_phrase",
                "results_per_page",
                "sort_by",
                "hit_num",
                "start",
                "end",
                "frequency_field",
            ]);
            reportValues.kwic = new Set([
                ...commonFields,
                "method",
                "arg_proxy",
                "arg_phrase",
                "results_per_page",
                "first_kwic_sorting_option",
                "second_kwic_sorting_option",
                "third_kwic_sorting_option",
                "start",
                "end",
                "frequency_field",
            ]);
            reportValues.collocation = new Set([...commonFields, "start", "colloc_filter_choice", "filter_frequency"]);
            reportValues.time_series = new Set([
                ...commonFields,
                "method",
                "arg_proxy",
                "arg_phrase",
                "start_date",
                "end_date",
                "year_interval",
                "max_time",
            ]);
            reportValues.aggregation = new Set([...commonFields, "method", "arg_proxy", "arg_phrase", "group_by"]);
            return reportValues;
        },
    },
    created() {
        if (!this.$philoConfig.valid_config) {
            document.body.innerHTML = `<h2>Invalid web config file: ${this.$philoConfig.web_config_path}<br/>Check for python syntax error in the config file</h2>`;
        } else {
            document.title = this.$philoConfig.dbname.replace(/<[^>]+>/, "");
            const html = document.documentElement;
            html.setAttribute("lang", "sv");
            this.$i18n.locale = localStorage.getItem("lang") || "en";
            this.accessAuthorized = this.$philoConfig.access_control ? false : true;
            let baseUrl = this.getBaseUrl(); // Make sure proxied access uses proxy server for access request
            if (this.$philoConfig.access_control) {
                this.$http
                    .get(`${baseUrl}/scripts/access_request.py`, {
                        headers: {
                            "Access-Control-Allow-Origin": "*",
                        },
                    })
                    .then((response) => {
                        this.accessAuthorized = response.data.access;
                        if (this.accessAuthorized) {
                            this.setupApp();
                        } else {
                            this.clientIp = response.data.incoming_address;
                            this.domainName = response.data.domain_name;
                        }
                    });
            } else {
                this.setupApp();
            }
        }
        if (this.$philoConfig.facets.length < 1) {
            this.showFacets = false;
        }
    },
    watch: {
        // call again the method if the route changes
        $route: "formDataUpdate",
        accessAuthorized(authorized) {
            if (authorized) {
                this.setupApp();
            }
        },
    },
    methods: {
        getBaseUrl() {
            let href = window.location.href;
            href = href.replace(/\/concordance.*/, "");
            href = href.replace(/\/kwic.*/, "");
            href = href.replace(/\/collocation.*/, "");
            href = href.replace(/\/aggregation.*/, "");
            href = href.replace(/\/table-of-contents.*/, "");
            href = href.replace(/\/navigate.*/, "");
            href = href.replace(/\/time_series.*/, "");
            href = href.replace(/\/bibliography.*/, "");
            return href;
        },

        setupApp() {
            this.$store.commit("setDefaultFields", this.defaultFieldValues);
            this.$store.commit("setReportValues", this.reportValues);
            this.formDataUpdate();
        },
        formDataUpdate() {
            let localParams = this.copyObject(this.defaultFieldValues);
            this.$store.commit("updateFormData", {
                ...localParams,
                ...this.$route.query,
            });
            if (!["textNavigation", "tableOfContents", "home"].includes(this.$route.name)) {
                this.evaluateRoute();
                this.urlUpdate = this.$route.fullPath;
            }
        },
        evaluateRoute() {
            if (this.$route.name == "bibliography") {
                this.report = "bibliography";
            }
            if (
                !["home", "textNavigation", "tableOfContents"].includes(this.$route.name) &&
                this.q.length > 0 &&
                this.$route.name == "bibliography"
            ) {
                this.$store.commit("updateFormDataField", {
                    key: "report",
                    value: "concordance",
                });
                this.debug(this, this.report);
                this.$router.push(this.paramsToRoute({ ...this.$store.state.formData }));
            } else {
                this.report = this.$route.name;
            }
        },
    },
};
</script>
<style lang="scss">
@import "./assets/styles/theme.module.scss";
@import "../node_modules/bootstrap/scss/bootstrap.scss";

a {
    text-decoration: none;
}

.btn:focus {
    box-shadow: none !important;
}

.modal-backdrop {
    opacity: 0.7;
}

.highlight {
    color: #900;
    font-weight: 700;
}

.passage-highlight {
    display: inline-block;
    color: royalblue;
}

li {
    list-style-type: none;
}

body,
.btn,
select,
.custom-control-label,
.custom-control,
.input-group-text,
input {
    font-size: 14px !important;
    font-family: "Open-Sans", sans-serif;
}

.text-view {
    font-family: "Source Serif Pro", serif;
    font-size: 0.9rem;
}

.custom-control {
    min-height: auto;
}

.toc-div1>a,
.toc-div2>a,
.toc-div3>a {
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
    background: #000;
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

/*Text formatting*/

span.note {
    display: inline;
}

.xml-l {
    display: block;
}

.xml-l::before {
    content: "";
    font-family: "Droid Sans Mono", sans-serif;
    font-size: 0.7em;
    white-space: pre;
    width: 35px;
    display: inline-block;
}

.xml-l[id]::before {
    content: attr(id);
    color: #bababa;
}

.xml-l[n]::before {
    content: attr(n);
    color: #bababa;
}

.xml-l[type="split"]::before {
    content: "";
}

.xml-milestone::before {
    content: attr(n) "\00a0";
    color: #909090;
    font-family: "Droid Sans Mono", sans-serif;
    font-size: 0.6em;
    vertical-align: 0.3em;
}

.xml-milestone[unit="card"]::before {
    content: "";
}

.xml-lb[type="hyphenInWord"] {
    display: inline;
}

.xml-gap .xml-desc {
    display: none;
}

.xml-gap::after {
    content: "*";
}

.xml-hi {
    font-style: italic;
    font-variant: small-caps;
}

.xml-w::before {
    margin: 0;
    padding: 0;
    float: left;
}

.xml-speaker {
    display: block;
}

/*Remove spacing before punctuation*/
.xml-w[pos=","],
.xml-w[pos="."],
.xml-w[pos=";"],
.xml-w[pos="?"],
.xml-w[pos="!"],
.xml-w[pos=":"],
.xml-w[pos="!"] {
    margin-left: -0.25em;
}
</style>