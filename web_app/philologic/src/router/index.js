import Vue from "vue";
import Router from "vue-router";

import concordance from "../components/Concordance"

Vue.use(Router);

export default new Router({
    mode: "history",
    // base: globalConfig.appPath,
    routes: [{
            path: "/concordance",
            name: "concordance",
            component: concordance
        }
        // {
        //     path: "/kwic",
        //     name: "/kwic",
        //     component: kwic
        // },
        // {
        //     path: "/collocation",
        //     name: "collocation",
        //     component: concordance
        // },
        // {
        //     path: "/bibliography",
        //     name: "bibliography",
        //     component: bibliography
        // },
        // {
        //     path: "/time",
        //     name: "timeSeries",
        //     component: timeSeries
        // }
    ],
    scrollBehavior(to, from, savedPosition) {
        if (savedPosition) {
            return savedPosition;
        } else {
            return {
                x: 0,
                y: 0
            };
        }
    }
});