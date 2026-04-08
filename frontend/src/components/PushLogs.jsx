import { useState, useEffect } from 'react'
import axios from 'axios'

function PushLogs() {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedLog, setSelectedLog] = useState(null)

  useEffect(() => {
    fetchLogs()
  }, [])

  const fetchLogs = async () => {
    setLoading(true)
    try {
      const response = await axios.get('/api/v1/push/logs')
      setLogs(response.data)
    } catch (error) {
      console.error('푸시 로그 조회 실패:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleLogClick = async (logId) => {
    try {
      const response = await axios.get(`/api/v1/push/logs/${logId}`)
      setSelectedLog(response.data)
    } catch (error) {
      console.error('푸시 로그 상세 조회 실패:', error)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'success':
        return 'bg-green-100 text-green-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      case 'partial':
        return 'bg-orange-100 text-orange-800'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusLabel = (status) => {
    switch (status) {
      case 'success':
        return '성공'
      case 'failed':
        return '실패'
      case 'partial':
        return '부분 성공'
      case 'pending':
        return '대기'
      default:
        return status
    }
  }

  if (loading) {
    return <div className="text-center py-8">로딩 중...</div>
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-800">푸시 발송 로그</h2>
        <button
          onClick={fetchLogs}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          새로고침
        </button>
      </div>

      {logs.length === 0 ? (
        <div className="text-center py-8 text-gray-500">푸시 발송 로그가 없습니다.</div>
      ) : (
        <div className="space-y-4">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    발송일시
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    제목
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    내용
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    성공/실패
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    상태
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    작업
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(log.created_at).toLocaleString('ko-KR')}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                      {log.title}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                      {log.body}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <span className="text-green-600 font-medium">{log.success_count}</span>
                      {' / '}
                      <span className="text-red-600 font-medium">{log.failure_count}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(log.status)}`}>
                        {getStatusLabel(log.status)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <button
                        onClick={() => handleLogClick(log.id)}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        상세보기
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {selectedLog && (
            <div className="mt-6 p-6 bg-gray-50 rounded-lg">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-800">푸시 로그 상세</h3>
                <button
                  onClick={() => setSelectedLog(null)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>
              <div className="space-y-2 text-sm">
                <div><strong>ID:</strong> {selectedLog.id}</div>
                <div><strong>Firebase 프로젝트 ID:</strong> {selectedLog.firebase_project_id}</div>
                <div><strong>제목:</strong> {selectedLog.title}</div>
                <div><strong>내용:</strong>
                  <div className="mt-2 p-3 bg-white rounded border">{selectedLog.body}</div>
                </div>
                {selectedLog.data && (
                  <div><strong>추가 데이터:</strong>
                    <pre className="mt-2 p-3 bg-white rounded border text-xs overflow-x-auto">
                      {JSON.stringify(selectedLog.data, null, 2)}
                    </pre>
                  </div>
                )}
                <div><strong>디바이스 토큰 수:</strong> {Array.isArray(selectedLog.device_tokens) ? selectedLog.device_tokens.length : 0}개</div>
                <div><strong>성공:</strong> <span className="text-green-600 font-medium">{selectedLog.success_count}</span></div>
                <div><strong>실패:</strong> <span className="text-red-600 font-medium">{selectedLog.failure_count}</span></div>
                {selectedLog.failed_tokens && selectedLog.failed_tokens.length > 0 && (
                  <div><strong>실패 토큰:</strong>
                    <ul className="mt-2 space-y-1">
                      {selectedLog.failed_tokens.map((token, index) => (
                        <li key={index} className="font-mono text-xs p-2 bg-red-50 text-red-800 rounded border border-red-200 break-all">
                          {token}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                <div><strong>상태:</strong>{' '}
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(selectedLog.status)}`}>
                    {getStatusLabel(selectedLog.status)}
                  </span>
                </div>
                {selectedLog.error_message && (
                  <div><strong>오류 메시지:</strong>
                    <div className="mt-2 p-3 bg-red-50 text-red-800 rounded border">{selectedLog.error_message}</div>
                  </div>
                )}
                <div><strong>생성 시간:</strong> {new Date(selectedLog.created_at).toLocaleString('ko-KR')}</div>
                {selectedLog.sent_at && (
                  <div><strong>발송 시간:</strong> {new Date(selectedLog.sent_at).toLocaleString('ko-KR')}</div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default PushLogs
