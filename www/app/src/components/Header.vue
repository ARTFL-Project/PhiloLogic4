<template>
    <nav class="navbar navbar-expand-lg navbar-light bg-light shadow" style="height: 53px">
        <div class="collapse navbar-collapse top-links">
            <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                <li class="nav-item">
                    <a
                        class="nav-link"
                        :href="philoConfig.link_to_home_page"
                        v-if="philoConfig.link_to_home_page != ''"
                        >{{ $t("header.goHome") }}</a
                    >
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="https://artfl-project.uchicago.edu">ARTFL Project</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="https://textual-optics-lab.uchicago.edu">Textual Optics Lab</a>
                </li>
            </ul>
        </div>
        <button
            type="button"
            class="nav-link position-absolute cite"
            data-bs-toggle="modal"
            data-bs-target="#academic-citation"
            v-if="philoConfig.academic_citation.collection.length > 0"
        >
            {{ $t("header.citeUs") }}
        </button>
        <router-link class="navbar-brand" to="/" v-html="philoConfig.dbname"></router-link>
        <ul class="navbar-nav ml-auto top-links">
            <li class="nav-item">
                <a class="nav-link" href="https://www.uchicago.edu">University of Chicago</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="https://atilf.fr">ATILF-CNRS</a>
            </li>
            <li class="nav-item">
                <a
                    class="nav-link"
                    href="https://artfl-project.uchicago.edu/content/contact-us"
                    title="Contact information for the ARTFL Project"
                    >{{ $t("header.contactUs") }}</a
                >
            </li>
        </ul>
        <a
            id="report-error-link"
            class="nav-link position-absolute"
            :href="philoConfig.report_error_link"
            target="_blank"
            v-if="philoConfig.report_error_link.length > 0"
            >{{ $t("header.reportError") }}</a
        >
        <div
            class="modal fade"
            id="academic-citation"
            tabindex="-1"
            aria-labelledby="academic-citation"
            aria-hidden="true"
        >
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">How to cite {{ philoConfig.dbname }}:</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <span v-if="docCitation.citation.length > 0"
                            ><citations :citation="docCitation.citation" separator=", " /> , &nbsp;</span
                        >
                        <span v-html="philoConfig.academic_citation.collection"></span>:
                        <a :href="citeURL">{{ citeURL }}</a>
                        <span>. Accessed on {{ date }}</span>
                    </div>
                </div>
            </div>
        </div>
    </nav>
</template>

<script>
import citations from "./Citations";

export default {
    name: "Header-component",
    components: { citations },
    inject: ["$http"],
    data() {
        return {
            philoConfig: this.$philoConfig,
            date: this.getDate(),
            docCitation: { citation: [] },
            citeURL: this.$philoConfig.academic_citation.custom_url || this.$dbUrl,
        };
    },
    created() {
        this.getDocCitation();
    },
    watch: {
        $route() {
            this.getDocCitation();
        },
    },
    methods: {
        getDate() {
            let today = new Date();
            let months = [
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ];
            let month = months[today.getMonth()];
            return `${today.getDate()} ${month}, ${today.getFullYear()}`;
        },
        getDocCitation() {
            let textObjectURL = this.$route.params;
            if ("pathInfo" in textObjectURL) {
                let philoID = textObjectURL.pathInfo.split("/").join(" ");
                this.$http
                    .get(`${this.$dbUrl}/scripts/get_academic_citation.py?philo_id=${philoID}`)
                    .then((response) => {
                        this.docCitation.citation = response.data.citation;
                    });
            } else {
                this.docCitation.citation = [];
            }
        },
    },
};
</script>

<style lang="scss" scoped>
@import "../assets/styles/theme.module.scss";
.top-links {
    margin-left: -0.25rem;
    font-size: 80%;
    margin-top: -2rem;
    font-variant: small-caps;
}
#right-side-links {
    font-size: 80%;
    margin-top: -1rem;
    font-variant: small-caps;
}
.navbar-brand {
    font-weight: 700;
    font-size: 1.6rem !important;
    font-variant: small-caps;
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    line-height: 80%;
}

#report-error-link {
    right: 0.5rem;
    bottom: 0.25rem;
    font-variant: small-caps;
    font-weight: 700;
}
.cite {
    left: 0.5rem;
    bottom: 0.25rem;
    font-variant: small-caps;
    font-weight: 700;
    background-color: inherit;
    border-width: 0;
    color: $link-color;
}
.modal-dialog {
    max-width: fit-content;
}
</style>