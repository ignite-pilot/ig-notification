import { useState } from 'react'
import EmailForm from './components/EmailForm'
import EmailLogs from './components/EmailLogs'
import PushForm from './components/PushForm'
import PushLogs from './components/PushLogs'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('send')

  const tabList = [
    { key: 'send', label: '이메일 발송' },
    { key: 'logs', label: '발송 로그' },
    { key: 'pushSend', label: '푸시 발송' },
    { key: 'pushLogs', label: '푸시 로그' },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-8 text-center">
          IG Notification System
        </h1>

        <div className="bg-white rounded-lg shadow-md">
          <div className="border-b border-gray-200">
            <nav className="flex">
              {tabList.map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`px-6 py-3 font-medium text-sm ${
                    activeTab === tab.key
                      ? 'text-blue-600 border-b-2 border-blue-600'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'send' && <EmailForm />}
            {activeTab === 'logs' && <EmailLogs />}
            {activeTab === 'pushSend' && <PushForm />}
            {activeTab === 'pushLogs' && <PushLogs />}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App

