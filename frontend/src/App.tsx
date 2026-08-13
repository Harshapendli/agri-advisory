import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Advisory from './pages/Advisory'
import Disease from './pages/Disease'
import History from './pages/History'
import Navbar from './components/Navbar'
import { useStore } from './store/useStore'

const qc = new QueryClient()

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const token = useStore(s => s.token)
  return token ? <>{children}</> : <Navigate to="/login" />
}

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-green-50">
      <Navbar />
      <main className="max-w-7xl mx-auto px-4 py-6">{children}</main>
    </div>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={qc}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<PrivateRoute><Layout><Dashboard /></Layout></PrivateRoute>} />
          <Route path="/advisory" element={<PrivateRoute><Layout><Advisory /></Layout></PrivateRoute>} />
          <Route path="/disease" element={<PrivateRoute><Layout><Disease /></Layout></PrivateRoute>} />
          <Route path="/history" element={<PrivateRoute><Layout><History /></Layout></PrivateRoute>} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
