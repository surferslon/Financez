import { useTranslation } from "react-i18next";

export default function Header() {
  const { t } = useTranslation();

  return (
    <div className="header-row">
        <div className="header-menu">
            <div className="logo-wrapper">
                <img style={{height: '35px'}} src=""/>
            </div>
            <a href="/reports" className="menu-item">
                {t('Main')}
            </a>
            <a href="/entries" className="menu-item">
                {t('Entries')}
            </a>
            <a href="/settings" className="menu-item">
                {t('Settings')}
            </a>
            <div style={{textAlign: "center"}}>
                'cur'
            </div>
        </div>
    </div>
  )
}
