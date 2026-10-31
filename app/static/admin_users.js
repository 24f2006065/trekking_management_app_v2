window.createAdminApp({
  data() {
    return { users: [], search: "", message: "" };
  },
  async mounted() {
    await this.loadUsers();
  },
  methods: {
    async loadUsers() {
      const response = await fetch(
        `/api/admin/users?search=${encodeURIComponent(this.search)}`,
      );
      const data = await response.json();
      this.users = data.users;
    },
    async changeStatus(user) {
      try {
        const result = await window.adminPost({
          action: "change_status",
          user_id: user.user_id,
          status: user.status,
        });
        this.message = result.message;
      } catch (error) {
        this.message = error.message;
      }
    },
  },
});
