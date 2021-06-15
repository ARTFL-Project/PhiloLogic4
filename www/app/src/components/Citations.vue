<template>
    <span class="philologic-cite ps-2">
        <span class="citation" v-for="(cite, citeIndex) in citation" :key="citeIndex">
            <span v-html="cite.prefix" v-if="cite.prefix"></span>
            <router-link :to="cite.href" :style="cite.style" v-if="cite.href">{{ cite.label }}</router-link>
            <span :style="cite.style" v-else>{{ cite.label }}</span>
            <span v-html="cite.suffix" v-if="cite.suffix"></span>
            <span v-html="cite.separator" v-if="cite.separator.length > 0 && citeIndex != maxIndex"></span>
            <span class="separator px-2" v-if="cite.separator.length == 0 && citeIndex != maxIndex">&#9679;</span>
        </span>
    </span>
</template>
<script>
export default {
    name: "citations",
    props: ["citation"],
    data() {
        return {
            maxIndex: this.citation.length - 1,
        };
    },
};
</script>
<style scoped>
.separator {
    font-size: 0.75rem;
    vertical-align: 0.05rem;
}
</style>
