window.createAdminApp({
  data() {
    return {
      trek: {
        trek_name: "",
        location: "",
        difficulty: "",
        duration_days: "",
        available_slots: "",
        start_date: "",
        end_date: "",
      },
      message: "",
    };
  },
  methods: {
    async addTrek() {
      try {
        const result = await window.adminPost({
          action: "add_trek",
          ...this.trek,
        });
        this.message = result.message;
        this.trek = {
          trek_name: "",
          location: "",
          difficulty: "",
          duration_days: "",
          available_slots: "",
          start_date: "",
          end_date: "",
        };
      } catch (error) {
        this.message = error.message;
      }
    },
  },
});
