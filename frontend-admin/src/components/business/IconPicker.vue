<template>
  <div class="icon-picker">
    <el-popover :visible="visible" placement="bottom-start" :width="400" trigger="click" @show="handleOpen" @hide="visible = false">
      <template #reference>
        <div class="icon-trigger" @click="visible = !visible">
          <el-icon v-if="modelValue" :size="18"><component :is="modelValue" /></el-icon>
          <span v-else class="placeholder">选择图标</span>
          <el-icon class="arrow"><ArrowDown /></el-icon>
        </div>
      </template>

      <div class="icon-popover">
        <el-input v-model="keyword" placeholder="搜索图标名称..." clearable :prefix-icon="Search" class="search-input" />
        <div class="icon-grid">
          <div
            v-for="icon in filteredIcons"
            :key="icon"
            class="icon-item"
            :class="{ active: modelValue === icon }"
            @click="selectIcon(icon)"
          >
            <el-icon :size="22"><component :is="icon" /></el-icon>
            <span class="icon-name">{{ icon }}</span>
          </div>
        </div>
        <div v-if="filteredIcons.length === 0" class="empty">未找到匹配图标</div>
      </div>
    </el-popover>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ArrowDown, Search } from '@element-plus/icons-vue'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

const props = defineProps<{ modelValue: string }>()
const emit = defineEmits<{ (e: 'update:modelValue', v: string): void }>()

const visible = ref(false)
const keyword = ref('')

// 获取所有图标名称（排除 ElIcon）
const allIcons = Object.keys(ElementPlusIconsVue).filter(k => k !== 'ElIcon')

const filteredIcons = computed(() => {
  if (!keyword.value) return allIcons.slice(0, 80)
  const kw = keyword.value.toLowerCase()
  return allIcons.filter(name => name.toLowerCase().includes(kw)).slice(0, 80)
})

function selectIcon(name: string) {
  emit('update:modelValue', name)
  visible.value = false
}

function handleOpen() {
  keyword.value = ''
}
</script>

<style lang="less" scoped>
.icon-trigger {
  display: flex; align-items: center; gap: 8px;
  border: 1px solid #dcdfe6; border-radius: 6px;
  padding: 8px 12px; cursor: pointer; min-width: 140px;
  transition: border-color 0.2s;
}
.icon-trigger:hover { border-color: #409eff; }
.placeholder { color: #c0c4cc; font-size: 13px; }
.arrow { margin-left: auto; color: #c0c4cc; transition: transform 0.2s; }

.icon-popover { display: flex; flex-direction: column; gap: 10px; }
.search-input { margin-bottom: 4px; }

.icon-grid {
  display: grid; grid-template-columns: repeat(6, 1fr); gap: 6px;
  max-height: 300px; overflow-y: auto; padding: 2px;
}
.icon-item {
  display: flex; flex-direction: column; align-items: center; gap: 2px;
  padding: 8px 4px; border-radius: 6px; cursor: pointer;
  border: 1px solid transparent; transition: all 0.15s;
}
.icon-item:hover { background: #ecf5ff; border-color: #d9ecff; }
.icon-item.active { background: #409eff; color: #fff; border-color: #409eff; }
.icon-name { font-size: 10px; color: #909399; text-align: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 100%; }
.icon-item.active .icon-name { color: #fff; }
.empty { text-align: center; color: #909399; padding: 20px 0; font-size: 13px; }
</style>