window.createAdminApp({
  data() {
    return { treks: [], staff: [], search: "", message: "" };
  },
  async mounted() {
    await this.loadTreks();
  },
  methods: {
    async loadTreks() {
      const response = await fetch(
        `/api/admin/treks?search=${encodeURIComponent(this.search)}`,
      );
      const data = await response.json();
      this.treks = data.treks;
      this.staff = data.staff;
      this.treks.forEach((trek) => {
        trek.staff_id = trek.assigned_staff_id || "";
      });
    },
    async updateTrek(trek) {
      try {
        const result = await window.adminPost({
          action: "update_trek",
          ...trek,
        });
        this.message = result.message;
      } catch (error) {
        this.message = error.message;
      }
    },
    async assignStaff(trek) {
      try {
        const result = await window.adminPost({
          action: "assign_staff",
          trek_id: trek.trek_id,
          staff_id: trek.staff_id,
        });
        this.message = result.message;
      } catch (error) {
        this.message = error.message;
      }
    },
    async deleteTrek(trekId) {
      if (!confirm("Remove this trek?")) return;
      try {
        const result = await window.adminPost({
          action: "delete_trek",
          trek_id: trekId,
        });
        this.message = result.message;
        await this.loadTreks();
      } catch (error) {
        this.message = error.message;
      }
    },
  },
});
