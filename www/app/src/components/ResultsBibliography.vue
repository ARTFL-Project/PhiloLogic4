<template>
    <ul id="results-bibliography" style>
        <li
            style="list-style-type: disc;"
            v-for="(result, resultIndex) in uniquedResults"
            :key="resultIndex"
        >
            <span class="cite">
                <citations :citation="result.citation"></citations>
            </span>&nbsp;:
            <router-link
                class="ml-2"
                :to="`/${report}?${buildLink(result.metadata_fields.title)}`"
            >{{ result.count }} occurrence(s)</router-link>
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
                    uniqueResults[uniqueResults.length - 1].count++;
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
                result.count = 1;
                uniqueResults.push(result);
                previousFilename = result.metadata_fields.filename;
            }
            return uniqueResults;
        }
    },
    methods: {
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