<template>
    <div id="app">
        <Header />
        <SearchForm v-if="authorized" />
        <router-view :key="$route.fullPath" v-if="authorized"></router-view>
        <access-control
            :client-ip="clientIp"
            :domain-name="domainName"
            :authorized="authorized"
            v-if="!authorized"
        />
        <b-container fluid v-if="authorized">
            <div class="text-center mb-4">
                <hr width="20%" />Powered by
                <br />
                <a
                    href="https://artfl-project.uchicago.edu/"
                    title="Philologic 4: Open Source ARTFL Search and Retrieval Engine"
                >
                    <img src="./assets/philo.png" height="40" width="110" />
                </a>
            </div>
        </b-container>
    </div>
</template>

<script>
import Header from "./components/Header.vue";
import SearchForm from "./components/SearchForm.vue";
import AccessControl from "./components/AccessControl.vue";
import { EventBus } from "./main.js";
import { mapFields } from "vuex-map-fields";

export default {
    name: "app",
    components: {
        Header,
        SearchForm,
        AccessControl
    },
    data() {
        return {
            authorized: true,
            clientIp: "",
            domainName: ""
        };
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
                end_byte: "",
                group_by: ""
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
                "hit_num",
                "start",
                "end",
                "frequency_field"
            ]);
            reportValues.kwic = new Set([
                ...commonFields,
                "results_per_page",
                "first_kwic_sorting_option",
                "second_kwic_sorting_option",
                "third_kwic_sorting_option",
                "start",
                "end",
                "frequency_field"
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
            reportValues.statistics = new Set([...commonFields, "group_by"]);
            return reportValues;
        }
    },
    created() {
        document.title = this.$philoConfig.dbname.replace(/<[^>]+>/, "");
        if (this.$philoConfig.access_control) {
            let promise = this.checkAccessAuthorization();
            promise.then(response => {
                this.authorized = response.data.access;
                if (this.authorized) {
                    this.setupApp();
                } else {
                    this.clientIp = response.data.incoming_address;
                    this.domainName = response.data.domain_name;
                }
            });
        } else {
            this.setupApp();
        }
        EventBus.$on("accessAuthorized", () => {
            this.setupApp();
            this.authorized = true;
        });
    },
    watch: {
        // call again the method if the route changes
        $route: "formDataUpdate"
    },
    methods: {
        setupApp() {
            this.$store.commit("setDefaultFields", this.defaultFieldValues);
            this.$store.commit("setReportValues", this.reportValues);
            this.formDataUpdate();
        },
        checkAccessAuthorization() {
            let promise = this.$http.get(
                `${this.$dbUrl}/scripts/access_request.py`
            );
            return promise;
        },
        formDataUpdate() {
            let localParams = this.copyObject(this.defaultFieldValues);
            this.$store.commit("updateFormData", {
                ...localParams,
                ...this.$route.query
            });
            if (
                !["textNavigation", "tableOfContents"].includes(
                    this.$route.name
                )
            ) {
                this.evaluateRoute();
                EventBus.$emit("urlUpdate");
            }
        },
        evaluateRoute() {
            if (this.$route.name == "bibliography") {
                this.report = "bibliography";
            }
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
