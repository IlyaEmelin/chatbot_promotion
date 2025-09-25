import { SurveyForm } from "../ui/SurveyForm"
import styles from "./formPage.module.css"

export const FormPage = () => {
  return (
    <div className={styles.form_page}>
      <SurveyForm />
    </div>
  )
}