<template>
  <AppLayout>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px">
      <h2>视频管理</h2>
      <el-button type="primary" @click="$router.push('/videos/create')">
        <el-icon><Plus /></el-icon> 生成视频
      </el-button>
    </div>
    <el-table :data="videos" v-loading="loading" empty-text="还没有生成视频">
      <el-table-column prop="script_text" label="文案" :show-overflow-tooltip="true">
        <template #default="{ row }">{{ row.script_text.slice(0, 50) }}{{ row.script_text.length > 50 ? '...' : '' }}</template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="cost_credits" label="消耗算粒" width="100" />
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">{{ new Date(row.created_at).toLocaleString() }}</template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" text type="primary" @click="$router.push(`/videos/${row.id}`)">详情</el-button>
          <el-button v-if="row.status === 'done'" size="small" text type="success" @click="download(row)">下载</el-button>
          <el-button size="small" text type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { getVideos, deleteVideo } from "../api/videos";
import AppLayout from "../components/AppLayout.vue";

const videos = ref<any[]>([]);
const loading = ref(false);

function statusType(status: string) {
  const map: Record<string, string> = { done: "success", failed: "danger", processing: "warning", queued: "info", tts_done: "warning" };
  return map[status] || "info";
}
function statusText(status: string) {
  const map: Record<string, string> = { done: "已完成", failed: "失败", processing: "生成中", queued: "排队中", tts_done: "语音完成" };
  return map[status] || status;
}
function download(row: any) {
  if (row.video_url) window.open(row.video_url);
}

async function fetchVideos() {
  loading.value = true;
  try { const resp = await getVideos(); videos.value = resp.data.items; }
  finally { loading.value = false; }
}

async function handleDelete(id: string) {
  try {
    await ElMessageBox.confirm("确定删除该视频吗？", "确认", { type: "warning" });
    await deleteVideo(id);
    ElMessage.success("已删除");
    fetchVideos();
  } catch { /* cancelled */ }
}

onMounted(fetchVideos);
</script>
