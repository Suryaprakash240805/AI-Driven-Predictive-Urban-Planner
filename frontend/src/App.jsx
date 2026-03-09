import { Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "@/pages/LoginPage";
import UserDashboard from "@/pages/UserDashboard";
import ValidatorDashboard from "@/pages/ValidatorDashboard";
import BuildingTypePage from "@/pages/BuildingTypePage";
import LandSelectionPage from "@/pages/LandSelectionPage";
import LayoutChoicePage from "@/pages/LayoutChoicePage";
import FinalReportPage from "@/pages/FinalReportPage";
import ProtectedRoute from "@/components/common/ProtectedRoute";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<UserDashboard />} />
        <Route path="/validator" element={<ValidatorDashboard />} />
        <Route path="/build-type" element={<BuildingTypePage />} />
        <Route path="/land-selection" element={<LandSelectionPage />} />
        <Route path="/layout-choice" element={<LayoutChoicePage />} />
        <Route path="/report/:id" element={<FinalReportPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
