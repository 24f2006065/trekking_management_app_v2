window.createAdminApp({
  data() {
    return { bookings: [], message: "" };
  },
  async mounted() {
    const response = await fetch("/api/admin/bookings");
    const data = await response.json();
    this.bookings = data.bookings;
  },
});
