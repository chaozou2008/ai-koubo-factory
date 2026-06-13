<template>
  <el-tag type="warning" @click="$router.push('/credits')" style="cursor: pointer">
    算粒: {{ userStore.balance }}
  </el-tag>
</template>

<script setup lang="ts">
import { useUserStore } from "../stores/user";
const userStore = useUserStore();
</script>
