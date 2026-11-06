window.createTrekkerApp({
  data() {
    return {
      treks: [],
      message: "",
      filters: { search: "", difficulty: "", location: "", duration: "" },
    };
  },
  async mounted() {
    await this.loadTreks();
  },
  methods: {
    async loadTreks() {
      const params = new URLSearchParams(this.filters);
      const response = await fetch(`/api/trekker/treks?${params}`);
      const data = await response.json();
      this.treks = data.treks;
    },
    async bookTrek(trek) {
      const response = await fetch("/api/trekker/bookings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ trek_id: trek.trek_id }),
      });
      const result = await response.json();
      this.message = result.message;
      if (response.ok) {
        await this.loadTreks();
      }
    },
  },
});
