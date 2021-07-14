export function paramsFilter(formValues) {
    let localFormData = {}
    let validFields = []
    if ("report" in formValues && formValues.report in this.$store.state.reportValues) {
        validFields = this.$store.state.reportValues[formValues.report]
    } else {
        validFields = new Set(Object.keys(formValues))
    }
    if (formValues.approximate == "no") {
        formValues.approximate_ratio = ""
    }
    for (const field in formValues) {
        let value = formValues[field]
        if (field === 'report') {
            continue
        }
        if (!validFields.has(field)) {
            continue
        }
        if (value.length > 0 || field === 'results_per_page') {
            if (
                (field === 'method' && value === 'proxy') ||
                (field === 'approximate' && value == 'no') ||
                (field === 'sort_by' && value === 'rowid')
            ) {
                continue
            } else if ((field == 'start' && value == 0) || (field == 'end' && value == 0)) {
                continue
            } else {
                localFormData[field] = value
            }
        } else if (field == 'hit_num') {
            localFormData[field] = value
        }
    }
    return localFormData
}
export function paramsToRoute(formValues) {
    let report
    if (formValues.q.length == 0 && !["bibliography", "aggregation", "time_series"].includes(formValues.report)) {
        report = "bibliography"
    } else {
        report = formValues.report
    }
    let localFormData = this.paramsFilter(formValues)
    let routeObject = {
        path: `/${report}`,
        query: localFormData
    }
    return routeObject
}
export function paramsToUrlString(params) {
    let filteredParams = this.paramsFilter(params)
    let queryParams = []
    for (let param in filteredParams) {
        queryParams.push(`${param}=${encodeURIComponent(filteredParams[param])}`)
    }
    return queryParams.join('&')
}
export function copyObject(objectToCopy) {
    return JSON.parse(JSON.stringify(objectToCopy))
}
export function saveToLocalStorage(urlString, results) {
    try {
        sessionStorage[urlString] = JSON.stringify(results)
        console.log('saved results to localStorage')
    } catch (e) {
        sessionStorage.clear()
        console.log('Clearing sessionStorage for space...')
        try {
            sessionStorage[urlString] = JSON.stringify(results)
            console.log('saved results to localStorage')
        } catch (e) {
            sessionStorage.clear()
            console.log('Quota exceeded error: the JSON object is too big...')
        }
    }
}
export function mergeResults(fullResults, newData, sortKey) {
    if (typeof fullResults === 'undefined' || Object.keys(fullResults).length === 0) {
        fullResults = newData
    } else {
        for (let key in newData) {
            let value = newData[key]
            if (typeof value.count !== 'undefined') {
                if (key in fullResults) {
                    fullResults[key].count += value.count
                } else {
                    fullResults[key] = value
                }
            }
        }
    }
    let sortedList = this.sortResults(fullResults, sortKey)
    return {
        sorted: sortedList,
        unsorted: fullResults
    }
}
export function sortResults(fullResults, sortKey) {
    let sortedList = []
    for (let key in fullResults) {
        sortedList.push({
            label: key,
            count: parseFloat(fullResults[key].count),
            metadata: fullResults[key].metadata
        })
    }
    if (sortKey === 'label') {
        sortedList.sort(function (a, b) {
            return a.label - b.label
        })
    } else {
        sortedList.sort(function (a, b) {
            return b.count - a.count
        })
    }
    return sortedList
}
export function deepEqual(x, y) {
    const ok = Object.keys,
        tx = typeof x,
        ty = typeof y;
    return x && y && tx === 'object' && tx === ty ? (
        ok(x).length === ok(y).length &&
        ok(x).every(key => this.deepEqual(x[key], y[key]))
    ) : (x === y);
}
export function dictionaryLookup(event, year) {
    if (event.key === "d") {
        var selection = window.getSelection().toString();
        var century = parseInt(year.slice(0, year.length - 2));
        var range = century.toString() + "00-" + String(century + 1) + "00";
        if (range == "NaN00-NaN00") {
            range = "";
        }
        var link = this.$philoConfig.dictionary_lookup + "?docyear=" + range + "&strippedhw=" + selection;
        window.open(link);
    }
}
export function debug(component, message) {
    console.log(`MESSAGE FROM ${component.$options.name}:`, message)
}

export default {
    paramsFilter, paramsToRoute, paramsToUrlString, copyObject, saveToLocalStorage, mergeResults, sortResults, deepEqual, dictionaryLookup, debug
}