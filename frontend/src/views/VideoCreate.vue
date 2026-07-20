<template>
  <AppLayout>
    <h2 style="margin-bottom: 24px">生成视频</h2>
    <div style="display:flex;gap:24px;align-items:flex-start">
      <!-- 左侧品类 -->
      <div style="width:200px;flex-shrink:0">
        <el-card shadow="hover">
          <template #header><b>选择品类</b></template>
          <div v-for="(group, idx) in categoryList" :key="idx">
            <div style="font-weight:bold;font-size:13px;color:#666;padding:8px 12px 4px">{{ group.label }}</div>
            <div
              v-for="t in group.templates"
              :key="t.id"
              :class="['cat-item', { active: form.template_id === t.id }]"
              @click="selectTemplate(t)"
            >
              <span>{{ t.name }}</span>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 右侧内容 -->
      <div style="flex:1;min-width:0">
        <el-card v-if="!form.category" shadow="hover">
          <el-empty description="请从左侧选择一个品类" />
        </el-card>

        <el-card v-else shadow="hover">
          <el-form label-position="top">
            <!-- 形象选择（所有品类都可选，非强制） -->
            <el-form-item label="数字人形象（可选，不上传则AI自动生成）">
              <div style="display:flex;gap:12px;flex-wrap:wrap">
                <div v-for="a in avatars" :key="a.id"
                  :class="['avatar-tile', { sel: form.avatar_id===a.id }]"
                  @click="form.avatar_id = a.id">
                  <img v-if="a.photo_urls?.front" :src="a.photo_urls.front"
                    style="width:80px;height:80px;border-radius:8px;object-fit:cover" />
                  <el-icon v-else :size="48" color="#999"><UserFilled /></el-icon>
                  <div style="font-weight:bold;margin:6px 0 2px">{{ a.name }}</div>
                  <el-tag size="small" :type="a.status==='active'?'success':'warning'">
                    {{ a.status==='active'?'就绪':a.status }}
                  </el-tag>
                </div>
                <div class="avatar-tile add" @click="$router.push('/avatars/create')">
                  <el-icon :size="28"><Plus /></el-icon>
                  <div style="margin-top:4px">新建形象</div>
                </div>
              </div>
            </el-form-item>

            <!-- 店铺照片 + 参考视频 -->
            <el-form-item label="店铺素材（可选）">
              <div style="display:flex;gap:12px">
                <el-upload :auto-upload="false" :limit="1" :on-change="(f:any)=>uploadSceneFile(f,'photo')"
                  :file-list="scenePhotoFiles" list-type="picture" accept="image/*">
                  <el-button><el-icon><Upload /></el-icon> 店铺照片</el-button>
                </el-upload>
                <el-input v-model="form.scene_image_url" placeholder="或手动填入照片URL" style="width:200px" />
              </div>
              <div style="margin-top:8px;display:flex;gap:12px">
                <el-upload :auto-upload="false" :limit="1" :on-change="(f:any)=>uploadSceneFile(f,'video')"
                  :file-list="sceneVideoFiles" accept="video/*">
                  <el-button><el-icon><VideoCamera /></el-icon> 店铺视频</el-button>
                </el-upload>
                <el-input v-model="form.reference_video_url" placeholder="或手动填入视频URL" style="width:200px" />
              </div>
            </el-form-item>

            <!-- 场景提示词 -->
            <el-form-item label="场景提示词">
              <el-input v-model="form.prompt" type="textarea" :rows="5"
                :placeholder="selectedTemplate?.config?.seedance_prompt || '描述视频场景...'" />
            </el-form-item>

            <!-- 时长（长视频模式下隐藏，自动用10s/段） -->
            <el-form-item v-if="!form.longVideo" label="视频时长">
              <el-slider v-model="form.duration" :min="4" :max="15" :step="1" show-input style="max-width:300px" />
            </el-form-item>

            <!-- AI 引擎选择 -->
            <el-form-item label="AI 引擎">
              <el-radio-group v-model="form.provider">
                <el-radio value="hailuo">海螺AI（MiniMax · 便宜）</el-radio>
                <el-radio value="seedance-mini">Seedance 2.0 Mini（火山引擎 · 高性价比）</el-radio>
                <el-radio value="seedance">Seedance 2.0（火山引擎 · 高质量）</el-radio>
              </el-radio-group>
            </el-form-item>

            <!-- 长视频模式（仅海螺） -->
            <el-form-item v-if="form.provider === 'hailuo'" label="视频模式">
              <el-radio-group v-model="form.longVideo">
                <el-radio :value="false">普通模式（6-10秒 · 10算粒）</el-radio>
                <el-radio :value="true">长视频模式（~30秒 · 3段拼接 · 30算粒）</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-alert :title="form.longVideo ? '长视频消耗 30 算粒（3段 × 10）' : '每条视频消耗 10 算粒'" type="warning" :closable="false" style="margin-bottom:16px" />
            <el-button type="primary" :loading="loading" size="large" @click="handleCreate">生成视频</el-button>
          </el-form>
        </el-card>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { getAvatars, uploadPhoto } from "../api/avatars";
import { getTemplates } from "../api/templates";
import { createVideo } from "../api/videos";
import { useUserStore } from "../stores/user";
import AppLayout from "../components/AppLayout.vue";

const router = useRouter();
const userStore = useUserStore();
const loading = ref(false);
const avatars = ref<any[]>([]);
const templates = ref<any[]>([]);
const form = ref({ avatar_id:"", template_id:"", script_text:"", prompt:"", scene_image_url:"", reference_video_url:"", duration:5, category:"", provider:"hailuo", longVideo:false });
const selectedTemplate = ref<any>(null);
const scenePhotoFiles = ref<any[]>([]);
const sceneVideoFiles = ref<any[]>([]);

async function uploadSceneFile(file: any, type: string) {
  try {
    const url = await uploadPhoto(file.raw);
    if (type === 'photo') form.value.scene_image_url = url;
    else form.value.reference_video_url = url;
    ElMessage.success('上传成功！');
  } catch { ElMessage.error('上传失败'); }
}
const categoryList = computed(() => {
  const m: Record<string,any> = {};
  for (const t of templates.value) {
    if (!m[t.industry]) m[t.industry] = { industry:t.industry, label:t.industry, templates:[] };
    m[t.industry].templates.push(t);
  }
  return Object.values(m);
});

function selectTemplate(t: any) {
  form.value.category = t.industry;
  form.value.template_id = t.id;
  selectedTemplate.value = t;
  form.value.prompt = t.config?.seedance_prompt || '';
  form.value.avatar_id = "";
}

onMounted(async () => {
  const [a, t] = await Promise.all([getAvatars(), getTemplates()]);
  avatars.value = a.data.items;
  templates.value = t.data.items;
});

async function handleCreate() {
  loading.value = true;
  try {
    const r = await createVideo(form.value.avatar_id, form.value.template_id, form.value.script_text,
      form.value.prompt, form.value.reference_video_url, form.value.duration, form.value.scene_image_url, form.value.provider, form.value.longVideo);
    await userStore.fetchBalance();
    ElMessage.success("已提交！");
    router.push(`/videos/${r.data.id}`);
  } catch {} finally { loading.value = false; }
}

// 切换到非海螺引擎时关闭长视频模式
watch(() => form.value.provider, (v) => {
  if (v !== 'hailuo') form.value.longVideo = false;
});
</script>

<style scoped>
.cat-item {
  padding: 10px 12px; border-radius: 6px; cursor: pointer;
  display: flex; align-items: center; gap: 8px; margin-bottom: 4px;
}
.cat-item:hover { background: #f0f5ff; }
.cat-item.active { background: #409EFF; color: #fff; }
.avatar-tile {
  width: 130px; text-align: center; padding: 16px 8px;
  border: 2px solid #eee; border-radius: 12px; cursor: pointer;
}
.avatar-tile:hover { border-color: #409EFF; background: #f0f5ff; }
.avatar-tile.sel { border-color: #409EFF; background: #ecf5ff; }
.avatar-tile.add { border-style: dashed; color: #999; min-height: 120px;
  display: flex; flex-direction: column; align-items: center; justify-content: center; }
</style>