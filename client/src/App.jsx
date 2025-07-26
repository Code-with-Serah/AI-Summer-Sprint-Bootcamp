import React from 'react'
import Footer from './components/Footer'
import Navbar from './components/Navbar'
import { Route, Routes,useLocation } from 'react-router-dom'
import Home from './pages/Home'
import {Toaster} from 'react-hot-toast'
import Series from './pages/series'
import PopularMovies from './pages/PopularMovies'
import TestConnection from './pages/TestConnection'


const App = () => {
  //The below line checks the url, if it starts with admin, the navbar won't be shown
  const isAdminRoute=useLocation().pathname.startsWith('/admin')
  return (
    <>
    <Toaster />
      {!isAdminRoute && <Navbar />}
      <Routes>
        <Route path='/' element={<Home/>} />
        <Route path='/series' element={<Series/>} />
        <Route path='/favourite' element={<testee/>} />
        <Route path='/MoviesList' element={<PopularMovies/>} />
        <Route path='/TestConnection' element={<TestConnection/>} />



      </Routes>
      {!isAdminRoute && <Footer />}

    </>
  )
}

export default App