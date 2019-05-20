module.exports = {
    devServer: {
        disableHostCheck: true,
        host: "0.0.0.0",
        headers: {
            'Access-Control-Allow-Origin': '*'
        }
    },
    chainWebpack: config => {
        config.externals({
            Vue: 'vue'
        })
    },
    runtimeCompiler: true

}