window.createAdminApp({
  data() {
    return {
      staff: { name: "", email: "", password: "", contact_details: "" },
      message: "",
    };
  },
  methods: {
    async addStaff() {
      try {
        const result = await window.adminPost({
          action: "add_staff",
          ...this.staff,
        });
        this.message = result.message;
        this.staff = { name: "", email: "", password: "", contact_details: "" };
      } catch (error) {
        this.message = error.message;
      }
    },
  },
});
