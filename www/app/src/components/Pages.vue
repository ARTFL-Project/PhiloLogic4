<template>
    <div id="page-links" class="mt-4 pb-4 text-center" v-if="pages.length > 0">
        <b-row>
            <b-col cols="12" sm="10" offset-sm="1" md="8" offset-md="2">
                <b-button-group class="shadow">
                    <b-button
                        v-for="page in pages"
                        :key="page.display"
                        :class="page.active"
                        variant="outline-secondary"
                        :to="page.route"
                    >
                        <span class="page-number">{{ page.display }}</span>
                        <span class="page-range">{{ page.range }}</span>
                    </b-button>
                </b-button-group>
            </b-col>
        </b-row>
    </div>
</template>
<script>
import { EventBus } from "../main.js";
import { mapFields } from "vuex-map-fields";

export default {
    name: "pages",
    computed: {
        ...mapFields([
            "formData.start",
            "formData.results_per_page",
            "resultsLength"
        ])
    },
    data() {
        return { pages: [] };
    },
    created() {
        EventBus.$on("totalResultsDone", () => {
            this.buildPages();
        });
        EventBus.$on("urlUpdate", () => {
            this.pages = [];
            this.buildPages();
        });
    },
    methods: {
        buildPages() {
            var start = this.start;
            var resultsPerPage = parseInt(this.results_per_page) || 25;
            var resultsLength = this.resultsLength;

            // first find out what page we are on currently.
            var currentPage = Math.floor(start / resultsPerPage) + 1 || 1;

            // then how many total pages the query has
            var totalPages = Math.floor(resultsLength / resultsPerPage);
            var remainder = resultsLength % resultsPerPage;
            if (remainder !== 0) {
                totalPages += 1;
            }
            totalPages = totalPages || 1;

            // construct the list of page numbers we will output.
            var pages = [];
            // up to four previous pages
            var prev = currentPage - 4;
            while (prev < currentPage) {
                if (prev > 0) {
                    pages.push(prev);
                }
                prev += 1;
            }
            // the current page
            pages.push(currentPage);
            // up to five following pages
            var next = currentPage + 5;
            while (next > currentPage) {
                if (next < totalPages) {
                    pages.push(next);
                }
                next -= 1;
            }
            // first and last if not already there
            if (pages[0] !== 1) {
                pages.unshift(1);
            }
            if (pages[-1] !== totalPages) {
                pages.push(totalPages);
            }
            pages.sort(function(a, b) {
                return a - b;
            });

            // now we construct the actual links from the page numbers
            var pageObject = [];
            let lastPageName = "";
            var pageEnd, pageStart, active;
            for (var i = 0; i < pages.length; i++) {
                var page = pages[i];
                pageStart = page * resultsPerPage - resultsPerPage + 1;
                pageEnd = page * resultsPerPage;
                if (page === currentPage) {
                    active = "active";
                } else {
                    active = "";
                }
                pageStart = resultsPerPage * (page - 1) + 1;
                pageEnd = pageStart + resultsPerPage - 1;
                if (pageEnd > resultsLength) {
                    pageEnd = resultsLength;
                }
                if (page === 1 && !2 in pages) {
                    page = "First";
                }
                if (page === totalPages) {
                    page = "Last";
                }
                if (page == lastPageName) {
                    continue;
                }
                lastPageName = page;
                let route = this.paramsToRoute({
                    ...this.$store.state.formData,
                    start: pageStart.toString(),
                    end: pageEnd.toString()
                });
                pageObject.push({
                    display: page,
                    route: route,
                    active: active,
                    range: `${pageStart}-${pageEnd}`
                });
            }
            this.pages = pageObject;
        }
    }
};
</script>
<style scoped>
.page {
    transition: width 0.4s ease !important;
    /* overflow: hidden; */
}
.btn {
    line-height: initial !important;
}
.page-number {
    display: block;
}
.page-range {
    font-size: 70%;
    opacity: 0.7;
}
</style>

