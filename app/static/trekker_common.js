window.createTrekkerApp = function (options) {
  options.template = "#trekker-page-template";
  options.components = {
    trekkerNavigation: {
      props: ["title"],
      template: "#trekker-navigation-template",
    },
  };
  const app = Vue.createApp(options);
  app.config.compilerOptions.delimiters = ["[[", "]]"];
  return app.mount("#trekker-app");
};
