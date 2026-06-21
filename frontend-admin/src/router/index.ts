import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory('/admin/'),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/auth/Login.vue'),
    },
    {
      path: '/',
      component: () => import('@/components/layout/AdminLayout.vue'),
      redirect: '/dashboard',
      children: [
        { path: '/dashboard', name: 'Dashboard', component: () => import('@/views/dashboard/Dashboard.vue') },
        { path: '/departments', name: 'DepartmentMgr', component: () => import('@/views/system/DepartmentMgr.vue') },
        { path: '/roles', name: 'RoleMgr', component: () => import('@/views/system/RoleMgr.vue') },
        { path: '/users', name: 'UserMgr', component: () => import('@/views/system/UserMgr.vue') },
        { path: '/h5-users', name: 'H5UserMgr', component: () => import('@/views/system/H5UserMgr.vue') },
        { path: '/menus', name: 'MenuMgr', component: () => import('@/views/system/MenuMgr.vue') },
        { path: '/ws-control', name: 'WsControl', component: () => import('@/views/system/WsControl.vue') },
      ],
    },
  ],
})

router.beforeEach((to) => {
  if (to.path === '/login') return true
  const token = localStorage.getItem('access_token')
  if (!token) return '/login'
  return true
})

export default router