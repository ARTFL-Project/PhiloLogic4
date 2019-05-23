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

export default {
    name: "app",
    components: {
        Header,
        SearchForm
    },
    data() {
        return {
            globalConfig: this.$globalConfig,
            metadata: this.$philoConfig.metadata
        };
    },
    created() {
        this.$store.commit("updateStore", {
            routeQuery: this.$route.query,
            metadata: this.metadata
        });
        this.$router.beforeEach((to, from, next) => {
            this.$store.commit("updateStore", {
                routeQuery: to.query,
                metadata: this.metadata
            });
            next();
            EventBus.$emit("urlUpdate");
        });
    },
    methods: {}
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
