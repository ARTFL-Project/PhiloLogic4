<template>
    <div class="container-fluid mt-4">
        <div id="access-control-container" class="mt-4">
            <div class="card mt-4 shadow" sub-title="Please read the following below">
                <div class="card-body">
                    <h3 class="card-title text-center">Access Restricted to ARTFL subscribing institutions</h3>
                    <h6 class="card-subtitle mb-2 text-muted text-center">Please read the following below</h6>
                    <form @submit.prevent @reset="onReset" @keyup.enter="submit()" id="password-access"
                        class="mt-4 p-2">
                        <h5 v-if="!accessDenied" class="mt-2 mb-3">
                            If you have a username and password, please enter them here:
                        </h5>
                        <h5 class="text-danger" v-if="incorrectLogin">
                            Your username or password don't match. Please try again.
                        </h5>
                        <div class="row mb-3">
                            <div class="cols-12 cols-sm-6 cols-md-5 cols-lg-4">
                                <div class="input-group">
                                    <button type="button" class="btn btn-outline-secondary"
                                        aria-label="Username">Username</button>
                                    <input type="text" class="form-control" style="max-width: 300px"
                                        v-model="accessInput.username" />
                                </div>
                            </div>
                        </div>
                        <div class="row mb-3">
                            <div class="cols-12 cols-sm-6 cols-md-5 cols-lg-4">
                                <div class="input-group">
                                    <button type="button" class="btn btn-outline-secondary"
                                        aria-label="Password">Password</button>
                                    <input type="text" class="form-control" style="max-width: 300px"
                                        v-model="accessInput.password" />
                                </div>
                            </div>
                        </div>
                        <div class="text-danger pb-3" v-if="incorrectLogin">Incorrect login, please try again.</div>
                        <div class="row">
                            <div class="cols-12">
                                <div class="btn-group" role="group">
                                    <button type="button" class="btn btn-outline-secondary" aria-label="Submit"
                                        @click="submit">
                                        Submit
                                    </button>
                                    <button type="reset" class="btn btn-danger" aria-label="Reset"
                                        @click="reset">Reset</button>
                                </div>
                            </div>
                        </div>
                    </form>
                    <div class="card mt-4 p-3 shadow-sm" style="font-size: 1.1rem">
                        <p>
                            Please
                            <a href="http://artfl-project.uchicago.edu/node/24">contact ARTFL</a>
                            for more information or to have your computer enabled if your institution is an
                            <a href="http://artfl-project.uchicago.edu/node/2">ARTFL subscriber</a>
                        </p>
                        <p>
                            If you belong to a subscribing institution and are attempting to access ARTFL from your
                            Internet Service Provider, please note that you should use your institution's
                            <b>proxy server</b> and should contact your networking support office. Your proxy server
                            must be configured to include <code>{{ domainName }}</code> to access this database.
                        </p>
                        <p>
                            Please consult
                            <a href="http://artfl-project.uchicago.edu/node/14">Subscription Information</a> to see how
                            your institution can gain access to ARTFL resources.
                        </p>
                        <p ng-if="access.clientIp">
                            Requesting Computer Address:
                            <code>{{ clientIp }}</code>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import { inject, ref } from "vue";

export default {
    props: ["clientIp", "domainName"],
    setup() {
        let accessDenied = ref(false);
        let incorrectLogin = ref(false);
        let accessInput = { username: "", password: "" };
        let http = inject("$http");
        let dbUrl = inject("$dbUrl");

        function submit() {
            http.get(
                `${dbUrl}/scripts/access_request.py?username=${encodeURIComponent(
                    accessInput.username
                )}&password=${encodeURIComponent(accessInput.password)}`
            ).then((response) => {
                let authorization = response.data;
                if (authorization.access) {
                    location.reload();
                } else {
                    incorrectLogin = true;
                }
            });
        }
        function reset() {
            accessInput = { username: "", password: "" };
        }
        return { accessDenied, accessInput, incorrectLogin, submit, reset };
    },
};
</script>
<style scoped>
code {
    color: #000;
    font-weight: 700;
}
</style>