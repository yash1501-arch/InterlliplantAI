'use client';

import Link from 'next/link';
import { ArrowLeft, Mail, MapPin, GraduationCap, Award, Code2, Database, BarChart3, Globe } from 'lucide-react';

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-slate-800 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <Link href="/landing" className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors">
            <ArrowLeft size={18} />
            <span className="text-sm">Back to Home</span>
          </Link>
          <Link href="/" className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium transition-colors">
            Launch Platform
          </Link>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-16">
        {/* Profile Hero */}
        <div className="flex flex-col md:flex-row items-center gap-10 mb-16">
          <div className="shrink-0">
            <div className="w-48 h-48 rounded-3xl overflow-hidden border-4 border-blue-500/30 shadow-2xl shadow-blue-500/10 relative">
              <img src="/images/narayan.jpg" alt="Narayan Parab" className="w-full h-full object-cover" />
              <div className="absolute inset-0 bg-gradient-to-t from-slate-950/40 to-transparent" />
            </div>
          </div>
          <div className="text-center md:text-left">
            <h1 className="text-4xl font-bold mb-2">Narayan Parab</h1>
            <p className="text-xl text-blue-400 font-medium mb-4">Data Analyst | Full Stack Developer | AI Engineer</p>
            <p className="text-slate-400 leading-relaxed max-w-lg">
              A passionate technologist with a strong foundation in data analytics, full-stack web development, 
              and AI systems. Skilled in transforming complex data into actionable insights and building 
              intelligent platforms that solve real-world industrial challenges.
            </p>
            <div className="flex flex-wrap gap-4 mt-6 justify-center md:justify-start text-sm text-slate-400">
              <span className="flex items-center gap-1.5"><MapPin size={14} className="text-blue-400" /> Mumbai, India</span>
              <span className="flex items-center gap-1.5"><Mail size={14} className="text-blue-400" /> narayanp1501@gmail.com</span>
              <span className="flex items-center gap-1.5"><GraduationCap size={14} className="text-blue-400" /> B.E. Information Technology</span>
            </div>
          </div>
        </div>

        {/* Skills Grid */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <Code2 size={22} className="text-blue-400" /> Technical Skills
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="p-5 bg-slate-900 border border-slate-800 rounded-xl">
              <h3 className="text-sm font-semibold text-blue-400 uppercase tracking-wider mb-3">AI & Data Science</h3>
              <div className="flex flex-wrap gap-2">
                {['Python', 'LangGraph', 'LangChain', 'FastAPI', 'Power BI', 'DAX', 'Data Visualization', 'SQL'].map(s => (
                  <span key={s} className="px-2.5 py-1 bg-blue-500/10 border border-blue-500/20 rounded-lg text-xs text-blue-300">{s}</span>
                ))}
              </div>
            </div>
            <div className="p-5 bg-slate-900 border border-slate-800 rounded-xl">
              <h3 className="text-sm font-semibold text-purple-400 uppercase tracking-wider mb-3">Frontend</h3>
              <div className="flex flex-wrap gap-2">
                {['React.js', 'Next.js', 'TypeScript', 'Angular', 'TailwindCSS', 'HTML/CSS', 'JavaScript'].map(s => (
                  <span key={s} className="px-2.5 py-1 bg-purple-500/10 border border-purple-500/20 rounded-lg text-xs text-purple-300">{s}</span>
                ))}
              </div>
            </div>
            <div className="p-5 bg-slate-900 border border-slate-800 rounded-xl">
              <h3 className="text-sm font-semibold text-green-400 uppercase tracking-wider mb-3">Backend & Databases</h3>
              <div className="flex flex-wrap gap-2">
                {['Node.js', 'Express.js', 'FastAPI', 'Neo4j', 'Qdrant', 'PostgreSQL', 'MongoDB'].map(s => (
                  <span key={s} className="px-2.5 py-1 bg-green-500/10 border border-green-500/20 rounded-lg text-xs text-green-300">{s}</span>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Education */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <GraduationCap size={22} className="text-blue-400" /> Education
          </h2>
          <div className="space-y-4">
            <div className="p-5 bg-slate-900 border border-slate-800 rounded-xl flex items-start gap-4">
              <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center shrink-0">
                <GraduationCap size={20} className="text-blue-400" />
              </div>
              <div>
                <h3 className="text-white font-semibold">Bachelor of Engineering — Information Technology</h3>
                <p className="text-sm text-slate-400">Atharva College of Engineering, Mumbai</p>
                <p className="text-xs text-slate-500 mt-1">2024</p>
              </div>
            </div>
            <div className="p-5 bg-slate-900 border border-slate-800 rounded-xl flex items-start gap-4">
              <div className="w-12 h-12 bg-purple-500/10 rounded-xl flex items-center justify-center shrink-0">
                <GraduationCap size={20} className="text-purple-400" />
              </div>
              <div>
                <h3 className="text-white font-semibold">Diploma of Engineering — Information Technology</h3>
                <p className="text-sm text-slate-400">Government Polytechnic, Mumbai</p>
                <p className="text-xs text-slate-500 mt-1">2021</p>
              </div>
            </div>
          </div>
        </section>

        {/* Certifications */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <Award size={22} className="text-blue-400" /> Certifications
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-5 bg-slate-900 border border-slate-800 rounded-xl text-center">
              <Award size={24} className="text-yellow-400 mx-auto mb-3" />
              <h3 className="text-sm font-semibold text-white">Software Engineering</h3>
              <p className="text-xs text-slate-400 mt-1">Skyscanner (Forage)</p>
              <p className="text-[10px] text-slate-500 mt-0.5">Apr 2025</p>
            </div>
            <div className="p-5 bg-slate-900 border border-slate-800 rounded-xl text-center">
              <BarChart3 size={24} className="text-blue-400 mx-auto mb-3" />
              <h3 className="text-sm font-semibold text-white">Data Visualization</h3>
              <p className="text-xs text-slate-400 mt-1">Tata Group (Forage)</p>
              <p className="text-[10px] text-slate-500 mt-0.5">Apr 2025</p>
            </div>
            <div className="p-5 bg-slate-900 border border-slate-800 rounded-xl text-center">
              <Database size={24} className="text-green-400 mx-auto mb-3" />
              <h3 className="text-sm font-semibold text-white">Data Analytics</h3>
              <p className="text-xs text-slate-400 mt-1">Deloitte Australia (Forage)</p>
              <p className="text-[10px] text-slate-500 mt-0.5">Apr 2025</p>
            </div>
          </div>
        </section>

        {/* About This Project */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <Globe size={22} className="text-blue-400" /> About IntelliPlant AI
          </h2>
          <div className="p-8 bg-gradient-to-br from-blue-500/5 to-purple-500/5 border border-slate-800 rounded-2xl">
            <p className="text-slate-300 leading-relaxed mb-4">
              IntelliPlant AI was built for the <strong className="text-white">ET AI Hackathon 2026</strong> to address 
              a critical challenge in industrial organizations: fragmented knowledge across thousands of documents, 
              leading to increased downtime, repeated incidents, and compliance failures.
            </p>
            <p className="text-slate-300 leading-relaxed mb-4">
              The platform leverages cutting-edge AI technologies including <strong className="text-blue-300">LangGraph</strong> for 
              multi-agent orchestration, <strong className="text-green-300">Neo4j</strong> knowledge graphs for relationship intelligence, 
              <strong className="text-purple-300">Qdrant</strong> vector search for semantic retrieval, and 
              <strong className="text-orange-300">Groq LLM</strong> for real-time reasoning.
            </p>
            <p className="text-slate-400 leading-relaxed">
              The result is a system that reduces information retrieval from 30-60 minutes to under 20 seconds,
              preserves organizational knowledge, proactively detects compliance gaps, and provides 
              explainable AI-powered engineering assistance with source citations.
            </p>
          </div>
        </section>

        {/* Footer */}
        <footer className="text-center pt-8 border-t border-slate-800">
          <p className="text-slate-500 text-sm">
            © 2026 IntelliPlant AI — Designed & Developed by <strong className="text-slate-300">Narayan Parab</strong>
          </p>
          <p className="text-xs text-slate-600 mt-2">ET AI Hackathon 2026 | Mumbai, India</p>
        </footer>
      </main>
    </div>
  );
}
