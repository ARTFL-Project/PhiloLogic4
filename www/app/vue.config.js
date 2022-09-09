module.exports = {
    devServer: {
        compress: true,
        allowedHosts: 'all',
        proxy: "https://anomander.uchicago.edu/philologic",
        headers: {
            'Access-Control-Allow-Origin': '*'
        }
    },
    publicPath: process.env.NODE_ENV === 'production' ? getBaseUrl() : '/',
    transpileDependencies: true,
}

function getBaseUrl() {
    const fs = require('fs')
    let appConfig = fs.readFileSync("appConfig.json")
    let dbUrl = JSON.parse(appConfig).dbUrl
    if (dbUrl == "") {
        let dbPath = __dirname.replace(/app$/, "")
        let dbname = dbPath.split("/").reverse()[1]
        let config = fs.readFileSync("/etc/philologic/philologic4.cfg", "utf8")
        let re = /url_root = "([^"]+)"/gm
        let match = re.exec(config)
        let rootPath = match[1]
        if (rootPath.endsWith("/")) {
            rootPath = rootPath.slice(0, -1)
        }
        dbUrl = rootPath + "/" + dbname + "/"
        let jsonString = JSON.stringify({ "dbUrl": dbUrl })
        fs.writeFileSync("./appConfig.json", jsonString)
        return url
    }
    return dbUrl
}