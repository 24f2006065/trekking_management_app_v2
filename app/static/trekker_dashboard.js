const trekkerPage = document.getElementById("trekker-app");

Vue.createApp({
    data() {
        return {
            userName: trekkerPage.dataset.userName,
        };
    },
}).mount("#trekker-app");
