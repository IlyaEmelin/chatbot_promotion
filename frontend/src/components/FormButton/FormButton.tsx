import styles from "./FormButton.module.css";

export const FormButton = ({ text }: { text: string }) => {
    return (
        <button className={styles.button} type="submit">{text}</button>
    )
}