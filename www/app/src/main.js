import { createApp } from "vue";
import vueScrollTo from "vue-scrollto";
import App from "./App.vue";
import router from "./router";
import store from "./store";
import {
    paramsFilter,
    paramsToRoute,
    paramsToUrlString,
    copyObject,
    saveToLocalStorage,
    mergeResults,
    sortResults,
    deepEqual,
    dictionaryLookup,
    debug,
} from "./mixins.js";
import axios from "axios";
import "bootstrap";

import appConfig from "../appConfig.json";
import i18n from "./i18n";

axios
    .get(`${appConfig.dbUrl}/scripts/get_web_config.py`, {})
    .then((response) => {
        const app = createApp(App).use(i18n);
        app.config.globalProperties.$philoConfig = response.data;
        app.config.globalProperties.$scrollTo = vueScrollTo.scrollTo;
        app.config.globalProperties.$dbUrl = appConfig.dbUrl;
        app.config.unwrapInjectedRef = true;
        app.provide("$http", axios);
        app.provide("$dbUrl", appConfig.dbUrl);
        app.provide("$philoConfig", response.data);
        app.use(router);
        app.use(store);
        app.mixin({
            methods: {
                paramsFilter,
                paramsToRoute,
                paramsToUrlString,
                copyObject,
                saveToLocalStorage,
                mergeResults,
                sortResults,
                deepEqual,
                dictionaryLookup,
                debug,
            },
        });
        app.directive("scroll", {
            mounted: function (el, binding) {
                el.scrollHandler = function (evt) {
                    if (binding.value(evt, el)) {
                        window.removeEventListener("scroll", el.scrollHandler);
                    }
                };
                window.addEventListener("scroll", el.scrollHandler);
            },
            unmounted: function (el) {
                window.removeEventListener("scroll", el.scrollHandler);
            },
        });

        router.isReady().then(() => app.mount("#app"));
    })
    .catch((error) => {
        // this.loading = false
        console.log(error.toString());
    });
