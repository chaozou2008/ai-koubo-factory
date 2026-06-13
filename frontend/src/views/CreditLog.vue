<template>
  <AppLayout>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px">
      <h2>算粒明细</h2>
      <el-tag type="warning" size="large">当前余额: {{ userStore.balance }}</el-tag>
    </div>
    <el-table :data="logs" v-loading="loading" empty-text="暂无记录">
      <el-table-column prop="type" label="类型" width="100">
        <template #default="{ row }">
          <el-tag :type="row.type === 'charge' ? 'success' : row.type === 'refund' ? 'info' : 'warning'">
            {{ row.type === 'charge' ? '充值' : row.type === 'refund' ? '退款' : '消耗' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="amount" label="数量" width="120">
        <template #default="{ row }">
          <span :style="{ color: row.amount > 0 ? '#67C23A' : '#F56C6C' }">
            {{ row.amount > 0 ? '+' : '' }}{{ row.amount }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="balance" label="余额" width="100" />
      <el-table-column prop="source" label="来源" />
      <el-table-column prop="created_at" label="时间" width="180">
        <template #default="{ row }">{{ new Date(row.created_at).toLocaleString() }}</template>
      </el-table-column>
    </el-table>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getCreditLog } from "../api/credits";
import { useUserStore } from "../stores/user";
import AppLayout from "../components/AppLayout.vue";

const userStore = useUserStore();
const logs = ref<any[]>([]);
const loading = ref(false);

onMounted(async () => {
  loading.value = true;
  try {
    const resp = await getCreditLog();
    logs.value = resp.data.items;
    await userStore.fetchBalance();
  } finally { loading.value = false; }
});
</script>
