<template>
    <span class="philologic-cite pl-2">
        <span class="citation" v-for="(citation, citeIndex) in citation" :key="citeIndex">
            <span v-if="citation.href">
                <span v-html="citation.prefix"></span>
                <router-link :to="'/' + citation.href" :style="citation.style">{{ citation.label }}</router-link>
                <span v-html="citation.suffix"></span>
                <span class="separator" v-if="citeIndex != citation.length - 1">&#9679;</span>
            </span>
            <span v-if="!citation.href">
                <span v-html="citation.prefix"></span>
                <span :style="citation.style">{{ citation.label }}</span>
                <span v-html="citation.suffix"></span>
                <span class="separator" v-if="citeIndex != citation.length - 1">&#9679;</span>
            </span>
        </span>
    </span>
</template>
<script>
export default {
    name: "citations",
    props: ["citation"]
};
</script>
<style scoped>
</style>


