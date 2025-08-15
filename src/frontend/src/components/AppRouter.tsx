import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import { Tab, TabList } from '@fluentui/react-components';
import { ChartMultiple24Regular, Chat24Regular } from '@fluentui/react-icons';
import App from './App';
import EvaluationDashboard from './evaluation/EvaluationDashboard';

const AppRouter: React.FC = () => {
    return (
        <div>
            {/* Navigation tabs */}
            <TabList defaultSelectedValue="chat">
                <Tab icon={<Chat24Regular />} value="chat">
                    <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }}>Chat</Link>
                </Tab>
                <Tab icon={<ChartMultiple24Regular />} value="evaluation">
                    <Link to="/evaluation/dashboard" style={{ textDecoration: 'none', color: 'inherit' }}>Evaluation</Link>
                </Tab>
            </TabList>

            {/* Routes */}
            <Routes>
                <Route path="/" element={<App />} />
                <Route path="/evaluation/dashboard" element={<EvaluationDashboard />} />
            </Routes>
        </div>
    );
};

export default AppRouter;
