<template>
    <div class="container-fluid mt-4" v-if="authorized">
        <b-row>
            <b-col cols="8" offset="2">
                <div id="object-title" class="text-center pt-4">
                    <span
                        class="citation"
                        v-for="(citation, citeIndex) in textNavigationCitation"
                        :key="citeIndex"
                    >
                        <span v-if="citation.href">
                            <span v-html="citation.prefix"></span>
                            <a :href="citation.href" :style="citation.style">{{ citation.label }}</a>
                            <span v-html="citation.suffix"></span>
                            <span
                                class="separator"
                                v-if="citeIndex != textNavigationCitation.length - 1"
                            >&#9679;</span>
                        </span>
                        <span v-if="!citation.href">
                            <span v-html="citation.prefix"></span>
                            <span :style="citation.style">{{ citation.label }}</span>
                            <span v-html="citation.suffix"></span>
                            <span
                                class="separator"
                                v-if="citeIndex != textNavigationCitation.length - 1"
                            >&#9679;</span>
                        </span>
                    </span>
                </div>
            </b-col>
        </b-row>
        <b-row
            id="toc-top-bar"
            class="text-center mt-4 mb-4"
            v-if="navBar === true || loading === false"
        >
            <b-col cols="12" id="nav-buttons" ui-scrollfix>
                <b-button id="back-to-top" class="d-none" size="sm" @click="backToTop()">
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
                <div id="toc-wrapper">
                    <div id="toc-titlebar" class="d-none">
                        <b-button
                            class="btn btn-primary btn-xs pull-right"
                            id="hide-toc"
                            @click="toggleTableOfContents()"
                        >X</b-button>
                    </div>
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
                        <div v-for="(element, tocIndex) in tocElementsToDisplay" :key="tocIndex">
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
                        <a
                            id="report-error"
                            class="btn btn-primary btn-sm"
                            target="_blank "
                            :href="philoConfig.report_error_link"
                            v-if="philoConfig.report_error_link !='' "
                        >Report Error</a>
                    </b-card>
                </div>
            </b-col>
        </b-row>
        <b-row id="all-content" loading="loading">
            <b-col
                cols="12"
                sm="10"
                offset-sm="1"
                lg="8"
                offset-lg="2"
                id="center-content"
                v-if="textObject.text"
            >
                <b-card no-body class="mt-3 mb-4 p-4 shadow">
                    <div
                        style="font-size: 80%; text-align: center;"
                        v-if="philoConfig.dictionary_lookup != ''"
                    >To look up a word in a dictionary, select the word with your mouse and press 'd' on your keyboard.</div>
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
import searchArguments from "./SearchArguments";
import { EventBus } from "../main.js";

export default {
    name: "textNavigation",
    components: {
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
            tocPosition: 0
        };
    },
    created() {
        this.report = "textNavigation";
        this.fetchText();
        this.fetchToC();
        var vm = this;
        EventBus.$on("navChange", function() {
            vm.fetchText();
            vm.currentPhiloId = vm.$route.params.pathInfo.split("/").join(" ");
        });
    },
    methods: {
        fetchText() {
            this.textRendered = false;
            this.textObjectURL = this.$route.params;
            this.philoID = this.textObjectURL.pathInfo.split("/").join(" ");
            if ("byte" in this.$route.query) {
                this.byte = this.$route.query.byte;
            } else {
                this.byte = "";
            }
            let navigationParams = {
                report: "navigation",
                philo_id: this.philoID,
                byte: this.byte
            };
            if (this.start_byte !== "") {
                navigationParams.start_byte = this.start_byte;
                navigationParams.end_byte = this.end_byte;
            }
            var vm = this;
            vm.$http
                .get(
                    "http://anomander.uchicago.edu/philologic/test/reports/navigation.py",
                    { params: navigationParams }
                )
                .then(function(response) {
                    vm.textObject = response.data;
                    // textNavigationValues.textObject = response.data;
                    vm.textNavigationCitation = response.data.citation;
                    vm.navBar = true;
                    if (vm.byte.length > 0) {
                        vm.highlight = true;
                    } else {
                        vm.highlight = false;
                    }
                    vm.loading = false;

                    let hash = vm.$route.hash; // For note link back
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
                    if (vm.byte != "") {
                        vm.$nextTick(function() {
                            vm.scrollToHighlight(".highlight");
                        });
                    }
                    if (vm.start_byte != "") {
                        vm.$nextTick(function() {
                            vm.scrollToHighlight(".start-highlight");
                        });
                    }

                    if (!vm.deepEqual(response.data.imgs, {})) {
                        vm.insertPageLinks(vm, response.data.imgs);
                        vm.insertInlineImgs(vm, response.data.imgs);
                    }
                    vm.setUpNavBar();
                })
                .catch(function(response) {
                    console.log(response);
                    vm.loading = false;
                });
        },
        scrollToHighlight(elementClass) {
            let offsetTop =
                document.querySelector(elementClass).getBoundingClientRect()
                    .top - 50;
            window.scrollBy({
                top: offsetTop,
                behavior: "smooth"
            });
        },
        insertPageLinks(vm, imgObj) {
            let currentObjImgs = imgObj.current_obj_img;
            let allImgs = imgObj.all_imgs;
            vm.beforeObjImgs = [];
            vm.afterObjImgs = [];
            if (currentObjImgs.length > 0) {
                let beforeIndex = 0;
                for (let i = 0; i < allImgs.length; i++) {
                    let img = allImgs[i];
                    if (currentObjImgs.indexOf(img[0]) === -1) {
                        if (img.length == 2) {
                            vm.beforeObjImgs.push([
                                vm.philoConfig.page_images_url_root +
                                    "/" +
                                    img[0],
                                vm.philoConfig.page_images_url_root +
                                    "/" +
                                    img[1]
                            ]);
                        } else {
                            vm.beforeObjImgs.push([
                                vm.philoConfig.page_images_url_root +
                                    "/" +
                                    img[0],
                                vm.philoConfig.page_images_url_root +
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
                            vm.afterObjImgs.push([
                                vm.philoConfig.page_images_url_root +
                                    "/" +
                                    img[0],
                                vm.philoConfig.page_images_url_root +
                                    "/" +
                                    img[1]
                            ]);
                        } else {
                            vm.afterObjImgs.push([
                                vm.philoConfig.page_images_url_root +
                                    "/" +
                                    img[0],
                                vm.philoConfig.page_images_url_root +
                                    "/" +
                                    img[0]
                            ]);
                        }
                    }
                }
            }
        },
        insertInlineImgs(vm, imgObj) {
            var currentObjImgs = imgObj.current_graphic_img;
            var allImgs = imgObj.graphics;
            vm.beforeGraphicsImgs = [];
            vm.afterGraphicsImgs = [];
            if (currentObjImgs.length > 0) {
                var beforeIndex = 0;
                for (var i = 0; i < allImgs.length; i++) {
                    var img = allImgs[i];
                    if (currentObjImgs.indexOf(img[0]) === -1) {
                        if (img.length == 2) {
                            vm.beforeGraphicsImgs.push([
                                vm.philoConfig.page_images_url_root +
                                    "/" +
                                    img[0],
                                vm.philoConfig.page_images_url_root +
                                    "/" +
                                    img[1]
                            ]);
                        } else {
                            vm.beforeGraphicsImgs.push([
                                vm.philoConfig.page_images_url_root +
                                    "/" +
                                    img[0],
                                vm.philoConfig.page_images_url_root +
                                    "/" +
                                    img[0]
                            ]);
                        }
                    } else {
                        beforeIndex = i;
                        break;
                    }
                }
                for (var i = beforeIndex; i < allImgs.length; i++) {
                    var img = allImgs[i];
                    if (currentObjImgs.indexOf(img[0]) === -1) {
                        if (img.length == 2) {
                            vm.afterGraphicsImgs.push([
                                vm.philoConfig.page_images_url_root +
                                    "/" +
                                    img[0],
                                vm.philoConfig.page_images_url_root +
                                    "/" +
                                    img[1]
                            ]);
                        } else {
                            vm.afterGraphicsImgs.push([
                                vm.philoConfig.page_images_url_root +
                                    "/" +
                                    img[0],
                                vm.philoConfig.page_images_url_root +
                                    "/" +
                                    img[0]
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
            var vm = this;
            if (docId !== this.tocElements.docId) {
                this.$http
                    .get(
                        "http://anomander.uchicago.edu/philologic/test/scripts/get_table_of_contents.py",
                        {
                            params: {
                                philo_id: this.currentPhiloId
                            }
                        }
                    )
                    .then(function(response) {
                        let tocElements = response.data.toc;
                        vm.start = response.data.current_obj_position - 100;
                        if (vm.start < 0) {
                            vm.start = 0;
                        }
                        vm.end = response.data.current_obj_position + 100;

                        vm.tocElements = {
                            docId: philoId.split(" ")[0],
                            elements: tocElements,
                            start: vm.start,
                            end: vm.end
                        };
                        let tocButton = document.querySelector("#show-toc");
                        tocButton.removeAttribute("disabled");
                        tocButton.classList.remove("disabled");
                    });
            } else {
                // this.tocElements = this.tocElements;
                this.start = this.tocElements.start;
                this.end = this.tocElements.end;
                let tocButton = document.querySelector("#show-toc");
                tocButton.removeAttribute("disabled");
                tocButton.classList.remove("disabled");
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
        textObjectSelection(philoId, index) {
            this.start = this.start + index - 100;
            if (this.start < 0) {
                this.start = 0;
            }
            this.end = this.end - index + 100;
            this.goToTextObject(philoId);
        },
        toggleTableOfContents() {
            if (this.tocOpen) {
                this.closeTableOfContents();
            } else {
                this.openTableOfContents();
            }
        },
        openTableOfContents() {
            // angular.element('#toc-wrapper').addClass('display');
            this.tocOpen = true;
            this.$nextTick(function() {
                document.querySelector(
                    "#toc-content"
                ).style.maxHeight = `${window.innerHeight - 450}px`;
            });
            // $timeout(function() {
            //     angular.element('.current-obj').velocity("scroll", {
            //         duration: 500,
            //         container: angular.element("#toc-content"),
            //         offset: -50
            //     });
            // }, 300);
        },
        closeTableOfContents() {
            // angular.element('#toc-wrapper').removeClass('display');
            this.tocOpen = false;
            // angular.element("#toc-content").scrollTop(0);
            // $timeout(function() {
            //     if (angular.element(document).height() == angular.element(window).height()) {
            //         angular.element('#toc-container').css('position', 'static');
            //     }
            // });
        },
        backToTop() {
            // angular.element("body").velocity('scroll', {
            //     duration: 800,
            //     easing: 'easeOutCirc',
            //     offset: 0
            // });
        },
        goToTextObject(philoID) {
            philoID = philoID.split(/[- ]/).join("/");
            if (this.tocOpen) {
                this.closeTableOfContents();
            }
            // $location.url(URL.path(philoID)).replace(); // deleting current page history and replace with new page
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
        dicoLookup(event, year) {
            var philoId = this.$route.params.pathInfo.split("/").join(" ");
            dictionaryLookup.evaluate(event, year);
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
    z-index: 101;
    background: #fff;
}
#toc-top-bar {
    opacity: 0.95;
    position: relative;
    z-index: 100;
}

#nav-buttons {
    position: absolute;
}

a.current-obj,
#toc-container a:hover {
    background: #e8e8e8;
    /* color: #fff !important; */
}

p {
    margin-bottom: 0.5rem;
}
/deep/ .highlight {
    background-color: red;
    color: #fff;
}
/* Styling for theater */

.xml-castitem::after {
    content: "\A";
    white-space: pre;
}

.xml-castlist > .xml-castitem:first-of-type::before {
    content: "\A";
    white-space: pre;
}

.xml-castgroup::before {
    content: "\A";
    white-space: pre;
}

b.headword {
    font-weight: 700 !important;
    font-size: 130%;
    display: block;
    margin-top: 20px;
}

#bibliographic-results b.headword {
    font-weight: 400 !important;
    font-size: 100%;
    display: inline;
}

.xml-lb {
    display: block;
}

.xml-sp .xml-lb:first-of-type {
    content: "";
    white-space: normal;
}

.xml-lb[type="hyphenInWord"] {
    display: inline;
}

#book-page .xml-sp {
    display: block;
}

.xml-sp::before {
    content: "\A";
    white-space: pre;
}

.xml-stage + .xml-sp:nth-of-type(n + 2)::before {
    content: "";
}

.xml-fw,
.xml-join {
    display: none;
}

.xml-speaker + .xml-stage::before {
    content: "";
    white-space: normal;
}

.xml-stage {
    font-style: italic;
}

.xml-stage::after {
    content: "\A";
    white-space: pre;
}

div1 div2::before {
    content: "\A";
    white-space: pre;
}

.xml-speaker {
    font-weight: 700;
}

.xml-pb {
    display: block;
    text-align: center;
    margin: 10px;
}

.xml-pb::before {
    content: "-" attr(n) "-";
    white-space: pre;
}

.xml-lg {
    display: block;
}

.xml-lg::after {
    content: "\A";
    white-space: pre;
}

.xml-lg:first-of-type::before {
    content: "\A";
    white-space: pre;
}

.xml-castList,
.xml-front,
.xml-castItem,
.xml-docTitle,
.xml-docImprint,
.xml-performance,
.xml-docAuthor,
.xml-docDate,
.xml-premiere,
.xml-casting,
.xml-recette,
.xml-nombre {
    display: block;
}

.xml-docTitle {
    font-style: italic;
    font-weight: bold;
}

.xml-docTitle,
.xml-docAuthor,
.xml-docDate {
    text-align: center;
}

.xml-docTitle span[type="main"] {
    font-size: 150%;
    display: block;
}

.xml-docTitle span[type="sub"] {
    font-size: 120%;
    display: block;
}

.xml-performance,
.xml-docImprint {
    margin-top: 10px;
}

.xml-set {
    display: block;
    font-style: italic;
    margin-top: 10px;
}

/*Dictionary formatting*/

body {
    counter-reset: section;
    /* Set the section counter to 0 */
}

.xml-prononciation::before {
    content: "(";
}

.xml-prononciation::after {
    content: ")\A";
}

.xml-nature {
    font-style: italic;
}

.xml-indent,
.xml-variante {
    display: block;
}

.xml-variante {
    padding-top: 10px;
    padding-bottom: 10px;
    text-indent: -1.3em;
    padding-left: 1.3em;
}

.xml-variante::before {
    counter-increment: section;
    content: counter(section) ")\00a0";
    font-weight: 700;
}

:not(.xml-rubrique) + .xml-indent {
    padding-top: 10px;
}

.xml-indent {
    padding-left: 1.3em;
}

.xml-cit {
    padding-left: 2.3em;
    display: block;
    text-indent: -1.3em;
}

.xml-indent > .xml-cit {
    padding-left: 1em;
}

.xml-cit::before {
    content: "\2012\00a0\00ab\00a0";
}

.xml-cit::after {
    content: "\00a0\00bb\00a0("attr(aut) "\00a0"attr(ref) ")";
    font-variant: small-caps;
}

.xml-rubrique {
    display: block;
    margin-top: 20px;
}

.xml-rubrique::before {
    content: attr(nom);
    font-variant: small-caps;
    font-weight: 700;
}

.xml-corps + .xml-rubrique {
    margin-top: 10px;
}

/*Methodique styling*/

div[type="article"] .headword {
    display: inline-block;
    margin-bottom: 10px;
}

.headword + p {
    display: inline;
}

.headword + p + p {
    margin-top: 10px;
}

/*Note handling*/

.popover {
    max-width: 350px;
    overflow: scroll;
}

.popover-content {
    text-align: justify;
}

.popover-content .xml-p:not(:first-of-type) {
    display: block;
    margin-top: 1em;
    margin-bottom: 1em;
}

.note-content {
    display: none;
}

.note,
.note-ref {
    vertical-align: 0.3em;
    font-size: 0.7em;
}

.note:hover,
.note-ref:hover {
    cursor: pointer;
    text-decoration: none;
}

div[type="notes"] .xml-note {
    margin: 15px 0px;
    display: block;
}

.xml-note::before {
    content: "note\00a0"attr(n) "\00a0:\00a0";
    font-weight: 700;
}

/*Page images*/

.xml-pb-image {
    display: block;
    text-align: center;
    margin: 10px;
}

.page-image-link {
    margin-top: 10px;
    /*display: block;*/
    text-align: center;
}

/*Inline images*/
.inline-img {
    max-width: 40%;
    float: right;
    height: auto;
    padding-left: 15px;
    padding-top: 15px;
}

.inline-img:hover {
    cursor: pointer;
}

.link-back {
    margin-left: 10px;
    line-height: initial;
}

.xml-add {
    color: #ef4500;
}

.xml-seg {
    display: block;
}

/*Table display*/

b.headword[rend="center"] {
    margin-bottom: 30px;
    text-align: center;
}

.xml-table {
    display: table;
    position: relative;
    text-align: center;
    border-collapse: collapse;
}

.xml-table .xml-pb-image {
    position: absolute;
    width: 100%;
    margin-top: 15px;
}

.xml-row {
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

.xml-row ~ .xml-row {
    font-weight: inherit;
    text-align: justify;
    font-variant: inherit;
}

.xml-pb-image + .xml-row {
    padding-top: 50px;
    padding-bottom: 10px;
    border-top-width: 0px;
}

.xml-cell {
    display: table-cell;
    padding-top: inherit; /*inherit padding when image is above */
    padding-bottom: inherit;
}
</style>


