const registerApp = Vue.createApp({
  template: "#register-template",
  data() {
    return { name: "", email: "", password: "", message: "" };
  },
  methods: {
    async register() {
      const response = await fetch("/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: this.name,
          email: this.email,
          password: this.password,
        }),
      });
      const result = await response.json();
      this.message = result.message;
      if (response.ok) {
        this.name = "";
        this.email = "";
        this.password = "";
      }
    },
  },
});

registerApp.mount("#register-app");
