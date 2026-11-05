Vue.createApp({
  template: "#staff-template",
  data() {
    return { userName: "", treks: [], message: "" };
  },
  computed: {
    totalParticipants() {
      return this.treks.reduce(
        (total, trek) => total + trek.registered_count,
        0,
      );
    },
  },
  async mounted() {
    const userResponse = await fetch("/api/current-user");
    const user = await userResponse.json();
    this.userName = user.name;
    await this.loadTreks();
  },
  methods: {
    async loadTreks() {
      const response = await fetch("/api/staff/treks");
      const data = await response.json();
      if (response.ok) {
        this.treks = data.treks;
      } else {
        this.message = data.message;
      }
    },
    async saveTrek(trek) {
      const response = await fetch(`/api/staff/treks/${trek.trek_id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          available_slots: trek.available_slots,
          status: trek.status,
        }),
      });
      const result = await response.json();
      this.message = result.message;
      if (response.ok) {
        await this.loadTreks();
      }
    },
  },
}).mount("#staff-app");
