import styles from "./Input.module.css";

type TInputProps = {
    label: string,
    type: string,
    name: string,
    placeholder: string
    handleChangeInput: (e: React.ChangeEvent<HTMLInputElement>) => void,
    error?: string,
    setShowPassword?: React.Dispatch<React.SetStateAction<boolean>>,
    showPassword?: boolean
}

export const Input = ({
    label,
    type,
    name,
    placeholder,
    handleChangeInput,
    error,
    setShowPassword,
    showPassword
}: TInputProps) => {
    return (
        <>
            <label className={styles.label}>
                {label}
                <div className={styles.passwordWrapper}>
                    <input 
                        className={styles.input} 
                        type={type} 
                        name ={name} 
                        placeholder={placeholder}
                        onChange={handleChangeInput} />
                        {setShowPassword && <button 
                            className={styles.showPasswordButton} 
                            type="button" 
                            onClick={() => setShowPassword(!showPassword)}>
                            {showPassword ? 
                                <img 
                                    className={styles.iconPassword} 
                                    src="/assets/hide-password.svg" 
                                    alt="скрыть пароль"
                                /> 
                                : 
                                <img 
                                    className={styles.iconPassword} 
                                    src="/assets/show-password.svg" 
                                    alt="показать пароль" 
                                />
                            }
                        </button>}
                </div>
                <span className={styles.error}>{error}</span>
            </label>
        </>
    )
}
