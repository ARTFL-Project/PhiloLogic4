<template>
    <div id="app">
        <Header/>
        <SearchForm/>
        <router-view></router-view>
    </div>
</template>

<script>
import Header from './components/Header.vue'
import SearchForm from './components/SearchForm.vue'

export default {
    name: 'app',
    components: {
        Header,
        SearchForm
    },
    data() {
        return {
            globalConfig: this.$globalConfig
        }
    }
}
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
</style>
