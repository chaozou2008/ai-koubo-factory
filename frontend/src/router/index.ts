import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/login",
      name: "Login",
      component: () => import("../views/Login.vue"),
      meta: { guest: true },
    },
    {
      path: "/register",
      name: "Register",
      component: () => import("../views/Register.vue"),
      meta: { guest: true },
    },
    {
      path: "/",
      redirect: "/videos/create",
    },
    {
      path: "/avatars",
      name: "AvatarList",
      component: () => import("../views/AvatarList.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/avatars/create",
      name: "AvatarCreate",
      component: () => import("../views/AvatarCreate.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/videos/create",
      name: "VideoCreate",
      component: () => import("../views/VideoCreate.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/videos",
      name: "VideoList",
      component: () => import("../views/VideoList.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/videos/:id",
      name: "VideoDetail",
      component: () => import("../views/VideoDetail.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/plans",
      name: "PlanList",
      component: () => import("../views/PlanList.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/credits",
      name: "CreditLog",
      component: () => import("../views/CreditLog.vue"),
      meta: { requiresAuth: true },
    },
  ],
});

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem("token");
  if (to.meta.requiresAuth && !token) {
    next("/login");
  } else if (to.meta.guest && token) {
    next("/");
  } else {
    next();
  }
});

export default router;
