const loginApp = Vue.createApp({
  template: "#login-template",
  data() {
    return { email: "", password: "", message: "" };
  },
  methods: {
    async login() {
      const response = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: this.email, password: this.password }),
      });
      const result = await response.json();
      if (response.ok) {
        window.location.href = result.redirect;
      } else {
        this.message = result.message;
      }
    },
  },
});

loginApp.mount("#login-app");
