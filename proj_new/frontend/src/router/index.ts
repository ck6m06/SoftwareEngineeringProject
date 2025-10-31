import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// 頁面懶加載
const Home = () => import('@/pages/Home.vue')
const Animals = () => import('@/pages/Animals.vue')
const AnimalDetail = () => import('@/pages/AnimalDetail.vue')
const Login = () => import('@/pages/Login.vue')
const Register = () => import('@/pages/Register.vue')
const ForgotPassword = () => import('@/pages/ForgotPassword.vue')
const ResetPassword = () => import('@/pages/ResetPassword.vue')
const EmailVerification = () => import('@/pages/EmailVerification.vue')
const NotificationCenter = () => import('@/pages/NotificationCenter.vue')
const MyApplications = () => import('@/pages/MyApplications.vue')
const MyRehomes = () => import('@/pages/MyRehomes.vue')
const RehomeForm = () => import('@/pages/RehomeForm.vue')
const ShelterBatch = () => import('@/pages/ShelterBatch.vue')
const ShelterAnimals = () => import('@/pages/ShelterAnimals.vue')
const AdminDashboard = () => import('@/pages/AdminDashboard.vue')
const ApplicationReview = () => import('@/pages/ApplicationReview.vue')
const MedicalRecords = () => import('@/pages/MedicalRecords.vue')
const Jobs = () => import('@/pages/Jobs.vue')
const Shelters = () => import('@/pages/Shelters.vue')
const ShelterDetail = () => import('@/pages/ShelterDetail.vue')
const AuditLogs = () => import('@/pages/AuditLogs.vue')
const UserProfile = () => import('@/pages/UserProfile.vue')
const AdminUsers = () => import('@/pages/AdminUsers.vue')

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: '首頁' }
  },
  {
    path: '/animals',
    name: 'Animals',
    component: Animals,
    meta: { title: '動物列表' }
  },
  {
    path: '/animals/:id',
    name: 'AnimalDetail',
    component: AnimalDetail,
    meta: { title: '動物詳情' }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: '登入', guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { title: '註冊', guest: true }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: ForgotPassword,
    meta: { title: '忘記密碼', guest: true }
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: ResetPassword,
    meta: { title: '重置密碼', guest: true }
  },
  {
    path: '/verify-email',
    name: 'EmailVerification',
    component: EmailVerification,
    meta: { title: 'Email 驗證' }
  },
  {
    path: '/notifications',
    name: 'Notifications',
    component: NotificationCenter,
    meta: { title: '通知中心', requiresAuth: true }
  },
  {
    path: '/my/applications',
    name: 'MyApplications',
    component: MyApplications,
    meta: { title: '我的申請', requiresAuth: true }
  },
  {
    path: '/my-rehomes',
    name: 'MyRehomes',
    component: MyRehomes,
    meta: { title: '我的送養', requiresAuth: true }
  },
  {
    path: '/rehome-form',
    name: 'RehomeForm',
    component: RehomeForm,
    meta: { title: '發佈送養', requiresAuth: true }
  },
  {
    path: '/shelter/dashboard',
    name: 'ShelterBatch',
    component: ShelterBatch,
    meta: { title: '批次送養', requiresAuth: true, requiresRole: 'SHELTER_MEMBER' }
  },
  {
    path: '/shelter/animals',
    name: 'ShelterAnimals',
    component: ShelterAnimals,
    meta: { title: '收容所動物管理', requiresAuth: true, requiresRole: 'SHELTER_MEMBER' }
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { title: '管理後台', requiresAuth: true, requiresRole: 'ADMIN' }
  },
  {
    path: '/shelter/applications',
    name: 'ShelterApplications',
    component: ApplicationReview,
    meta: { title: '申請審核', requiresAuth: true, requiresRole: 'SHELTER_MEMBER' }
  },
  {
    path: '/applications',
    name: 'ApplicationReview',
    component: ApplicationReview,
    meta: { title: '審核管理', requiresAuth: true, requiresRole: ['GENERAL_MEMBER', 'SHELTER_MEMBER'] }
  },
  {
    path: '/medical-records',
    name: 'MedicalRecords',
    component: MedicalRecords,
    meta: { title: '醫療記錄', requiresAuth: true, requiresRole: ['ADMIN', 'SHELTER_MEMBER', 'GENERAL_MEMBER'] }
  },
  {
    path: '/jobs',
    name: 'Jobs',
    component: Jobs,
    meta: { title: '任務狀態', requiresAuth: true, requiresRole: 'ADMIN' }
  },
  {
    path: '/shelters',
    name: 'Shelters',
    component: Shelters,
    meta: { title: '收容所列表' }
  },
  {
    path: '/shelters/:id',
    name: 'ShelterDetail',
    component: ShelterDetail,
    meta: { title: '收容所詳情' }
  },
  {
    path: '/audit-logs',
    name: 'AuditLogs',
    component: AuditLogs,
    meta: { title: '審計日誌', requiresAuth: true, requiresRole: 'ADMIN' }
  },
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: AdminUsers,
    meta: { title: '用戶管理', requiresAuth: true, requiresRole: 'ADMIN' }
  },
  {
    path: '/profile',
    name: 'UserProfile',
    component: UserProfile,
    meta: { title: '個人資料', requiresAuth: true }
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守衛
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  
  // 設定頁面標題
  if (to.meta.title) {
    document.title = `${to.meta.title} - 貓狗領養平台`
  }
  
  // 檢查是否需要登入
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }
  
  // 檢查角色權限
  if (to.meta.requiresRole) {
    const requiredRoles = Array.isArray(to.meta.requiresRole) 
      ? to.meta.requiresRole 
      : [to.meta.requiresRole]
    
    if (!authStore.user?.role || !requiredRoles.includes(authStore.user.role)) {
      next({ name: 'Home' })
      return
    }
  }
  
  // 已登入使用者不能訪問登入/註冊頁面
  if (to.meta.guest && authStore.isAuthenticated) {
    next({ name: 'Home' })
    return
  }
  
  next()
})

export default router
