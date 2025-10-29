<template>
  <div class="lesson-detail" v-loading="loading">
    <el-card v-if="lesson">
      <template #header>
        <div class="lesson-header">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/courses' }">课程</el-breadcrumb-item>
            <el-breadcrumb-item :to="{ path: `/courses/${lesson.course_slug}` }">
              {{ lesson.course_title }}
            </el-breadcrumb-item>
            <el-breadcrumb-item>{{ lesson.title }}</el-breadcrumb-item>
          </el-breadcrumb>
          <h1>Day{{ lesson.day_number.toString().padStart(2, '0') }} - {{ lesson.title }}</h1>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="18">
          <div class="search-bar">
            <el-input
              v-model="searchTerm"
              placeholder="搜索课文内容或课程资源"
              clearable
              @clear="onSearchCleared"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
          <div class="lesson-content">
            <MarkdownViewer :content="lesson.content" />
          </div>

          <div class="lesson-resources" v-if="lesson.resources && lesson.resources.length > 0">
            <h3>课程资源</h3>
            <el-table v-if="filteredResources.length" :data="filteredResources">
              <el-table-column prop="title" label="资源名称" />
              <el-table-column prop="file_type" label="类型" width="100" />
              <el-table-column label="操作" width="120">
                <template #default="{ row }">
                  <el-button type="primary" size="small" @click="downloadResource(row)">
                    下载
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-empty v-else description="没有匹配的资源" />
          </div>

          <div class="search-results" v-if="searchTerm">
            <h3>搜索结果</h3>
            <el-empty v-if="!matchingSnippets.length" description="未找到匹配内容" />
            <el-timeline v-else>
              <el-timeline-item
                v-for="item in matchingSnippets"
                :key="item.line"
                :timestamp="'第 ' + item.line + ' 行'"
              >
                <p class="snippet" v-html="highlightSnippet(item.snippet)"></p>
              </el-timeline-item>
            </el-timeline>
          </div>

          <div class="github-link" v-if="githubLink">
            <el-divider />
            <el-button type="success" plain @click="openGithubLink" style="width: 100%">
              <el-icon><Link /></el-icon>
              GitHub 原文
            </el-button>
          </div>
        </el-col>

        <el-col :span="6" class="info-column">
          <el-card class="sidebar-card floating-card">
            <h3>学习信息</h3>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="预计时长">
                {{ lesson.estimated_time }}分钟
              </el-descriptions-item>
              <el-descriptions-item label="浏览次数">
                {{ lesson.view_count }}
              </el-descriptions-item>
              <el-descriptions-item label="点赞数">
                {{ lesson.like_count }}
              </el-descriptions-item>
            </el-descriptions>

            <div class="actions" style="margin-top: 20px">
              <el-button type="primary" @click="markAsCompleted" style="width: 100%">
                标记为已完成
              </el-button>
              <el-button @click="handleLike" style="width: 100%; margin-top: 10px">
                <el-icon><Star /></el-icon> 点赞
              </el-button>
            </div>

            <div class="code-link" v-if="lesson.code_url" style="margin-top: 20px">
              <el-button type="success" @click="openCodeUrl" style="width: 100%">
                <el-icon><Link /></el-icon> 查看代码
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { courseApi, progressApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Star, Link, Search } from '@element-plus/icons-vue'
import MarkdownViewer from '@/components/MarkdownViewer.vue'

const route = useRoute()
const lesson = ref(null)
const loading = ref(false)
const searchTerm = ref('')

const loadLesson = async () => {
  loading.value = true
  try {
    lesson.value = await courseApi.getLessonDetail(route.params.slug)
  } catch (error) {
    ElMessage.error('加载课程失败')
  } finally {
    loading.value = false
  }
}

const markAsCompleted = async () => {
  try {
    await progressApi.updateProgress(lesson.value.id, { status: 'completed' })
    ElMessage.success('已标记为完成')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleLike = async () => {
  try {
    await courseApi.likeLesson(route.params.slug)
    ElMessage.success('点赞成功')
    lesson.value.like_count++
  } catch (error) {
    ElMessage.error('点赞失败')
  }
}

const downloadResource = (resource) => {
  window.open(resource.file, '_blank')
}

const openCodeUrl = () => {
  window.open(lesson.value.code_url, '_blank')
}

const filteredResources = computed(() => {
  if (!lesson.value?.resources) {
    return []
  }

  const keyword = searchTerm.value.trim().toLowerCase()
  if (!keyword) {
    return lesson.value.resources
  }

  return lesson.value.resources.filter((resource) => {
    const title = resource.title?.toLowerCase() || ''
    const type = resource.file_type?.toLowerCase() || ''
    return title.includes(keyword) || type.includes(keyword)
  })
})

const matchingSnippets = computed(() => {
  const keyword = searchTerm.value.trim().toLowerCase()
  if (!keyword || !lesson.value?.content) {
    return []
  }

  const lines = lesson.value.content.split('\n')
  const results = []

  lines.forEach((line, index) => {
    const plain = line.trim()
    if (!plain) {
      return
    }
    const lower = plain.toLowerCase()
    const position = lower.indexOf(keyword)
    if (position !== -1) {
      const start = Math.max(0, position - 40)
      const end = Math.min(plain.length, position + keyword.length + 40)
      const snippet = plain.slice(start, end)
      results.push({
        line: index + 1,
        snippet: `${start > 0 ? '…' : ''}${snippet}${end < plain.length ? '…' : ''}`,
      })
    }
  })

  return results.slice(0, 6)
})

const escapeRegExp = (value) => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

const highlightSnippet = (snippet) => {
  const keyword = searchTerm.value.trim()
  if (!keyword) {
    return snippet
  }
  const pattern = new RegExp(escapeRegExp(keyword), 'gi')
  return snippet.replace(pattern, (match) => `<mark>${match}</mark>`)
}

const onSearchCleared = () => {
  searchTerm.value = ''
}

const githubLink = computed(() => {
  if (!lesson.value) {
    return ''
  }

  const courseTitle = lesson.value.course_title || ''
  const courseSlug = lesson.value.course_slug || ''
  const courseMatch = courseTitle.match(/Day\d{2}-\d{2}/)
  let courseSegment = courseMatch ? courseMatch[0] : ''

  if (!courseSegment && courseSlug) {
    const slugMatch = courseSlug.match(/day\d{2}-\d{2}/i)
    if (slugMatch) {
      courseSegment = slugMatch[0].replace(/^./, (char) => char.toUpperCase())
    }
  }

  if (!courseSegment) {
    return ''
  }

  const title = (lesson.value.title || '').trim()
  if (!title) {
    return ''
  }

  const fileName = `${String(lesson.value.day_number).padStart(2, '0')}.${title.replace(/[\\/]/g, '-')}.md`
  const encodePath = (value) => encodeURIComponent(value).replace(/%2F/g, '/')
  const baseUrl = 'https://github.com/marvel1203/Python-100-Days/blob/master'
  return `${baseUrl}/${encodePath(courseSegment)}/${encodePath(fileName)}`
})

const openGithubLink = () => {
  if (githubLink.value) {
    window.open(githubLink.value, '_blank')
  }
}

onMounted(() => {
  loadLesson()
})
</script>

<style scoped>
.lesson-header h1 {
  margin: 15px 0;
}

.lesson-content {
  padding: 20px 0;
}

.lesson-resources {
  margin-top: 30px;
}

.search-bar {
  margin-bottom: 20px;
}

.search-results {
  margin-top: 30px;
}

.snippet {
  margin: 0;
  line-height: 1.6;
  color: #334155;
}

.github-link {
  margin-top: 32px;
}

mark {
  background-color: #fde68a;
  padding: 0 2px;
  border-radius: 2px;
}

.sidebar-card h3 {
  margin-top: 0;
}
</style>

<style scoped>
.info-column {
  position: sticky;
  top: 110px;
  align-self: flex-start;
}

.floating-card {
  border: none;
  border-radius: 20px;
  box-shadow: 0 20px 45px rgba(15, 23, 42, 0.12);
  background: linear-gradient(160deg, rgba(255, 255, 255, 0.96), rgba(248, 250, 252, 0.92));
  backdrop-filter: blur(14px);
  position: relative;
  overflow: hidden;
}

.floating-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 110% -10%, rgba(56, 189, 248, 0.18), transparent 55%);
  pointer-events: none;
}

.floating-card h3 {
  margin-top: 0;
}

@media screen and (max-width: 1200px) {
  .info-column {
    position: static;
    margin-top: 24px;
  }
}

@media screen and (max-width: 992px) {
  .floating-card {
    box-shadow: none;
    backdrop-filter: none;
  }
}
</style>
