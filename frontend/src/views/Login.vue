<template>
  <div class="auth-container">
    <el-card class="auth-card" shadow="always">
      <h1 style="text-align: center; margin-bottom: 24px">AI口播工厂</h1>
      <el-form :model="form" label-position="top">
        <el-form-item label="手机号">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-button type="primary" :loading="loading" block @click="handleLogin">登录</el-button>
      </el-form>
      <p style="text-align: center; margin-top: 16px">
        还没有账号？<el-link type="primary" @click="$router.push('/register')">立即注册</el-link>
      </p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { login } from "../api/auth";
import { useUserStore } from "../stores/user";

const router = useRouter();
const userStore = useUserStore();
const loading = ref(false);
const form = ref({ phone: "", password: "" });

async function handleLogin() {
  loading.value = true;
  try {
    const resp = await login(form.value.phone, form.value.password);
    localStorage.setItem("token", resp.data.access_token);
    await userStore.fetchMe();
    ElMessage.success("登录成功");
    router.push("/");
  } catch {
    // interceptor handles error message
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.auth-container { display: flex; justify-content: center; align-items: center; height: 100vh; background: #f0f2f5; }
.auth-card { width: 400px; }
</style>
