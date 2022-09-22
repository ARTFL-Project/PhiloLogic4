<template>
    <span class="philologic-cite ps-2">
        <span class="citation text-view" v-for="(cite, citeIndex) in citation" :key="citeIndex">
            <span v-html="cite.prefix" v-if="cite.prefix"></span>
            <router-link :to="cite.href" :style="cite.style" v-if="cite.href">{{ cite.label }}</router-link>
            <span :style="cite.style" v-else>{{ cite.label }}</span>
            <span v-html="cite.suffix" v-if="cite.suffix"></span>
            <span v-if="citeIndex != citation.length - 1"
                ><span class="separator px-2" v-if="!separator">&#9679;</span><span v-else>{{ separator }}</span></span
            >
        </span>
    </span>
</template>
<script>
export default {
    name: "citations-generator",
    props: ["citation", "separator"],
};
</script>
<style scoped>
.separator {
    font-size: 0.75rem;
    vertical-align: 0.05rem;
}
.citation {
    font-weight: 600;
}
</style>
