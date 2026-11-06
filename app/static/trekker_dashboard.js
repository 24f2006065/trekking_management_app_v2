window.createTrekkerApp({
  data() {
    return { name: "", availableTreks: 0, bookings: [] };
  },
  async mounted() {
    const response = await fetch("/api/trekker/dashboard");
    const data = await response.json();
    this.name = data.name;
    this.availableTreks = data.available_treks;
    this.bookings = data.bookings;
  },
});
