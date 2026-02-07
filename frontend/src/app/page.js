"use client";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, BookOpen, Search, ArrowLeft, Feather, Wind, Sun } from "lucide-react";

export default function Home() {
  const [activeTab, setActiveTab] = useState("oracle"); 
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [silenceMessage, setSilenceMessage] = useState(""); // For "Empty State"
  const [libraryData, setLibraryData] = useState([]);
  const [selectedHymn, setSelectedHymn] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [dailyVerse, setDailyVerse] = useState(null); // For "Verse of the Day"

  // 1. Fetch Library & Daily Verse on Load
  useEffect(() => {
    // Get Library
    fetch("http://127.0.0.1:8000/library")
      .then((res) => res.json())
      .then((data) => setLibraryData(data.books || []))
      .catch((err) => console.error("Library fetch failed:", err));

    // Get Verse of the Day
    fetch("http://127.0.0.1:8000/random")
      .then((res) => res.json())
      .then((data) => setDailyVerse(data))
      .catch((err) => console.error("Random verse failed:", err));
  }, []);

  // 2. Solve Function (With Silence Check)
  const solveLife = async () => {
    if (!query) return;
    setLoading(true);
    setResults([]);
    setSilenceMessage(""); // Reset message

    try {
      const res = await fetch("http://127.0.0.1:8000/solve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ problem: query }),
      });
      const data = await res.json();
      
      // Check if the Veda returned solutions or silence
      if (data.solutions && data.solutions.length > 0) {
        setResults(data.solutions);
      } else {
        setSilenceMessage(data.message || "The Veda is silent.");
      }
    } catch (err) { console.error(err); }
    setLoading(false);
  };

  const filteredLibrary = libraryData.filter((hymn) =>
    hymn.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen relative overflow-hidden text-amber-50 selection:bg-amber-500/30">
      
      {/* --- LAYER 1: THE ATMOSPHERE (Background) --- */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute inset-0 bg-neutral-950" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(217,119,6,0.15),transparent_70%)]" />
        <div className="absolute top-0 left-0 w-full h-full opacity-20 bg-[url('https://www.transparenttextures.com/patterns/stardust.png')]" />
      </div>

      {/* --- LAYER 2: THE CONTENT --- */}
      <div className="relative z-10 max-w-6xl mx-auto px-6 py-12 flex flex-col min-h-screen">
        
        {/* HEADER */}
        <header className="text-center mb-10 relative">
          <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
            <h1 className="font-cinzel text-5xl md:text-7xl font-bold bg-gradient-to-b from-amber-100 to-amber-600 bg-clip-text text-transparent tracking-widest drop-shadow-2xl">
              ATHARVA
            </h1>
            <span className="absolute -bottom-4 left-1/2 -translate-x-1/2 text-xs font-inter tracking-[0.3em] text-amber-500/60 uppercase whitespace-nowrap">
              VedaOS • v1.1
            </span>
          </motion.div>
        </header>

        {/* NAVIGATION */}
        <nav className="flex justify-center gap-6 mb-12">
          {['oracle', 'library'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`relative px-8 py-3 rounded-2xl border transition-all duration-500 font-cinzel tracking-wider text-sm ${
                activeTab === tab
                  ? "bg-amber-950/40 border-amber-500/50 text-amber-100 shadow-[0_0_20px_rgba(245,158,11,0.2)]"
                  : "bg-transparent border-transparent text-amber-500/40 hover:text-amber-300"
              }`}
            >
              {activeTab === tab && (
                <motion.div layoutId="glow" className="absolute inset-0 rounded-2xl bg-amber-500/10 blur-md" />
              )}
              <span className="relative flex items-center gap-2">
                {tab === 'oracle' ? <Sparkles size={14}/> : <BookOpen size={14}/>}
                {tab.toUpperCase()}
              </span>
            </button>
          ))}
        </nav>

        {/* MAIN INTERFACE */}
        <AnimatePresence mode="wait">
          
          {/* --- MODE A: THE ORACLE --- */}
          {activeTab === "oracle" && (
            <motion.div 
              key="oracle"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="max-w-3xl mx-auto w-full"
            >
              {/* FEATURE: VERSE OF THE DAY (Only shows if no results yet) */}
              {!results.length && !silenceMessage && dailyVerse && (
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mb-8 p-6 bg-amber-900/10 border border-amber-500/20 rounded-xl text-center relative overflow-hidden"
                >
                  <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-amber-500/50 to-transparent opacity-50"></div>
                  <div className="flex justify-center items-center gap-2 text-amber-400 mb-2 uppercase text-xs tracking-widest font-bold">
                    <Sun size={14} /> Hymn of the Moment
                  </div>
                  <p className="font-cinzel text-lg text-amber-100/90 italic">"{dailyVerse.verse}"</p>
                  <p className="text-xs text-amber-600 mt-3 font-inter">{dailyVerse.title} • {dailyVerse.source}</p>
                </motion.div>
              )}

              {/* INPUT */}
              <div className="relative group">
                <div className="absolute -inset-1 bg-gradient-to-r from-amber-500/20 via-orange-500/20 to-amber-500/20 rounded-2xl blur opacity-30 group-hover:opacity-70 transition duration-1000"></div>
                <div className="relative bg-neutral-900/80 backdrop-blur-xl border border-amber-500/20 rounded-2xl p-2 flex items-center shadow-2xl">
                  <input
                    type="text"
                    placeholder="Pour your troubles here (e.g., 'How to find peace?')..."
                    className="w-full bg-transparent border-none px-6 py-4 text-xl font-light text-amber-50 placeholder:text-neutral-600 focus:outline-none focus:ring-0 font-inter"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && solveLife()}
                  />
                  <button
                    onClick={solveLife}
                    disabled={loading}
                    className="bg-gradient-to-br from-amber-600 to-amber-800 text-white p-4 rounded-xl hover:scale-105 transition-transform shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? <Wind className="animate-spin" /> : <Feather />}
                  </button>
                </div>
              </div>

              {/* FEATURE: SILENCE MESSAGE (Empty State) */}
              {silenceMessage && (
                <motion.div 
                  initial={{ opacity: 0 }} 
                  animate={{ opacity: 1 }} 
                  className="mt-12 text-center p-8 border border-neutral-800 rounded-xl bg-neutral-900/30"
                >
                  <Wind size={40} className="mx-auto text-neutral-600 mb-4 animate-pulse" />
                  <p className="text-xl font-cinzel text-neutral-400">{silenceMessage}</p>
                  <p className="text-sm text-neutral-600 mt-2 font-inter">Try simplifying your query or focus on the core emotion.</p>
                </motion.div>
              )}

              {/* RESULTS */}
              <div className="mt-16 grid gap-8 pb-20">
                {results.map((item, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.2, type: "spring" }}
                    className="relative bg-neutral-900/60 border-l-2 border-amber-500/50 p-8 rounded-r-xl backdrop-blur-sm group hover:bg-neutral-800/60 transition-colors"
                  >
                    <div className="absolute -left-[9px] top-8 w-4 h-4 rounded-full bg-neutral-950 border-2 border-amber-500 group-hover:bg-amber-500 transition-colors" />
                    
                    <h3 className="font-cinzel text-2xl text-amber-400 mb-4">{item.title}</h3>
                    <p className="font-inter text-lg leading-relaxed text-neutral-300 italic font-light">
                      "{item.verse}"
                    </p>
                    <div className="mt-6 flex justify-between items-center border-t border-white/5 pt-4">
                      <span className="text-xs font-cinzel text-amber-700 uppercase tracking-widest">
                        {item.source}
                      </span>
                      <span className="text-xs font-mono text-neutral-600">
                        Match: {(item.score * 100).toFixed(0)}%
                      </span>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {/* --- MODE B: THE LIBRARY --- */}
          {activeTab === "library" && (
            <motion.div 
              key="library"
              initial={{ opacity: 0 }} 
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="w-full h-[70vh] flex flex-col"
            >
              {selectedHymn ? (
                /* READING MODE */
                <motion.div 
                  initial={{ opacity: 0, x: 20 }} 
                  animate={{ opacity: 1, x: 0 }}
                  className="h-full bg-neutral-900/40 backdrop-blur-2xl border border-amber-500/10 rounded-2xl p-6 md:p-10 overflow-y-auto custom-scrollbar relative"
                >
                  <button 
                    onClick={() => setSelectedHymn(null)}
                    className="sticky top-0 z-50 mb-8 flex items-center gap-2 text-amber-500 hover:text-amber-300 transition-colors uppercase text-xs font-bold tracking-widest bg-neutral-950/80 px-4 py-2 rounded-full w-fit backdrop-blur"
                  >
                    <ArrowLeft size={14} /> Return
                  </button>
                  
                  <article className="max-w-2xl mx-auto text-center">
                    <h2 className="font-cinzel text-3xl md:text-4xl text-amber-200 mb-8">{selectedHymn.title}</h2>
                    <div className="w-full h-px bg-gradient-to-r from-transparent via-amber-500/50 to-transparent mb-12"></div>
                    <p className="font-inter text-lg leading-loose text-neutral-300 text-justify whitespace-pre-wrap">
                      {selectedHymn.content}
                    </p>
                    <div className="mt-16 flex justify-center">
                      <div className="px-6 py-2 border border-amber-900/50 rounded-full text-xs text-amber-700 uppercase tracking-widest">
                        Book {selectedHymn.book} • Hymn {selectedHymn.hymn}
                      </div>
                    </div>
                  </article>
                </motion.div>
              ) : (
                /* SHELF MODE */
                <div className="flex flex-col h-full">
                  <div className="relative mb-8 max-w-md mx-auto w-full">
                    <Search className="absolute left-4 top-3.5 text-neutral-500" size={18} />
                    <input 
                      type="text" 
                      placeholder="Search the ancient texts..." 
                      className="w-full bg-neutral-900/50 border border-neutral-800 rounded-full py-3 pl-12 pr-6 text-sm text-amber-100 focus:border-amber-500/50 focus:outline-none transition-colors font-inter"
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>

                  {/* MOBILE GRID FIX: grid-cols-1 on mobile, 2 on tablet, 3 on desktop */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 overflow-y-auto pr-2 pb-20 custom-scrollbar">
                    {filteredLibrary.map((hymn, i) => (
                      <motion.div
                        key={i}
                        whileHover={{ y: -5, backgroundColor: "rgba(23, 23, 23, 0.9)" }}
                        onClick={() => setSelectedHymn(hymn)}
                        className="cursor-pointer bg-neutral-900/30 border border-white/5 p-6 rounded-xl hover:border-amber-500/30 transition-all group flex flex-col justify-between h-40"
                      >
                        <div>
                          <div className="flex justify-between items-start mb-2">
                            <span className="text-[10px] font-bold text-neutral-600 uppercase tracking-wider group-hover:text-amber-500/70 transition-colors">
                              BK {hymn.book} • HY {hymn.hymn}
                            </span>
                            <Feather size={12} className="text-neutral-700 group-hover:text-amber-500 transition-colors opacity-0 group-hover:opacity-100" />
                          </div>
                          <h3 className="font-cinzel text-amber-100/90 text-lg leading-tight line-clamp-2 group-hover:text-amber-400 transition-colors">
                            {hymn.title}
                          </h3>
                        </div>
                        <div className="w-full h-0.5 bg-gradient-to-r from-amber-500/0 via-amber-500/0 to-amber-500/0 group-hover:via-amber-500/50 transition-all duration-500" />
                      </motion.div>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}