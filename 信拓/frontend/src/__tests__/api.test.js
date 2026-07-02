/**
 * 前端单元测试 - API 模块
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock axios
vi.mock('axios', () => {
  const mockRequest = {
    get: vi.fn(),
    post: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  }
  return {
    default: {
      create: vi.fn(() => mockRequest),
    },
  }
})

// Mock element-plus
vi.mock('element-plus', () => ({
  ElMessage: { error: vi.fn() },
}))

describe('API 模块', () => {
  let request

  beforeEach(async () => {
    vi.resetModules()
    const mod = await import('../api/request.js')
    request = mod.default
  })

  it('request 实例应被正确创建', () => {
    expect(request).toBeDefined()
    expect(request.get).toBeDefined()
    expect(request.post).toBeDefined()
  })
})

describe('API 函数定义', () => {
  it('应导出所有必要的 API 函数', async () => {
    const api = await import('../api/index.js')
    // 事故数据
    expect(api.getAccidents).toBeDefined()
    expect(api.getAccidentDetail).toBeDefined()
    expect(api.getFilterOptions).toBeDefined()
    expect(api.exportAccidents).toBeDefined()

    // 统计分析
    expect(api.getSummary).toBeDefined()
    expect(api.getHeatmap).toBeDefined()
    expect(api.getHourly).toBeDefined()
    expect(api.getSankey).toBeDefined()
    expect(api.getWordcloud).toBeDefined()
    expect(api.getReasonPeriodCross).toBeDefined()

    // 关联规则
    expect(api.runMining).toBeDefined()
    expect(api.getRules).toBeDefined()
    expect(api.getLatestParams).toBeDefined()

    // 数据管理
    expect(api.importData).toBeDefined()
    expect(api.triggerCrawl).toBeDefined()
    expect(api.getCrawlLogs).toBeDefined()
    expect(api.getCrawlStatus).toBeDefined()
  })

  it('exportAccidents 应通过 window.open 打开下载', async () => {
    const api = await import('../api/index.js')
    const mockOpen = vi.fn()
    vi.stubGlobal('open', mockOpen)

    api.exportAccidents({ reason: '酒驾', source: '南京' })
    expect(mockOpen).toHaveBeenCalledTimes(1)

    const url = mockOpen.mock.calls[0][0]
    expect(url).toContain('/api/accidents/export')
    expect(url).toContain('reason=')
    expect(url).toContain('source=')

    vi.unstubAllGlobals()
  })

  it('exportAccidents 空参数时不报错', async () => {
    const api = await import('../api/index.js')
    const mockOpen = vi.fn()
    vi.stubGlobal('open', mockOpen)

    api.exportAccidents({})
    expect(mockOpen).toHaveBeenCalledTimes(1)

    api.exportAccidents(null)
    expect(mockOpen).toHaveBeenCalledTimes(2)

    vi.unstubAllGlobals()
  })
})
