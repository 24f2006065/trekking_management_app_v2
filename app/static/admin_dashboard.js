<<<<<<< HEAD
window.createAdminApp({
  data() {
    return {
      counts: { treks: 0, users: 0, staff: 0, bookings: 0 },
      message: "",
    };
  },
  async mounted() {
    const response = await fetch("/api/admin/dashboard");
    this.counts = await response.json();
  },
});
=======
const adminPage = document.getElementById("admin-app");

Vue.createApp({
    data() {
        return {
            userName: adminPage.dataset.userName,
        };
    },
}).mount("#admin-app");
>>>>>>> 15774dd347894ba1ce8744bd70298dcca0c8e2f7
