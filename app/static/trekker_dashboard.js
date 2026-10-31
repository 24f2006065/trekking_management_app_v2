Vue.createApp({
  template: "#trekker-template",
  data() {
    return { userName: "" };
  },
  async mounted() {
    const response = await fetch("/api/current-user");
    const result = await response.json();
    this.userName = result.name;
  },
}).mount("#trekker-app");
