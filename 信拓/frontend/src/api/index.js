import request from './request'

// 事故数据
export const getAccidents = (params) => request.get('/accidents', { params })
export const getAccidentDetail = (id) => request.get(`/accidents/${id}`)
export const getFilterOptions = () => request.get('/accidents/filters/options')
export const exportAccidents = (params) => {
  const query = new URLSearchParams()
  Object.entries(params || {}).forEach(([k, v]) => {
    if (v) query.append(k, v)
  })
  const url = `/api/accidents/export?${query.toString()}`
  window.open(url, '_blank')
}

// 统计分析
export const getSummary = () => request.get('/analysis/summary')
export const getHeatmap = () => request.get('/analysis/heatmap')
export const getHourly = () => request.get('/analysis/hourly')
export const getSankey = () => request.get('/analysis/sankey')
export const getWordcloud = () => request.get('/analysis/wordcloud')
export const getReasonPeriodCross = () => request.get('/analysis/reason-period-cross')

// 关联规则
export const runMining = (params) => request.post('/mining/run', params)
export const getRules = (params) => request.get('/mining/rules', { params })
export const getLatestParams = () => request.get('/mining/rules/latest-params')

// 数据管理
export const importData = () => request.post('/data/import')
export const triggerCrawl = () => request.post('/crawl/trigger')
export const getCrawlLogs = (limit = 20) => request.get('/crawl/logs', { params: { limit } })
export const getCrawlStatus = () => request.get('/crawl/status')
