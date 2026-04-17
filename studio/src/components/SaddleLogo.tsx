export function SaddleLogo(): JSX.Element {
  return (
    <svg width="40" height="40" viewBox="0 0 64 64" fill="none" aria-label="Saddle Logo">
      <rect x="4" y="8" width="56" height="48" rx="10" fill="var(--stripe-ink)" />
      <path
        d="M16 23C16 19.7 18.7 17 22 17H42C45.3 17 48 19.7 48 23C48 26.3 45.3 29 42 29H22C18.7 29 16 31.7 16 35C16 38.3 18.7 41 22 41H42"
        stroke="var(--stripe-brand)"
        strokeWidth="5"
        strokeLinecap="round"
      />
      <circle cx="44" cy="41" r="5" fill="var(--stripe-brand)" />
    </svg>
  );
}
