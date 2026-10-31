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
