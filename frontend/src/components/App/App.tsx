import './App.css'
import { Header } from '../Header/Header'
import { Footer } from '../Footer/Footer'
import { Main } from '../Main/Main'
import { Route, Routes, useNavigate } from 'react-router-dom'
import { Modal } from '../Modal/Modal'
import { Login } from '../pages/Login/Login'
import { Register } from '../pages/Rgister/Register'
import { OnlyUnAuth } from '../Protected-route/Protected-route'
import { SurveyWidget } from '../../../chatbot/src/components/SurveyWidget/SurveyWidget'

function App() {
  const navigate = useNavigate();
  return (
    <>
      <Header /> 
      <Main />
      <Routes>
        <Route 
          path='/login' 
          element={
            <OnlyUnAuth>
              <Modal title='Вход' onClose={() => navigate(-1)}>
                <Login />
              </Modal>
            </OnlyUnAuth>
          }>
        </Route>
        <Route 
          path='/register' 
          element={
            <OnlyUnAuth>
              <Modal title='Регистрация' onClose={() => navigate(-1)}>
                <Register />
              </Modal>
            </OnlyUnAuth>
          }>
        </Route>
      </Routes>
      <Footer /> 
      <SurveyWidget />
    </>
  )
}

export default App
