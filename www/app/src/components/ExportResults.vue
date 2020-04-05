<template>
    <div>
        <p>ONLY results from the current page will be generated.</p>
        <h6>With text in HTML:</h6>
        <b-button @click="getResults('json', false)">JSON</b-button>&nbsp;
        <b-button @click="getResults('csv', false)">CSV</b-button>
        <h6 class="mt-2">With plain text:</h6>
        <b-button @click="getResults('json', true)">JSON</b-button>&nbsp;
        <b-button @click="getResults('csv', true)">CSV</b-button>
    </div>
</template>
<script>
import { mapFields } from "vuex-map-fields";

export default {
    name: "ExportResults",
    computed: {
        ...mapFields(["formData.report"])
    },
    methods: {
        getResults(format, html) {
            this.$http
                .get(
                    `${
                        this.$dbUrl
                    }/scripts/export_results.py?${this.paramsToUrlString({
                        ...this.$store.state.formData,
                        filter_html: html.toString(),
                        output_format: format,
                        report: ""
                    })}&report=${this.report}`
                )
                .then(response => {
                    let text = "";
                    let element = document.createElement("a");
                    let filename = `${this.paramsToUrlString(
                        this.$store.state.formData
                    )}.${format}`;
                    if (format == "json") {
                        text = JSON.stringify(response.data);
                    } else if (format == "csv") {
                        text = response.data;
                    }
                    element.setAttribute(
                        "href",
                        "data:text/plain;charset=utf-8," +
                            encodeURIComponent(text)
                    );
                    element.setAttribute("download", filename);
                    element.style.display = "none";
                    document.body.appendChild(element);
                    element.click();
                    document.body.removeChild(element);
                });
        }
    }
};
</script>