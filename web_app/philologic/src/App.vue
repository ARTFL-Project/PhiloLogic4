<template>
  <div id="app">
    <Header/>
    <SearchForm/>
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
</style>
