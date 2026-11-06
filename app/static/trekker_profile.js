window.createTrekkerApp({
  data() {
    return { profile: { name: "", email: "" }, message: "" };
  },
  async mounted() {
    const response = await fetch("/api/trekker/profile");
    this.profile = await response.json();
  },
  methods: {
    async saveProfile() {
      const response = await fetch("/api/trekker/profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(this.profile),
      });
      const result = await response.json();
      this.message = result.message;
    },
  },
});
