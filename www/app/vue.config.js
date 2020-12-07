module.exports = {
    devServer: {
        compress: true,
        // disableHostCheck: true,
        host: "localhost",
        proxy: "https://marat.uchicago.edu/philologic5/:8080",
        headers: {
            'Access-Control-Allow-Origin': '*'
        }
    },
    chainWebpack: config => {
        config.externals({
            Vue: 'vue'
        })
    },
    runtimeCompiler: true,
    publicPath: process.env.NODE_ENV === 'production' ? getBaseUrl() : '/'
}

function getBaseUrl() {
    const globalConfig = require('./appConfig.json')
    return globalConfig.dbUrl
}