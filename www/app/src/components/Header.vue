<template>
    <nav class="navbar navbar-expand-lg navbar-light bg-light shadow" style="height: 53px">
        <div class="collapse navbar-collapse" id="nav-collapse">
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
        <ul id="error-report" class="ml-auto" v-if="philoConfig.report_error_link">
            <li class="nav-item">
                <a class="nav-link" :href="philoConfig.report_error_link" target="_blank">Error Report</a>
            </li>
        </ul>
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
#nav-collapse {
    margin-left: -0.25rem;
    font-size: 80%;
    margin-top: -2rem;
    font-variant: small-caps;
}
#error-report {
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