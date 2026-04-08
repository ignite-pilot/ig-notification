import { useState } from 'react'
import axios from 'axios'

function PushForm() {
  const [firebaseProjectId, setFirebaseProjectId] = useState('')
  const [deviceTokens, setDeviceTokens] = useState([''])
  const [title, setTitle] = useState('')
  const [body, setBody] = useState('')
  const [extraData, setExtraData] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })

  const handleTokenChange = (index, value) => {
    const newTokens = [...deviceTokens]
    newTokens[index] = value
    setDeviceTokens(newTokens)
  }

  const addToken = () => {
    if (deviceTokens.length >= 500) {
      setMessage({ type: 'error', text: '디바이스 토큰은 최대 500개까지 입력 가능합니다.' })
      return
    }
    setDeviceTokens([...deviceTokens, ''])
  }

  const removeToken = (index) => {
    const newTokens = deviceTokens.filter((_, i) => i !== index)
    setDeviceTokens(newTokens.length > 0 ? newTokens : [''])
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage({ type: '', text: '' })

    try {
      const filteredTokens = deviceTokens.filter(token => token.trim() !== '')

      if (filteredTokens.length === 0) {
        setMessage({ type: 'error', text: '디바이스 토큰을 최소 1개 이상 입력해주세요.' })
        setLoading(false)
        return
      }

      if (filteredTokens.length > 500) {
        setMessage({ type: 'error', text: '디바이스 토큰은 최대 500개까지 허용됩니다.' })
        setLoading(false)
        return
      }

      // 추가 데이터 JSON 검증 (입력된 경우)
      if (extraData.trim()) {
        try {
          JSON.parse(extraData.trim())
        } catch {
          setMessage({ type: 'error', text: '추가 데이터가 유효한 JSON 형식이 아닙니다.' })
          setLoading(false)
          return
        }
      }

      const formDataToSend = new FormData()
      formDataToSend.append('firebase_project_id', firebaseProjectId)
      formDataToSend.append('device_tokens', JSON.stringify(filteredTokens))
      formDataToSend.append('title', title)
      formDataToSend.append('body', body)
      if (extraData.trim()) {
        formDataToSend.append('data', extraData.trim())
      }

      const response = await axios.post('/api/v1/push/send', formDataToSend, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'X-API-Key': import.meta.env.VITE_API_KEY || ''
        }
      })

      const responseData = response.data
      if (responseData.status === 'success' || responseData.status === 'partial') {
        setMessage({ type: 'success', text: responseData.message })
        // 성공 시 폼 초기화
        setFirebaseProjectId('')
        setDeviceTokens([''])
        setTitle('')
        setBody('')
        setExtraData('')
      } else {
        setMessage({ type: 'error', text: responseData.message })
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || '푸시 알림 발송 중 오류가 발생했습니다.'
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {message.text && (
        <div className={`p-4 rounded ${
          message.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {message.text}
        </div>
      )}

      {/* Firebase 프로젝트 ID */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Firebase 프로젝트 ID *
        </label>
        <input
          type="text"
          value={firebaseProjectId}
          onChange={(e) => setFirebaseProjectId(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
          placeholder="예: reborn-9f1ac"
          required
        />
        <p className="mt-1 text-xs text-gray-500">
          AWS Secrets Manager의 Secret 이름 규칙: prod/ignite-pilot/{'{'}firebase_project_id{'}'}-android-key
        </p>
      </div>

      {/* 디바이스 토큰 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          디바이스 토큰 * (최대 500개)
        </label>
        {deviceTokens.map((token, index) => (
          <div key={index} className="flex gap-2 mb-2">
            <input
              type="text"
              value={token}
              onChange={(e) => handleTokenChange(index, e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
              placeholder="FCM 디바이스 토큰을 입력하세요"
              required
            />
            {deviceTokens.length > 1 && (
              <button
                type="button"
                onClick={() => removeToken(index)}
                className="px-3 py-2 bg-red-500 text-white rounded-md hover:bg-red-600"
              >
                삭제
              </button>
            )}
          </div>
        ))}
        {deviceTokens.length < 500 && (
          <button
            type="button"
            onClick={addToken}
            className="mt-2 px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
          >
            + 토큰 추가
          </button>
        )}
        <p className="mt-1 text-xs text-gray-500">
          현재 {deviceTokens.filter(t => t.trim() !== '').length}개 입력됨
        </p>
      </div>

      {/* 알림 제목 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          알림 제목 *
        </label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="알림 제목을 입력하세요"
          required
        />
      </div>

      {/* 알림 내용 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          알림 내용 *
        </label>
        <textarea
          value={body}
          onChange={(e) => setBody(e.target.value)}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="알림 내용을 입력하세요"
          required
        />
      </div>

      {/* 추가 데이터 (선택) */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          추가 데이터 (선택, JSON 형식)
        </label>
        <textarea
          value={extraData}
          onChange={(e) => setExtraData(e.target.value)}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
          placeholder={'{"key": "value", "type": "notification"}'}
        />
        <p className="mt-1 text-xs text-gray-500">
          JSON 객체 형식으로 입력하세요. 모든 값은 문자열로 전송됩니다.
        </p>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {loading ? '발송 중...' : '푸시 알림 발송'}
      </button>
    </form>
  )
}

export default PushForm
