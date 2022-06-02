<template>
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Export Results</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <p v-if="report == 'concordance' || report == 'kwic' || report == 'bibliography'">
                    ONLY results from the current page will be generated.
                </p>
                <div v-if="report == 'concordance' || report == 'kwic'">
                    <h6>With text in HTML:</h6>
                    <button type="button" class="btn btn-secondary" @click="getResults('json', false)">JSON</button
                    >&nbsp;
                    <button type="button" class="btn btn-secondary" @click="getResults('csv', false)">CSV</button>
                </div>
                <h6 class="mt-2" v-if="report == 'concordance' || report == 'kwic'">With plain text:</h6>
                <button type="button" class="btn btn-secondary" @click="getResults('json', true)">JSON</button>&nbsp;
                <button type="button" class="btn btn-secondary" @click="getResults('csv', true)">CSV</button>
            </div>
        </div>
    </div>
</template>
<script>
import { mapFields } from "vuex-map-fields";

export default {
    name: "ExportResults",
    computed: {
        ...mapFields(["formData.report"]),
    },
    inject: ["$http"],
    methods: {
        getResults(format, html) {
            this.$http
                .get(
                    `${this.$dbUrl}/scripts/export_results.py?${this.paramsToUrlString({
                        ...this.$store.state.formData,
                        filter_html: html.toString(),
                        output_format: format,
                        report: "",
                    })}&report=${this.report}`
                )
                .then((response) => {
                    let text = "";
                    let element = document.createElement("a");
                    let filename = `${this.paramsToUrlString({ ...this.$store.state.formData })}.${format}`;
                    if (format == "json") {
                        text = JSON.stringify(response.data);
                    } else if (format == "csv") {
                        text = response.data;
                    }
                    element.setAttribute("href", "data:text/plain;charset=utf-8," + encodeURIComponent(text));
                    element.setAttribute("download", filename);
                    element.style.display = "none";
                    document.body.appendChild(element);
                    element.click();
                    document.body.removeChild(element);
                });
        },
    },
};
</script>