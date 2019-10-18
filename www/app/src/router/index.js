import Vue from 'vue'
import Router from 'vue-router'

import concordance from '../components/Concordance'
import kwic from '../components/Kwic'
import bibliography from '../components/Bibliography'
import collocation from '../components/Collocation'
import timeSeries from '../components/TimeSeries'
import textNavigation from '../components/TextNavigation'
import tableOfContents from '../components/TableOfContents'
import landingPage from '../components/LandingPage'
import statistics from "../components/Statistics"
import appConfig from '../../appConfig.json'


Vue.use(Router)

export default new Router({
    mode: 'history',
    base: appConfig.dbUrl.replace(/https?:\/\/[^/]+\//, ""),
    routes: [{
            path: '/',
            name: 'home',
            component: landingPage
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
            path: "/navigate/:pathInfo([\\d\/]+)",
            name: "textNavigation",
            component: textNavigation
        },
        {
            path: "/navigate/:pathInfo(\\d+)/table-of-contents",
            name: "tableOfContents",
            component: tableOfContents
        },
        {
            path: "/statistics",
            name: 'statistics',
            component: statistics
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