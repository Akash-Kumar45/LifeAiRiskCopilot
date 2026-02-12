'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { RefreshCw } from 'lucide-react';
import { modelApi, ModelDetail } from '@/lib/api';

export default function ModelDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [model, setModel] = useState<ModelDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    const fetchModel = async () => {
      try {
        const modelData = await modelApi.getById(id);
        setModel(modelData);
      } catch (error) {
        console.error('Error fetching model:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchModel();
  }, [id]);

  const handleAnalyze = async () => {
    if (!model) return;
    
    setAnalyzing(true);
    try {
      const updatedModel = await modelApi.analyze(model.id);
      setModel(updatedModel);
    } catch (error) {
      console.error('Error analyzing model:', error);
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto py-10">
        <p>Loading model details...</p>
      </div>
    );
  }

  if (!model) {
    return (
      <div className="container mx-auto py-10">
        <p>Model not found</p>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Approved':
        return 'bg-green-100 text-green-800';
      case 'Drafted':
        return 'bg-yellow-100 text-yellow-800';
      case 'Pending':
        return 'bg-gray-100 text-gray-800';
      case 'Proposed':
        return 'bg-blue-100 text-blue-800';
      case 'Gap':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="container mx-auto py-8 px-4 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">{model.name}</h1>
        <p className="text-gray-600 mt-2">{model.description}</p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Model Documentation</CardTitle>
            <CardDescription>AI-generated documentation for this model</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="prose max-w-none">
              {model.documentation ? (
                <pre className="whitespace-pre-wrap text-sm text-gray-800 font-sans">
                  {model.documentation}
                </pre>
              ) : (
                <p className="text-gray-500 italic">No documentation available</p>
              )}
            </div>
          </CardContent>
        </Card>
        
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Model Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Governance Status</h3>
                  <Badge className={getStatusColor(model.governance_status)}>
                    {model.governance_status}
                  </Badge>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Risk Level</h3>
                  <Badge 
                    variant={model.risk_level === 'High' ? 'destructive' : model.risk_level === 'Medium' ? 'default' : 'secondary'}
                  >
                    {model.risk_level}
                  </Badge>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Created</h3>
                  <p>{new Date(model.created_at).toLocaleDateString()}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Last Updated</h3>
                  <p>{new Date(model.updated_at).toLocaleDateString()}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Button 
            onClick={handleAnalyze} 
            disabled={analyzing}
            className="w-full"
          >
            {analyzing ? (
              <>
                <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              'Analyze with Copilot'
            )}
          </Button>
        </div>
      </div>
      
      {/* Control Mapping Table */}
      <Card>
        <CardHeader>
          <CardTitle>Control Mapping</CardTitle>
          <CardDescription>Mapping of OSFI controls to AI rationale</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>OSFI Control</TableHead>
                <TableHead>AI Rationale</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {model.controls && model.controls.length > 0 ? (
                model.controls.map((control, index) => (
                  <TableRow key={index}>
                    <TableCell className="font-medium">{control.osfi_control}</TableCell>
                    <TableCell>{control.ai_rationale}</TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(control.status)}>
                        {control.status}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={3} className="text-center text-gray-500">
                    No control mappings available
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
