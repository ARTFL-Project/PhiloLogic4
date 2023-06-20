import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import VueI18nPlugin from "@intlify/unplugin-vue-i18n/vite";
import { fileURLToPath, URL } from "node:url";
import { resolve, dirname } from "node:path";

export default defineConfig({
    plugins: [
        vue(),
        VueI18nPlugin({
            include: resolve(
                dirname(fileURLToPath(
                    import.meta.url)),
                "./src/locales/**"
            ),
        }),
    ],
    base: process.env.NODE_ENV === "production" ? getBaseUrl() : "/",
    resolve: {
        alias: {
            "@": fileURLToPath(new URL("./src",
                import.meta.url)),
        },
        // TODO: Remove by explicitely adding extension in imports
        extensions: [".js", ".json", ".vue"],
    },
    server: {
        hmr: {
            overlay: false,
        },
        // cors: true,
    },
});

function getBaseUrl() {
    const fs = require("fs");
    let appConfig = fs.readFileSync("appConfig.json");
    let dbUrl = JSON.parse(appConfig).dbUrl;
    if (dbUrl == "") {
        let dbPath = __dirname.replace(/app$/, "");
        let dbname = dbPath.split("/").reverse()[1];
        let config = fs.readFileSync("/etc/philologic/philologic4.cfg", "utf8");
        let re = /url_root = "([^"]+)"/gm;
        let match = re.exec(config);
        let rootPath = match[1];
        if (rootPath.endsWith("/")) {
            rootPath = rootPath.slice(0, -1);
        }
        dbUrl = rootPath + "/" + dbname + "/";
        let jsonString = JSON.stringify({ dbUrl: dbUrl });
        fs.writeFileSync("./appConfig.json", jsonString);
        return dbUrl;
    }
    return dbUrl;
}