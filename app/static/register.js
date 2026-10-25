const registerPage = document.getElementById("register-app");

Vue.createApp({
    data() {
        return {
            message: registerPage.dataset.message,
        };
    },
}).mount("#register-app");
