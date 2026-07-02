/**
 * 前端单元测试 - 工具函数与业务逻辑
 */
import { describe, it, expect } from 'vitest'

// 提取各视图中的工具函数进行独立测试

describe('reasonTagType 映射', () => {
  // 复制自 AccidentList.vue / AccidentDetail.vue 的 tagType 逻辑
  function reasonTagType(reason) {
    const map = {
      '酒驾': 'danger', '闯红灯': 'warning', '超速': '',
      '分心驾驶': 'info', '疲劳驾驶': 'warning', '逆向行驶': 'danger',
      '抢黄灯': 'warning', '信号灯故障': 'info',
    }
    return map[reason] || ''
  }

  it('酒驾应返回 danger', () => {
    expect(reasonTagType('酒驾')).toBe('danger')
  })

  it('闯红灯应返回 warning', () => {
    expect(reasonTagType('闯红灯')).toBe('warning')
  })

  it('超速应返回空字符串', () => {
    expect(reasonTagType('超速')).toBe('')
  })

  it('分心驾驶应返回 info', () => {
    expect(reasonTagType('分心驾驶')).toBe('info')
  })

  it('疲劳驾驶应返回 warning', () => {
    expect(reasonTagType('疲劳驾驶')).toBe('warning')
  })

  it('逆向行驶应返回 danger', () => {
    expect(reasonTagType('逆向行驶')).toBe('danger')
  })

  it('抢黄灯应返回 warning', () => {
    expect(reasonTagType('抢黄灯')).toBe('warning')
  })

  it('信号灯故障应返回 info', () => {
    expect(reasonTagType('信号灯故障')).toBe('info')
  })

  it('其他/未知原因应返回空字符串', () => {
    expect(reasonTagType('其他')).toBe('')
    expect(reasonTagType('未知')).toBe('')
    expect(reasonTagType(undefined)).toBe('')
    expect(reasonTagType(null)).toBe('')
  })
})

describe('parseItems 解析', () => {
  // 复制自 MiningView.vue 的 parseItems 逻辑
  function parseItems(str) {
    if (!str) return []
    return str.split(',').map(s => s.trim())
  }

  it('正常解析逗号分隔字符串', () => {
    expect(parseItems('accident:酒驾, vehicle:小轿车')).toEqual([
      'accident:酒驾', 'vehicle:小轿车'
    ])
  })

  it('单个项目', () => {
    expect(parseItems('period:早高峰')).toEqual(['period:早高峰'])
  })

  it('空字符串返回空数组', () => {
    expect(parseItems('')).toEqual([])
  })

  it('null/undefined 返回空数组', () => {
    expect(parseItems(null)).toEqual([])
    expect(parseItems(undefined)).toEqual([])
  })

  it('三个项目', () => {
    const result = parseItems('accident:闯红灯, vehicle:电动车, period:早高峰')
    expect(result).toHaveLength(3)
    expect(result[0]).toBe('accident:闯红灯')
    expect(result[1]).toBe('vehicle:电动车')
    expect(result[2]).toBe('period:早高峰')
  })
})

describe('统计卡片数据格式化', () => {
  it('日期格式化 - 截取前10位', () => {
    const latestTime = '2024-03-15T08:30:00'
    expect(latestTime.slice(0, 10)).toBe('2024-03-15')
  })

  it('空日期时显示默认值', () => {
    const latestTime = null
    expect(latestTime?.slice(0, 10) || '-').toBe('-')
  })
})

describe('crawlStatus 状态标签映射', () => {
  function statusTagType(status) {
    if (status === 'SUCCESS') return 'success'
    if (status === 'RUNNING') return 'warning'
    return 'danger'
  }

  it('SUCCESS 映射 success', () => {
    expect(statusTagType('SUCCESS')).toBe('success')
  })

  it('RUNNING 映射 warning', () => {
    expect(statusTagType('RUNNING')).toBe('warning')
  })

  it('FAIL 映射 danger', () => {
    expect(statusTagType('FAIL')).toBe('danger')
  })
})

describe('支持度/置信度格式化', () => {
  it('支持度百分比显示', () => {
    expect((0.123 * 100).toFixed(1)).toBe('12.3')
  })

  it('置信度百分比显示', () => {
    expect((0.789 * 100).toFixed(1)).toBe('78.9')
  })

  it('提升度保留两位小数', () => {
    expect((1.567).toFixed(2)).toBe('1.57')
  })
})

describe('筛选参数清理', () => {
  it('清理空值参数', () => {
    const params = { page: 1, size: 20, keyword: '', reason: '酒驾', vehicle_type: '', source: '' }
    Object.keys(params).forEach(k => { if (!params[k]) delete params[k] })
    expect(params).toEqual({ page: 1, size: 20, reason: '酒驾' })
  })

  it('保留有值的参数', () => {
    const params = { page: 1, keyword: '测试', reason: '闯红灯' }
    Object.keys(params).forEach(k => { if (!params[k]) delete params[k] })
    expect(params).toEqual({ page: 1, keyword: '测试', reason: '闯红灯' })
  })
})
