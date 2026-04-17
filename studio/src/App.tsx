import { Navigate, Route, Routes } from "react-router-dom";
import { WelcomePage } from "./pages/WelcomePage";
import { ModeStudioPage } from "./pages/ModeStudioPage";

export default function App(): JSX.Element {
  return (
    <Routes>
      <Route path="/" element={<WelcomePage />} />
      <Route path="/studio" element={<ModeStudioPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
