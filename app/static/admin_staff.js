window.createAdminApp({
  data() {
    return { staff: [], search: "", message: "" };
  },
  async mounted() {
    await this.loadStaff();
  },
  methods: {
    async loadStaff() {
      const response = await fetch(
        `/api/admin/staff?search=${encodeURIComponent(this.search)}`,
      );
      const data = await response.json();
      this.staff = data.staff;
    },
    async changeStatus(staffMember) {
      try {
        const result = await window.adminPost({
          action: "change_status",
          user_id: staffMember.user_id,
          status: staffMember.status,
        });
        this.message = result.message;
      } catch (error) {
        this.message = error.message;
      }
    },
  },
});
