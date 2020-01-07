<template>
    <span class="philologic-cite pl-2">
        <span class="citation" v-for="(citation, citeIndex) in citation" :key="citeIndex">
            <span v-if="citation.href">
                <span v-html="citation.prefix"></span>
                <router-link :to="'/' + citation.href" :style="citation.style">{{ citation.label }}</router-link>
                <span v-html="citation.suffix"></span>
                <span v-html="citation.separator" v-if="citation.separator.length > 0 && citeIndex != maxIndex"></span>
                <span class="separator" v-if="citation.separator.length > 0 && citeIndex != maxIndex">&#9679;</span>
            </span>
            <span v-if="!citation.href">
                <span v-html="citation.prefix"></span>
                <span :style="citation.style">{{ citation.label }}</span>
                <span v-html="citation.suffix"></span>
                <span v-html="citation.separator" v-if="citation.separator.length > 0 && citeIndex != maxIndex"></span>
                <span class="separator" v-if="citation.separator.length > 0 && citeIndex != maxIndex">&#9679;</span>
            </span>
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
