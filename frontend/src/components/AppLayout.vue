<template>
  <el-container class="app-layout">
    <el-header class="app-header">
      <div class="header-left">
        <h2 @click="$router.push('/')" style="cursor: pointer">AI口播工厂</h2>
      </div>
      <div class="header-right">
        <CreditBadge />
        <el-dropdown trigger="click">
          <el-button type="text" style="color: #333">
            {{ userStore.user?.phone }} <el-icon><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="$router.push('/credits')">算粒明细</el-dropdown-item>
              <el-dropdown-item @click="$router.push('/plans')">升级套餐</el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    <el-container>
      <el-aside width="200px" class="app-aside">
        <el-menu router :default-active="$route.path" background-color="#fafafa">
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <span>工作台</span>
          </el-menu-item>
          <el-menu-item index="/avatars">
            <el-icon><UserFilled /></el-icon>
            <span>我的形象</span>
          </el-menu-item>
          <el-menu-item index="/videos">
            <el-icon><VideoCamera /></el-icon>
            <span>视频管理</span>
          </el-menu-item>
          <el-menu-item index="/plans">
            <el-icon><Goods /></el-icon>
            <span>套餐中心</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main class="app-main">
        <slot />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "../stores/user";
import CreditBadge from "./CreditBadge.vue";

const router = useRouter();
const userStore = useUserStore();

onMounted(() => userStore.fetchMe());

function handleLogout() {
  userStore.logout();
  router.push("/login");
}
</script>

<style scoped>
.app-layout { height: 100vh; }
.app-header { display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #e5e5e5; }
.header-right { display: flex; align-items: center; gap: 16px; }
.app-aside { border-right: 1px solid #e5e5e5; padding-top: 16px; }
.app-main { background: #f5f5f5; padding: 24px; }
</style>
