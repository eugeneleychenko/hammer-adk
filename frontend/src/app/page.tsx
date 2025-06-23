"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { io, Socket } from "socket.io-client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import {
  Upload,
  FileText,
  Play,
  Pause,
  SkipForward,
  CheckCircle,
  AlertCircle,
  Target,
  Shield,
  Search,
  Handshake,
  RotateCcw,
  Heart,
  MessageSquare,
  DollarSign,
  Waves,
  User,
  Check,
  Zap,
  Settings,
  TrendingUp,
  GraduationCap,
} from "lucide-react"
import LessonsDashboard from "@/components/LessonsDashboard"
import { JobTracker } from "@/lib/jobTracker"
import { getApiUrl, getWebSocketUrl } from "@/lib/config"

// Agent definitions with icons and descriptions
const agents = [
  {
    id: 1,
    name: "Opening Gambit Analyzer",
    icon: Target,
    color: "bg-blue-500",
    description: "Analyzes call openings and rapport establishment",
  },
  {
    id: 2,
    name: "Objection Specialist",
    icon: Shield,
    color: "bg-red-500",
    description: "Identifies and analyzes customer objections",
  },
  {
    id: 3,
    name: "Needs Assessment",
    icon: Search,
    color: "bg-green-500",
    description: "Tracks discovery questions and customer needs",
  },
  {
    id: 4,
    name: "Rapport Building",
    icon: Handshake,
    color: "bg-purple-500",
    description: "Identifies trust-building moments",
  },
  {
    id: 5,
    name: "Pattern Recognition",
    icon: RotateCcw,
    color: "bg-orange-500",
    description: "Finds recurring phrases and sequences",
  },
  {
    id: 6,
    name: "Emotional Intelligence",
    icon: Heart,
    color: "bg-pink-500",
    description: "Tracks emotional dynamics",
  },
  {
    id: 7,
    name: "Language Optimizer",
    icon: MessageSquare,
    color: "bg-indigo-500",
    description: "Analyzes effective phrases",
  },
  {
    id: 8,
    name: "Budget Handling",
    icon: DollarSign,
    color: "bg-yellow-500",
    description: "Tracks pricing discussions and negotiation",
  },
  { id: 9, name: "Conversation Flow", icon: Waves, color: "bg-teal-500", description: "Maps conversation structure" },
  {
    id: 10,
    name: "Client Profiling",
    icon: User,
    color: "bg-cyan-500",
    description: "Identifies customer personality types",
  },
  { id: 11, name: "Micro Commitments", icon: Check, color: "bg-emerald-500", description: "Tracks small agreements" },
  {
    id: 12,
    name: "Urgency Builder",
    icon: Zap,
    color: "bg-amber-500",
    description: "Analyzes soft urgency techniques",
  },
  {
    id: 13,
    name: "Technical Navigation",
    icon: Settings,
    color: "bg-violet-500",
    description: "Handles technical difficulties",
  },
  {
    id: 14,
    name: "Cross-Selling",
    icon: TrendingUp,
    color: "bg-rose-500",
    description: "Captures cross-sell timing and techniques",
  },
]

// Sample insights for the ticker
const sampleInsights = [
  "Referral opening detected in 73% of successful calls",
  "Price objections handled best with value reframing",
  "Personal stories increase rapport by 45%",
  "Budget discussions early in call increase close rate by 40%",
  "Emotional validation reduces objections by 30%",
  "Soft urgency techniques improve conversion by 25%",
  "Technical issues resolved quickly maintain rapport",
  "Cross-selling opportunities identified in 85% of calls",
]

interface UploadedFile {
  id: string
  name: string
  status: "uploading" | "ready" | "processing" | "complete" | "error"
  progress: number
  currentAgent?: number
}

interface AgentStatus {
  id: number
  status: "idle" | "processing" | "complete" | "error" | "paused"
  progress: number
  currentFile?: string
  completedFiles: number
  insights: string[]
  timeElapsed: number
  estimatedRemaining: number
}

// Result file types metadata
const resultFileTypes = [
  { key: "enhanced_prompt", label: "Master System Prompt" },
  { key: "synthesized_learnings", label: "Synthesized Learnings" }
] as const

// Result preview cache type
interface ResultPreviewCache {
  [jobId: string]: {
    [resultKey: string]: {
      status: "loading" | "loaded" | "error"
      content?: string
    }
  }
}

export default function PromptGeneratorUI() {
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [agentStatuses, setAgentStatuses] = useState<AgentStatus[]>(
    agents.map((agent) => ({
      id: agent.id,
      status: "idle",
      progress: 0,
      completedFiles: 0,
      insights: [],
      timeElapsed: 0,
      estimatedRemaining: 0,
    })),
  )
  const [isProcessing, setIsProcessing] = useState(false)
  const [overallProgress, setOverallProgress] = useState(0)
  const [currentInsight, setCurrentInsight] = useState(0)
  const [dragActive, setDragActive] = useState(false)
  const [socket, setSocket] = useState<Socket | null>(null)
  const [analysisResults, setAnalysisResults] = useState<Record<string, any>>({})
  const [viewingResults, setViewingResults] = useState<string | null>(null)
  // cache for individual result file previews
  const [resultPreviews, setResultPreviews] = useState<ResultPreviewCache>({})
  const [activePreview, setActivePreview] = useState<{ jobId: string; key: string } | null>(null)
  const [processedOrder, setProcessedOrder] = useState<number[]>([])

  // Load persisted jobs on component mount
  useEffect(() => {
    const activeJobs = JobTracker.getActiveJobs()
    if (activeJobs.length > 0) {
      setFiles(activeJobs.map(job => ({
        id: job.id,
        name: job.fileName,
        status: job.status,
        progress: job.progress
      })))
      
      // Re-establish socket connection for active jobs
      if (activeJobs.some(job => job.status === 'processing')) {
        setIsProcessing(true)
      }
    }
  }, [])

  // Real file upload to API
  const handleFileUpload = async (uploadedFiles: FileList) => {
    const newFiles: UploadedFile[] = Array.from(uploadedFiles).map((file, index) => ({
      id: `file-${Date.now()}-${index}`,
      name: file.name,
      status: "uploading",
      progress: 0,
    }))

    setFiles((prev) => [...prev, ...newFiles])

    // Upload each file to the API
    for (const file of newFiles) {
      // Save initial job state
      JobTracker.saveJob({
        id: file.id,
        fileName: file.name,
        status: "uploading",
        progress: 0,
        startTime: Date.now()
      })

      try {
        const formData = new FormData()
        const actualFile = Array.from(uploadedFiles).find(f => f.name === file.name)
        if (actualFile) {
          formData.append('file', actualFile)
          
          const uploadResponse = await fetch(getApiUrl('/upload'), {
            method: 'POST',
            body: formData
          })
          
          if (uploadResponse.ok) {
            const uploadResult = await uploadResponse.json()
            setFiles((prev) => prev.map((f) => 
              f.id === file.id 
                ? { ...f, id: uploadResult.job_id, status: "ready", progress: 100 } 
                : f
            ))
            // Update job tracker with new job ID
            JobTracker.saveJob({
              id: uploadResult.job_id,
              fileName: file.name,
              status: "ready",
              progress: 100,
              startTime: Date.now()
            })
          } else {
            setFiles((prev) => prev.map((f) => 
              f.id === file.id 
                ? { ...f, status: "error", progress: 0 } 
                : f
            ))
            JobTracker.updateJobStatus(file.id, "error", 0)
          }
        }
      } catch (error) {
        console.error('Upload error:', error)
        setFiles((prev) => prev.map((f) => 
          f.id === file.id 
            ? { ...f, status: "error", progress: 0 } 
            : f
        ))
        JobTracker.updateJobStatus(file.id, "error", 0)
      }
    }
  }

  // Handle drag and drop
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files)
    }
  }

  // Start real processing via API
  const startProcessing = async () => {
    setIsProcessing(true)

    // Start analysis for each ready file
    const readyFiles = files.filter(f => f.status === "ready")
    
    for (const file of readyFiles) {
      try {
        // Start analysis
        const analysisResponse = await fetch(getApiUrl(`/analyze/${file.id}`), {
          method: 'POST'
        })
        
        if (analysisResponse.ok) {
          setFiles((prev) => prev.map((f) => 
            f.id === file.id 
              ? { ...f, status: "processing" } 
              : f
          ))
        }
      } catch (error) {
        console.error('Analysis start error:', error)
        setFiles((prev) => prev.map((f) => 
          f.id === file.id 
            ? { ...f, status: "error" } 
            : f
        ))
      }
    }
  }

  // WebSocket connection for real-time progress
  useEffect(() => {
    const newSocket = io(getWebSocketUrl())
    setSocket(newSocket)

    newSocket.on('connected', (data) => {
      console.log('Connected to analysis server:', data.message)
    })

    newSocket.on('analysis_progress', (data) => {
      console.log('Received analysis_progress:', data)
      const { job_id, agent_name, status, progress, message } = data
      
      // Map backend agent names to frontend agent IDs
      const agentMapping: Record<string, number> = {
        'opening_gambit': 1,
        'objection_specialist': 2,
        'needs_assessment': 3,
        'rapport_building': 4,
        'pattern_recognition': 5,
        'emotional_intelligence': 6,
        'language_optimizer': 7,
        'budget_handling': 8,
        'conversation_flow': 9,
        'client_profiling': 10,
        'micro_commitments': 11,
        'urgency_builder': 12,
        'technical_navigation': 13,
        'cross_selling': 14
      }

      if (agent_name === 'system') {
        console.log('Updating system status:', status, progress)
        // Update file status for system messages
        const newStatus = status === 'complete' ? 'complete' : 'processing'
        setFiles((prev) => prev.map((f) => 
          f.id === job_id 
            ? { 
                ...f, 
                status: newStatus,
                progress: progress 
              } 
            : f
        ))
        // Update job tracker
        JobTracker.updateJobStatus(job_id, newStatus, progress)
      } else {
        // Update specific agent status
        const agentId = agentMapping[agent_name]
        console.log('Agent mapping:', agent_name, '→', agentId)
        if (agentId) {
          console.log('Updating agent', agentId, 'with status:', status, 'progress:', progress)
          setAgentStatuses((prev) => {
            const updated = prev.map((a) =>
              a.id === agentId
                ? {
                    ...a,
                    status: status as any,
                    progress: progress,
                    currentFile: files.find(f => f.id === job_id)?.name,
                    insights: status === 'complete' && message 
                      ? [...a.insights, message]
                      : a.insights,
                    completedFiles: status === 'complete' ? a.completedFiles + 1 : a.completedFiles
                  }
                : a
            )
            // if agent just completed, record its order
            if (status === 'complete' && !processedOrder.includes(agentId)) {
              setProcessedOrder((po) => [...po, agentId])
            }
            return updated
          })

          // Auto-fetch results when analysis completes
          setTimeout(() => fetchResults(job_id), 1000)
        }
      }
    })

    return () => {
      newSocket.disconnect()
    }
  }, [])

  // Rotate insights ticker
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentInsight((prev) => (prev + 1) % sampleInsights.length)
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  // Calculate overall progress
  useEffect(() => {
    const totalFiles = files.length
    const completedFiles = files.filter((f) => f.status === "complete").length
    setOverallProgress(totalFiles > 0 ? (completedFiles / totalFiles) * 100 : 0)
  }, [files])

  // Fetch results for completed files
  const fetchResults = async (jobId: string) => {
    try {
      const response = await fetch(getApiUrl(`/results/${jobId}`))
      if (response.ok) {
        const results = await response.json()
        setAnalysisResults(prev => ({ ...prev, [jobId]: results }))
      }
    } catch (error) {
      console.error('Error fetching results:', error)
    }
  }

  const fetchResultFile = async (jobId: string, key: string) => {
    // if already loaded or loading, do nothing
    if (resultPreviews[jobId]?.[key]?.status === "loading" || resultPreviews[jobId]?.[key]?.status === "loaded") {
      return
    }

    setResultPreviews(prev => ({
      ...prev,
      [jobId]: {
        ...prev[jobId],
        [key]: { status: "loading" }
      }
    }))

    try {
      const res = await fetch(getApiUrl(`/download/${jobId}/${key}`))
      if (!res.ok) throw new Error("Not available")
      const text = await res.text()
      setResultPreviews(prev => ({
        ...prev,
        [jobId]: {
          ...prev[jobId],
          [key]: { status: "loaded", content: text }
        }
      }))
    } catch {
      setResultPreviews(prev => ({
        ...prev,
        [jobId]: {
          ...prev[jobId],
          [key]: { status: "error", content: "Unavailable" }
        }
      }))
    }
  }

  const readyFiles = files.filter((f) => f.status === "ready" || f.status === "complete")

  const sortedAgents = [...agents].sort((a, b) => {
    // if both in processedOrder, compare index
    const aIndex = processedOrder.indexOf(a.id)
    const bIndex = processedOrder.indexOf(b.id)

    if (aIndex !== -1 && bIndex !== -1) return aIndex - bIndex
    // completed ones come before others
    if (aIndex !== -1) return -1
    if (bIndex !== -1) return 1
    // current processing agent to top
    const aStatus = agentStatuses.find(s => s.id === a.id)
    const bStatus = agentStatuses.find(s => s.id === b.id)
    if (aStatus?.status === 'processing' && bStatus?.status !== 'processing') return -1
    if (bStatus?.status === 'processing' && aStatus?.status !== 'processing') return 1
    return a.id - b.id
  })

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold text-slate-900">System Prompt Generator</h1>
          <p className="text-lg text-slate-600 max-w-3xl mx-auto">
            Upload your sales call transcripts and generate optimized system prompts powered by 14 specialized AI agents that analyze every aspect of your sales conversations.
          </p>
        </div>

        {/* Upload Zone */}
        <Card className="border-2 border-dashed border-slate-300 hover:border-blue-400 transition-colors">
          <CardContent className="p-8">
            <div
              className={`text-center space-y-4 ${dragActive ? "bg-blue-50 border-blue-400" : ""}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <Upload className="mx-auto h-12 w-12 text-slate-400" />
              <div>
                <p className="text-lg font-medium text-slate-700">Drop sales call PDFs here to generate system prompts</p>
                <p className="text-sm text-slate-500">Supports PDF files up to 10MB each - generates optimized prompts from analysis</p>
              </div>
              <input
                type="file"
                multiple
                accept=".pdf"
                onChange={(e) => e.target.files && handleFileUpload(e.target.files)}
                className="hidden"
                id="file-upload"
              />
              <Button asChild variant="outline" className="bg-white text-black">
                <label htmlFor="file-upload" className="cursor-pointer">
                  Browse Files
                </label>
              </Button>
            </div>

            {/* Uploaded Files */}
            {files.length > 0 && (
              <div className="mt-6 grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                {files.map((file) => (
                  <div key={file.id} className="bg-white rounded-lg p-3 shadow-sm border">
                    <div className="flex items-center space-x-2">
                      <FileText className="h-4 w-4 text-slate-500" />
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-medium text-slate-700 truncate">{file.name}</p>
                        <div className="flex items-center space-x-1 mt-1">
                          {file.status === "uploading" && (
                            <div className="h-2 w-2 bg-blue-500 rounded-full animate-pulse" />
                          )}
                          {file.status === "ready" && <CheckCircle className="h-3 w-3 text-green-500" />}
                          {file.status === "processing" && (
                            <div className="h-2 w-2 bg-yellow-500 rounded-full animate-pulse" />
                          )}
                          {file.status === "complete" && <CheckCircle className="h-3 w-3 text-green-500" />}
                          {file.status === "error" && <AlertCircle className="h-3 w-3 text-red-500" />}
                          <span className="text-xs text-slate-500">{file.status}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Overall Progress */}
        {files.length > 0 && (
          <Card>
            <CardContent className="p-6">
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-semibold">Overall Progress</h3>
                  <div className="flex space-x-2">
                    {!isProcessing && readyFiles.length > 0 && (
                      <Button onClick={startProcessing} className="bg-blue-600 hover:bg-blue-700">
                        <Play className="h-4 w-4 mr-2" />
                        Start Analysis
                      </Button>
                    )}
                    <Button 
                      onClick={() => {
                        JobTracker.clearCompletedJobs()
                        setFiles([])
                        setIsProcessing(false)
                        setAgentStatuses(agents.map((agent) => ({
                          id: agent.id,
                          status: "idle",
                          progress: 0,
                          completedFiles: 0,
                          insights: [],
                          timeElapsed: 0,
                          estimatedRemaining: 0,
                        })))
                      }} 
                      variant="outline"
                      className="text-xs"
                    >
                      Clear State
                    </Button>
                  </div>
                </div>
                <Progress value={overallProgress} className="h-3" />
                <div className="flex justify-between text-sm text-slate-600">
                  <span>
                    {files.filter((f) => f.status === "complete").length}/{files.length} PDFs Complete
                  </span>
                  <span>{Math.round(overallProgress)}%</span>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Agent Status Cards */}
        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-slate-900">Analysis Agents</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {sortedAgents.map((agent) => {
              const status = agentStatuses.find((s) => s.id === agent.id)!
              const IconComponent = agent.icon

              return (
                <Card
                  key={agent.id}
                  className={`relative overflow-hidden transition-all duration-300 ${
                    status.status === "processing"
                      ? "ring-2 ring-blue-400 shadow-lg"
                      : status.status === "complete"
                        ? "ring-2 ring-green-400"
                        : status.status === "error"
                          ? "ring-2 ring-red-400"
                          : ""
                  }`}
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-lg ${agent.color} text-white`}>
                        <IconComponent className="h-5 w-5" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <CardTitle className="text-sm font-semibold truncate">{agent.name}</CardTitle>
                        <p className="text-xs text-slate-500 mt-1">{agent.description}</p>
                      </div>
                    </div>
                  </CardHeader>

                  <CardContent className="space-y-4">
                    {/* Progress Bar */}
                    <div className="space-y-2">
                      <div className="flex justify-between text-xs">
                        <span>Progress</span>
                        <span>{Math.round(status.progress)}%</span>
                      </div>
                      <Progress value={status.progress} className="h-2" />
                    </div>

                    {/* Current Status */}
                    {status.status === "processing" && status.currentFile && (
                      <div className="space-y-2">
                        <p className="text-xs font-medium text-slate-700">Currently Processing:</p>
                        <p className="text-xs text-slate-600 truncate">📄 {status.currentFile}</p>
                        <p className="text-xs text-slate-500">
                          ⏱️ {Math.floor(status.timeElapsed / 60)}:
                          {(status.timeElapsed % 60).toString().padStart(2, "0")} / ~
                          {Math.floor(status.estimatedRemaining / 60)}:
                          {(status.estimatedRemaining % 60).toString().padStart(2, "0")} remaining
                        </p>
                      </div>
                    )}

                    {/* Latest Insight */}
                    {status.insights.length > 0 && (
                      <div className="space-y-2">
                        <p className="text-xs font-medium text-slate-700">Latest Insight:</p>
                        <p className="text-xs text-slate-600 italic">&quot;{status.insights[status.insights.length - 1]}&quot;</p>
                      </div>
                    )}

                    {/* Stats */}
                    <div className="flex justify-between items-center pt-2 border-t">
                      <div className="flex space-x-3 text-xs">
                        <span className="flex items-center space-x-1">
                          <CheckCircle className="h-3 w-3 text-green-500" />
                          <span>{status.completedFiles}</span>
                        </span>
                        {status.status === "error" && (
                          <span className="flex items-center space-x-1">
                            <AlertCircle className="h-3 w-3 text-red-500" />
                            <span>1</span>
                          </span>
                        )}
                      </div>

                      <Badge
                        variant={
                          status.status === "processing"
                            ? "default"
                            : status.status === "complete"
                              ? "secondary"
                              : status.status === "error"
                                ? "destructive"
                                : "outline"
                        }
                      >
                        {status.status}
                      </Badge>
                    </div>

                    {/* Action Buttons */}
                    {status.status === "processing" && (
                      <div className="flex space-x-2">
                        <Button size="sm" variant="outline" className="flex-1 text-xs bg-white text-black">
                          <Pause className="h-3 w-3 mr-1" />
                          Pause
                        </Button>
                        <Button size="sm" variant="outline" className="flex-1 text-xs bg-white text-black">
                          <SkipForward className="h-3 w-3 mr-1" />
                          Skip
                        </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>

        {/* Insights Ticker */}
        {isProcessing && (
          <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
            <CardContent className="p-4">
              <div className="flex items-center space-x-4">
                <div className="flex-shrink-0">
                  <div className="h-3 w-3 bg-blue-500 rounded-full animate-pulse"></div>
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-blue-900">Live Insight: {sampleInsights[currentInsight]}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Results & Downloads */}
        {files.some(f => f.status === "complete") && (
          <Card>
            <CardHeader>
              <CardTitle>Analysis Results & Downloads</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {files.filter(f => f.status === "complete").map((file) => (
                <div key={file.id} className="border rounded-lg p-4">
                  <h4 className="font-semibold text-lg mb-3">{file.name}</h4>
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
                    {resultFileTypes.map(({ key, label }) => {
                      const previewStatus = resultPreviews[file.id]?.[key]?.status
                      // Show disabled button if fetch resulted in error
                      return (
                        <Button
                          key={key}
                          variant="outline"
                          size="sm"
                          disabled={previewStatus === "error"}
                          className="text-xs"
                          onClick={() => {
                            fetchResultFile(file.id, key).then(() => {
                              setActivePreview(prev =>
                                prev && prev.jobId === file.id && prev.key === key ? null : { jobId: file.id, key }
                              )
                            })
                          }}
                        >
                          {label}
                        </Button>
                      )
                    })}
                  </div>

                  {/* Inline preview */}
                  {activePreview && activePreview.jobId === file.id && (
                    <div className="mt-4 p-4 bg-gray-50 rounded-lg max-h-96 overflow-auto border">
                      {(() => {
                        const { key } = activePreview
                        const preview = resultPreviews[file.id]?.[key]
                        if (!preview) return <p className="text-sm">Loading...</p>
                        if (preview.status === "loading") return <p className="text-sm">Loading {key}...</p>
                        if (preview.status === "error") return <p className="text-sm text-red-500">{key} not available.</p>
                        return (
                          <pre className="text-xs whitespace-pre-wrap">
                            {preview.content}
                          </pre>
                        )
                      })()}
                    </div>
                  )}

                  <div className="mt-4 pt-4 border-t">
                    <Button 
                      variant="secondary" 
                      size="sm"
                      onClick={() => {
                        if (!analysisResults[file.id]) {
                          fetchResults(file.id)
                        }
                        setViewingResults(viewingResults === file.id ? null : file.id)
                      }}
                      className="mb-3"
                    >
                      {viewingResults === file.id ? 'Hide' : 'View'} Full Analysis Results
                    </Button>
                    
                    {viewingResults === file.id && analysisResults[file.id] && (
                      <div className="bg-gray-50 p-4 rounded-lg max-h-96 overflow-auto">
                        <h5 className="font-semibold mb-2">Analysis Summary:</h5>
                        <div className="text-sm space-y-2">
                          <p><strong>Source:</strong> {analysisResults[file.id].source_file}</p>
                          <p><strong>Date:</strong> {new Date(analysisResults[file.id].analysis_date).toLocaleString()}</p>
                          <p><strong>Agents Run:</strong> {analysisResults[file.id].agents_run?.join(', ')}</p>
                          
                          {analysisResults[file.id].master_insights && (
                            <div className="mt-4">
                              <h6 className="font-semibold">Key Insights:</h6>
                              <div className="bg-white p-3 rounded border mt-2">
                                <pre className="text-xs whitespace-pre-wrap">
                                  {JSON.stringify(analysisResults[file.id].master_insights, null, 2)}
                                </pre>
                              </div>
                            </div>
                          )}

                          {/* Lessons Learned */}
                          {analysisResults[file.id].lessons_learned && Array.isArray(analysisResults[file.id].lessons_learned) && (
                            <div className="mt-4">
                              <h6 className="font-semibold">Lessons Learned:</h6>
                              <ul className="list-disc list-inside text-sm space-y-1 mt-2">
                                {analysisResults[file.id].lessons_learned.map((lesson: string, idx: number) => (
                                  <li key={idx}>{lesson}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Lessons Learning System */}
        {files.some(f => f.status === "complete") && (
          <div className="space-y-6">
            <div className="flex items-center space-x-3">
              <GraduationCap className="h-8 w-8 text-blue-600" />
              <div>
                <h2 className="text-2xl font-bold text-slate-900">Learning System</h2>
                <p className="text-slate-600">Self-improving lessons extraction and plateau detection</p>
              </div>
            </div>
            
            <LessonsDashboard 
              socket={socket || undefined}
              isVisible={files.some(f => f.status === "complete")}
            />
          </div>
        )}
      </div>
    </div>
  )
}
