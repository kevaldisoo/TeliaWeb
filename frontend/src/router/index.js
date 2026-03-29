import { createRouter, createWebHistory } from 'vue-router'
import ProjectAssignmentView from '../views/ProjectAssignmentView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'project-assignment',
      component: ProjectAssignmentView,
    },
  ],
})

export default router
