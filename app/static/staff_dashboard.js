const staffPage = document.getElementById("staff-app");

Vue.createApp({
    data() {
        return {
            userName: staffPage.dataset.userName,
        };
    },
}).mount("#staff-app");
