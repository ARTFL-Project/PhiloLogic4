<template>
    <div class="container-fluid mt-4">
        <div class="row">
            <div class="col-8 offset-2">
                <div id="object-title" class="text-center pt-4">
                    <h5>
                        <citations :citation="textNavigationCitation"></citations>
                    </h5>
                </div>
            </div>
        </div>
        <div class="row text-center mt-4" id="toc-wrapper" v-if="navBar === true || loading === false">
            <div id="toc-top-bar">
                <div id="nav-buttons" v-scroll="handleScroll">
                    <button type="button" class="btn btn-secondary btn-sm" id="back-to-top" @click="backToTop()">
                        <span class="d-none d-sm-inline-block">Back to top</span>
                        <span class="d-inline-block d-sm-none">Top</span>
                    </button>
                    <div class="btn-group btn-group-sm" style="pointer-events: all">
                        <button
                            type="button"
                            class="btn btn-secondary"
                            disabled
                            id="prev-obj"
                            @click="goToTextObject(textObject.prev)"
                        >
                            &lt;
                        </button>
                        <button
                            type="button"
                            class="btn btn-secondary"
                            id="show-toc"
                            disabled
                            @click="toggleTableOfContents()"
                        >
                            Table of contents
                        </button>
                        <button
                            type="button"
                            class="btn btn-secondary"
                            disabled
                            id="next-obj"
                            @click="goToTextObject(textObject.next)"
                        >
                            &gt;
                        </button>
                    </div>
                    <a
                        id="report-error"
                        class="btn btn-secondary btn-sm position-absolute"
                        target="_blank "
                        :href="philoConfig.report_error_link"
                        v-if="philoConfig.report_error_link != ''"
                        >Report Error</a
                    >
                </div>
                <div id="toc">
                    <div id="toc-titlebar" class="d-none">
                        <button type="button" class="btn btn-secondary" id="hide-toc" @click="toggleTableOfContents()">
                            X
                        </button>
                    </div>
                    <transition name="slide-fade">
                        <div
                            class="card p-3 shadow"
                            id="toc-content"
                            :style="tocHeight"
                            :scroll-to="tocPosition"
                            v-if="tocOpen"
                        >
                            <div class="toc-more before" v-if="start !== 0">
                                <button type="button" class="btn btn-default btn-sm" @click="loadBefore()"></button>
                            </div>
                            <div v-for="(element, tocIndex) in tocElementsToDisplay" :key="tocIndex">
                                <div
                                    :id="element.philo_id"
                                    :class="'toc-' + element.philo_type"
                                    @click="textObjectSelection(element.philo_id, tocIndex, $event)"
                                >
                                    <span :class="'bullet-point-' + element.philo_type"></span>
                                    <a :class="{ 'current-obj': element.philo_id === currentPhiloId }" href>
                                        {{ element.label }}
                                    </a>
                                </div>
                            </div>
                            <div class="toc-more after" v-if="end < tocElements.length">
                                <button type="button" class="btn btn-default btn-sm" @click="loadAfter()"></button>
                            </div>
                        </div>
                    </transition>
                </div>
            </div>
        </div>
        <div style="font-size: 80%; text-align: center" v-if="philoConfig.dictionary_lookup != ''">
            To look up a word in a dictionary, select the word with your mouse and press 'd' on your keyboard.
        </div>
        <div class="row" id="all-content">
            <div
                class="col-12 col-sm-10 offset-sm-1 col-lg-8 offset-lg-2"
                id="center-content"
                v-if="textObject.text"
                style="text-align: center"
            >
                <div class="card mt-2 mb-4 p-4 shadow d-inline-block">
                    <div id="book-page" class="text-view">
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
                            :philo-id="philoID"
                            @keydown="dicoLookup($event)"
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
                                v-for="(img, afterGraphIndex) in afterGraphicsImgs"
                                :key="afterGraphIndex"
                                data-gallery
                            ></a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div
            id="blueimp-gallery"
            class="blueimp-gallery blueimp-gallery-controls"
            data-full-screen="true"
            data-continuous="false"
            style="display: none"
        >
            <div class="slides"></div>
            <h3 class="title"></h3>
            <a class="prev img-buttons">&lt;</a>
            <a class="next img-buttons">&gt;</a>
            <a id="full-size-image" class="img-buttons">&nearr;</a>
            <a class="close img-buttons">&#10005;</a>
            <ol class="indicator"></ol>
        </div>
    </div>
</template>
<script>
import { mapFields } from "vuex-map-fields";
import citations from "./Citations";
import Gallery from "blueimp-gallery";
import "blueimp-gallery/css/blueimp-gallery.min.css";
import { Popover } from "bootstrap";

export default {
    name: "textNavigation",
    components: {
        citations,
    },
    inject: ["$http"],
    computed: {
        ...mapFields({
            report: "formData.report",
            start_byte: "formData.start_byte",
            end_byte: "formData.end_byte",
            textNavigationCitation: "textNavigationCitation",
            navBar: "navBar",
            tocElements: "tocElements",
            byte: "byte",
            searching: "searching",
            accessAuthorized: "accessAuthorized",
        }),
        tocElementsToDisplay: function () {
            return this.tocElements.elements.slice(this.start, this.end);
        },
        tocHeight() {
            return `max-height: ${window.innerHeight - 200}`;
        },
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
            navBarVisible: false,
            timeToRender: 0,
            gallery: null,
        };
    },
    created() {
        this.report = "textNavigation";
        this.fetchToC();
        this.fetchText();
    },
    watch: {
        $route() {
            if (this.$route.name == "textNavigation") {
                this.destroyPopovers();
                this.fetchText();
                this.fetchToC();
            }
        },
    },
    mounted() {
        let tocButton = document.querySelector("#show-toc");
        this.navButtonPosition = tocButton.getBoundingClientRect().top;
    },
    unmounted() {
        if (this.gallery) {
            this.gallery.close();
        }
        this.destroyPopovers();
    },
    methods: {
        fetchText() {
            this.searching = true;
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
                philo_id: this.philoID,
            };
            if (this.start_byte !== "") {
                navigationParams.start_byte = this.start_byte;
                navigationParams.end_byte = this.end_byte;
            }
            let urlQuery = `${byteString}&${this.paramsToUrlString(navigationParams)}`;
            this.timeToRender = new Date().getTime();
            this.$http
                .get(`${this.$dbUrl}/reports/navigation.py?${urlQuery}`)
                .then((response) => {
                    this.textObject = response.data;
                    this.textNavigationCitation = response.data.citation;
                    this.navBar = true;
                    if (this.byte.length > 0) {
                        this.highlight = true;
                    } else {
                        this.highlight = false;
                    }

                    if (!this.deepEqual(response.data.imgs, {})) {
                        this.insertPageLinks(response.data.imgs);
                        this.insertInlineImgs(response.data.imgs);
                    }
                    this.setUpNavBar();
                    this.$nextTick(() => {
                        // Handle inline notes if there are any
                        let notes = document.getElementsByClassName("note");
                        if (notes.length > 0) {
                            Array.from(notes).forEach((note) => {
                                let innerHTML = note.nextElementSibling.innerHTML;
                                new Popover(note, { html: true, content: innerHTML, trigger: "focus" });
                            });
                        }

                        // Handle ref notes if there are any
                        let noteRefs = document.getElementsByClassName("note-ref");
                        if (noteRefs.length > 0) {
                            Array.from(noteRefs).forEach((noteRef) => {
                                let getNotes = () => {
                                    this.$http
                                        .get(`${this.$dbUrl}/scripts/get_notes.py?`, {
                                            params: {
                                                target: noteRef.getAttribute("target"),
                                                philo_id: this.$route.params.pathInfo.split("/").join(" "),
                                            },
                                        })
                                        .then((response) => {
                                            new Popover(noteRef, {
                                                html: true,
                                                content: response.data.text,
                                                trigger: "focus",
                                            });
                                            noteRef.removeEventListener("click", getNotes);
                                        });
                                };
                                noteRef.addEventListener("click", getNotes());
                            });
                        }

                        let linkBack = document.getElementsByClassName("link-back");
                        if (linkBack.length > 0) {
                            Array.from(linkBack).forEach((el) => {
                                if (el) {
                                    var goToNote = () => {
                                        let link = el.getAttribute("link");
                                        this.$router.push(link);
                                        el.removeEventListener("click", goToNote);
                                    };
                                    el.addEventListener("click", goToNote);
                                }
                            });
                        }

                        // Scroll to highlight
                        if (this.byte != "") {
                            let element = document.getElementsByClassName("highlight")[0];
                            let parent = element.parentElement;
                            if (parent.classList.contains("note-content")) {
                                let note = parent.previousSibling;
                                this.$scrollTo(note, 250, {
                                    easing: "ease-out",
                                    offset: -150,
                                    onDone: function () {
                                        note.focus();
                                    },
                                });
                            } else {
                                this.$scrollTo(element, 250, {
                                    easing: "ease-out",
                                    offset: -150,
                                });
                            }
                        } else if (this.start_byte != "") {
                            this.$scrollTo(document.getElementsByClassName("start-highlight")[0], 250, {
                                easing: "ease-out",
                                offset: -150,
                            });
                        } else if (this.$route.hash) {
                            // for note link back
                            let note = document.querySelector(this.$route.hash);
                            this.$scrollTo(note, 250, {
                                easing: "ease-out",
                                offset: -150,
                                onDone: () => {
                                    note.focus();
                                },
                            });
                        }

                        this.setUpGallery();
                        this.searching = false;
                    });
                })
                .catch((error) => {
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
                                `${this.philoConfig.page_images_url_root}/${img[0]}`,
                                `${this.philoConfig.page_images_url_root}/${img[1]}`,
                            ]);
                        } else {
                            this.beforeObjImgs.push([
                                `${this.philoConfig.page_images_url_root}/${img[0]}`,
                                `${this.philoConfig.page_images_url_root}/${img[0]}`,
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
                                `${this.philoConfig.page_images_url_root}/${img[0]}`,
                                `${this.philoConfig.page_images_url_root}/${img[1]}`,
                            ]);
                        } else {
                            this.afterObjImgs.push([
                                `${this.philoConfig.page_images_url_root}/${img[0]}`,
                                `${this.philoConfig.page_images_url_root}/${img[0]}`,
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
                                `${this.philoConfig.page_images_url_root}/${img[0]}`,
                                `${this.philoConfig.page_images_url_root}/${img[1]}`,
                            ]);
                        } else {
                            this.beforeGraphicsImgs.push([
                                `${this.philoConfig.page_images_url_root}/${img[0]}`,
                                `${this.philoConfig.page_images_url_root}/${img[0]}`,
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
                                `${this.philoConfig.page_images_url_root}/${img[0]}`,
                                `${this.philoConfig.page_images_url_root}/${img[1]}`,
                            ]);
                        } else {
                            this.afterGraphicsImgs.push([
                                `${this.philoConfig.page_images_url_root}/${img[0]}`,
                                `${this.philoConfig.page_images_url_root}/${img[0]}`,
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
                            philo_id: this.currentPhiloId,
                        },
                    })
                    .then((response) => {
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
                            end: this.end,
                        };
                        let tocButton = document.querySelector("#show-toc");
                        tocButton.removeAttribute("disabled");
                        tocButton.classList.remove("disabled");
                    })
                    .catch((error) => {
                        this.debug(this, error);
                    });
            } else {
                this.start = this.tocElements.start;
                this.end = this.tocElements.end;
                this.$nextTick(function () {
                    let tocButton = document.querySelector("#show-toc");
                    tocButton.removeAttribute("disabled");
                    tocButton.classList.remove("disabled");
                });
            }
        },
        setUpGallery() {
            // Image Gallery handling
            for (let imageType of ["page-image-link", "inline-img", "external-img"]) {
                Array.from(document.getElementsByClassName(imageType)).forEach((item) => {
                    item.addEventListener("click", (event) => {
                        event.preventDefault();
                        let target = event.target;
                        this.gallery = Gallery(
                            [...document.getElementsByClassName(imageType)].map(
                                (item) => item.getAttribute("href") || item.getAttribute("src")
                            ),
                            {
                                index: Array.from(document.getElementsByClassName(imageType)).indexOf(target),
                                continuous: false,
                                thumbnailIndicators: false,
                            }
                        );
                    });
                });
                document.getElementById("full-size-image").addEventListener("click", () => {
                    let imageIndex = this.gallery.getIndex();
                    let img = Array.from(document.getElementsByClassName(imageType))[imageIndex].getAttribute(
                        "large-img"
                    );
                    window.open(img);
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
                this.tocOpen = false;
            } else {
                this.tocOpen = true;
                this.$nextTick(() => {
                    this.$scrollTo(document.querySelector(".current-obj"), 500, {
                        container: document.querySelector("#toc-content"),
                    });
                });
            }
        },
        backToTop() {
            window.scrollTo({ top: 0, behavior: "smooth" });
        },
        goToTextObject(philoID) {
            philoID = philoID.split(/[- ]/).join("/");
            if (this.tocOpen) {
                this.tocOpen = false;
            }
            this.$router.push({ path: `/navigate/${philoID}` });
        },
        textObjectSelection(philoId, index, event) {
            event.preventDefault();
            let newStart = this.tocElements.start + index - 100;
            if (newStart < 0) {
                newStart = 0;
            }
            this.tocElements = {
                ...this.tocElements,
                start: newStart,
                end: this.tocElements.end - index + 100,
            };
            this.goToTextObject(philoId);
        },
        setUpNavBar() {
            let prevButton = document.querySelector("#prev-obj");
            let nextButton = document.querySelector("#next-obj");
            if (this.textObject.next === "" || typeof this.textObject.next === "undefined") {
                nextButton.classList.add("disabled");
            } else {
                nextButton.removeAttribute("disabled");
                nextButton.classList.remove("disabled");
            }
            if (this.textObject.prev === "" || typeof this.textObject.prev === "undefined") {
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
                    let topBar = document.getElementById("toc-top-bar");
                    topBar.style.top = 0;
                    topBar.classList.add("visible", "shadow");
                    let tocWrapper = document.getElementById("toc-wrapper");
                    tocWrapper.style.top = "31px";
                    let navButtons = document.getElementById("nav-buttons");
                    navButtons.classList.add("visible");
                    let backToTop = document.getElementById("back-to-top");
                    backToTop.classList.add("visible");
                    let reportError = document.getElementById("report-error");
                    if (reportError != null) {
                        reportError.classList.add("visible");
                    }
                }
            } else if (window.scrollY < this.navButtonPosition) {
                this.navBarVisible = false;
                let topBar = document.getElementById("toc-top-bar");
                topBar.style.top = "initial";
                topBar.classList.remove("visible", "shadow");
                let tocWrapper = document.getElementById("toc-wrapper");
                tocWrapper.style.top = "0px";
                let navButtons = document.getElementById("nav-buttons");
                navButtons.style.top = "initial";
                navButtons.classList.remove("visible");
                let backToTop = document.getElementById("back-to-top");
                backToTop.classList.remove("visible");
                let reportError = document.getElementById("report-error");
                if (reportError != null) {
                    reportError.classList.remove("visible");
                }
            }
        },
        dicoLookup(event) {
            if (event.key === "d") {
                let selection = window.getSelection().toString();
                let link;
                if (this.$philoConfig.dictionary_lookup.keywords) {
                    link = `${this.philoConfig.dictionary_lookup.url_root}?${this.philoConfig.dictionary_lookup_keywords.selected_keyword}=${selection}&`;
                    let keyValues = [];
                    for (const [key, value] of Object.entries(
                        this.philoConfig.dictionary_lookup_keywords.immutable_key_values
                    )) {
                        keyValues.push(`${key}=${value}`);
                    }
                    for (const [key, value] of Object.entries(
                        this.philoConfig.dictionary_lookup_keywords.variable_key_values
                    )) {
                        let fieldValue = this.textObject.metadata_fields[value] || "";
                        keyValues.push(`${key}=${fieldValue}`);
                    }
                    link += keyValues.join("&");
                } else {
                    link = `${this.philoConfig.dictionary_lookup.url_root}/${selection}`;
                }
                window.open(link);
            }
        },
        destroyPopovers() {
            document.querySelectorAll(".note, .note-ref").forEach((note) => {
                let popover = Popover.getInstance(note);
                if (popover != null) {
                    Popover.getInstance(note).dispose();
                }
            });
        },
    },
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
    max-height: 90vh;
    overflow: scroll;
    text-align: justify;
    line-height: 180%;
    z-index: 50;
    background: #fff;
}
#toc-wrapper {
    position: relative;
    z-index: 49;
    pointer-events: all;
}
#toc-top-bar {
    height: 31px;
    width: 100%;
    pointer-events: none;
}
#toc {
    margin-top: 31px;
    pointer-events: all;
}
#toc-top-bar.visible {
    position: fixed;
}
#nav-buttons.visible {
    position: fixed;
    backdrop-filter: blur(0.5rem);
    background-color: rgba(255, 255, 255, 0.3);
    pointer-events: all;
}
#back-to-top {
    position: absolute;
    left: 0;
    opacity: 0;
    transition: opacity 0.25s;
    pointer-events: none;
}
#report-error {
    position: absolute;
    right: 0;
    opacity: 0;
    transition: opacity 0.25s;
    pointer-events: none;
}
#back-to-top.visible,
#report-error.visible {
    opacity: 0.95;
    pointer-events: all;
}

#nav-buttons {
    position: absolute;
    opacity: 0.9;
    width: 100%;
}
#toc-nav-bar {
    background-color: #ddd;
    opacity: 0.95;
    backdrop-filter: blur(5px) contrast(0.8);
}

a.current-obj,
#toc-container a:hover {
    background: #e8e8e8;
}

#book-page {
    text-align: justify;
}

:deep(.xml-pb) {
    display: block;
    text-align: center;
    margin: 10px;
}

:deep(.xml-pb::before) {
    content: "-" attr(n) "-";
    white-space: pre;
}

:deep(p) {
    margin-bottom: 0.5rem;
}
:deep(.highlight) {
    background-color: red;
    color: #fff;
}
:deep(.xml-div1::after), /* clear floats from inline images */
:deep(.xml-div2::after),
:deep(.xml-div3::after) {
    content: "";
    display: block;
    clear: right;
}

/* Styling for theater */

:deep(.xml-castitem::after) {
    content: "\A";
    white-space: pre;
}

:deep(.xml-castlist > .xml-castitem:first-of-type::before) {
    content: "\A";
    white-space: pre;
}

:deep(.xml-castgroup::before) {
    content: "\A";
    white-space: pre;
}

:deep(b.headword) {
    font-weight: 700 !important;
    font-size: 130%;
    font-variant: small-caps;
    display: block;
    margin-top: 20px;
}
:deep(b.headword::before) {
    content: "\A";
    white-space: pre;
}

:deep(#bibliographic-results b.headword) {
    font-weight: 400 !important;
    font-size: 100%;
    display: inline;
}

:deep(.xml-lb),
:deep(.xml-l) {
    text-align: justify;
    display: block;
}

:deep(.xml-sp .xml-lb:first-of-type) {
    content: "";
    white-space: normal;
}

:deep(.xml-lb[type="hyphenInWord"]) {
    display: inline;
}

#book-page .xml-sp {
    display: block;
}

:deep(.xml-sp::before) {
    content: "\A";
    white-space: pre;
}

:deep(.xml-stage + .xml-sp:nth-of-type(n + 2)::before) {
    content: "";
}

:deep(.xml-fw, .xml-join) {
    display: none;
}

:deep(.xml-speaker + .xml-stage::before) {
    content: "";
    white-space: normal;
}

:deep(.xml-stage) {
    font-style: italic;
}

:deep(.xml-stage::after) {
    content: "\A";
    white-space: pre;
}

:deep(div1 div2::before) {
    content: "\A";
    white-space: pre;
}

:deep(.xml-speaker) {
    font-weight: 700;
}

:deep(.xml-pb) {
    display: block;
    text-align: center;
    margin: 10px;
}

:deep(.xml-pb::before) {
    content: "-" attr(n) "-";
    white-space: pre;
}

:deep(.xml-lg) {
    display: block;
}

:deep(.xml-lg::after) {
    content: "\A";
    white-space: pre;
}

:deep(.xml-lg:first-of-type::before) {
    content: "\A";
    white-space: pre;
}

:deep(.xml-castList) :deep(.xml-front),
:deep(.xml-castItem),
:deep(.xml-docTitle),
:deep(.xml-docImprint),
:deep(.xml-performance),
:deep(.xml-docAuthor),
:deep(.xml-docDate),
:deep(.xml-premiere),
:deep(.xml-casting),
:deep(.xml-recette),
:deep(.xml-nombre) {
    display: block;
}

:deep(.xml-docTitle) {
    font-style: italic;
    font-weight: bold;
}

:deep(.xml-docAuthor),
:deep(.xml-docTitle),
:deep(.xml-docDate) {
    text-align: center;
}

:deep(.xml-docTitle span[type="main"]) {
    font-size: 150%;
    display: block;
}

:deep(.xml-docTitle span[type="sub"]) {
    font-size: 120%;
    display: block;
}

:deep(.xml-performance),
:deep(.xml-docImprint) {
    margin-top: 10px;
}

:deep(.xml-set) {
    display: block;
    font-style: italic;
    margin-top: 10px;
}

/*Dictionary formatting*/

body {
    counter-reset: section;
    /* Set the section counter to 0 */
}

:deep(.xml-prononciation::before) {
    content: "(";
}

:deep(.xml-prononciation::after) {
    content: ")\A";
}

:deep(.xml-nature) {
    font-style: italic;
}

:deep(.xml-indent),
:deep(.xml-variante) {
    display: block;
}

:deep(.xml-variante) {
    padding-top: 10px;
    padding-bottom: 10px;
    text-indent: -1.3em;
    padding-left: 1.3em;
}

:deep(.xml-variante::before) {
    counter-increment: section;
    content: counter(section) ")\00a0";
    font-weight: 700;
}

:deep(:not(.xml-rubrique) + .xml-indent) {
    padding-top: 10px;
}

:deep(.xml-indent) {
    padding-left: 1.3em;
}

:deep(.xml-cit) {
    padding-left: 2.3em;
    display: block;
    text-indent: -1.3em;
}

:deep(.xml-indent > .xml-cit) {
    padding-left: 1em;
}

:deep(.xml-cit::before) {
    content: "\2012\00a0\00ab\00a0";
}

:deep(.xml-cit::after) {
    content: "\00a0\00bb\00a0("attr(aut) "\00a0"attr(ref) ")";
    font-variant: small-caps;
}

:deep(.xml-rubrique) {
    display: block;
    margin-top: 20px;
}

:deep(.xml-rubrique::before) {
    content: attr(nom);
    font-variant: small-caps;
    font-weight: 700;
}

:deep(.xml-corps + .xml-rubrique) {
    margin-top: 10px;
}

/*Methodique styling*/

:deep(div[type="article"] .headword) {
    display: inline-block;
    margin-bottom: 10px;
}

:deep(.headword + p) {
    display: inline;
}

:deep(.headword + p + p) {
    margin-top: 10px;
}

/*Note handling*/

:deep(.popover) {
    max-width: 350px;
    overflow: scroll;
}

:deep(.popover-content) {
    text-align: justify;
}

:deep(.popover-content .xml-p:not(:first-of-type)) {
    display: block;
    margin-top: 1em;
    margin-bottom: 1em;
}

:deep(.note-content) {
    display: none;
}

:deep(.note),
:deep(.note-ref) {
    vertical-align: 0.3em;
    font-size: 0.7em;
}

:deep(.note:hover),
:deep(.note-ref:hover) {
    cursor: pointer;
    text-decoration: none;
}

:deep(div[type="notes"] .xml-note) {
    margin: 15px 0px;
    display: block;
}

:deep(.xml-note::before) {
    content: "note\00a0"attr(n) "\00a0:\00a0";
    font-weight: 700;
}

/*Page images*/

:deep(.xml-pb-image) {
    display: block;
    text-align: center;
    margin: 10px;
}

:deep(.page-image-link) {
    margin-top: 10px;
    /*display: block;*/
    text-align: center;
}

/*Inline images*/
:deep(.inline-img) {
    max-width: 40%;
    float: right;
    height: auto;
    padding-left: 15px;
    padding-top: 15px;
}

:deep(.inline-img:hover) {
    cursor: pointer;
}

:deep(.link-back) {
    margin-left: 10px;
    line-height: initial;
}

:deep(.xml-add) {
    color: #ef4500;
}

:deep(.xml-seg) {
    display: block;
}

/*Table display*/

:deep(b.headword[rend="center"]) {
    margin-bottom: 30px;
    text-align: center;
}

:deep(.xml-table) {
    display: table;
    position: relative;
    text-align: center;
    border-collapse: collapse;
}

:deep(.xml-table .xml-pb-image) {
    position: absolute;
    width: 100%;
    margin-top: 15px;
}

:deep(.xml-row) {
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

:deep(.xml-row ~ .xml-row) {
    font-weight: inherit;
    text-align: justify;
    font-variant: inherit;
}

:deep(.xml-pb-image + .xml-row) {
    padding-top: 50px;
    padding-bottom: 10px;
    border-top-width: 0px;
}

:deep(.xml-cell) {
    display: table-cell;
    padding-top: inherit; /*inherit padding when image is above */
    padding-bottom: inherit;
}
:deep(s) {
    text-decoration: none;
}
.slide-fade-enter-active {
    transition: all 0.3s ease-out;
}
.slide-fade-leave-active {
    transition: all 0.3s ease-out;
}
.slide-fade-enter-from,
.slide-fade-leave-to {
    transform: translateY(-30px);
    opacity: 0;
}

/* Image button styling */
.img-buttons {
    font-size: 45px !important;
    color: #fff !important;
}
#full-size-image {
    right: 90px;
    font-weight: 700 !important;
    font-size: 20px !important;
    left: auto;
    margin: -15px;
    text-decoration: none;
    cursor: pointer;
    position: absolute;
    top: 28px;
    color: #fff;
    opacity: 0.8;
    border: 3px solid;
    padding: 0 0.25rem;
}
#full-size-image:hover {
    opacity: 1;
}
</style>
