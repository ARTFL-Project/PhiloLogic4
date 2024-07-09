<template>
    <div style="margin-top: 0.2rem">
        <div class="dropdown">
            <button class="btn btn-sm btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown"
                aria-expanded="false" aria-label="Change language">
                <img src="../assets/language.png" aria-label="language picker" height="18" width="18" />
            </button>
            <ul class="dropdown-menu">
                <li v-for="locale in $i18n.availableLocales" :key="`locale-${locale}`" @click="changeLocale(locale)">
                    {{ localNames[locale] }}
                </li>
            </ul>
        </div>
    </div>
</template>
<script>
export default {
    name: "locale-changer",
    data() {
        return {
            localNames: {
                en: "English",
                fr: "Français",
            },
        };
    },
    methods: {
        changeLocale(locale) {
            localStorage.setItem("lang", locale);
            this.$i18n.locale = locale;
        },
    },
};
</script>
<style lang="scss" scoped>
@import "../assets/styles/theme.module.scss";

button {
    font-size: inherit !important;
    border-width: 0 !important;
}

li {
    font-size: 80% !important;
}

button,
li {
    font-variant: small-caps;
    padding-left: 0.5rem;
    padding-right: 0.5rem;
}

li:hover {
    color: #fff;
    background: $link-color;
    cursor: pointer;
}

.dropdown-menu {
    left: initial !important;
    right: 0;
    min-width: initial;
    padding: 0;
}
</style>