<template>
    <div>
        <b-navbar toggleable="lg" type="light" variant="light" class="shadow">
            <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>
            <b-collapse id="nav-collapse" is-nav>
                <b-navbar-nav>
                    <b-nav-item href="https://textual-optics-lab.uchicago.edu">Textual Optics Lab</b-nav-item>
                    <b-nav-item href="https://artfl-project.uchicago.edu">ARTFL Project</b-nav-item>
                </b-navbar-nav>
            </b-collapse>
            <b-navbar-brand
                style="font-weight: 700; font-size: 1.6rem; font-variant: small-caps; position: absolute; left: 50%; transform: translateX(-50%); line-height: 80%"
                to="/"
                v-html="philoConfig.dbname"
            ></b-navbar-brand>
            <b-navbar-nav class="ml-auto">
                <b-nav-item
                    :href="philoConfig.report_error_link"
                    target="_blank"
                    style="font-variant: small-caps;"
                >Error Report</b-nav-item>
            </b-navbar-nav>
        </b-navbar>
    </div>
</template>

<script>
export default {
    name: "Header",
    data() {
        return {
            philoConfig: this.$philoConfig
        };
    },
    created() {}
};
</script>

<style>
#nav-collapse {
    margin-left: -1rem;
    font-size: 75%;
    margin-top: -2rem;
    font-variant: small-caps;
}
</style>