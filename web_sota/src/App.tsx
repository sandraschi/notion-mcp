import {
  Navigate,
  Route,
  BrowserRouter as Router,
  Routes,
} from "react-router-dom";
import { AppLayout } from "@/components/layout/app-layout";
import { Chat } from "@/pages/chat";
import { Dashboard } from "@/pages/dashboard";
import { DataMigration } from "@/pages/data";
import { Explorer } from "@/pages/explorer";
import { Help } from "@/pages/help";
import Logging from "@/pages/Logging";
import { Plugins } from "@/pages/plugins";
import { Settings } from "@/pages/settings";
import { Skills } from "@/pages/skills";
import { Status } from "@/pages/status";
import { Tools } from "@/pages/tools";
import { SemanticSearch } from "./pages/search";

function App() {
  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/search" element={<SemanticSearch />} />
          <Route path="/explorer" element={<Explorer />} />
          <Route path="/plugins" element={<Plugins />} />
          <Route path="/data" element={<DataMigration />} />
          <Route path="/tools" element={<Tools />} />
          <Route path="/skills" element={<Skills />} />
          <Route path="/status" element={<Status />} />
          <Route path="/logging" element={<Logging />} />
          <Route path="/help" element={<Help />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppLayout>
    </Router>
  );
}

export default App;
