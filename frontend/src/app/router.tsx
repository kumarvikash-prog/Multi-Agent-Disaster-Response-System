import { BrowserRouter, Route, Routes } from "react-router-dom";
import { StatusPage } from "../pages/StatusPage";

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<StatusPage />} />
        {/* Phase 1 routes are added in M1.1+ */}
      </Routes>
    </BrowserRouter>
  );
}
