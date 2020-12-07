import Vue from 'vue'
import Router from 'vue-router'

const concordance = () => import('../components/Concordance');
const kwic = () => import('../components/Kwic');
const bibliography = () => import('../components/Bibliography');
const collocation = () => import('../components/Collocation');
const timeSeries = () => import('../components/TimeSeries');
const textNavigation = () => import('../components/TextNavigation');
const tableOfContents = () => import('../components/TableOfContents');
const landingPage = () => import('../components/LandingPage');
const aggregation = () => import("../components/Aggregation");
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
        path: "/navigate/:pathInfo([\\d/]+)",
        name: "textNavigation",
        component: textNavigation
    },
    {
        path: "/navigate/:pathInfo(\\d+)/table-of-contents",
        name: "tableOfContents",
        component: tableOfContents
    },
    {
        path: "/aggregation",
        name: 'aggregation',
        component: aggregation
    },
    // for compatibility with old Philo links: still used in landing page
    {
        path: "/query",
        redirect: to => {
            return {
                name: to.query.report,
                params: to.params
            }
        }
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

// function determineRoute() {
//     console.log(process.env.NODE_ENV)
//     return appConfig.dbUrl.replace(/https?:\/\/[^/]+\//, "")
// }