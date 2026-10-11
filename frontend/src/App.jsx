import React, { useState } from 'react';
import { DISEASE_DATA } from './data/diseaseDatabase';

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState('organic');

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;
    setLoading(true);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const res = await fetch(`${API_BASE_URL}/predict`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setResult(data);
    } catch {
      setResult({ status: "rejected", message: "Failed to connect to API server." });
    } finally {
      setLoading(false);
    }
  };

  const details = result?.disease ? DISEASE_DATA[result.disease] : null;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <header className="border-b border-slate-800 bg-slate-900/80 p-4 sticky top-0 z-50 flex justify-between items-center">
        <h1 className="font-extrabold text-lg text-emerald-400 flex items-center gap-2">
          <span>🌱</span> AgriLens
        </h1>
        <span className="text-xs px-2 py-1 rounded bg-slate-800 border border-slate-700 text-slate-400">v2.0</span>
      </header>

      <main className="flex-1 max-w-md w-full mx-auto p-4 space-y-4">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl">
          <div className="relative min-h-[220px] w-full rounded-xl bg-slate-950 border-2 border-dashed border-slate-800 overflow-hidden flex items-center justify-center p-2">
            {previewUrl ? (
              <img src={previewUrl} alt="Leaf preview" className="w-full h-full object-contain rounded-lg max-h-64" />
            ) : (
              <p className="text-xs text-slate-500 font-medium text-center">Tap to snap or upload leaf image</p>
            )}
            <input 
              type="file" 
              accept="image/*" 
              capture="environment" 
              onChange={handleFileSelect} 
              className="absolute inset-0 opacity-0 cursor-pointer z-10" 
            />
          </div>

          <button
            onClick={handleAnalyze}
            disabled={!selectedFile || loading}
            className="w-full mt-4 py-3 bg-emerald-500 hover:bg-emerald-400 disabled:bg-slate-800 disabled:text-slate-600 text-slate-950 font-bold rounded-xl transition shadow-lg shadow-emerald-500/10"
          >
            {loading ? "Analyzing Leaf..." : "Run AI Scan"}
          </button>
        </div>

        {result && (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-3 shadow-2xl">
            {result.status === "rejected" ? (
              <p className="text-sm text-rose-400 font-medium">⚠️ {result.message}</p>
            ) : (
              <>
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className="text-lg font-bold text-slate-100">{details?.name || result.disease}</h2>
                    <p className="text-xs italic text-slate-400">{details?.scientificName}</p>
                  </div>
                  <span className="text-xl font-extrabold text-emerald-400">{result.confidence_percentage}%</span>
                </div>

                <div className="flex border-b border-slate-800 text-xs font-semibold pt-2">
                  {['organic', 'chemical', 'prevention'].map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`pb-2 px-3 capitalize transition ${activeTab === tab ? 'border-b-2 border-emerald-400 text-emerald-400' : 'text-slate-500'}`}
                    >
                      {tab}
                    </button>
                  ))}
                </div>

                <ul className="text-xs space-y-2 text-slate-300 pt-2">
                  {details?.[`${activeTab}Treatment` || 'prevention']?.map((step, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-emerald-400">•</span>
                      <span>{step}</span>
                    </li>
                  ))}
                </ul>
              </>
            )}
          </div>
        )}
      </main>
    </div>
  );
}