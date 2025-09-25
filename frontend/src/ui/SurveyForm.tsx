import { useState, ChangeEvent, FormEvent } from 'react';
import styles from './SurveyForm.module.css';

interface SurveyFormData {
  contactName: string;
  callStatus: 'received' | 'relative' | 'friend' | 'colleague' | 'social';
  organization: string;
  birthDate: string;
  email: string;
  phone: string;
  city: string;
  needHelp: string;
  hasVolunteersNeeded: 'yes' | 'no' | '';
  volunteersInTCF: 'yes' | 'no' | '';
  volunteersInOtherFunds: 'yes' | 'no' | '';
  volunteerSupport: 'yes' | 'no' | '';
  helpFormat: 'personal' | 'phone';
}

// type RadioFieldName = 'callStatus' | 'hasVolunteersNeeded' | 'volunteersInTCF' | 'volunteersInOtherFunds' | 'volunteerSupport' | 'helpFormat';

export const SurveyForm: React.FC = () => {
  const [formData, setFormData] = useState<SurveyFormData>({
    contactName: '',
    callStatus: 'received',
    organization: '',
    birthDate: '',
    email: '',
    phone: '',
    city: '',
    needHelp: '',
    hasVolunteersNeeded: '',
    volunteersInTCF: '',
    volunteersInOtherFunds: '',
    volunteerSupport: '',
    helpFormat: 'personal'
  });

  const handleInputChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>): void => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e: FormEvent<HTMLFormElement>): void => {
    e.preventDefault();
    console.log('Form data:', formData);
    // отправка данных
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Анкета для помощи</h1>
      <p className={styles.subtitle}>
        Давайте немного познакомимся: заполните каждое из полей, приведенных ниже
      </p>
      
      <form className={styles.form} onSubmit={handleSubmit}>
        {/* Контактное лицо */}
        <div className={styles.field}>
          <label className={styles.label}>Контактное лицо</label>
          <input
            type="text"
            name="contactName"
            value={formData.contactName}
            onChange={handleInputChange}
            className={styles.input}
          />
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Ваш статус для подающего</label>
          <div className={styles.radioGroup}>
            <label className={styles.radioLabel}>
              <input
                type="radio"
                name="callStatus"
                value="received"
                checked={formData.callStatus === 'received'}
                onChange={handleInputChange}
              />
              <span className={styles.radioText}>Я сам</span>
            </label>
            <label className={styles.radioLabel}>
              <input
                type="radio"
                name="callStatus"
                value="relative"
                checked={formData.callStatus === 'relative'}
                onChange={handleInputChange}
              />
              <span className={styles.radioText}>Родственник</span>
            </label>
            <label className={styles.radioLabel}>
              <input
                type="radio"
                name="callStatus"
                value="friend"
                checked={formData.callStatus === 'friend'}
                onChange={handleInputChange}
              />
              <span className={styles.radioText}>Друзья</span>
            </label>
            <label className={styles.radioLabel}>
              <input
                type="radio"
                name="callStatus"
                value="colleague"
                checked={formData.callStatus === 'colleague'}
                onChange={handleInputChange}
              />
              <span className={styles.radioText}>Коллеги по работе</span>
            </label>
            <label className={styles.radioLabel}>
              <input
                type="radio"
                name="callStatus"
                value="social"
                checked={formData.callStatus === 'social'}
                onChange={handleInputChange}
              />
              <span className={styles.radioText}>Социальная служба</span>
            </label>
          </div>
        </div>

        <div className={styles.field}>
          <label className={styles.label}>ФИО подающего</label>
          <input
            type="text"
            name="organization"
            value={formData.organization}
            onChange={handleInputChange}
            className={styles.input}
          />
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Дата рождения подающего</label>
          <input
            type="date"
            name="birthDate"
            value={formData.birthDate}
            onChange={handleInputChange}
            className={styles.input}
          />
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Email</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleInputChange}
            className={styles.input}
            placeholder="example@mail.com"
          />
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Телефон</label>
          <input
            type="tel"
            name="phone"
            value={formData.phone}
            onChange={handleInputChange}
            className={styles.input}
          />
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Город</label>
          <input
            type="text"
            name="city"
            value={formData.city}
            onChange={handleInputChange}
            className={styles.input}
          />
        </div>

        <div className={styles.field}>
          <label className={styles.label}>В чем нужна помощь?</label>
          <textarea
            name="needHelp"
            value={formData.needHelp}
            onChange={handleInputChange}
            className={styles.textarea}
            rows={4}
          />
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Есть ли у вас волонтеры на подобранные ТСР?</label>
          <div className={styles.radioGroup}>
            <label className={styles.radioLabel}>
              <input
                type="radio"
                name="hasVolunteersNeeded"
                value="yes"
                checked={formData.hasVolunteersNeeded === 'yes'}
                onChange={handleInputChange}
              />
              <span className={styles.radioText}>Да</span>
            </label>
            <label className={styles.radioLabel}>
              <input
                type="radio"
                name="hasVolunteersNeeded"
                value="no"
                checked={formData.hasVolunteersNeeded === 'no'}
                onChange={handleInputChange}
              />
              <span className={styles.radioText}>Нет</span>
            </label>
          </div>
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Волонтеры ли ТСР в ИПРА?</label>
          <div className={styles.radioGroup}>
            <label className={styles.radioLabel}>
              <input
                type="radio"
                name="volunteersInTCF"
                value="yes"
                checked={formData.volunteersInTCF === 'yes'}
                onChange={handleInputChange}
              />
              <span className={styles.radioText}>Да</span>
            </label>
            <label className={styles.radioLabel}>
              <input
                type="radio"
                name="volunteersInTCF"
                value="no"
                checked={formData.volunteersInTCF === 'no'}
                onChange={handleInputChange}
              />
              <span className={styles.radioText}>Нет</span>
            </label>
          </div>
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Есть ли у вас волонтеры техники общению с другими фондами?</label>
          <div className={styles.radioGroup}>
            <label className={styles.radioLabel}>
              <input
                type="radio"
                name="volunteersInOtherFunds"
                value="yes"
                checked={formData.volunteersInOtherFunds === 'yes'}
                onChange={handleInputChange}
              />
              <span className={styles.radioText}>Да</span>
            </label>
            <label className={styles.radioLabel}>
              <input
                type="radio"
                name="volunteersInOtherFunds"
                value="no"
                checked={formData.volunteersInOtherFunds === 'no'}
                onChange={handleInputChange}
              />
              <span className={styles.radioText}>Нет</span>
            </label>
          </div>
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Нужна ли вам волонтерская поддержка в составлении рекомендаций ИПРА, приглашения МСЭ, получения ТСР от СФР?</label>
          <div className={styles.radioGroup}>
            <label className={styles.radioLabel}>
              <input
                type="radio"
                name="volunteerSupport"
                value="yes"
                checked={formData.volunteerSupport === 'yes'}
                onChange={handleInputChange}
              />
              <span className={styles.radioText}>Да</span>
            </label>
            <label className={styles.radioLabel}>
              <input
                type="radio"
                name="volunteerSupport"
                value="no"
                checked={formData.volunteerSupport === 'no'}
                onChange={handleInputChange}
              />
              <span className={styles.radioText}>Нет</span>
            </label>
          </div>
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Как вы хотите получить отвор?</label>
          <div className={styles.radioGroup}>
            <label className={styles.radioLabel}>
              <input
                type="radio"
                name="helpFormat"
                value="personal"
                checked={formData.helpFormat === 'personal'}
                onChange={handleInputChange}
              />
              <span className={styles.radioText}>Личная встреча, выявление всех лиц пожар благодарность свыше ответ выздор</span>
            </label>
            <label className={styles.radioLabel}>
              <input
                type="radio"
                name="helpFormat"
                value="phone"
                checked={formData.helpFormat === 'phone'}
                onChange={handleInputChange}
              />
              <span className={styles.radioText}>По телефону, личными всего время и переговоры связали своей благ</span>
            </label>
          </div>
        </div>

        <button type="submit" className={styles.submitButton}>
          ОТПРАВИТЬ
        </button>
      </form>
    </div>
  );
};