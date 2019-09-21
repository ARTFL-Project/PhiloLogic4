<template>
    <div class="container-fluid mt-4" v-if="authorized">
        <b-row>
            <b-col cols="8" offset="2">
                <div id="object-title" class="text-center pt-4">
                    <h5>
                        <citations :citation="textNavigationCitation"></citations>
                    </h5>
                </div>
            </b-col>
        </b-row>
        <b-row
            id="toc-wrapper"
            class="text-center mt-4"
            v-if="navBar === true || loading === false"
        >
            <div id="toc-top-bar" class="shadow"></div>
            <b-col cols="12" id="nav-buttons" v-scroll="handleScroll">
                <b-button id="back-to-top" size="sm" @click="backToTop()">
                    <span class="d-xs-none d-sm-inline-block">Back to top</span>
                    <span class="d-xs-inline-block d-sm-none">Top</span>
                </b-button>
                <b-button-group size="sm">
                    <b-button
                        disabled="disabled"
                        id="prev-obj"
                        @click="goToTextObject(textObject.prev)"
                    >&lt;</b-button>
                    <b-button
                        id="show-toc"
                        disabled="disabled"
                        @click="toggleTableOfContents()"
                    >Table of contents</b-button>
                    <b-button
                        disabled="disabled"
                        id="next-obj"
                        @click="goToTextObject(textObject.next)"
                    >&gt;</b-button>
                </b-button-group>
                <a
                    id="report-error"
                    class="btn btn-secondary btn-sm position-absolute"
                    target="_blank "
                    :href="philoConfig.report_error_link"
                    v-if="philoConfig.report_error_link !='' "
                >Report Error</a>
                <div id="toc-wrapper">
                    <div id="toc-titlebar" class="d-none">
                        <b-button
                            class="btn btn-primary btn-xs pull-right"
                            id="hide-toc"
                            @click="toggleTableOfContents()"
                        >X</b-button>
                    </div>
                    <transition name="slide-fade">
                        <b-card
                            no-body
                            id="toc-content"
                            class="p-3 shadow"
                            :style="tocHeight"
                            :scroll-to="tocPosition"
                            v-if="tocOpen"
                        >
                            <div class="toc-more before" v-if="start !== 0">
                                <b-button
                                    type="button"
                                    class="btn btn-default btn-sm glyphicon glyphicon-menu-up"
                                    @click="loadBefore()"
                                ></b-button>
                            </div>
                            <div
                                v-for="(element, tocIndex) in tocElementsToDisplay"
                                :key="tocIndex"
                            >
                                <div
                                    :id="element.philo_id"
                                    :class="'toc-' + element.philo_type"
                                    @click="textObjectSelection(element.philo_id, tocIndex)"
                                >
                                    <span :class="'bullet-point-' + element.philo_type"></span>
                                    <a
                                        :class="{'current-obj': element.philo_id === currentPhiloId }"
                                        href
                                    >{{ element.label }}</a>
                                </div>
                            </div>
                            <div class="toc-more after" v-if="end < tocElements.length">
                                <b-button
                                    type="button"
                                    class="btn btn-default btn-sm glyphicon glyphicon-menu-down"
                                    @click="loadAfter()"
                                ></b-button>
                            </div>
                        </b-card>
                    </transition>
                </div>
            </b-col>
        </b-row>
        <div
            style="font-size: 80%; text-align: center;"
            v-if="philoConfig.dictionary_lookup != ''"
        >To look up a word in a dictionary, select the word with your mouse and press 'd' on your keyboard.</div>
        <b-row id="all-content" loading="loading">
            <b-col
                cols="12"
                sm="10"
                offset-sm="1"
                lg="8"
                offset-lg="2"
                id="center-content"
                v-if="textObject.text"
                style="text-align: center"
            >
                <b-card no-body class="mt-2 mb-4 p-4 shadow d-inline-block">
                    <div id="book-page">
                        <div id="previous-pages" v-if="beforeObjImgs">
                            <span class="xml-pb-image">
                                <a
                                    :href="img[0]"
                                    :large-img="img[1]"
                                    class="page-image-link"
                                    v-for="(img, imageIndex) in beforeObjImgs"
                                    :key="imageIndex"
                                    data-gallery
                                ></a>
                            </span>
                        </div>
                        <div id="previous-graphics" v-if="beforeGraphicsImgs">
                            <a
                                :href="img[0]"
                                :large-img="img[1]"
                                class="inline-img"
                                v-for="(img, beforeIndex) in beforeGraphicsImgs"
                                :key="beforeIndex"
                                data-gallery
                            ></a>
                        </div>
                        <div
                            id="text-obj-content"
                            class="text-content-area"
                            v-html="textObject.text"
                            compile-template
                            select-word
                            :philo-id="philoID"
                            @keydown="dicoLookup($event, textObject.metadata_fields.year)"
                            tabindex="0"
                        ></div>
                        <div id="next-pages" v-if="afterObjImgs">
                            <span class="xml-pb-image">
                                <a
                                    :href="img[0]"
                                    :large-img="img[1]"
                                    class="page-image-link"
                                    v-for="(img, afterIndex) in afterObjImgs"
                                    :key="afterIndex"
                                    data-gallery
                                ></a>
                            </span>
                        </div>
                        <div id="next-graphics" v-if="afterGraphicsImgs">
                            <a
                                :href="img[0]"
                                :large-img="img[1]"
                                class="inline-img"
                                v-for="(img , afterGraphIndex) in afterGraphicsImgs"
                                :key="afterGraphIndex"
                                data-gallery
                            ></a>
                        </div>
                    </div>
                </b-card>
            </b-col>
        </b-row>
        <!-- <access-control v-if="!authorized"></access-control> -->
        <!-- <div
        id="blueimp-gallery"
        class="blueimp-gallery blueimp-gallery-controls"
        data-full-screen="true"
        data-continuous="false"
        style="display: none"
    >
        <div class="slides"></div>
        <h3 class="title"></h3>
        <a class="prev">
            <span class="glyphicon glyphicon-arrow-left"></span>
        </a>
        <a class="next">
            <span class="glyphicon glyphicon-arrow-right"></span>
        </a>
        <a
            id="full-size-image"
            class="glyphicon glyphicon-new-window"
            @click="fullSizeImage()"
        ></a>
        <a class="close">&#10005;</a>
        <ol class="indicator"></ol>
        </div>-->
    </div>
</template>
<script>
import { mapFields } from "vuex-map-fields";
import citations from "./Citations";
import searchArguments from "./SearchArguments";
import { EventBus } from "../main.js";

export default {
    name: "textNavigation",
    components: {
        citations,
        searchArguments
    },
    computed: {
        ...mapFields({
            report: "formData.report",
            start_byte: "formData.start_byte",
            end_byte: "formData.end_byte",
            textNavigationCitation: "textNavigationCitation",
            navBar: "navBar",
            tocElements: "tocElements",
            byte: "byte"
        }),
        tocElementsToDisplay: function() {
            return this.tocElements.elements.slice(this.start, this.end);
        },
        tocHeight() {
            return `max-height: ${window.innerHeight - 200}`;
        }
    },
    data() {
        return {
            philoConfig: this.$philoConfig,
            textObject: {},
            beforeObjImgs: [],
            afterObjImgs: [],
            beforeGraphicsImgs: [],
            afterGraphicsImgs: [],
            navbar: null,
            loading: false,
            tocOpen: false,
            done: false,
            authorized: true,
            textRendered: false,
            textObjectURL: "",
            philoID: "",
            highlight: false,
            start: 0,
            end: 0,
            tocPosition: 0,
            navButtonPosition: 0,
            navBarVisible: false
        };
    },
    created() {
        this.report = "textNavigation";
        this.fetchText();
        this.fetchToC();
        EventBus.$on("navChange", () => {
            this.fetchText();
            this.currentPhiloId = this.$route.params.pathInfo
                .split("/")
                .join(" ");
        });
    },
    methods: {
        fetchText() {
            this.textRendered = false;
            this.textObjectURL = this.$route.params;
            this.philoID = this.textObjectURL.pathInfo.split("/").join(" ");
            let byteString = "";
            if ("byte" in this.$route.query) {
                this.byte = this.$route.query.byte;
                if (typeof this.$route.query.byte == "object") {
                    byteString = `byte=${this.byte.join("&byte=")}`;
                } else {
                    byteString = `byte=${this.byte}`;
                }
            } else {
                this.byte = "";
            }
            let navigationParams = {
                report: "navigation",
                philo_id: this.philoID
            };
            if (this.start_byte !== "") {
                navigationParams.start_byte = this.start_byte;
                navigationParams.end_byte = this.end_byte;
            }
            let urlQuery = `${byteString}&${this.paramsToUrlString(
                navigationParams
            )}`;
            this.$http
                .get(`${this.$dbUrl}/reports/navigation.py?${urlQuery}`)
                .then(response => {
                    this.textObject = response.data;
                    // textNavigationValues.textObject = response.data;
                    this.textNavigationCitation = response.data.citation;
                    this.navBar = true;
                    if (this.byte.length > 0) {
                        this.highlight = true;
                    } else {
                        this.highlight = false;
                    }
                    this.loading = false;

                    let hash = this.$route.hash; // For note link back
                    // if (hash) {
                    //     $timeout(function() {
                    //         angular
                    //             .element("#" + hash)
                    //             .css({
                    //                 backgroundColor: "red",
                    //                 color: "white"
                    //             })
                    //             .velocity("scroll", {
                    //                 duration: 200,
                    //                 offset: -50
                    //             });
                    //     });
                    // }
                    if (this.byte != "") {
                        this.$nextTick(() => {
                            this.$scrollTo(
                                document.querySelectorAll(".highlight")[0],
                                1000,
                                { easing: "ease-out", offset: -100 }
                            );
                        }, 1000);
                    }
                    if (this.start_byte != "") {
                        this.$nextTick(() => {
                            this.$scrollTo(
                                document.querySelectorAll(
                                    ".start-highlight"
                                )[0],
                                1000,
                                { easing: "ease-out", offset: -100 }
                            );
                        }, 1000);
                    }

                    if (!this.deepEqual(response.data.imgs, {})) {
                        this.insertPageLinks(response.data.imgs);
                        this.insertInlineImgs(response.data.imgs);
                    }
                    this.setUpNavBar();
                })
                .catch(error => {
                    this.debug(this, error);
                    this.loading = false;
                });
        },
        insertPageLinks(imgObj) {
            let currentObjImgs = imgObj.current_obj_img;
            let allImgs = imgObj.all_imgs;
            this.beforeObjImgs = [];
            this.afterObjImgs = [];
            if (currentObjImgs.length > 0) {
                let beforeIndex = 0;
                for (let i = 0; i < allImgs.length; i++) {
                    let img = allImgs[i];
                    if (currentObjImgs.indexOf(img[0]) === -1) {
                        if (img.length == 2) {
                            this.beforeObjImgs.push([
                                this.philoConfig.page_images_url_root +
                                    "/" +
                                    img[0],
                                this.philoConfig.page_images_url_root +
                                    "/" +
                                    img[1]
                            ]);
                        } else {
                            this.beforeObjImgs.push([
                                this.philoConfig.page_images_url_root +
                                    "/" +
                                    img[0],
                                this.philoConfig.page_images_url_root +
                                    "/" +
                                    img[0]
                            ]);
                        }
                    } else {
                        beforeIndex = i;
                        break;
                    }
                }
                for (let i = beforeIndex; i < allImgs.length; i++) {
                    let img = allImgs[i];
                    if (currentObjImgs.indexOf(img[0]) === -1) {
                        if (img.length == 2) {
                            this.afterObjImgs.push([
                                this.philoConfig.page_images_url_root +
                                    "/" +
                                    img[0],
                                this.philoConfig.page_images_url_root +
                                    "/" +
                                    img[1]
                            ]);
                        } else {
                            this.afterObjImgs.push([
                                this.philoConfig.page_images_url_root +
                                    "/" +
                                    img[0],
                                this.philoConfig.page_images_url_root +
                                    "/" +
                                    img[0]
                            ]);
                        }
                    }
                }
            }
        },
        insertInlineImgs(imgObj) {
            var currentObjImgs = imgObj.current_graphic_img;
            var allImgs = imgObj.graphics;
            var img;
            this.beforeGraphicsImgs = [];
            this.afterGraphicsImgs = [];
            if (currentObjImgs.length > 0) {
                var beforeIndex = 0;
                for (let i = 0; i < allImgs.length; i++) {
                    img = allImgs[i];
                    if (currentObjImgs.indexOf(img[0]) === -1) {
                        if (img.length == 2) {
                            this.beforeGraphicsImgs.push([
                                `${this.philoConfig.page_images_url_root}/${
                                    img[0]
                                }`,
                                `${this.philoConfig.page_images_url_root}/${
                                    img[1]
                                }`
                            ]);
                        } else {
                            this.beforeGraphicsImgs.push([
                                `${this.philoConfig.page_images_url_root}/${
                                    img[0]
                                }`,
                                `${this.philoConfig.page_images_url_root}/${
                                    img[0]
                                }`
                            ]);
                        }
                    } else {
                        beforeIndex = i;
                        break;
                    }
                }
                for (let i = beforeIndex; i < allImgs.length; i++) {
                    img = allImgs[i];
                    if (currentObjImgs.indexOf(img[0]) === -1) {
                        if (img.length == 2) {
                            this.afterGraphicsImgs.push([
                                `${this.philoConfig.page_images_url_root}/${
                                    img[0]
                                }`,
                                `${this.philoConfig.page_images_url_root}/${
                                    img[1]
                                }`
                            ]);
                        } else {
                            this.afterGraphicsImgs.push([
                                `${this.philoConfig.page_images_url_root}/${
                                    img[0]
                                }`,
                                `${this.philoConfig.page_images_url_root}/${
                                    img[0]
                                }`
                            ]);
                        }
                    }
                }
            }
        },
        fetchToC() {
            this.tocPosition = "";
            var philoId = this.$route.params.pathInfo.split("/").join(" ");
            let docId = philoId.split(" ")[0];
            this.currentPhiloId = philoId;
            if (docId !== this.tocElements.docId) {
                this.$http
                    .get(`${this.$dbUrl}/scripts/get_table_of_contents.py`, {
                        params: {
                            philo_id: this.currentPhiloId
                        }
                    })
                    .then(response => {
                        let tocElements = response.data.toc;
                        this.start = response.data.current_obj_position - 100;
                        if (this.start < 0) {
                            this.start = 0;
                        }
                        this.end = response.data.current_obj_position + 100;

                        this.tocElements = {
                            docId: philoId.split(" ")[0],
                            elements: tocElements,
                            start: this.start,
                            end: this.end
                        };
                        this.$nextTick(function() {
                            let tocButton = document.querySelector("#show-toc");
                            tocButton.removeAttribute("disabled");
                            tocButton.classList.remove("disabled");
                            this.navButtonPosition = tocButton.getBoundingClientRect().top;
                        });
                    })
                    .catch(error => {
                        this.debug(this, error);
                    });
            } else {
                this.start = this.tocElements.start;
                this.end = this.tocElements.end;
                this.$nextTick(function() {
                    let tocButton = document.querySelector("#show-toc");
                    tocButton.removeAttribute("disabled");
                    tocButton.classList.remove("disabled");
                });
            }
        },
        loadBefore() {
            var firstElement = this.tocElements[this.start - 2].philo_id;
            this.start -= 200;
            if (this.start < 0) {
                this.start = 0;
            }
            this.tocPosition = firstElement;
        },
        loadAfter() {
            this.end += 200;
        },
        toggleTableOfContents() {
            if (this.tocOpen) {
                this.closeTableOfContents();
            } else {
                this.openTableOfContents();
            }
        },
        openTableOfContents() {
            this.tocOpen = true;
            this.$nextTick(() => {
                this.$scrollTo(document.querySelector(".current-obj"), 500, {
                    container: document.querySelector("#toc-content")
                });
            });
        },
        closeTableOfContents() {
            this.tocOpen = false;
        },
        backToTop() {
            window.scrollTo({ top: 0, behavior: "smooth" });
        },
        goToTextObject(philoID) {
            philoID = philoID.split(/[- ]/).join("/");
            if (this.tocOpen) {
                this.closeTableOfContents();
            }
            this.$router.push({ path: `/navigate/${philoID}` });
            EventBus.$emit("navChange");
        },
        textObjectSelection(philoId, index) {
            event.preventDefault();
            let newStart = this.tocElements.start + index - 100;
            if (newStart < 0) {
                newStart = 0;
            }
            this.tocElements = {
                ...this.tocElements,
                start: newStart,
                end: this.tocElements.end - index + 100
            };
            this.goToTextObject(philoId);
        },
        setUpNavBar() {
            let prevButton = document.querySelector("#prev-obj");
            let nextButton = document.querySelector("#next-obj");
            if (
                this.textObject.next === "" ||
                typeof this.textObject.next === "undefined"
            ) {
                nextButton.classList.add("disabled");
            } else {
                nextButton.removeAttribute("disabled");
                nextButton.classList.remove("disabled");
            }
            if (
                this.textObject.prev === "" ||
                typeof this.textObject.prev === "undefined"
            ) {
                prevButton.classList.add("disabled");
            } else {
                prevButton.removeAttribute("disabled");
                prevButton.classList.remove("disabled");
            }
        },
        handleScroll() {
            if (!this.navBarVisible) {
                if (window.scrollY > this.navButtonPosition) {
                    this.navBarVisible = true;
                    let topBar = document.querySelector("#toc-top-bar");
                    topBar.style.top = 0;
                    topBar.classList.add("visible");
                    let navButtons = document.querySelector("#nav-buttons");
                    navButtons.style.top = 0;
                    navButtons.classList.add("fixed");
                    let backToTop = document.querySelector("#back-to-top");
                    backToTop.classList.add("visible");
                    let reportError = document.querySelector("#report-error");
                    reportError.classList.add("visible");
                }
            } else if (window.scrollY < this.navButtonPosition) {
                this.navBarVisible = false;
                let topBar = document.querySelector("#toc-top-bar");
                topBar.style.top = "initial";
                topBar.classList.remove("visible");
                let navButtons = document.querySelector("#nav-buttons");
                navButtons.style.top = "initial";
                navButtons.classList.remove("fixed");
                let backToTop = document.querySelector("#back-to-top");
                backToTop.classList.remove("visible");
                let reportError = document.querySelector("#report-error");
                reportError.classList.remove("visible");
            }
        },
        dicoLookup(event, year) {
            if (event.key === "d") {
                let selection = window.getSelection().toString();
                let century = parseInt(year.slice(0, year.length - 2));
                let range = `${century.toString()}00-${String(century + 1)}00`;
                if (range == "NaN00-NaN00") {
                    range = "";
                }
                let link = `${this.philoConfig.dictionary_lookup}?docyear=${range}&strippedhw=${selection}`;
                window.open(link);
            }
        }
    }
};
</script>
<style scoped>
.separator {
    padding: 5px;
    font-size: 60%;
    display: inline-block;
    vertical-align: middle;
}
#toc-content {
    display: inline-block;
    position: relative;
    overflow: scroll;
    text-align: justify;
    line-height: 180%;
    z-index: 50;
    background: #fff;
}
#toc-wrapper {
    position: relative;
    z-index: 49;
}
#toc-top-bar {
    height: 31px;
    background: #d8d8d8;
    opacity: 0;
    transition: opacity 0.25s;
    width: 100%;
    pointer-events: none;
}
#toc-top-bar::before {
    filter: blur(20px);
}
#toc-top-bar.visible {
    opacity: 0.95;
    position: fixed;
}
#nav-buttons.fixed {
    position: fixed;
    opacity: 0.95;
}
#back-to-top {
    position: absolute;
    left: 0;
    opacity: 0;
    transition: opacity 0.25s;
    pointer-events: none;
}
#report-error {
    right: 0;
    opacity: 0;
    transition: opacity 0.25s;
    pointer-events: none;
}
#back-to-top.visible,
#report-error.visible {
    pointer-events: initial;
    opacity: 0.95;
}

#nav-buttons {
    position: absolute;
}

a.current-obj,
#toc-container a:hover {
    background: #e8e8e8;
}

#book-page {
    text-align: justify;
}

/deep/ .xml-pb {
    display: block;
    text-align: center;
    margin: 10px;
}

/deep/ .xml-pb::before {
    content: "-" attr(n) "-";
    white-space: pre;
}

/deep/ p {
    margin-bottom: 0.5rem;
}
/deep/ .highlight {
    background-color: red;
    color: #fff;
}
/* Styling for theater */

/deep/ .xml-castitem::after {
    content: "\A";
    white-space: pre;
}

/deep/ .xml-castlist > .xml-castitem:first-of-type::before {
    content: "\A";
    white-space: pre;
}

/deep/ .xml-castgroup::before {
    content: "\A";
    white-space: pre;
}

b.headword {
    font-weight: 700 !important;
    font-size: 130%;
    display: block;
    margin-top: 20px;
}

/deep/ #bibliographic-results b.headword {
    font-weight: 400 !important;
    font-size: 100%;
    display: inline;
}

/deep/ .xml-lb,
/deep/ .xml-l {
    text-align: justify;
    display: block;
}

/deep/ .xml-sp .xml-lb:first-of-type {
    content: "";
    white-space: normal;
}

/deep/ .xml-lb[type="hyphenInWord"] {
    display: inline;
}

#book-page .xml-sp {
    display: block;
}

/deep/ .xml-sp::before {
    content: "\A";
    white-space: pre;
}

/deep/ .xml-stage + .xml-sp:nth-of-type(n + 2)::before {
    content: "";
}

/deep/ .xml-fw,
/deep/ .xml-join {
    display: none;
}

/deep/ .xml-speaker + .xml-stage::before {
    content: "";
    white-space: normal;
}

/deep/ .xml-stage {
    font-style: italic;
}

/deep/ .xml-stage::after {
    content: "\A";
    white-space: pre;
}

/deep/ div1 div2::before {
    content: "\A";
    white-space: pre;
}

/deep/ .xml-speaker {
    font-weight: 700;
}

/deep/ .xml-pb {
    display: block;
    text-align: center;
    margin: 10px;
}

/deep/ .xml-pb::before {
    content: "-" attr(n) "-";
    white-space: pre;
}

/deep/ .xml-lg {
    display: block;
}

/deep/ .xml-lg::after {
    content: "\A";
    white-space: pre;
}

/deep/ .xml-lg:first-of-type::before {
    content: "\A";
    white-space: pre;
}

/deep/ .xml-castList,
/deep/ .xml-front,
/deep/ .xml-castItem,
/deep/ .xml-docTitle,
/deep/ .xml-docImprint,
/deep/ .xml-performance,
/deep/ .xml-docAuthor,
/deep/ .xml-docDate,
/deep/ .xml-premiere,
/deep/ .xml-casting,
/deep/ .xml-recette,
/deep/ .xml-nombre {
    display: block;
}

/deep/ .xml-docTitle {
    font-style: italic;
    font-weight: bold;
}

/deep/ .xml-docTitle,
/deep/ .xml-docAuthor,
/deep/ .xml-docDate {
    text-align: center;
}

/deep/ .xml-docTitle span[type="main"] {
    font-size: 150%;
    display: block;
}

/deep/ .xml-docTitle span[type="sub"] {
    font-size: 120%;
    display: block;
}

/deep/ .xml-performance,
/deep/ .xml-docImprint {
    margin-top: 10px;
}

/deep/ .xml-set {
    display: block;
    font-style: italic;
    margin-top: 10px;
}

/*Dictionary formatting*/

body {
    counter-reset: section;
    /* Set the section counter to 0 */
}

/deep/ .xml-prononciation::before {
    content: "(";
}

/deep/ .xml-prononciation::after {
    content: ")\A";
}

/deep/ .xml-nature {
    font-style: italic;
}

/deep/ .xml-indent,
/deep/ .xml-variante {
    display: block;
}

/deep/ .xml-variante {
    padding-top: 10px;
    padding-bottom: 10px;
    text-indent: -1.3em;
    padding-left: 1.3em;
}

/deep/ .xml-variante::before {
    counter-increment: section;
    content: counter(section) ")\00a0";
    font-weight: 700;
}

/deep/ :not(.xml-rubrique) + .xml-indent {
    padding-top: 10px;
}

/deep/ .xml-indent {
    padding-left: 1.3em;
}

/deep/ .xml-cit {
    padding-left: 2.3em;
    display: block;
    text-indent: -1.3em;
}

/deep/ .xml-indent > .xml-cit {
    padding-left: 1em;
}

/deep/ .xml-cit::before {
    content: "\2012\00a0\00ab\00a0";
}

/deep/ .xml-cit::after {
    content: "\00a0\00bb\00a0("attr(aut) "\00a0"attr(ref) ")";
    font-variant: small-caps;
}

/deep/ .xml-rubrique {
    display: block;
    margin-top: 20px;
}

/deep/ .xml-rubrique::before {
    content: attr(nom);
    font-variant: small-caps;
    font-weight: 700;
}

/deep/ .xml-corps + .xml-rubrique {
    margin-top: 10px;
}

/*Methodique styling*/

/deep/ div[type="article"] .headword {
    display: inline-block;
    margin-bottom: 10px;
}

/deep/ .headword + p {
    display: inline;
}

/deep/ .headword + p + p {
    margin-top: 10px;
}

/*Note handling*/

/deep/ .popover {
    max-width: 350px;
    overflow: scroll;
}

/deep/ .popover-content {
    text-align: justify;
}

/deep/ .popover-content .xml-p:not(:first-of-type) {
    display: block;
    margin-top: 1em;
    margin-bottom: 1em;
}

/deep/ .note-content {
    display: none;
}

/deep/ .note,
/deep/ .note-ref {
    vertical-align: 0.3em;
    font-size: 0.7em;
}

/deep/ .note:hover,
/deep/ .note-ref:hover {
    cursor: pointer;
    text-decoration: none;
}

/deep/ div[type="notes"] .xml-note {
    margin: 15px 0px;
    display: block;
}

/deep/ .xml-note::before {
    content: "note\00a0"attr(n) "\00a0:\00a0";
    font-weight: 700;
}

/*Page images*/

/deep/ .xml-pb-image {
    display: block;
    text-align: center;
    margin: 10px;
}

/deep/ .page-image-link {
    margin-top: 10px;
    /*display: block;*/
    text-align: center;
}

/*Inline images*/
/deep/ .inline-img {
    max-width: 40%;
    float: right;
    height: auto;
    padding-left: 15px;
    padding-top: 15px;
}

/deep/ .inline-img:hover {
    cursor: pointer;
}

/deep/ .link-back {
    margin-left: 10px;
    line-height: initial;
}

/deep/ .xml-add {
    color: #ef4500;
}

/deep/ .xml-seg {
    display: block;
}

/*Table display*/

/deep/ b.headword[rend="center"] {
    margin-bottom: 30px;
    text-align: center;
}

/deep/ .xml-table {
    display: table;
    position: relative;
    text-align: center;
    border-collapse: collapse;
}

/deep/ .xml-table .xml-pb-image {
    position: absolute;
    width: 100%;
    margin-top: 15px;
}

/deep/ .xml-row {
    display: table-row;
    font-weight: 700;
    text-align: left;
    min-height: 50px;
    font-variant: small-caps;
    padding-top: 10px;
    padding-bottom: 10px;
    padding-right: 20px;
    border-bottom: #ddd 1px solid;
}

/deep/ .xml-row ~ .xml-row {
    font-weight: inherit;
    text-align: justify;
    font-variant: inherit;
}

/deep/ .xml-pb-image + .xml-row {
    padding-top: 50px;
    padding-bottom: 10px;
    border-top-width: 0px;
}

/deep/ .xml-cell {
    display: table-cell;
    padding-top: inherit; /*inherit padding when image is above */
    padding-bottom: inherit;
}
.slide-fade-enter-active {
    transition: all 0.3s ease-out;
}
.slide-fade-leave-active {
    transition: all 0.3s ease-out;
}
.slide-fade-enter, .slide-fade-leave-to
/* .slide-fade-leave-active below version 2.1.8 */ {
    transform: translateY(-30px);
    opacity: 0;
}
</style>


