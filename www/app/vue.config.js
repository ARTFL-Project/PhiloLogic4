module.exports = {
    devServer: {
        compress: true,
        disableHostCheck: true,
        // host: "localhost",
        proxy: "https://anomander.uchicago.edu/philologic",
        headers: {
            'Access-Control-Allow-Origin': '*'
        }
    },
    chainWebpack: config => {
        config.module
            .rule('vue')
            .use('vue-loader')
    },
    runtimeCompiler: true,
    publicPath: process.env.NODE_ENV === 'production' ? getBaseUrl() : '/'
}

function getBaseUrl() {
    const fs = require('fs')
    let dbPath = __dirname.replace(/app$/, "")
    let dbname = dbPath.split("/").reverse()[1]
    let config = fs.readFileSync("/etc/philologic/philologic4.cfg", "utf8")
    let re = /url_root = "([^"]+)"/gm
    let match = re.exec(config)
    let url = new URL(dbname, match[1])
    let jsonString = JSON.stringify({ dbUrl: url.href })
    fs.writeFileSync("./appConfig.json", jsonString)
    return url.href
}