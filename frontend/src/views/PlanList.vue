<template>
  <AppLayout>
    <h2 style="margin-bottom: 24px">套餐中心</h2>
    <el-row :gutter="16">
      <el-col :span="8" v-for="plan in plans" :key="plan.id">
        <el-card shadow="hover" class="plan-card">
          <h3>{{ plan.name }}</h3>
          <div class="plan-price">¥{{ plan.monthly_price }}<span>/月</span></div>
          <el-divider />
          <p>每月 {{ plan.credits_per_month }} 算粒</p>
          <p v-if="plan.features">可创建 {{ plan.features.avatars }} 个形象</p>
          <p v-if="plan.features">最高 {{ plan.features.resolution }} 分辨率</p>
          <el-button type="primary" style="margin-top: 16px" block>订阅 (即将上线)</el-button>
        </el-card>
      </el-col>
    </el-row>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getPlans } from "../api/plans";
import AppLayout from "../components/AppLayout.vue";

const plans = ref<any[]>([]);

onMounted(async () => {
  const resp = await getPlans();
  plans.value = resp.data.items;
});
</script>

<style scoped>
.plan-card { text-align: center; padding: 16px; }
.plan-price { font-size: 32px; font-weight: bold; color: #409EFF; margin: 12px 0; }
.plan-price span { font-size: 14px; font-weight: normal; color: #999; }
</style>
