import { useState } from 'react'
import axios from 'axios'

function EmailForm() {
  const [formData, setFormData] = useState({
    recipientEmails: [''],
    senderEmail: 'percusmaro@gmail.com',
    smtpHost: 'smtp.gmail.com',
    smtpPort: 465,
    smtpUsername: 'percusmaro@gmail.com',
    smtpPassword: 'bcasmtygslphzqnk',
    useSsl: true,
    verifySsl: true, // SSL 인증서 검증 여부
    ccEmails: [''],
    bccEmails: [''],
    subject: '',
    body: ''
  })
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })

  const handleRecipientChange = (index, value) => {
    const newRecipients = [...formData.recipientEmails]
    newRecipients[index] = value
    setFormData({ ...formData, recipientEmails: newRecipients })
  }

  const addRecipient = () => {
    setFormData({
      ...formData,
      recipientEmails: [...formData.recipientEmails, '']
    })
  }

  const removeRecipient = (index) => {
    const newRecipients = formData.recipientEmails.filter((_, i) => i !== index)
    setFormData({ ...formData, recipientEmails: newRecipients.length > 0 ? newRecipients : [''] })
  }

  const handleCcChange = (index, value) => {
    const newCc = [...formData.ccEmails]
    newCc[index] = value
    setFormData({ ...formData, ccEmails: newCc })
  }

  const addCc = () => {
    setFormData({
      ...formData,
      ccEmails: [...formData.ccEmails, '']
    })
  }

  const removeCc = (index) => {
    const newCc = formData.ccEmails.filter((_, i) => i !== index)
    setFormData({ ...formData, ccEmails: newCc.length > 0 ? newCc : [''] })
  }

  const handleBccChange = (index, value) => {
    const newBcc = [...formData.bccEmails]
    newBcc[index] = value
    setFormData({ ...formData, bccEmails: newBcc })
  }

  const addBcc = () => {
    setFormData({
      ...formData,
      bccEmails: [...formData.bccEmails, '']
    })
  }

  const removeBcc = (index) => {
    const newBcc = formData.bccEmails.filter((_, i) => i !== index)
    setFormData({ ...formData, bccEmails: newBcc.length > 0 ? newBcc : [''] })
  }

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files)
    if (selectedFiles.length > 10) {
      setMessage({ type: 'error', text: '첨부파일은 최대 10개까지 가능합니다.' })
      return
    }
    
    let totalSize = 0
    selectedFiles.forEach(file => {
      totalSize += file.size
    })
    
    if (totalSize > 30 * 1024 * 1024) {
      setMessage({ type: 'error', text: '첨부파일 총 크기는 30MB를 넘을 수 없습니다.' })
      return
    }
    
    setFiles(selectedFiles)
    setMessage({ type: '', text: '' })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage({ type: '', text: '' })

    try {
      // Filter empty emails
      const recipients = formData.recipientEmails.filter(email => email.trim() !== '')
      const cc = formData.ccEmails.filter(email => email.trim() !== '')
      const bcc = formData.bccEmails.filter(email => email.trim() !== '')

      if (recipients.length === 0) {
        setMessage({ type: 'error', text: '받는 사람 이메일을 최소 1개 이상 입력해주세요.' })
        setLoading(false)
        return
      }

      if (recipients.length > 100) {
        setMessage({ type: 'error', text: '최대 100명까지 발송 가능합니다.' })
        setLoading(false)
        return
      }

      const formDataToSend = new FormData()
      formDataToSend.append('recipient_emails', JSON.stringify(recipients))
      formDataToSend.append('sender_email', formData.senderEmail)
      formDataToSend.append('smtp_host', formData.smtpHost)
      formDataToSend.append('smtp_port', formData.smtpPort)
      formDataToSend.append('smtp_username', formData.smtpUsername)
      formDataToSend.append('smtp_password', formData.smtpPassword)
      formDataToSend.append('use_ssl', formData.useSsl)
      formDataToSend.append('verify_ssl', formData.verifySsl)
      if (cc.length > 0) {
        formDataToSend.append('cc_emails', JSON.stringify(cc))
      }
      if (bcc.length > 0) {
        formDataToSend.append('bcc_emails', JSON.stringify(bcc))
      }
      formDataToSend.append('subject', formData.subject)
      formDataToSend.append('body', formData.body)

      files.forEach(file => {
        formDataToSend.append('files', file)
      })

      const response = await axios.post('/api/v1/email/send', formDataToSend, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      if (response.data.status === 'success') {
        setMessage({ type: 'success', text: response.data.message })
        
        // Reset form only on success (keep SMTP settings as default)
        setFormData({
          recipientEmails: [''],
          senderEmail: 'percusmaro@gmail.com',
          smtpHost: 'smtp.gmail.com',
          smtpPort: 465,
          smtpUsername: 'percusmaro@gmail.com',
          smtpPassword: 'bcasmtygslphzqnk',
          useSsl: true,
          verifySsl: true,
          ccEmails: [''],
          bccEmails: [''],
          subject: '',
          body: ''
        })
        setFiles([])
      } else {
        setMessage({ type: 'error', text: response.data.message })
        // Keep form data on failure
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || '이메일 발송 중 오류가 발생했습니다.'
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

      {/* 받는 사람 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          받는 사람 이메일 *
        </label>
        {formData.recipientEmails.map((email, index) => (
          <div key={index} className="flex gap-2 mb-2">
            <input
              type="email"
              value={email}
              onChange={(e) => handleRecipientChange(index, e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="example@email.com"
              required
            />
            {formData.recipientEmails.length > 1 && (
              <button
                type="button"
                onClick={() => removeRecipient(index)}
                className="px-3 py-2 bg-red-500 text-white rounded-md hover:bg-red-600"
              >
                삭제
              </button>
            )}
          </div>
        ))}
        {formData.recipientEmails.length < 100 && (
          <button
            type="button"
            onClick={addRecipient}
            className="mt-2 px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
          >
            + 추가
          </button>
        )}
      </div>

      {/* 보내는 사람 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          보내는 사람 이메일 *
        </label>
        <input
          type="email"
          value={formData.senderEmail}
          onChange={(e) => setFormData({ ...formData, senderEmail: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="sender@email.com"
          required
        />
        {formData.smtpHost && formData.smtpHost.includes('gmail') && (
          <p className="mt-1 text-xs text-gray-500">
            💡 Gmail: 보내는 사람 이메일과 SMTP 사용자명이 동일해야 합니다
          </p>
        )}
      </div>

      {/* SMTP 설정 */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            SMTP 호스트 *
          </label>
          <input
            type="text"
            value={formData.smtpHost}
            onChange={(e) => setFormData({ ...formData, smtpHost: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="smtp.gmail.com"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            SMTP 포트 *
          </label>
          <input
            type="number"
            value={formData.smtpPort}
            onChange={(e) => setFormData({ ...formData, smtpPort: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            SMTP 사용자명 *
          </label>
          <input
            type="text"
            value={formData.smtpUsername}
            onChange={(e) => setFormData({ ...formData, smtpUsername: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="your-email@gmail.com"
            required
          />
          {formData.smtpHost && formData.smtpHost.includes('gmail') && (
            <p className="mt-1 text-xs text-gray-500">
              💡 Gmail: 전체 이메일 주소를 입력하세요 (예: user@gmail.com)
            </p>
          )}
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            SMTP 비밀번호 *
          </label>
          <input
            type="password"
            value={formData.smtpPassword}
            onChange={(e) => setFormData({ ...formData, smtpPassword: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="앱 비밀번호 또는 일반 비밀번호"
            required
          />
          {formData.smtpHost && formData.smtpHost.includes('gmail') && (
            <p className="mt-1 text-xs text-blue-600">
              ⚠️ Gmail: 일반 비밀번호가 아닌 <strong>앱 비밀번호</strong>를 사용해야 합니다.<br/>
              <a href="https://support.google.com/accounts/answer/185833" target="_blank" rel="noopener noreferrer" className="underline">
                앱 비밀번호 생성 방법
              </a>
            </p>
          )}
        </div>
      </div>

      <div className="space-y-2">
        <div>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={formData.useSsl}
              onChange={(e) => setFormData({ ...formData, useSsl: e.target.checked })}
              className="mr-2"
            />
            <span className="text-sm font-medium text-gray-700">SSL 사용</span>
          </label>
        </div>
        <div>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={formData.verifySsl}
              onChange={(e) => setFormData({ ...formData, verifySsl: e.target.checked })}
              className="mr-2"
            />
            <span className="text-sm font-medium text-gray-700">SSL 인증서 검증 (체크 해제 시 self-signed 인증서 허용)</span>
          </label>
        </div>
      </div>

      {/* 참조 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          참조 (CC)
        </label>
        {formData.ccEmails.map((email, index) => (
          <div key={index} className="flex gap-2 mb-2">
            <input
              type="email"
              value={email}
              onChange={(e) => handleCcChange(index, e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="cc@email.com"
            />
            {formData.ccEmails.length > 1 && (
              <button
                type="button"
                onClick={() => removeCc(index)}
                className="px-3 py-2 bg-red-500 text-white rounded-md hover:bg-red-600"
              >
                삭제
              </button>
            )}
          </div>
        ))}
        <button
          type="button"
          onClick={addCc}
          className="mt-2 px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
        >
          + 추가
        </button>
      </div>

      {/* 숨은 참조 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          숨은 참조 (BCC)
        </label>
        {formData.bccEmails.map((email, index) => (
          <div key={index} className="flex gap-2 mb-2">
            <input
              type="email"
              value={email}
              onChange={(e) => handleBccChange(index, e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="bcc@email.com"
            />
            {formData.bccEmails.length > 1 && (
              <button
                type="button"
                onClick={() => removeBcc(index)}
                className="px-3 py-2 bg-red-500 text-white rounded-md hover:bg-red-600"
              >
                삭제
              </button>
            )}
          </div>
        ))}
        <button
          type="button"
          onClick={addBcc}
          className="mt-2 px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
        >
          + 추가
        </button>
      </div>

      {/* 제목 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          메일 제목 *
        </label>
        <input
          type="text"
          value={formData.subject}
          onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
      </div>

      {/* 본문 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          메일 본문 *
        </label>
        <textarea
          value={formData.body}
          onChange={(e) => setFormData({ ...formData, body: e.target.value })}
          rows={10}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
      </div>

      {/* 첨부파일 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          첨부 파일 (최대 10개, 총 30MB)
        </label>
        <input
          type="file"
          multiple
          onChange={handleFileChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        {files.length > 0 && (
          <div className="mt-2">
            <p className="text-sm text-gray-600">선택된 파일:</p>
            <ul className="list-disc list-inside text-sm text-gray-600">
              {files.map((file, index) => (
                <li key={index}>
                  {file.name} ({(file.size / 1024).toFixed(2)} KB)
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {loading ? '발송 중...' : '이메일 발송'}
      </button>
    </form>
  )
}

export default EmailForm

