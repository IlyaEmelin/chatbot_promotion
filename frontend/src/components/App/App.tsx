import './App.css'
import { Header } from '../Header/Header'
import { Footer } from '../Footer/Footer'
import { Main } from '../Main/Main'
import { Route, Routes } from 'react-router-dom'
import { FormPage } from '../../pages/formPage'

function App() {

  return (
    <>
      <Header />
      <Routes>
        <Route path="/" element={<Main />} />
        <Route path="/form" element={<FormPage />} />
      </Routes>
      <Footer />     
    </>
  )
}

export default App
