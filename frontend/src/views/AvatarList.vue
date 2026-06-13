<template>
  <AppLayout>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px">
      <h2>我的形象</h2>
      <el-button type="primary" @click="$router.push('/avatars/create')">创建形象</el-button>
    </div>
    <el-table :data="avatars" v-loading="loading" empty-text="还没有数字人形象，点击右上角创建">
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="status" label="状态">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'warning'">
            {{ row.status === 'active' ? '已就绪' : row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间">
        <template #default="{ row }">{{ new Date(row.created_at).toLocaleDateString() }}</template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button size="small" text type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { getAvatars, deleteAvatar } from "../api/avatars";
import AppLayout from "../components/AppLayout.vue";

const avatars = ref<any[]>([]);
const loading = ref(false);

async function fetchAvatars() {
  loading.value = true;
  try {
    const resp = await getAvatars();
    avatars.value = resp.data.items;
  } finally {
    loading.value = false;
  }
}

async function handleDelete(id: string) {
  try {
    await ElMessageBox.confirm("确定删除该形象吗？", "确认", { type: "warning" });
    await deleteAvatar(id);
    ElMessage.success("已删除");
    fetchAvatars();
  } catch {
    // cancelled
  }
}

onMounted(fetchAvatars);
</script>
