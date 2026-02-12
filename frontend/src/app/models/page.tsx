'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { AdvancedFilters } from '@/components/ui/filters';
import { SearchHistory } from '@/components/ui/search-history';
import { ModelForm } from '@/components/ui/model-form';
import { modelApi } from '@/lib/api';
import { 
  BrainCircuitIcon, 
  ShieldCheckIcon, 
  TrendingUpIcon, 
  AlertTriangleIcon,
  PlusIcon,
  SearchIcon,
  ArrowRightIcon
} from 'lucide-react';

export default function ModelsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({});
  const [models, setModels] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [displayCount, setDisplayCount] = useState(4);
  
  const normalizeModel = (model: any) => {
    const status = String(model.status || model.governance_status || 'draft');
    const normalizedStatus = status.charAt(0).toUpperCase() + status.slice(1).toLowerCase();
    const risk = model.riskLevel || model.risk_level || 'Medium';
    const updated = model.updated_at || model.created_at;

    return {
      id: String(model.id),
      name: model.name || 'Unnamed Model',
      description: model.description || '',
      category: model.category || 'General',
      riskLevel: risk,
      status: normalizedStatus,
      accuracy: model.accuracy || 'N/A',
      lastUpdated: updated ? new Date(updated).toLocaleDateString() : model.lastUpdated || 'N/A'
    };
  };

  const normalizeModels = (items: any[]) => items.map(normalizeModel);

  const handleModelCreated = () => {
    // Refresh models list
    const fetchModels = async () => {
      try {
        const results = await modelApi.getAll(filters);
        setModels(normalizeModels(results));
        setError(null);
      } catch (error) {
        console.error('Error refreshing models:', error);
        setError('Unable to load models from API.');
        setModels([]);
      }
    };
    fetchModels();
  };

  useEffect(() => {
    const fetchModels = async () => {
      setLoading(true);
      try {
        if (searchTerm) {
          const results = await modelApi.search(searchTerm);
          setModels(normalizeModels(results));
        } else {
          const results = await modelApi.getAll(filters);
          setModels(normalizeModels(results));
        }
        setError(null);
      } catch (error) {
        console.error('Error fetching models:', error);
        setError('Unable to load models from API.');
        setModels([]);
      } finally {
        setLoading(false);
      }
    };

    const debounce = setTimeout(fetchModels, 300);
    return () => clearTimeout(debounce);
  }, [searchTerm, filters]);

  const filteredModels = models.filter(model => 
    model.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    model.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (model.category || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'High': return 'bg-red-500/20 text-red-300 border-red-500/30';
      case 'Medium': return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30';
      case 'Low': return 'bg-green-500/20 text-green-300 border-green-500/30';
      default: return 'bg-gray-500/20 text-gray-300 border-gray-500/30';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Active': return 'bg-green-500/20 text-green-300 border-green-500/30';
      case 'Draft': return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
      case 'Inactive': return 'bg-gray-500/20 text-gray-300 border-gray-500/30';
      default: return 'bg-gray-500/20 text-gray-300 border-gray-500/30';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/" className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                  <BrainCircuitIcon className="w-6 h-6 text-white" />
                </div>
                <span className="text-2xl font-bold text-white">LifeAI</span>
              </Link>
              <div className="hidden md:flex space-x-6 ml-8">
                <Link href="/dashboard" className="text-gray-300 hover:text-white transition-colors">Dashboard</Link>
                <Link href="/models" className="text-white font-medium">Models</Link>
              </div>
            </div>
            <Button 
              onClick={() => setShowForm(true)}
              className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
            >
              <PlusIcon className="w-4 h-4 mr-2" />
              New Model
            </Button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-4">AI Models</h1>
          <p className="text-xl text-gray-300">Manage and monitor your AI models across the enterprise</p>
        </div>

        {/* Filters and Search */}
        <div className="flex flex-col sm:flex-row gap-4 mb-8">
          <div className="relative flex-1">
            <SearchHistory 
              onSelectSearch={setSearchTerm}
              currentSearch={searchTerm}
            >
              <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input 
                type="text" 
                placeholder="Search models by name, category, or description..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-white/10 border border-white/20 rounded-lg pl-12 pr-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 backdrop-blur-sm"
              />
            </SearchHistory>
          </div>
          <AdvancedFilters onFiltersChange={setFilters} />
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="bg-gradient-to-br from-blue-500/20 to-blue-600/20 border-blue-400/30 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-200 text-sm font-medium">Total Models</p>
                  <p className="text-3xl font-bold text-white">{models.length}</p>
                </div>
                <BrainCircuitIcon className="w-8 h-8 text-blue-400" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-green-500/20 to-green-600/20 border-green-400/30 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-200 text-sm font-medium">Active</p>
                  <p className="text-3xl font-bold text-white">{models.filter(m => m.status === 'Active').length}</p>
                </div>
                <ShieldCheckIcon className="w-8 h-8 text-green-400" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-yellow-500/20 to-yellow-600/20 border-yellow-400/30 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-yellow-200 text-sm font-medium">Draft</p>
                  <p className="text-3xl font-bold text-white">{models.filter(m => m.status === 'Draft').length}</p>
                </div>
                <AlertTriangleIcon className="w-8 h-8 text-yellow-400" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-purple-500/20 to-purple-600/20 border-purple-400/30 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-purple-200 text-sm font-medium">Inactive</p>
                  <p className="text-3xl font-bold text-white">{models.filter(m => m.status === 'Inactive').length}</p>
                </div>
                <TrendingUpIcon className="w-8 h-8 text-purple-400" />
              </div>
            </CardContent>
          </Card>
        </div>

        {error && (
          <div className="mb-6 rounded-lg border border-red-500/40 bg-red-500/15 px-4 py-3 text-sm text-red-200">
            {error}
          </div>
        )}

        {/* Models Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {loading ? (
            <div className="col-span-full text-center py-12">
              <p className="text-gray-400 text-lg">Loading models...</p>
            </div>
          ) : filteredModels.length > 0 ? (
            filteredModels.slice(0, displayCount).map((model) => (
              <Card key={model.id} className="bg-white/5 border-white/10 backdrop-blur-sm hover:bg-white/10 transition-all duration-300 group">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-white text-lg mb-2 group-hover:text-blue-300 transition-colors">
                        {model.name}
                      </CardTitle>
                      <CardDescription className="text-gray-400 text-sm leading-relaxed">
                        {model.description}
                      </CardDescription>
                    </div>
                    <div className="flex flex-col gap-2 ml-4">
                      <Badge className={getRiskColor(model.riskLevel)}>
                        {model.riskLevel} Risk
                      </Badge>
                      <Badge className={getStatusColor(model.status)}>
                        {model.status}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-gray-400 text-xs uppercase tracking-wide">Accuracy</p>
                      <p className="text-white font-semibold">{model.accuracy}</p>
                    </div>
                    <div>
                      <p className="text-gray-400 text-xs uppercase tracking-wide">Category</p>
                      <p className="text-white font-semibold">{model.category}</p>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <p className="text-gray-500 text-sm">Updated {model.lastUpdated}</p>
                    <Link 
                      href={`/models/${model.id}`}
                      className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 transition-colors group/link"
                    >
                      View Details
                      <ArrowRightIcon className="w-4 h-4 group-hover/link:translate-x-1 transition-transform" />
                    </Link>
                  </div>
                </CardContent>
              </Card>
            ))
          ) : (
            <div className="col-span-full text-center py-12">
              <p className="text-gray-400 text-lg">No models found matching "{searchTerm}"</p>
            </div>
          )}
        </div>

        {/* Load More */}
        {filteredModels.length > displayCount && (
          <div className="text-center mt-12">
            <Button 
              onClick={() => setDisplayCount(prev => prev + 4)}
              variant="outline" 
              className="bg-white/10 border-white/20 text-white hover:bg-white/20 px-8 py-3"
            >
              Load More Models ({filteredModels.length - displayCount} remaining)
            </Button>
          </div>
        )}
      </div>
      
      {showForm && (
        <ModelForm 
          onClose={() => setShowForm(false)}
          onSuccess={handleModelCreated}
        />
      )}
    </div>
  );
}
