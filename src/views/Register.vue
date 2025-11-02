<template>
  <div class="register-container">
    <div class="register-box">
      <div class="register-header">
        <el-icon :size="48" color="#409EFF">
          <UserFilled />
        </el-icon>
        <h1>用户注册</h1>
        <p>User Registration</p>
      </div>

      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="rules"
        class="register-form"
        label-position="top"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码（至少6位）"
            size="large"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            size="large"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item label="注册角色" prop="role">
          <el-select
            v-model="registerForm.role"
            placeholder="请选择注册角色"
            size="large"
            style="width: 100%"
          >
            <el-option label="患者" value="patient" />
            <el-option label="医生" value="doctor" />
          </el-select>
        </el-form-item>

        <!-- 患者额外信息 -->
        <template v-if="registerForm.role === 'patient'">
          <el-form-item label="真实姓名" prop="realName">
            <el-input
              v-model="registerForm.realName"
              placeholder="请输入真实姓名"
              size="large"
            />
          </el-form-item>

          <el-form-item label="身份证号" prop="idCard">
            <el-input
              v-model="registerForm.idCard"
              placeholder="请输入身份证号"
              size="large"
            />
          </el-form-item>

          <el-form-item label="手机号码" prop="phone">
            <el-input
              v-model="registerForm.phone"
              placeholder="请输入手机号码"
              size="large"
            />
          </el-form-item>
        </template>

        <!-- 医生额外信息 -->
        <template v-if="registerForm.role === 'doctor'">
          <el-form-item label="医生姓名" prop="realName">
            <el-input
              v-model="registerForm.realName"
              placeholder="请输入医生姓名"
              size="large"
            />
          </el-form-item>

          <el-form-item label="所属科室" prop="department">
            <el-select
              v-model="registerForm.department"
              placeholder="请选择所属科室"
              size="large"
              style="width: 100%"
            >
              <el-option label="内科" value="内科" />
              <el-option label="外科" value="外科" />
              <el-option label="儿科" value="儿科" />
              <el-option label="妇产科" value="妇产科" />
              <el-option label="骨科" value="骨科" />
              <el-option label="眼科" value="眼科" />
              <el-option label="耳鼻喉科" value="耳鼻喉科" />
              <el-option label="皮肤科" value="皮肤科" />
            </el-select>
          </el-form-item>

          <el-form-item label="职称" prop="title">
            <el-select
              v-model="registerForm.title"
              placeholder="请选择职称"
              size="large"
              style="width: 100%"
            >
              <el-option label="主任医师" value="主任医师" />
              <el-option label="副主任医师" value="副主任医师" />
              <el-option label="主治医师" value="主治医师" />
              <el-option label="住院医师" value="住院医师" />
            </el-select>
          </el-form-item>

          <el-form-item label="执业证号" prop="licenseNumber">
            <el-input
              v-model="registerForm.licenseNumber"
              placeholder="请输入执业证号"
              size="large"
            />
          </el-form-item>
        </template>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            style="width: 100%"
            :loading="loading"
            @click="handleRegister"
          >
            注册
          </el-button>
        </el-form-item>

        <el-form-item>
          <el-button
            size="large"
            style="width: 100%"
            @click="goToLogin"
          >
            返回登录
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, UserFilled } from '@element-plus/icons-vue'
import { authAPI } from '@/api'

const router = useRouter()
const registerFormRef = ref(null)
const loading = ref(false)

const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  role: 'patient',
  realName: '',
  idCard: '',
  phone: '',
  department: '',
  title: '',
  licenseNumber: ''
})

const validatePassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入密码'))
  } else if (value.length < 6) {
    callback(new Error('密码长度至少为6位'))
  } else {
    callback()
  }
}

const validateConfirmPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validateIdCard = (rule, value, callback) => {
  if (registerForm.role === 'patient' && !value) {
    callback(new Error('请输入身份证号'))
  } else if (value && !/^\d{17}[\dXx]$/.test(value)) {
    callback(new Error('请输入正确的身份证号'))
  } else {
    callback()
  }
}

const validatePhone = (rule, value, callback) => {
  if (registerForm.role === 'patient' && !value) {
    callback(new Error('请输入手机号码'))
  } else if (value && !/^1[3-9]\d{9}$/.test(value)) {
    callback(new Error('请输入正确的手机号码'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3到20个字符', trigger: 'blur' }
  ],
  password: [{ validator: validatePassword, trigger: 'blur' }],
  confirmPassword: [{ validator: validateConfirmPassword, trigger: 'blur' }],
  role: [{ required: true, message: '请选择注册角色', trigger: 'change' }],
  realName: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  idCard: [{ validator: validateIdCard, trigger: 'blur' }],
  phone: [{ validator: validatePhone, trigger: 'blur' }],
  department: [{ required: true, message: '请选择所属科室', trigger: 'change' }],
  title: [{ required: true, message: '请选择职称', trigger: 'change' }],
  licenseNumber: [{ required: true, message: '请输入执业证号', trigger: 'blur' }]
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      
      try {
        // 构建注册数据
        const registerData = {
          username: registerForm.username,
          password: registerForm.password,
          role: registerForm.role,
          name: registerForm.realName,
        }
        
        // 根据角色添加额外字段
        if (registerForm.role === 'patient') {
          registerData.idCard = registerForm.idCard
          registerData.phone = registerForm.phone
        } else if (registerForm.role === 'doctor') {
          registerData.department = registerForm.department
          registerData.title = registerForm.title
          registerData.licenseNumber = registerForm.licenseNumber
        }
        
        const res = await authAPI.register(registerData)
        
        if (res.code === 200) {
          ElMessage.success('注册成功，请登录')
          router.push('/login')
        } else {
          ElMessage.error(res.message || '注册失败')
        }
      } catch (error) {
        ElMessage.error(error.message || '注册失败，请重试')
      } finally {
        loading.value = false
      }
    }
  })
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.register-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px 0;
}

.register-box {
  width: 480px;
  max-width: 90%;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  margin: 20px 0;
}

.register-header {
  text-align: center;
  margin-bottom: 32px;
}

.register-header h1 {
  font-size: 24px;
  color: #303133;
  margin: 16px 0 8px;
}

.register-header p {
  font-size: 14px;
  color: #909399;
}

.register-form {
  margin-top: 24px;
}

.register-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}
</style>
