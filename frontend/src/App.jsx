import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import LoginPage from './pages/LoginPage.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import CopywritingPage from './pages/CopywritingPage.jsx'
import ImagePage from './pages/ImagePage.jsx'
import VideoPage from './pages/VideoPage.jsx'
import AssetsPage from './pages/AssetsPage.jsx'
import MediaPage from './pages/MediaPage.jsx'
import ProductsPage from './pages/ProductsPage.jsx'
import PipelinePage from './pages/PipelinePage.jsx'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/app" element={<Layout />}>
          <Route index element={<Navigate to="/app/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="products" element={<ProductsPage />} />
          <Route path="copywriting" element={<CopywritingPage />} />
          <Route path="pipeline" element={<PipelinePage />} />
          <Route path="images" element={<ImagePage />} />
          <Route path="videos" element={<VideoPage />} />
          <Route path="assets" element={<AssetsPage />} />
          <Route path="media" element={<MediaPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
