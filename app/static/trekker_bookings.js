window.createTrekkerApp({
  data() {
    return { bookings: [] };
  },
  async mounted() {
    const response = await fetch("/api/trekker/bookings");
    const data = await response.json();
    this.bookings = data.bookings;
  },
});
