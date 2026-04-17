import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { text, type Lang } from "../i18n";
import { SaddleLogo } from "../components/SaddleLogo";

export function WelcomePage(): JSX.Element {
  const [lang, setLang] = useState<Lang>("en");
  useEffect(() => {
    const saved = localStorage.getItem("saddle_studio_lang");
    if (saved === "en" || saved === "zh") setLang(saved);
  }, []);
  const t = text[lang];
  const toggle = (): void => {
    const next: Lang = lang === "en" ? "zh" : "en";
    setLang(next);
    localStorage.setItem("saddle_studio_lang", next);
  };
  return (
    <main className="page page-welcome">
      <section className="hero-card">
        <div className="header-tools">
          <button className="btn btn-secondary" onClick={toggle}>
            {t.langToggle}
          </button>
        </div>
        <div className="hero-brand">
          <SaddleLogo />
          <h1>Saddle Studio</h1>
        </div>
        <p className="hero-lead">{t.welcomeLead}</p>
        <div className="hero-points">
          <span>{t.welcomePoint1}</span>
          <span>{t.welcomePoint2}</span>
          <span>{t.welcomePoint3}</span>
        </div>
        <Link className="btn btn-primary" to="/studio">
          {t.enterStudio}
        </Link>
      </section>
    </main>
  );
}
