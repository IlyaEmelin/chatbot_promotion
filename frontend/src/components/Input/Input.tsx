import styles from "./Input.module.css";

type TInputProps = {
    label: string,
    type: string,
    name: string,
    placeholder: string
    handleChangeInput: (e: React.ChangeEvent<HTMLInputElement>) => void,
}

export const Input = ({
    label,
    type,
    name,
    placeholder,
    handleChangeInput,
}: TInputProps) => {
    return (
        <>
            <label className={styles.label}>
                {label}
                <input 
                    className={styles.input} 
                    type={type} 
                    name ={name} 
                    placeholder={placeholder}
                    onChange={handleChangeInput} />
            </label>
        </>
    )
}
