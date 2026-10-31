window.createAdminApp = function (options) {
  options.template = "#admin-page-template";
  options.components = {
    adminNavigation: {
      props: ["title"],
      template: "#admin-navigation-template",
    },
  };
  const app = Vue.createApp(options);
  app.config.compilerOptions.delimiters = ["[[", "]]"];
  return app.mount("#admin-app");
};

window.adminPost = async function (data) {
  const response = await fetch("/api/admin/actions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  const result = await response.json();
  if (!response.ok) {
    throw new Error(result.message);
  }
  return result;
};
