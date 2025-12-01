import styles from "./FormButton.module.css";

export const FormButton = ({ text, disabled }: { text: string, disabled?: boolean }) => {
    return (
        <button className={styles.button} type="submit" disabled={disabled}>{text}</button>
    )
}