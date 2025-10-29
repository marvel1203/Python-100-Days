<template>
  <div class="user-management">
    <el-card>
      <template #header>
        <div class="header">
          <div class="header-title">
            <h2>用户管理</h2>
            <p class="subtitle">集中管理账号，同时快速跳转到智能助教配置中心。</p>
          </div>
          <div class="header-actions">
            <el-button type="info" plain @click="goAISettings">
              <el-icon><ChatDotRound /></el-icon>
              AI 助手配置
            </el-button>
            <el-button type="primary" @click="showCreateDialog">
              <el-icon><Plus /></el-icon>
              创建用户
            </el-button>
          </div>
        </div>
      </template>

      <el-form :inline="true" class="search-form">
        <el-form-item label="搜索">
          <el-input
            v-model="searchQuery"
            placeholder="输入用户名或邮箱搜索"
            clearable
            @clear="fetchUsers"
            @keyup.enter="fetchUsers"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchUsers">搜索</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="users" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="权限" width="150">
          <template #default="{ row }">
            <el-tag v-if="row.is_superuser" type="danger">超级管理员</el-tag>
            <el-tag v-else-if="row.is_staff" type="warning">管理员</el-tag>
            <el-tag v-else type="info">普通用户</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="date_joined" label="注册时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.date_joined) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="editUser(row)">编辑</el-button>
            <el-button
              size="small"
              :type="row.is_active ? 'warning' : 'success'"
              @click="toggleUserStatus(row)"
            >
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
            <el-button
              size="small"
              type="danger"
              @click="deleteUser(row)"
              :disabled="row.is_superuser"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-if="total > 0"
        class="pagination"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @current-change="fetchUsers"
        @size-change="fetchUsers"
      />
    </el-card>

    <!-- 创建/编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '创建用户' : '编辑用户'"
      width="500px"
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userFormRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" :disabled="dialogMode === 'edit'" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="dialogMode === 'create'">
          <el-input v-model="userForm.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="姓" prop="first_name">
          <el-input v-model="userForm.first_name" />
        </el-form-item>
        <el-form-item label="名" prop="last_name">
          <el-input v-model="userForm.last_name" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="userForm.is_active" />
        </el-form-item>
        <el-form-item label="管理员">
          <el-switch v-model="userForm.is_staff" />
        </el-form-item>
        <el-form-item label="超级管理员">
          <el-switch v-model="userForm.is_superuser" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitUserForm" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, ChatDotRound } from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()
const loading = ref(false)
const users = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchQuery = ref('')

const dialogVisible = ref(false)
const dialogMode = ref('create')
const submitting = ref(false)
const userFormRef = ref()

const userForm = reactive({
  username: '',
  email: '',
  password: '',
  first_name: '',
  last_name: '',
  is_active: true,
  is_staff: false,
  is_superuser: false
})

const userFormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ]
}

const fetchUsers = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    
    const response = await axios.get('/api/users/manage/', { params })
    users.value = response.data.results
    total.value = response.data.count
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const showCreateDialog = () => {
  dialogMode.value = 'create'
  resetUserForm()
  dialogVisible.value = true
}

const editUser = (user) => {
  dialogMode.value = 'edit'
  Object.assign(userForm, {
    id: user.id,
    username: user.username,
    email: user.email,
    first_name: user.first_name || '',
    last_name: user.last_name || '',
    is_active: user.is_active,
    is_staff: user.is_staff,
    is_superuser: user.is_superuser,
    password: ''
  })
  dialogVisible.value = true
}

const resetUserForm = () => {
  Object.assign(userForm, {
    username: '',
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    is_active: true,
    is_staff: false,
    is_superuser: false
  })
  userFormRef.value?.resetFields()
}

const submitUserForm = async () => {
  if (!userFormRef.value) return
  
  await userFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (dialogMode.value === 'create') {
        await axios.post('/api/users/manage/', userForm)
        ElMessage.success('创建用户成功')
      } else {
        const { password: _password, ...updateData } = userForm
        await axios.put(`/api/users/manage/${userForm.id}/`, updateData)
        ElMessage.success('更新用户成功')
      }
      dialogVisible.value = false
      fetchUsers()
    } catch (error) {
      const message = error.response?.data?.username?.[0] 
        || error.response?.data?.email?.[0]
        || error.response?.data?.detail 
        || '操作失败'
      ElMessage.error(message)
    } finally {
      submitting.value = false
    }
  })
}

const toggleUserStatus = async (user) => {
  try {
    await axios.post(`/api/users/manage/${user.id}/toggle_active/`)
    ElMessage.success(`已${user.is_active ? '禁用' : '启用'}用户`)
    fetchUsers()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const deleteUser = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.username}" 吗？此操作不可恢复。`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await axios.delete(`/api/users/manage/${user.id}/`)
    ElMessage.success('删除用户成功')
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const goAISettings = () => {
  router.push('/settings/ai')
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.user-management {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
}

.header h2 {
  margin: 0;
}

.header-title {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.subtitle {
  margin: 0;
  font-size: 13px;
  color: rgba(100, 116, 139, 0.85);
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
