<template>
    <b-container fluid>
        <div id="access-control-container" class="mt-4">
            <b-card
                class="text-center mt-4 shadow"
                title="Access Restricted to ARTFL subscribing institutions"
                title-tag="h3"
                sub-title="Please read the following below"
            >
                <b-form
                    @submit.prevent
                    @reset="reset()"
                    @keyup.enter="submit()"
                    id="password-access"
                    class="mt-4 p-4"
                    style="text-align: justify"
                >
                    <h5 v-if="!accessDenied" class="mt-2 mb-3">
                        If you have a username and password, please enter them here:
                    </h5>
                    <h5 class="text-danger" v-if="accessDenied">
                        Your username or password don't match. Please try again.
                    </h5>
                    <b-row class="mb-3">
                        <b-col cols="12" sm="6" md="5" lg="4">
                            <b-input-group prepend="Username">
                                <b-form-input v-model="accessInput.username"></b-form-input>
                            </b-input-group>
                        </b-col>
                    </b-row>
                    <b-row class="mb-3">
                        <b-col cols="12" sm="6" md="5" lg="4">
                            <b-input-group prepend="Password">
                                <b-form-input v-model="accessInput.password"></b-form-input>
                            </b-input-group>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col cols="12">
                            <b-button-group>
                                <b-button @click="submit">Submit</b-button>
                                <b-button type="reset" variant="danger" @click="reset">Reset</b-button>
                            </b-button-group>
                        </b-col>
                    </b-row>
                </b-form>
                <b-card class="mt-4 p4">
                    <p>
                        Please
                        <a href="http://artfl-project.uchicago.edu/node/24">contact ARTFL</a>
                        for more information or to have your computer enabled if your institution is an
                        <a href="http://artfl-project.uchicago.edu/node/2">ARTFL subscriber</a>
                    </p>
                    <p>
                        If you belong to a subscribing institution and are attempting to access ARTFL from your Internet
                        Service Provider, please note that you should use your institution's
                        <b>proxy server</b> and should contact your networking support office. Your proxy server must be
                        configured to include <tt>{{ domainName }}</tt> to access this database.
                    </p>
                    <p>
                        Please consult
                        <a href="http://artfl-project.uchicago.edu/node/14">Subscription Information</a> to see how your
                        institution can gain access to ARTFL resources.
                    </p>
                    <p ng-if="access.clientIp">
                        Requesting Computer Address:
                        <tt>{{ clientIp }}</tt>
                    </p>
                </b-card>
            </b-card>
        </div>
    </b-container>
</template>
<script>
import { emitter } from "../main.js";

export default {
    name: "AccessControl",
    props: ["authorized", "clientIp", "domainName"],
    inject: ["$http"],
    data() {
        return {
            accessInput: { username: "", password: "" },
            accessDenied: false,
        };
    },
    created() {},
    methods: {
        submit() {
            this.$http
                .get(
                    `${this.$dbUrl}/scripts/access_request.py?username=${encodeURIComponent(
                        this.accessInput.username
                    )}&password=${encodeURIComponent(this.accessInput.password)}`
                )
                .then((response) => {
                    var authorization = response.data;
                    if (authorization.access) {
                        emitter.emit("accessAuthorized");
                    } else {
                        this.accessDenied = true;
                    }
                });
        },
        reset() {
            this.accessInput = { username: "", password: "" };
        },
    },
};
</script>