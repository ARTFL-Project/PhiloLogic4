<template>
    <div id="page-links" class="mt-4 pb-4 text-center" v-if="pages.length > 0">
        <div class="row">
            <div class="col-12 col-sm-10 offset-sm-1 col-md-8 offset-md-2">
                <div class="btn-group shadow" role="group">
                    <button
                        type="button"
                        class="btn btn-outline-secondary"
                        v-for="page in pages"
                        :key="page.display"
                        :class="page.active"
                        @click="goToPage(page.start, page.end)"
                    >
                        <span class="page-number">{{ page.display }}</span>
                        <span class="page-range">{{ page.range }}</span>
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import { mapFields } from "vuex-map-fields";

export default {
    name: "pages",
    computed: {
        ...mapFields(["formData.results_per_page", "resultsLength", "totalResultsDone", "urlUpdate"]),
    },
    data() {
        return { pages: [] };
    },
    watch: {
        totalResultsDone(done) {
            if (done) {
                this.buildPages();
            }
        },
        urlUpdate() {
            this.buildPages();
        },
    },
    methods: {
        buildPages() {
            let start = parseInt(this.$route.query.start);
            let resultsPerPage = parseInt(this.results_per_page) || 25;
            let resultsLength = this.resultsLength;

            // first find out what page we are on currently.
            let currentPage = Math.floor(start / resultsPerPage) + 1 || 1;

            // then how many total pages the query has
            let totalPages = Math.floor(resultsLength / resultsPerPage);
            let remainder = resultsLength % resultsPerPage;
            if (remainder !== 0) {
                totalPages += 1;
            }
            totalPages = totalPages || 1;

            // construct the list of page numbers we will output.
            let pages = [];
            // up to four previous pages
            let prev = currentPage - 4;
            while (prev < currentPage) {
                if (prev > 0) {
                    pages.push(prev);
                }
                prev += 1;
            }
            // the current page
            pages.push(currentPage);
            // up to five following pages
            let next = currentPage + 5;
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
            pages.sort(function (a, b) {
                return a - b;
            });

            // now we construct the actual links from the page numbers
            let pageObject = [];
            let lastPageName = "";
            let pageEnd, pageStart, active;
            for (let page of pages) {
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
                if (page === 1 && pages.length > 1) {
                    page = "First";
                }
                if (page === totalPages) {
                    page = "Last";
                }
                if (page == lastPageName) {
                    continue;
                }
                lastPageName = page;
                pageObject.push({
                    display: page,
                    active: active,
                    start: pageStart.toString(),
                    end: pageEnd.toString(),
                    range: `${pageStart}-${pageEnd}`,
                });
            }
            this.pages = pageObject;
        },
        goToPage(start, end) {
            let route = this.paramsToRoute({
                ...this.$store.state.formData,
                start: start,
                end: end,
            });
            return this.$router.push(route);
        },
    },
};
</script>
<style scoped>
.page {
    transition: width 0.4s ease !important;
}
.btn {
    line-height: initial !important;
}
.page-number {
    display: block;
    font-size: 110%;
}
.page-range {
    font-size: 80%;
    opacity: 0.7;
}
</style>
