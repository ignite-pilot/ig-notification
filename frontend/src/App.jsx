import { useState } from 'react'
import EmailForm from './components/EmailForm'
import EmailLogs from './components/EmailLogs'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('send')

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-8 text-center">
          IG Notification System
        </h1>
        
        <div className="bg-white rounded-lg shadow-md">
          <div className="border-b border-gray-200">
            <nav className="flex">
              <button
                onClick={() => setActiveTab('send')}
                className={`px-6 py-3 font-medium text-sm ${
                  activeTab === 'send'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                이메일 발송
              </button>
              <button
                onClick={() => setActiveTab('logs')}
                className={`px-6 py-3 font-medium text-sm ${
                  activeTab === 'logs'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                발송 로그
              </button>
            </nav>
          </div>
          
          <div className="p-6">
            {activeTab === 'send' && <EmailForm />}
            {activeTab === 'logs' && <EmailLogs />}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App

