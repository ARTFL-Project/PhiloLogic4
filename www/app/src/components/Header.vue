<template>
    <nav class="navbar navbar-expand-lg navbar-light bg-light shadow" style="height: 53px" v-once>
        <div class="collapse navbar-collapse top-links">
            <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                <li class="nav-item">
                    <a class="nav-link" :href="philoConfig.link_to_home_page" v-if="philoConfig.link_to_home_page != ''"
                        >Go to home page</a
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
                    >Contact Us</a
                >
            </li>
        </ul>
        <a
            class="nav-link position-absolute"
            style="right: -0.5rem; bottom: -0.25rem; font-variant: small-caps; font-weight: 700"
            :href="philoConfig.report_error_link"
            target="_blank"
            >Report Error</a
        >
    </nav>
</template>

<script>
import { inject } from "vue";

export default {
    name: "Header-component",
    setup() {
        const philoConfig = inject("$philoConfig");
        return {
            philoConfig,
        };
    },
};
</script>

<style>
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
</style>