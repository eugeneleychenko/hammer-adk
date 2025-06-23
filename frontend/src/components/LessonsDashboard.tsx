"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  GraduationCap, 
  TrendingUp, 
  TrendingDown, 
  Minus,
  AlertTriangle,
  CheckCircle,
  Clock,
  BarChart3
} from 'lucide-react';
import { Socket } from 'socket.io-client';
import { getApiUrl } from '@/lib/config';

interface LessonsMetrics {
  total_pdfs_processed: number;
  total_lessons: number;
  deduplication_rate: number;
  plateau_status: boolean;
  recent_lessons_added: number;
  unique_categories: number;
  data_collection_status: 'active_learning' | 'diminishing_returns' | 'plateau_reached' | 'full_saturation';
  estimated_completion: number;
}

interface PlateauStatus {
  is_plateaued: boolean;
  recommendations: string[];
  plateau_detected_date?: string;
  recent_lessons_added: number;
  trend_direction: 'increasing' | 'stable' | 'decreasing';
  uniqueness_rate: number;
  deduplication_rate: number;
}

interface LessonCategory {
  name: string;
  total_lessons: number;
  recent_additions: number;
  saturation_level: 'low' | 'medium' | 'high' | 'saturated';
}

interface LessonsDashboardProps {
  socket?: Socket;
  isVisible?: boolean;
}

export default function LessonsDashboard({ socket, isVisible = true }: LessonsDashboardProps) {
  const [metrics, setMetrics] = useState<LessonsMetrics | null>(null);
  const [plateauStatus, setPlateauStatus] = useState<PlateauStatus | null>(null);
  const [categories, setCategories] = useState<LessonCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch lessons data
  const fetchLessonsData = async () => {
    try {
      setLoading(true);
      
      // Fetch metrics
      const metricsResponse = await fetch(getApiUrl('/lessons/metrics'));
      if (metricsResponse.ok) {
        const metricsData = await metricsResponse.json();
        setMetrics(metricsData);
      }
      
      // Fetch plateau status
      const plateauResponse = await fetch(getApiUrl('/lessons/plateau-status'));
      if (plateauResponse.ok) {
        const plateauData = await plateauResponse.json();
        setPlateauStatus(plateauData);
      }
      
      // Fetch categories
      const categoriesResponse = await fetch(getApiUrl('/lessons/categories'));
      if (categoriesResponse.ok) {
        const categoriesData = await categoriesResponse.json();
        setCategories(categoriesData.categories || []);
      }
      
      setError(null);
    } catch (err) {
      console.error('Error fetching lessons data:', err);
      setError('Failed to load lessons data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isVisible) {
      fetchLessonsData();
    }
  }, [isVisible]);

  // Socket listeners for real-time updates
  useEffect(() => {
    if (socket && isVisible) {
      const handleLessonsUpdate = () => {
        // Refresh data when lessons are updated
        fetchLessonsData();
      };

      socket.on('lessons_extraction_progress', handleLessonsUpdate);
      socket.on('lessons_deduplication_complete', handleLessonsUpdate);

      return () => {
        socket.off('lessons_extraction_progress', handleLessonsUpdate);
        socket.off('lessons_deduplication_complete', handleLessonsUpdate);
      };
    }
  }, [socket, isVisible]);

  if (!isVisible) {
    return null;
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <GraduationCap className="h-6 w-6 text-blue-600" />
              <span>Learning System</span>
            </CardTitle>
            <CardDescription>Loading lessons data...</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="animate-pulse space-y-3">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              <div className="h-4 bg-gray-200 rounded w-5/6"></div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-red-600">
            <AlertTriangle className="h-6 w-6" />
            <span>Learning System</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-red-600">{error}</p>
        </CardContent>
      </Card>
    );
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active_learning':
        return <TrendingUp className="h-4 w-4 text-green-500" />;
      case 'diminishing_returns':
        return <Minus className="h-4 w-4 text-yellow-500" />;
      case 'plateau_reached':
        return <TrendingDown className="h-4 w-4 text-orange-500" />;
      case 'full_saturation':
        return <CheckCircle className="h-4 w-4 text-blue-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active_learning':
        return 'bg-green-100 text-green-800';
      case 'diminishing_returns':
        return 'bg-yellow-100 text-yellow-800';
      case 'plateau_reached':
        return 'bg-orange-100 text-orange-800';
      case 'full_saturation':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getSaturationColor = (level: string) => {
    switch (level) {
      case 'low':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'high':
        return 'bg-orange-100 text-orange-800';
      case 'saturated':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Lessons Overview */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <GraduationCap className="h-6 w-6 text-blue-600" />
              <span>Lessons Overview</span>
            </CardTitle>
            <CardDescription>Current learning system metrics</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {metrics && (
              <>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-gray-600">Total Lessons</p>
                    <p className="text-2xl font-bold text-blue-600">{metrics.total_lessons}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-gray-600">PDFs Processed</p>
                    <p className="text-2xl font-bold text-gray-900">{metrics.total_pdfs_processed}</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-gray-600">Recent Additions</p>
                    <p className="text-xl font-semibold text-green-600">{metrics.recent_lessons_added}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-gray-600">Categories</p>
                    <p className="text-xl font-semibold text-gray-900">{metrics.unique_categories}</p>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium text-gray-600">Learning Progress</span>
                    <span className="text-gray-900">{metrics.estimated_completion.toFixed(1)}%</span>
                  </div>
                  <Progress value={metrics.estimated_completion} className="h-2" />
                </div>

                <div className="flex items-center justify-between">
                  <Badge className={getStatusColor(metrics.data_collection_status)}>
                    <div className="flex items-center space-x-1">
                      {getStatusIcon(metrics.data_collection_status)}
                      <span className="capitalize">{metrics.data_collection_status.replace('_', ' ')}</span>
                    </div>
                  </Badge>
                  <div className="text-sm text-gray-600">
                    Dedup Rate: {(metrics.deduplication_rate * 100).toFixed(1)}%
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* Plateau Detection */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="h-6 w-6 text-purple-600" />
              <span>Plateau Detection</span>
            </CardTitle>
            <CardDescription>Learning trend analysis</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {plateauStatus && (
              <>
                <div className="flex items-center justify-between">
                  <span className="font-medium">Status:</span>
                  <Badge className={plateauStatus.is_plateaued ? 'bg-orange-100 text-orange-800' : 'bg-green-100 text-green-800'}>
                    {plateauStatus.is_plateaued ? 'Plateau Detected' : 'Active Learning'}
                  </Badge>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-600">Trend:</span>
                    <div className="flex items-center space-x-1 mt-1">
                      {plateauStatus.trend_direction === 'increasing' && <TrendingUp className="h-4 w-4 text-green-500" />}
                      {plateauStatus.trend_direction === 'stable' && <Minus className="h-4 w-4 text-yellow-500" />}
                      {plateauStatus.trend_direction === 'decreasing' && <TrendingDown className="h-4 w-4 text-red-500" />}
                      <span className="capitalize">{plateauStatus.trend_direction}</span>
                    </div>
                  </div>
                  <div>
                    <span className="font-medium text-gray-600">Uniqueness:</span>
                    <p className="mt-1">{(plateauStatus.uniqueness_rate * 100).toFixed(1)}%</p>
                  </div>
                </div>

                {plateauStatus.is_plateaued && plateauStatus.recommendations.length > 0 && (
                  <div className="space-y-2">
                    <p className="font-medium text-gray-900">Recommendations:</p>
                    <ul className="space-y-1 text-sm text-gray-700">
                      {plateauStatus.recommendations.map((rec, index) => (
                        <li key={index} className="flex items-start space-x-2">
                          <span className="text-orange-500 mt-0.5">•</span>
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {plateauStatus.plateau_detected_date && (
                  <div className="text-xs text-gray-500">
                    Plateau detected: {new Date(plateauStatus.plateau_detected_date).toLocaleDateString()}
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Category Breakdown */}
      {categories.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Lesson Categories</CardTitle>
            <CardDescription>Breakdown by lesson type and saturation level</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {categories.map((category, index) => (
                <div key={index} className="border rounded-lg p-3 space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-gray-900 capitalize">
                      {category.name.replace('_', ' ')}
                    </h4>
                    <Badge className={getSaturationColor(category.saturation_level)}>
                      {category.saturation_level}
                    </Badge>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-gray-600">Total:</span>
                      <p className="font-semibold">{category.total_lessons}</p>
                    </div>
                    <div>
                      <span className="text-gray-600">Recent:</span>
                      <p className="font-semibold text-green-600">+{category.recent_additions}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}