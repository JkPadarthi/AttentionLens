import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from '@/components/Layout'
import { AnalyzePage } from '@/pages/AnalyzePage'
import { InterventionPage } from '@/pages/InterventionPage'

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<AnalyzePage />} />
          <Route path="/intervene" element={<InterventionPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App
