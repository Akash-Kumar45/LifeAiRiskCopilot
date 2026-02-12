'use client';

import { useState } from 'react';
import { Button } from './button';
import { Card, CardContent, CardHeader, CardTitle } from './card';
import { Badge } from './badge';
import { FilterIcon, XIcon } from 'lucide-react';

interface FilterProps {
  onFiltersChange: (filters: any) => void;
}

export function AdvancedFilters({ onFiltersChange }: FilterProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [filters, setFilters] = useState({
    risk: '',
    status: '',
    dateFrom: '',
    dateTo: ''
  });

  const updateFilter = (key: string, value: string) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const clearFilters = () => {
    const emptyFilters = { risk: '', status: '', dateFrom: '', dateTo: '' };
    setFilters(emptyFilters);
    onFiltersChange(emptyFilters);
  };

  const activeFiltersCount = Object.values(filters).filter(v => v).length;

  return (
    <div className="relative">
      <Button 
        variant="outline" 
        className="bg-white/10 border-white/20 text-white hover:bg-white/20"
        onClick={() => setIsOpen(!isOpen)}
      >
        <FilterIcon className="w-4 h-4 mr-2" />
        Filters
        {activeFiltersCount > 0 && (
          <Badge className="ml-2 bg-blue-500 text-white">{activeFiltersCount}</Badge>
        )}
      </Button>

      {isOpen && (
        <Card className="absolute top-12 right-0 w-80 bg-white/10 border-white/20 backdrop-blur-sm z-50">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-white text-sm">Advanced Filters</CardTitle>
            <Button variant="ghost" size="sm" onClick={() => setIsOpen(false)}>
              <XIcon className="w-4 h-4 text-white" />
            </Button>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-white text-sm font-medium">Risk Level</label>
              <select 
                value={filters.risk}
                onChange={(e) => updateFilter('risk', e.target.value)}
                className="w-full mt-1 bg-white/10 border border-white/20 rounded text-white p-2"
              >
                <option value="">All Risk Levels</option>
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
              </select>
            </div>

            <div>
              <label className="text-white text-sm font-medium">Status</label>
              <select 
                value={filters.status}
                onChange={(e) => updateFilter('status', e.target.value)}
                className="w-full mt-1 bg-white/10 border border-white/20 rounded text-white p-2"
              >
                <option value="">All Statuses</option>
                <option value="Active">Active</option>
                <option value="Draft">Draft</option>
                <option value="Inactive">Inactive</option>
              </select>
            </div>

            <div>
              <label className="text-white text-sm font-medium">Date From</label>
              <input 
                type="date"
                value={filters.dateFrom}
                onChange={(e) => updateFilter('dateFrom', e.target.value)}
                className="w-full mt-1 bg-white/10 border border-white/20 rounded text-white p-2"
              />
            </div>

            <div>
              <label className="text-white text-sm font-medium">Date To</label>
              <input 
                type="date"
                value={filters.dateTo}
                onChange={(e) => updateFilter('dateTo', e.target.value)}
                className="w-full mt-1 bg-white/10 border border-white/20 rounded text-white p-2"
              />
            </div>

            <Button 
              variant="outline" 
              onClick={clearFilters}
              className="w-full bg-red-500/20 border-red-500/30 text-red-300 hover:bg-red-500/30"
            >
              Clear All Filters
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}