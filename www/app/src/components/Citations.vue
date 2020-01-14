<template>
    <span class="philologic-cite pl-2">
        <span class="citation" v-for="(citation, citeIndex) in citation" :key="citeIndex">
            <span v-html="citation.prefix"></span>
            <router-link :to="'/' + citation.href" :style="citation.style" v-if="citation.href">{{
                citation.label
            }}</router-link>
            <span :style="citation.style" v-else>{{ citation.label }}</span>
            <span v-html="citation.suffix"></span>
            <span v-html="citation.separator" v-if="citation.separator.length > 0 && citeIndex != maxIndex"></span>
            <span class="separator" v-if="citation.separator.length == 0 && citeIndex != maxIndex"
                >&nbsp;&#9679;&nbsp;</span
            >
        </span>
    </span>
</template>
<script>
export default {
    name: "citations",
    props: ["citation"],
    data() {
        return {
            maxIndex: this.citation.length - 1
        }
    }
}
</script>
<style scoped></style>
