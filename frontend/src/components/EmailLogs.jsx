import { useState, useEffect } from 'react'
import axios from 'axios'

function EmailLogs() {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedLog, setSelectedLog] = useState(null)

  useEffect(() => {
    fetchLogs()
  }, [])

  const fetchLogs = async () => {
    try {
      const response = await axios.get('/api/v1/email/logs')
      setLogs(response.data)
    } catch (error) {
      console.error('로그 조회 실패:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleLogClick = async (logId) => {
    try {
      const response = await axios.get(`/api/v1/email/logs/${logId}`)
      setSelectedLog(response.data)
    } catch (error) {
      console.error('로그 상세 조회 실패:', error)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'success':
        return 'bg-green-100 text-green-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return <div className="text-center py-8">로딩 중...</div>
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-800">발송 로그</h2>
        <button
          onClick={fetchLogs}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          새로고침
        </button>
      </div>

      {logs.length === 0 ? (
        <div className="text-center py-8 text-gray-500">발송 로그가 없습니다.</div>
      ) : (
        <div className="space-y-4">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    발송 시간
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    보내는 사람
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    받는 사람
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    제목
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
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {log.sender_email}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {Array.isArray(log.recipient_emails) 
                        ? log.recipient_emails.join(', ')
                        : log.recipient_emails}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {log.subject}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(log.status)}`}>
                        {log.status === 'success' ? '성공' : log.status === 'failed' ? '실패' : '대기'}
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
                <h3 className="text-lg font-semibold text-gray-800">로그 상세</h3>
                <button
                  onClick={() => setSelectedLog(null)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>
              <div className="space-y-2 text-sm">
                <div><strong>ID:</strong> {selectedLog.id}</div>
                <div><strong>보내는 사람:</strong> {selectedLog.sender_email}</div>
                <div><strong>받는 사람:</strong> {Array.isArray(selectedLog.recipient_emails) ? selectedLog.recipient_emails.join(', ') : selectedLog.recipient_emails}</div>
                {selectedLog.cc_emails && selectedLog.cc_emails.length > 0 && (
                  <div><strong>참조:</strong> {Array.isArray(selectedLog.cc_emails) ? selectedLog.cc_emails.join(', ') : selectedLog.cc_emails}</div>
                )}
                {selectedLog.bcc_emails && selectedLog.bcc_emails.length > 0 && (
                  <div><strong>숨은 참조:</strong> {Array.isArray(selectedLog.bcc_emails) ? selectedLog.bcc_emails.join(', ') : selectedLog.bcc_emails}</div>
                )}
                <div><strong>제목:</strong> {selectedLog.subject}</div>
                <div><strong>본문:</strong> <div className="mt-2 p-3 bg-white rounded border">{selectedLog.body}</div></div>
                <div><strong>SMTP 호스트:</strong> {selectedLog.smtp_host}</div>
                <div><strong>SMTP 포트:</strong> {selectedLog.smtp_port}</div>
                <div><strong>SSL 사용:</strong> {selectedLog.use_ssl}</div>
                <div><strong>상태:</strong> <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(selectedLog.status)}`}>
                  {selectedLog.status === 'success' ? '성공' : selectedLog.status === 'failed' ? '실패' : '대기'}
                </span></div>
                {selectedLog.error_message && (
                  <div><strong>오류 메시지:</strong> <div className="mt-2 p-3 bg-red-50 text-red-800 rounded border">{selectedLog.error_message}</div></div>
                )}
                <div><strong>첨부파일 수:</strong> {selectedLog.attachment_count}</div>
                <div><strong>첨부파일 총 크기:</strong> {(selectedLog.total_attachment_size / 1024).toFixed(2)} KB</div>
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

export default EmailLogs

