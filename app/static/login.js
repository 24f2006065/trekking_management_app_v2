const loginPage = document.getElementById("login-app");

Vue.createApp({
    data() {
        return {
            message: loginPage.dataset.message,
        };
    },
}).mount("#login-app");
