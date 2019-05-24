<template>
    <div id="app">
        <Header/>
        <SearchForm/>
        <router-view></router-view>
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
        this.evaluateRoute();
        this.$router.beforeEach((to, from, next) => {
            if (typeof this.$router.query.q == "undefined") {
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
            if (this.$route.name != "home") {
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
                        routeQuery: this.$route.query,
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
</style>
