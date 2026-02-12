'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { SearchHistory } from '@/components/ui/search-history';
import { dashboardApi, DashboardSummary } from '@/lib/api';
import {
  BarChart3Icon,
  TrendingUpIcon,
  AlertTriangleIcon,
  ShieldCheckIcon,
  BrainCircuitIcon,
  UsersIcon,
  SettingsIcon,
  BellIcon,
  SearchIcon,
} from 'lucide-react';

function formatRelativeTime(isoDate: string): string {
  const diffMs = Date.now() - new Date(isoDate).getTime();
  if (Number.isNaN(diffMs)) return 'recently';
  const minutes = Math.floor(diffMs / (1000 * 60));
  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hours ago`;
  const days = Math.floor(hours / 24);
  return `${days} day${days > 1 ? 's' : ''} ago`;
}

export default function DashboardPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadSummary = async () => {
      try {
        const payload = await dashboardApi.getSummary();
        setSummary(payload);
        setError(null);
      } catch (err) {
        console.error('Failed to load dashboard summary:', err);
        setError('Unable to load dashboard data from API.');
      } finally {
        setLoading(false);
      }
    };
    loadSummary();
  }, []);

  useEffect(() => {
    const performSearch = async () => {
      if (searchTerm.trim()) {
        try {
          const results = await dashboardApi.search(searchTerm);
          setSearchResults(results);
        } catch (err) {
          console.error('Search failed:', err);
          setSearchResults([]);
        }
      } else {
        setSearchResults([]);
      }
    };

    const debounce = setTimeout(performSearch, 300);
    return () => clearTimeout(debounce);
  }, [searchTerm]);

  const metrics = summary?.metrics;
  const totalModels = metrics?.total_models ?? 0;
  const activeModels = metrics?.active_models ?? 0;
  const highRiskModels = metrics?.high_risk_models ?? 0;
  const openGaps = metrics?.open_gaps ?? 0;
  const controlsVerified = metrics?.controls_verified ?? 0;
  const riskScore = totalModels > 0 ? Math.max(0, 10 - (highRiskModels / totalModels) * 10) : 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      <header className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                <BrainCircuitIcon className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">LifeAI Risk Copilot</h1>
                <p className="text-sm text-gray-400">Enterprise Dashboard</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="relative">
                <SearchHistory onSelectSearch={setSearchTerm} currentSearch={searchTerm}>
                  <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input
                    type="text"
                    placeholder="Search models, controls..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="bg-white/10 border border-white/20 rounded-lg pl-10 pr-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 backdrop-blur-sm"
                  />
                </SearchHistory>
                {searchResults.length > 0 && (
                  <div className="absolute top-full left-0 right-0 bg-white/10 border border-white/20 rounded-lg mt-1 backdrop-blur-sm z-50 max-h-80 overflow-y-auto">
                    {searchResults.map((result, index) => (
                      <div key={index} className="p-3 hover:bg-white/10 border-b border-white/10 last:border-b-0 cursor-pointer">
                        <p className="text-white text-sm font-medium">{result.name}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs px-2 py-1 rounded bg-blue-500/20 text-blue-300">
                            {result.type}
                          </span>
                          {result.category && <span className="text-xs text-gray-400">{result.category}</span>}
                          {result.severity && (
                            <span className={`text-xs px-2 py-1 rounded ${
                              result.severity === 'high'
                                ? 'bg-red-500/20 text-red-300'
                                : result.severity === 'medium'
                                ? 'bg-yellow-500/20 text-yellow-300'
                                : 'bg-green-500/20 text-green-300'
                            }`}>
                              {result.severity}
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              <Button variant="ghost" size="icon" className="text-white hover:bg-white/10">
                <BellIcon className="w-5 h-5" />
              </Button>
              <Button variant="ghost" size="icon" className="text-white hover:bg-white/10">
                <SettingsIcon className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {error && (
          <div className="mb-6 rounded-lg border border-red-500/40 bg-red-500/15 px-4 py-3 text-sm text-red-200">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-gradient-to-br from-blue-500/20 to-blue-600/20 border-blue-400/30 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-blue-100">Active Models</CardTitle>
              <BrainCircuitIcon className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{activeModels}</div>
              <p className="text-xs text-blue-200">of {totalModels} total models</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-500/20 to-green-600/20 border-green-400/30 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-green-100">Risk Score</CardTitle>
              <ShieldCheckIcon className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{riskScore.toFixed(1)}/10</div>
              <p className="text-xs text-green-200">{highRiskModels} high-risk model(s)</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-orange-500/20 to-orange-600/20 border-orange-400/30 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-orange-100">Open Gaps</CardTitle>
              <AlertTriangleIcon className="h-4 w-4 text-orange-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{openGaps}</div>
              <p className="text-xs text-orange-200">Control mapping gaps requiring review</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-500/20 to-purple-600/20 border-purple-400/30 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-purple-100">Controls Verified</CardTitle>
              <TrendingUpIcon className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{controlsVerified}</div>
              <p className="text-xs text-purple-200">Approved/implemented controls</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <Card className="bg-white/5 border-white/10 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <BarChart3Icon className="w-5 h-5" />
                  Portfolio Overview
                </CardTitle>
                <CardDescription className="text-gray-400">
                  Snapshot from live model and control data
                </CardDescription>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <p className="text-gray-400">Loading dashboard data...</p>
                ) : (
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="rounded-lg border border-white/10 p-4 bg-blue-500/10">
                      <p className="text-gray-300">Total Models</p>
                      <p className="text-xl font-semibold text-white">{totalModels}</p>
                    </div>
                    <div className="rounded-lg border border-white/10 p-4 bg-green-500/10">
                      <p className="text-gray-300">Active Models</p>
                      <p className="text-xl font-semibold text-white">{activeModels}</p>
                    </div>
                    <div className="rounded-lg border border-white/10 p-4 bg-orange-500/10">
                      <p className="text-gray-300">Open Gaps</p>
                      <p className="text-xl font-semibold text-white">{openGaps}</p>
                    </div>
                    <div className="rounded-lg border border-white/10 p-4 bg-purple-500/10">
                      <p className="text-gray-300">Controls Verified</p>
                      <p className="text-xl font-semibold text-white">{controlsVerified}</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          <div>
            <Card className="bg-white/5 border-white/10 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <AlertTriangleIcon className="w-5 h-5" />
                  Recent Alerts
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {summary?.recent_alerts.length ? (
                  summary.recent_alerts.map((alert) => (
                    <div key={alert.id} className={`flex items-start space-x-3 p-3 rounded-lg border ${
                      alert.severity === 'high'
                        ? 'bg-red-500/10 border-red-500/20'
                        : alert.severity === 'medium'
                        ? 'bg-yellow-500/10 border-yellow-500/20'
                        : 'bg-blue-500/10 border-blue-500/20'
                    }`}>
                      <div className={`w-2 h-2 rounded-full mt-2 ${
                        alert.severity === 'high'
                          ? 'bg-red-500'
                          : alert.severity === 'medium'
                          ? 'bg-yellow-500'
                          : 'bg-blue-500'
                      }`}></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-white">{alert.title}</p>
                        <p className="text-xs text-gray-400">{alert.model_name}</p>
                        <p className="text-xs text-gray-500 mt-1">{formatRelativeTime(alert.created_at)}</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-400 text-sm">No alerts found yet.</p>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        <div className="mt-8">
          <Card className="bg-white/5 border-white/10 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <UsersIcon className="w-5 h-5" />
                Active Models Status
              </CardTitle>
              <CardDescription className="text-gray-400">
                Live status derived from current model inventory and controls
              </CardDescription>
            </CardHeader>
            <CardContent>
              {summary?.model_status.length ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {summary.model_status.map((model) => (
                    <div key={model.id} className="p-4 bg-gradient-to-br from-slate-500/10 to-indigo-500/10 border border-white/10 rounded-lg">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-semibold text-white">{model.name}</h3>
                        <Badge className={`${
                          model.status === 'Active'
                            ? 'bg-green-500/20 text-green-300 border-green-500/30'
                            : model.status === 'Draft'
                            ? 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30'
                            : 'bg-gray-500/20 text-gray-300 border-gray-500/30'
                        }`}>
                          {model.status}
                        </Badge>
                      </div>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between text-gray-300">
                          <span>Risk:</span>
                          <span className={
                            model.risk_level === 'High'
                              ? 'text-red-400'
                              : model.risk_level === 'Medium'
                              ? 'text-yellow-400'
                              : 'text-green-400'
                          }>
                            {model.risk_level}
                          </span>
                        </div>
                        <div className="flex justify-between text-gray-300">
                          <span>Control Gaps:</span>
                          <span>{model.gaps}</span>
                        </div>
                        <div className="flex justify-between text-gray-300">
                          <span>Controls Total:</span>
                          <span>{model.controls_total}</span>
                        </div>
                        <div className="flex justify-between text-gray-300">
                          <span>Last Updated:</span>
                          <span>{formatRelativeTime(model.last_updated)}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-400 text-sm">No models available yet. Create models to populate this section.</p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
