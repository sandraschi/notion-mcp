import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from '@/components/layout/app-layout';
import { Dashboard } from '@/pages/dashboard';
import { Chat } from '@/pages/chat';
import { SemanticSearch } from "./pages/search";
import { Tools } from '@/pages/tools';
import { Help } from '@/pages/help';
import { Settings } from '@/pages/settings';
import { Explorer } from '@/pages/explorer'; // New import
import { Plugins } from '@/pages/plugins'; // New import
import { DataMigration } from '@/pages/data'; // New import

function App() {
  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/search" element={<SemanticSearch />} /> {/* Changed from SemanticSearch */}
          <Route path="/explorer" element={<Explorer />} /> {/* New route */}
          <Route path="/plugins" element={<Plugins />} /> {/* New route */}
          <Route path="/data" element={<DataMigration />} /> {/* New route */}
          <Route path="/tools" element={<Tools />} />
          <Route path="/help" element={<Help />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppLayout>
    </Router>
  );
}

export default App;
