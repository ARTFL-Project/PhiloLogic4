import Vue from 'vue'
import Router from 'vue-router'

import concordance from '../components/Concordance'
import kwic from '../components/Kwic'
import bibliography from '../components/Bibliography'
import collocation from '../components/Collocation'
import timeSeries from '../components/TimeSeries'
import textNavigation from '../components/TextNavigation'

Vue.use(Router)

export default new Router({
    mode: 'history',
    // base: globalConfig.appPath,
    routes: [{
            path: '/',
            name: 'home'
        },
        {
            path: '/concordance',
            name: 'concordance',
            component: concordance
        },
        {
            path: '/kwic',
            name: 'kwic',
            component: kwic
        },
        {
            path: '/bibliography',
            name: 'bibliography',
            component: bibliography
        },
        {
            path: "/collocation",
            name: "collocation",
            component: collocation
        },
        {
            path: "/time_series",
            name: "timeSeries",
            component: timeSeries
        },
        {
            path: "/navigate/:pathInfo*\/",
            name: "textNavigation",
            component: textNavigation
        }
    ],
    scrollBehavior(to, from, savedPosition) {
        if (savedPosition) {
            return savedPosition
        } else {
            return {
                x: 0,
                y: 0
            }
        }
    }
})