const adminPage = document.getElementById("admin-app");

Vue.createApp({
    data() {
        return {
            userName: adminPage.dataset.userName,
        };
    },
}).mount("#admin-app");
