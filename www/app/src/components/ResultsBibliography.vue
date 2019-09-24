<template>
    <ul id="results-bibliography" style>
        <li
            style="list-style-type: disc;"
            v-for="(result, resultIndex) in uniquedResults"
            :key="resultIndex"
            @mouseover="showConcordanceLink(resultIndex)"
            @mouseleave="hideConcordanceLink(resultIndex)"
        >
            <span class="cite">
                <citations :citation="result.citation"></citations>
            </span>
            <router-link
                class="bib pl-2"
                style="display: none"
                :to="`/${report}?${buildLink(result.metadata_fields.title)}`"
            >See results in this work</router-link>
        </li>
    </ul>
</template>
<script>
import citations from "./Citations";
import { mapFields } from "vuex-map-fields";

export default {
    name: "ResultsBibliography",
    components: { citations },
    props: ["results"],
    computed: {
        ...mapFields(["formData.report"]),
        uniquedResults() {
            let uniqueResults = [];
            let previousFilename = "";
            for (let result of this.results) {
                if (result.metadata_fields.filename == previousFilename) {
                    continue;
                }
                result = this.copyObject(result);
                let citation = [];
                for (let i = 0; i < result.citation.length; i++) {
                    if (result.citation[i].object_type == "doc") {
                        citation.push(result.citation[i]);
                    }
                }
                result.citation = citation;
                uniqueResults.push(result);
                previousFilename = result.metadata_fields.filename;
            }
            return uniqueResults;
        }
    },
    methods: {
        showConcordanceLink(index) {
            let element = document.querySelector(
                `#results-bibliography > li:nth-child(${index + 1}) > .bib`
            );
            if (element != null) {
                element.style.display = "";
            }
        },
        hideConcordanceLink(index) {
            let element = document.querySelector(
                `#results-bibliography > li:nth-child(${index + 1}) > .bib`
            );
            if (element != null) {
                element.style.display = "none";
            }
        },
        buildLink(title) {
            return this.paramsToUrlString({
                ...this.$store.state.formData,
                title: `"${title}"`
            });
        }
    }
};
</script>
<style scoped>
#results-bibliography {
    padding-inline-start: 2rem;
    margin-bottom: 0;
}
</style>