import { useCallback, useEffect, useState } from 'react'
import { AlertCircle, Brain, CheckCircle2, Crosshair, Upload, Zap } from 'lucide-react'
import { AnimatePresence, motion } from 'framer-motion'
import { analyzeWafer } from '../api'
import { DashboardHeader } from '../components/ui'

export function AnalyzePage() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl)
      }
    }
  }, [previewUrl])

  const handleFile = useCallback((file) => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
    }

    setSelectedFile(file)
    setResult(null)
    setError('')

    if (file) {
      setPreviewUrl(URL.createObjectURL(file))
    } else {
      setPreviewUrl('')
    }
  }, [previewUrl])

  function handleFileChange(event) {
    const file = event.target.files?.[0] || null
    handleFile(file)
  }

  const onDrop = useCallback((event) => {
    event.preventDefault()
    const file = event.dataTransfer.files?.[0]
    if (file) {
      handleFile(file)
    }
  }, [handleFile])

  async function handleAnalyze() {
    if (!selectedFile) return
    setLoading(true)
    setError('')

    try {
      const payload = await analyzeWafer(selectedFile)
      setResult(payload)
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }

  function reset() {
    handleFile(null)
  }

  const prediction = result?.prediction || {}
  const heatmapSrc = result?.heatmap_base64 ? `data:image/png;base64,${result.heatmap_base64}` : ''

  const loadingSteps = [
    { label: 'ResNet-18 inference complete', state: 'done' },
    { label: 'MobileNetV2 processing...', state: 'active' },
    { label: 'EfficientNetB0 queued', state: 'idle' },
    { label: 'Heatmap generation queued', state: 'idle' },
  ]

  return (
    <div className="analyze-page">
      <DashboardHeader
        eyebrow="Inspection Workbench"
        title="Wafer Analysis"
        description="Upload a wafer image to run wafer classification, heatmap generation, and Gemini summary analysis across the connected CNN ensemble."
      />

      <div className="analyze-grid">
        <div className="analyze-column">
          {!previewUrl ? (
            <div
              onDrop={onDrop}
              onDragOver={(event) => event.preventDefault()}
              className="analyze-dropzone stat-card wafer-grid"
              onClick={() => document.getElementById('wafer-file-input')?.click()}
            >
              <Upload className="analyze-upload-icon" />
              <p className="analyze-drop-title">Drag & drop wafer image or click to browse</p>
              <p className="analyze-drop-subtitle">Supports PNG, JPG, JPEG up to 50MB</p>
              <input
                id="wafer-file-input"
                type="file"
                accept=".png,.jpg,.jpeg,image/*"
                className="hidden-input"
                onChange={handleFileChange}
              />
            </div>
          ) : (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="stat-card analyze-preview-card">
              <div className="analyze-preview-head">
                <span className="analyze-file-name">{selectedFile?.name}</span>
                <button type="button" onClick={reset} className="analyze-clear-button">Clear</button>
              </div>
              <div className="analyze-preview-frame">
                <img src={previewUrl} alt="Wafer preview" className="analyze-preview-image" />
              </div>
            </motion.div>
          )}

          {previewUrl && !result ? (
            <button className="primary-button analyze-run-button" onClick={handleAnalyze} disabled={loading}>
              {loading ? (
                <span className="button-inline"><span className="button-spinner" />Running CNN Ensemble...</span>
              ) : (
                <span className="button-inline"><Zap size={16} />Run AI Analysis</span>
              )}
            </button>
          ) : null}

          {error ? <div className="error-state">{error}</div> : null}
        </div>

        <div className="analyze-column">
          <AnimatePresence mode="wait">
            {loading ? (
              <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="stat-card analyze-heatmap-card analyze-loading-card">
                <div className="analyze-spinner-lg" />
                <p className="analyze-loading-title">Analyzing wafer image...</p>
                <div className="analyze-loading-steps">
                  {loadingSteps.map((step) => (
                    <div key={step.label} className="analyze-loading-step">
                      {step.state === 'done' ? <CheckCircle2 size={14} className="step-done" /> : null}
                      {step.state === 'active' ? <span className="step-spinner" /> : null}
                      {step.state === 'idle' ? <span className="step-idle" /> : null}
                      <span>{step.label}</span>
                    </div>
                  ))}
                </div>
              </motion.div>
            ) : result ? (
              <motion.div key="result" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="stat-card analyze-heatmap-card">
                <div className="analyze-panel-head">
                  <span>Defect Heatmap</span>
                </div>
                <div className="analyze-heatmap-stage wafer-grid">
                  {heatmapSrc ? <img src={heatmapSrc} alt="Defect heatmap" className="analyze-heatmap-image" /> : null}
                </div>
              </motion.div>
            ) : (
              <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="stat-card analyze-heatmap-card analyze-empty-card">
                <AlertCircle className="analyze-empty-icon" />
                <p>Upload an image to see heatmap results</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      <AnimatePresence>
        {result ? (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="analyze-results-grid">
            <div className="stat-card analyze-result-card">
              <div className="analyze-result-head">
                <Crosshair size={16} className="tone-primary" />
                <h3>Prediction</h3>
              </div>
              <div className="analyze-prediction-value">{prediction.defect_type || 'Unknown'}</div>
              <div className="analyze-progress-row">
                <div className="analyze-progress-track">
                  <div className="analyze-progress-fill" style={{ width: `${(prediction.confidence || 0) * 100}%` }} />
                </div>
                <span>{prediction.confidence != null ? `${(prediction.confidence * 100).toFixed(1)}%` : '-'}</span>
              </div>
              <p className="analyze-result-meta">CNN Ensemble (3 models)</p>
            </div>

            <div className="stat-card analyze-result-card">
              <div className="analyze-result-head">
                <Brain size={16} className="tone-accent" />
                <h3>Current Wafer Insight</h3>
              </div>
              <p className="analyze-insight-text">{result.current_wafer_insight || result.insight}</p>
            </div>

            <div className="stat-card analyze-result-card">
              <div className="analyze-result-head">
                <Brain size={16} className="tone-accent" />
                <h3>Manufacturing Process Insight</h3>
              </div>
              <p className="analyze-insight-text">{result.process_insight || 'No process insight is available for this wafer.'}</p>
            </div>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </div>
  )
}