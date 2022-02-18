<template>
    <span class="philologic-cite ps-2">
        <span class="citation text-view" v-for="(cite, citeIndex) in filterNone(citation)" :key="citeIndex">
            <span v-html="cite.prefix" v-if="cite.prefix"></span>
            <router-link :to="cite.href" :style="cite.style" v-if="cite.href">{{ cite.label }}</router-link>
            <span :style="cite.style" v-else>{{ cite.label }}</span>
            <span v-html="cite.suffix" v-if="cite.suffix"></span>
            <span class="separator px-2" v-if="citeIndex != citation.length - 1">&#9679;</span>
        </span>
    </span>
</template>
<script>
export default {
    name: "citations",
    props: ["citation"],
    setup() {
        const filterNone = (citation) => {
            if (Symbol.iterator in Object(citation)) {
                let filteredCitation = [];
                for (let cite of citation) {
                    if (cite.label != "None") {
                        filteredCitation.push(cite);
                    }
                }
                return filteredCitation;
            }
            return citation;
        };
        return { filterNone };
    },
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
