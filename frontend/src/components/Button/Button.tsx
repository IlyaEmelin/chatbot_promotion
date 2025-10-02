import styles from "./Button.module.css";

export const Button = ({ text, type }: { text: string, type: "button" | "submit" }) => {
    return (
        <button className={styles.button} type={type}>
            {text}
        </button>
    );
};