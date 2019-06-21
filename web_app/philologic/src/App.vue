<template>
    <div id="app">
        <Header/>
        <SearchForm/>
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
        ...mapFields(["formData.report", "formData.q"])
    },
    data() {
        return {
            globalConfig: this.$globalConfig,
            metadata: this.$philoConfig.metadata
        };
    },
    created() {
        document.title = this.$philoConfig.dbname;
        this.evaluateRoute();
        this.$router.beforeEach((to, from, next) => {
            console.log("TO:", to, "FROM:", from);
            if (
                typeof this.$route.query.q == "undefined" &&
                this.$route.name != "navigate"
            ) {
                this.report = "bibliography";
            } else {
                this.$store.commit("updateStore", {
                    routeQuery: to.query,
                    metadata: this.metadata
                });
            }
            next();
            EventBus.$emit("urlUpdate");
        });
    },
    methods: {
        evaluateRoute() {
            if (
                this.$route.name != "home" &&
                this.$route.name != "textNavigation" &&
                this.$route.name != "tableOfContents"
            ) {
                let queryParams = this.copyObject(this.$route.query);
                if (typeof queryParams.q == "undefined") {
                    queryParams.report = "bibliography";
                    this.$store.commit("updateStore", {
                        routeQuery: queryParams,
                        metadata: this.metadata
                    });
                    this.$router.push(
                        this.paramsToRoute(this.$store.state.formData)
                    );
                } else if (
                    this.$route.query.q.length > 0 &&
                    this.$route.name == "bibliography"
                ) {
                    let queryParams = this.copyObject(this.$route.query);
                    queryParams.report == "concordance";
                    this.$store.commit("updateStore", {
                        routeQuery: queryParams,
                        metadata: this.metadata
                    });
                    this.$router.push(
                        this.paramsToRoute(this.$store.state.formData)
                    );
                } else {
                    this.$store.commit("updateStore", {
                        routeQuery: queryParams,
                        metadata: this.metadata
                    });
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
</style>
