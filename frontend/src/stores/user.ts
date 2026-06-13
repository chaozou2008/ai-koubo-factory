import { defineStore } from "pinia";
import { ref } from "vue";
import client from "../api/client";

export const useUserStore = defineStore("user", () => {
  const user = ref<any>(null);
  const balance = ref(0);
  const isLoggedIn = ref(false);

  async function fetchMe() {
    try {
      const resp = await client.get("/api/auth/me");
      user.value = resp.data;
      balance.value = resp.data.credits_balance;
      isLoggedIn.value = true;
    } catch {
      isLoggedIn.value = false;
    }
  }

  async function fetchBalance() {
    const resp = await client.get("/api/credits/balance");
    balance.value = resp.data.balance;
  }

  function logout() {
    localStorage.removeItem("token");
    user.value = null;
    isLoggedIn.value = false;
  }

  return { user, balance, isLoggedIn, fetchMe, fetchBalance, logout };
});
