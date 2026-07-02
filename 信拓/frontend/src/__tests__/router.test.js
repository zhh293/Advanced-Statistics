/**
 * 前端单元测试 - 路由配置
 */
import { describe, it, expect } from 'vitest'
import router from '../router/index.js'

describe('路由配置', () => {
  it('应包含所有必要路由', () => {
    const routes = router.getRoutes()
    const routeNames = routes.map(r => r.name)

    expect(routeNames).toContain('Dashboard')
    expect(routeNames).toContain('AccidentList')
    expect(routeNames).toContain('AccidentDetail')
    expect(routeNames).toContain('HeatmapView')
    expect(routeNames).toContain('SankeyView')
    expect(routeNames).toContain('MiningView')
    expect(routeNames).toContain('CrawlManage')
  })

  it('Dashboard 路由路径应为 /', () => {
    const route = router.getRoutes().find(r => r.name === 'Dashboard')
    expect(route.path).toBe('/')
  })

  it('AccidentList 路由路径应为 /accidents', () => {
    const route = router.getRoutes().find(r => r.name === 'AccidentList')
    expect(route.path).toBe('/accidents')
  })

  it('AccidentDetail 路由应包含动态参数 :id', () => {
    const route = router.getRoutes().find(r => r.name === 'AccidentDetail')
    expect(route.path).toBe('/accidents/:id')
  })

  it('共有 7 个路由', () => {
    const routes = router.getRoutes()
    expect(routes.length).toBe(7)
  })

  it('所有路由组件应使用懒加载', () => {
    const routes = router.options.routes
    routes.forEach(route => {
      // 懒加载的组件是一个函数
      expect(typeof route.component).toBe('function')
    })
  })
})
