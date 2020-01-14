<template>
    <div>
        <p>
            Results from the current page will be generated.
            <br />
            <br />Choose between the following options:
        </p>
        <b-button-group size="sm" vertical>
            <b-button @click="getResults('json', false)">JSON (with HTML)</b-button>
            <b-button @click="getResults('json', true)">JSON (with no HTML)</b-button>
            <b-button @click="getResults('csv', false)">CSV (with HTML)</b-button>
            <b-button @click="getResults('csv', true)">CSV (with no HTML)</b-button>
        </b-button-group>
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