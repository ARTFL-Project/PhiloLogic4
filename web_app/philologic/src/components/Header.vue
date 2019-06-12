<template>
    <div>
        <b-navbar toggleable="lg" type="light" variant="light" class="shadow">
            <b-navbar-brand to="/">{{ philoConfig.dbname }}</b-navbar-brand>

            <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

            <b-collapse id="nav-collapse" is-nav>
                <b-navbar-nav>
                    <b-nav-item href="https://textual-optics-lab.uchicago.edu">Textual Optics Lab</b-nav-item>
                    <b-nav-item href="https://artfl-project.uchicago.edu">ARTFL Project</b-nav-item>
                </b-navbar-nav>
            </b-collapse>
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
</style>