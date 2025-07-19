// src/App.tsx
import React, { useState, useRef, useMemo } from "react";

/* UI components */
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

/* ---------- Config ---------- */
const API_BASE = "http://localhost:8000";

/* ---------- Small Reusable Bits ---------- */
const SectionTitle: React.FC<{ title: string; emoji?: string }> = ({ title, emoji }) => (
  <h2 className="text-sm font-semibold tracking-wide uppercase mb-2 flex items-center gap-1">
    {emoji && <span>{emoji}</span>}
    {title}
  </h2>
);

const StatBadge: React.FC<{ label: string; value: string | number | null | undefined }> = ({ label, value }) => (
  <div className="flex flex-col items-start px-3 py-2 border rounded-md bg-white">
    <span className="text-[10px] font-medium text-neutral-500 uppercase">{label}</span>
    <span className="text-sm font-semibold">{value ?? "—"}</span>
  </div>
);

/* ---------- Types (lightweight) ---------- */
interface Scorecard {
  composite: number;
  explanation: string;
  updated_at?: string;
  scores?: Record<string, number>;
}
interface Financials {
  price?: number;
  change_percent?: number;
  market_cap?: string;
  pe?: number;
  rev_growth_yoy?: number;
  gross_margin_pct?: number;
  [k: string]: any;
}
interface JobsData {
  count?: number;
  job_count?: number;
  sample_keywords?: string[];
  [k: string]: any;
}

/* ---------- Main Component ---------- */
const App: React.FC = () => {
  const [company, setCompany] = useState("");
  const [loading, setLoading] = useState(false);

  // Core data
  const [intel, setIntel] = useState<string | null>(null);
  const [roast, setRoast] = useState<string | null>(null);
  const [gossip, setGossip] = useState<string | null>(null);
  const [scorecard, setScorecard] = useState<Scorecard | null>(null);
  const [financials, setFinancials] = useState<Financials | null>(null);
  const [jobs, setJobs] = useState<JobsData | null>(null);

  // NEW: Additional future data slices
  const [trends, setTrends] = useState<{ headlines?: any[]; mentions?: any[] } | null>(null);
  const [timeline, setTimeline] = useState<any[] | null>(null);
  const [riskItems, setRiskItems] = useState<string[] | null>(null);
  const [peerInput, setPeerInput] = useState("");
  const [peerCompare, setPeerCompare] = useState<any[] | null>(null);

  // NEW: AI follow-up Q/A
  const [aiQuestion, setAiQuestion] = useState("");
  const [aiAnswer, setAiAnswer] = useState<string | null>(null);
  const [aiLoading, setAiLoading] = useState(false);

  // Errors
  const [errors, setErrors] = useState<Record<string, string>>({});

  const intelRef = useRef<HTMLDivElement>(null);

  const resetState = () => {
    setIntel(null);
    setRoast(null);
    setGossip(null);
    setScorecard(null);
    setFinancials(null);
    setJobs(null);
    setErrors({});
    setTrends(null);
    setTimeline(null);
    setRiskItems(null);
    setPeerCompare(null);
    setAiAnswer(null);
  };

  const safeJson = async (res: Response) => {
    try {
      return await res.json();
    } catch {
      return null;
    }
  };

  const handleFetch = async () => {
    if (!company.trim() || loading) return;
    setLoading(true);
    resetState();

    const body = JSON.stringify({ company: company.trim() });
    const headers = { "Content-Type": "application/json" };

    try {
      const [
        roastRes,
        gossipRes,
        intelRes,
        scoreRes,
        finRes,
        jobsRes
        // (Future: add trendsRes, timelineRes, riskRes etc.)
      ] = await Promise.allSettled([
        fetch(`${API_BASE}/roast`, { method: "POST", headers, body }),
        fetch(`${API_BASE}/gossip/gossip`, { method: "POST", headers, body }),
        fetch(`${API_BASE}/companies/intel`, { method: "POST", headers, body }),
        fetch(`${API_BASE}/companies/scorecard-real`, { method: "POST", headers, body }),
        fetch(`${API_BASE}/companies/financials`, { method: "POST", headers, body }),
        fetch(`${API_BASE}/companies/jobs`, { method: "POST", headers, body })
      ]);

      const process = async (
        label: string,
        result: PromiseSettledResult<Response>,
        setter: (v: any) => void,
        pick?: (data: any) => any
      ) => {
        if (result.status === "fulfilled") {
          if (!result.value.ok) {
            setErrors(e => ({ ...e, [label]: `${result.value.status}` }));
            return;
          }
          const data = await safeJson(result.value);
            if (data == null) {
              setErrors(e => ({ ...e, [label]: "bad_json" }));
              return;
            }
            setter(pick ? pick(data) : data);
        } else {
          setErrors(e => ({ ...e, [label]: "fetch_fail" }));
        }
      };

      await process("roast", roastRes, (d) => setRoast(d?.roast?.roast || d?.roast || d?.message || null));
      await process("gossip", gossipRes, (d) => setGossip(d?.gossip || null));
      await process("intel", intelRes, (d) => setIntel(d?.what_they_cookin || null));
      await process("scorecard", scoreRes, (d) => setScorecard(d));
      await process("financials", finRes, (d) => setFinancials(d));
      await process("jobs", jobsRes, (d) => setJobs(d));

      // NEW: Fake placeholder fillers (remove when real endpoints exist)
      setTrends({
        headlines: [
          { title: "AI initiative expands", impact: "+", ts: Date.now() - 3600_000 },
          { title: "Regulatory inquiry rumor", impact: "-", ts: Date.now() - 7200_000 }
        ],
        mentions: [
          { channel: "GitHub", changePct: 12 },
          { channel: "Reddit", changePct: -5 }
        ]
      });
      setTimeline([
        { date: "2024-Q4", event: "Launched flagship product beta" },
        { date: "2025-Q1", event: "Opened new R&D hub" }
      ]);
      setRiskItems([
        "Supply chain concentration in 2 vendors",
        "Pending regulatory review (privacy)",
        "Moderate ESG controversy exposure"
      ]);

      setTimeout(() => intelRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 100);
    } catch (err: any) {
      setErrors(e => ({ ...e, global: err.message || "unknown" }));
    } finally {
      setLoading(false);
    }
  };

  // NEW: Derived “AI Snapshot” (thin heuristic until server summarizer)
  const aiSnapshot = useMemo(() => {
    if (!intel && !financials && !scorecard) return null;
    const parts: string[] = [];
    if (financials?.price) parts.push(`Price ${financials.price}`);
    if (scorecard?.composite != null) parts.push(`Composite ${scorecard.composite}`);
    if (scorecard?.scores?.innovation != null) parts.push(`Innov ${scorecard.scores.innovation}`);
    if (intel) parts.push(intel.split("\n")[0]);
    return parts.join(" • ");
  }, [intel, financials, scorecard]);

  // NEW: Handle AI follow-up question (stub)
  const handleAskAI = async () => {
    if (!aiQuestion.trim()) return;
    setAiLoading(true);
    setAiAnswer(null);
    try {
      // For now just echo; later call: POST /ai/query { company, question, context }
      const synthetic =
        `Answer (stub): Fusing your context for ${company} — ${aiQuestion.trim()}.\n\n` +
        `When backend ready: server will send condensed narrative referencing current intel + metrics.`;
      setTimeout(() => {
        setAiAnswer(synthetic);
        setAiLoading(false);
      }, 600);
    } catch (e: any) {
      setAiAnswer("AI query failed.");
      setAiLoading(false);
    }
  };

  // NEW: Peer compare (client-only stub)
  const handlePeerCompare = async () => {
    if (!peerInput.trim()) return;
    // Later: POST /companies/compare { base: company, peers: [...] }
    const peers = peerInput.split(",").map(s => s.trim().toUpperCase()).filter(Boolean);
    setPeerCompare(
      peers.map(p => ({
        ticker: p,
        composite: Math.round(Math.random() * 40 + 50),
        pe: (Math.random() * 30 + 10).toFixed(1),
        revGrowth: (Math.random() * 25 - 5).toFixed(1) + "%"
      }))
    );
  };

  const hasData = intel || roast || gossip || scorecard || financials || jobs || trends || timeline;

  return (
    <div className="min-h-screen bg-white text-black flex flex-col">
      {/* Header / Search */}
      <header className="border-b px-4 py-3 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div className="flex flex-col">
          <h1 className="text-xl font-bold tracking-tight">
            WhatchuCookin<span className="ml-1">🔥</span>
          </h1>
          <p className="text-xs text-neutral-500">
            Company intel + vibe check + raw signals
          </p>
        </div>
        <div className="flex gap-2 w-full md:w-auto">
          <Input
            placeholder="Enter company (e.g. NVIDIA, Apple, Tesla)"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            className="text-sm"
          />
          <Button onClick={handleFetch} disabled={loading}>
            {loading ? "Loading..." : "Cook"}
          </Button>
        </div>
      </header>

      {/* Body Layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar */}
        <aside className="w-full md:w-80 border-r overflow-y-auto p-4 space-y-4 bg-white">
          <div ref={intelRef}>
            <SectionTitle title="Intel" emoji="📊" />
            <Card className="bg-white border">
              <CardContent className="p-3">
                {!intel && !loading && (
                  <p className="text-xs text-neutral-400">
                    No intel yet. Search a company.
                  </p>
                )}
                {loading && (
                  <p className="text-xs text-neutral-500 animate-pulse">
                    Pulling signals…
                  </p>
                )}
                {intel && (
                  <p className="text-sm leading-snug whitespace-pre-line">
                    {intel}
                  </p>
                )}
              </CardContent>
            </Card>
          </div>

          <div>
            <SectionTitle title="Roast" emoji="🍗" />
            <Card className="bg-white border">
              <CardContent className="p-3">
                {loading && !roast && (
                  <p className="text-xs text-neutral-500 animate-pulse">
                    Heating up…
                  </p>
                )}
                {roast && <p className="text-sm italic">{roast}</p>}
                {errors.roast && !roast && !loading && (
                  <p className="text-xs text-red-500">Error.</p>
                )}
              </CardContent>
            </Card>
          </div>

            <div>
              <SectionTitle title="Gossip" emoji="🗣️" />
              <Card className="bg-white border">
                <CardContent className="p-3">
                  {loading && !gossip && (
                    <p className="text-xs text-neutral-500 animate-pulse">
                      Spilling tea…
                    </p>
                  )}
                  {gossip && <p className="text-sm italic">{gossip}</p>}
                  {errors.gossip && !gossip && !loading && (
                    <p className="text-xs text-red-500">Error.</p>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* NEW: Snapshot */}
            <div>
              <SectionTitle title="AI Snapshot" emoji="⚡" />
              <Card className="bg-white border">
                <CardContent className="p-3">
                  {!aiSnapshot && (
                    <p className="text-xs text-neutral-400">
                      Will auto-summarize once data loads.
                    </p>
                  )}
                  {aiSnapshot && (
                    <p className="text-xs leading-snug">{aiSnapshot}</p>
                  )}
                </CardContent>
              </Card>
            </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto p-4 space-y-6">
          {/* Scorecard */}
          <section>
            <div className="flex items-center justify-between mb-2">
              <SectionTitle title="Scorecard" emoji="🧠" />
              {scorecard && (
                <span className="text-[10px] text-neutral-500">
                  Updated{" "}
                  {scorecard.updated_at
                    ? new Date(scorecard.updated_at).toLocaleTimeString()
                    : "now"}
                </span>
              )}
            </div>
            <Card className="bg-white border">
              <CardContent className="p-4">
                {!scorecard && !loading && (
                  <p className="text-xs text-neutral-400">No score yet.</p>
                )}
                {loading && !scorecard && (
                  <p className="text-xs text-neutral-500 animate-pulse">
                    Computing composite…
                  </p>
                )}
                {scorecard && (
                  <div className="space-y-3">
                    <div className="flex flex-wrap gap-2">
                      <StatBadge label="Composite" value={scorecard.composite} />
                      <StatBadge label="Innovation" value={scorecard.scores?.innovation} />
                      <StatBadge label="Product" value={scorecard.scores?.product_momentum} />
                      <StatBadge label="Brand" value={scorecard.scores?.brand_clout} />
                      <StatBadge label="Financial" value={scorecard.scores?.financial_quality} />
                      <StatBadge label="Momentum" value={scorecard.scores?.market_momentum} />
                      <StatBadge label="Talent" value={scorecard.scores?.talent_demand} />
                      <StatBadge label="Ethics/Risk" value={scorecard.scores?.ethics_risk} />
                    </div>
                    <p className="text-xs leading-snug text-neutral-700">
                      {scorecard.explanation}
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </section>

          {/* Financials */}
          <section>
            <SectionTitle title="Financials" emoji="💹" />
            <Card className="bg-white border">
              <CardContent className="p-4 space-y-3">
                {!financials && !loading && (
                  <p className="text-xs text-neutral-400">—</p>
                )}
                {loading && !financials && (
                  <p className="text-xs text-neutral-500 animate-pulse">
                    Fetching price & margins…
                  </p>
                )}
                {financials && (
                  <div className="flex flex-wrap gap-3">
                    <StatBadge label="Price" value={financials.price} />
                    <StatBadge label="Change %" value={financials.change_percent} />
                    <StatBadge label="Market Cap" value={financials.market_cap} />
                    <StatBadge label="P/E" value={financials.pe} />
                    <StatBadge label="Revenue YoY %" value={financials.rev_growth_yoy} />
                    <StatBadge label="Gross Margin %" value={financials.gross_margin_pct} />
                  </div>
                )}
              </CardContent>
            </Card>
          </section>

          {/* Jobs */}
          <section>
            <SectionTitle title="Jobs" emoji="🧪" />
            <Card className="bg-white border">
              <CardContent className="p-4">
                {!jobs && !loading && (
                  <p className="text-xs text-neutral-400">—</p>
                )}
                {loading && !jobs && (
                  <p className="text-xs text-neutral-500 animate-pulse">
                    Scanning roles…
                  </p>
                )}
                {jobs && (
                  <div className="flex flex-col gap-2">
                    <div className="flex flex-wrap gap-3">
                      <StatBadge
                        label="Active Roles"
                        value={jobs.count ?? jobs.job_count ?? "—"}
                      />
                      {jobs.sample_keywords?.slice(0, 6).map(k => (
                        <StatBadge key={k} label="KW" value={k} />
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </section>

          {/* NEW: Trends */}
          <section>
            <SectionTitle title="Trends" emoji="📈" />
            <Card className="bg-white border">
              <CardContent className="p-4 space-y-4">
                {!trends && !loading && (
                  <p className="text-xs text-neutral-400">—</p>
                )}
                {loading && !trends && (
                  <p className="text-xs text-neutral-500 animate-pulse">
                    Aggregating trending signals…
                  </p>
                )}
                {trends && (
                  <div className="space-y-3">
                    <div>
                      <p className="text-[10px] font-medium uppercase text-neutral-500 mb-1">
                        Headlines
                      </p>
                      <ul className="space-y-1">
                        {trends.headlines?.map((h, i) => (
                          <li key={i} className="text-xs flex gap-2">
                            <span className="text-neutral-400">
                              {h.impact === "+" ? "⬆" : "⬇"}
                            </span>
                            <span>{h.title}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <p className="text-[10px] font-medium uppercase text-neutral-500 mb-1">
                        Mentions
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {trends.mentions?.map((m, i) => (
                          <StatBadge
                            key={i}
                            label={m.channel}
                            value={
                              (m.changePct > 0 ? "+" : "") + m.changePct + "%"
                            }
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </section>

          {/* NEW: Peer Compare */}
          <section>
            <SectionTitle title="Peer Compare" emoji="🤝" />
            <Card className="bg-white border">
              <CardContent className="p-4 space-y-3">
                <div className="flex gap-2">
                  <Input
                    placeholder="Enter peer tickers (e.g. AMD, INTC)"
                    value={peerInput}
                    onChange={(e) => setPeerInput(e.target.value)}
                    className="text-xs"
                  />
                  <Button
                    variant="outline"
                    onClick={handlePeerCompare}
                    disabled={!peerInput.trim()}
                  >
                    Go
                  </Button>
                </div>
                {!peerCompare && (
                  <p className="text-[10px] text-neutral-400">
                    Add peers to benchmark.
                  </p>
                )}
                {peerCompare && (
                  <div className="flex flex-wrap gap-2">
                    {peerCompare.map(p => (
                      <div
                        key={p.ticker}
                        className="border rounded-md px-2 py-2 flex flex-col min-w-[110px]"
                      >
                        <span className="text-[10px] font-semibold">
                          {p.ticker}
                        </span>
                        <span className="text-[10px]">
                          Comp: {p.composite}
                        </span>
                        <span className="text-[10px]">P/E: {p.pe}</span>
                        <span className="text-[10px]">
                          Rev: {p.revGrowth}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </section>

          {/* NEW: Risk & Ethics */}
          <section>
            <SectionTitle title="Risk / Ethics" emoji="🛡️" />
            <Card className="bg-white border">
              <CardContent className="p-4">
                {!riskItems && !loading && (
                  <p className="text-xs text-neutral-400">—</p>
                )}
                {loading && !riskItems && (
                  <p className="text-xs text-neutral-500 animate-pulse">
                    Mapping exposures…
                  </p>
                )}
                {riskItems && (
                  <ul className="space-y-1">
                    {riskItems.map((r, i) => (
                      <li key={i} className="text-xs">
                        • {r}
                      </li>
                    ))}
                  </ul>
                )}
              </CardContent>
            </Card>
          </section>

          {/* NEW: Timeline */}
            <section>
              <SectionTitle title="Timeline" emoji="🕒" />
              <Card className="bg-white border">
                <CardContent className="p-4">
                  {!timeline && !loading && (
                    <p className="text-xs text-neutral-400">—</p>
                  )}
                  {loading && !timeline && (
                    <p className="text-xs text-neutral-500 animate-pulse">
                      Building chronology…
                    </p>
                  )}
                  {timeline && (
                    <ul className="space-y-1">
                      {timeline.map((ev, i) => (
                        <li key={i} className="text-xs">
                          <span className="font-medium">{ev.date}:</span>{" "}
                          {ev.event}
                        </li>
                      ))}
                    </ul>
                  )}
                </CardContent>
              </Card>
            </section>

          {/* NEW: Ask AI */}
          <section>
            <SectionTitle title="Ask AI" emoji="🤖" />
            <Card className="bg-white border">
              <CardContent className="p-4 space-y-3">
                <div className="flex gap-2">
                  <Input
                    placeholder="Ask a follow-up (e.g. summarize innovation risk)"
                    value={aiQuestion}
                    onChange={(e) => setAiQuestion(e.target.value)}
                    className="text-xs"
                  />
                  <Button
                    variant="outline"
                    onClick={handleAskAI}
                    disabled={!aiQuestion.trim() || aiLoading}
                  >
                    {aiLoading ? "Thinking…" : "Ask"}
                  </Button>
                </div>
                {aiAnswer && (
                  <p className="text-xs whitespace-pre-line">{aiAnswer}</p>
                )}
              </CardContent>
            </Card>
          </section>

          {/* Analysis Placeholder */}
          <section>
            <SectionTitle title="Analysis (Coming Soon)" emoji="🧬" />
            <Card className="bg-white border">
              <CardContent className="p-4">
                <p className="text-xs text-neutral-500">
                  Upcoming: multi-peer diffs, sentiment time series, GitHub
                  velocity charts, supply chain map, anomaly alerts, PDF export.
                </p>
                <div className="flex gap-2 mt-3">
                  <Button variant="outline" size="sm" disabled>
                    Export PDF
                  </Button>
                  <Button variant="outline" size="sm" disabled>
                    Save Favorite
                  </Button>
                </div>
              </CardContent>
            </Card>
          </section>

          {!hasData && !loading && (
            <p className="text-center text-[11px] text-neutral-400">
              Enter a company to generate its intel & full stack signals.
            </p>
          )}
        </main>
      </div>

      {errors.global && (
        <div className="fixed bottom-2 left-1/2 -translate-x-1/2 bg-red-600 text-white text-xs px-3 py-2 rounded shadow">
          {errors.global}
        </div>
      )}
    </div>
  );
};

export default App;
