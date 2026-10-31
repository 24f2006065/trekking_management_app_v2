window.createAdminApp({
  data() {
    return { treks: [], message: "" };
  },
  async mounted() {
    const response = await fetch("/api/admin/statistics");
    const data = await response.json();
    this.treks = data.treks;
  },
});
