// src/App.tsx
import React, { useState, useRef } from "react";

/* UI components */
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

/* ---------- Config ---------- */
const API_BASE = "http://localhost:8000";

/* ---------- Small Reusable Bits ---------- */
const SectionTitle: React.FC<{ title: string; emoji?: string }> = ({ title, emoji }) => (
  <h2 className="text-sm font-semibold tracking-wide uppercase mb-2 flex items-center gap-1">
    {emoji && <span>{emoji}</span>} {title}
  </h2>
);

const StatBadge: React.FC<{ label: string; value: string | number | null | undefined }> = ({
  label,
  value,
}) => (
  <div className="flex flex-col items-start px-3 py-2 border rounded-md bg-white">
    <span className="text-[10px] font-medium text-neutral-500 uppercase">{label}</span>
    <span className="text-sm font-semibold">{value ?? "—"}</span>
  </div>
);

const KeywordBadge: React.FC<{ keyword: string }> = ({ keyword }) => (
  <span className="px-2 py-1 bg-neutral-100 text-neutral-800 text-xs rounded-full">{keyword}</span>
);

/* ---------- Jobs Panel Component ---------- */
interface JobListing {
  title: string;
  location?: string;
  [key: string]: any;
}

const JobsPanel: React.FC<{ jobs: any }> = ({ jobs }) => {
  const [activeTab, setActiveTab] = React.useState<"overview" | "listings">("overview");
  const [query, setQuery] = React.useState("");
  const [sort, setSort] = React.useState<"az" | "za">("az");

  const listings: JobListing[] = Array.isArray(jobs.listings) ? jobs.listings : [];

  const filteredListings = React.useMemo(() => {
    const q = query.toLowerCase();
    let items = listings.filter(
      (j) =>
        j.title.toLowerCase().includes(q) ||
        (j.location && j.location.toLowerCase().includes(q))
    );
    items = items.sort((a, b) =>
      sort === "az" ? a.title.localeCompare(b.title) : b.title.localeCompare(a.title)
    );
    return items;
  }, [listings, query, sort]);

  const keywordChips: string[] = (jobs.sample_keywords || []).slice(0, 25);

  return (
    <div className="space-y-4">
      {/* Tabs */}
      <div className="flex items-center gap-4 border-b pb-1 text-xs font-medium uppercase tracking-wide">
        <button
          onClick={() => setActiveTab("overview")}
          className={`pb-1 ${
            activeTab === "overview" ? "border-b-2 border-black" : "text-neutral-400"
          }`}
        >
          Overview
        </button>
        <button
          onClick={() => setActiveTab("listings")}
          className={`pb-1 ${
            activeTab === "listings" ? "border-b-2 border-black" : "text-neutral-400"
          }`}
        >
          Listings
        </button>
      </div>

      {activeTab === "overview" && (
        <div className="space-y-3">
          <div className="flex flex-wrap gap-2">
            <StatBadge label="Open Roles" value={jobs.job_count as number} />
            <StatBadge label="Locations" value={jobs.locations?.length as number} />
            <StatBadge label="Remote Only" value={jobs.remote_only ? "Yes" : "No"} />
          </div>
          {keywordChips.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {keywordChips.map((kw) => (
                <KeywordBadge keyword={kw} key={kw} />
              ))}
            </div>
          ) : (
            <p className="text-[10px] text-neutral-400">No keyword signals yet.</p>
          )}
          {jobs.locations?.length ? (
            <p className="text-[10px] text-neutral-500">
              Top locations: {jobs.locations.slice(0, 5).join(", ")}
            </p>
          ) : null}
        </div>
      )}

      {activeTab === "listings" && (
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <Input
              placeholder="Filter title or location…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="text-xs w-48"
            />
            <select
              className="text-xs border rounded px-2 py-1 bg-white"
              value={sort}
              onChange={(e) => setSort(e.target.value as "az" | "za")}
            >
              <option value="az">Title A–Z</option>
              <option value="za">Title Z–A</option>
            </select>
            <span className="text-[10px] text-neutral-500">
              {filteredListings.length} / {listings.length} shown
            </span>
          </div>

          <div className="max-h-56 overflow-y-auto border rounded divide-y">
            {filteredListings.length ? (
              filteredListings.map((j, i) => (
                <div key={i} className="p-2">
                  <p className="text-sm font-medium">{j.title}</p>
                  {j.location && (
                    <p className="text-[10px] text-neutral-500">{j.location}</p>
                  )}
                </div>
              ))
            ) : (
              <p className="text-xs p-3 text-neutral-400">No matching roles.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

/* ---------- Simple Sparkline Component ---------- */
interface SparklinePoint {
  date: string; // ISO date
  count: number;
}
const HiringTrendSparkline: React.FC<{ data: SparklinePoint[] }> = ({ data }) => {
  if (!data.length) return <p className="text-[10px] text-neutral-400">No history yet.</p>;

  // Sort by date ascending
  const pts = [...data].sort(
    (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
  );
  const counts = pts.map((p) => p.count);
  const min = Math.min(...counts);
  const max = Math.max(...counts);
  const range = max - min || 1;

  const width = 240;
  const height = 60;
  const step = width / Math.max(pts.length - 1, 1);

  const path = pts
    .map((p, i) => {
      const x = i * step;
      const y = height - ((p.count - min) / range) * (height - 10) - 5;
      return `${i === 0 ? "M" : "L"}${x},${y}`;
    })
    .join(" ");

  return (
    <div className="space-y-1">
      <svg width="100%" viewBox={`0 0 ${width} ${height}`} className="overflow-visible">
        <path d={path} fill="none" stroke="black" strokeWidth={2} />
        {pts.map((p, i) => {
          const x = i * step;
          const y = height - ((p.count - min) / range) * (height - 10) - 5;
          return <circle key={p.date} cx={x} cy={y} r={3} fill="black" />;
        })}
      </svg>
      <p className="text-[10px] text-neutral-500">
        {pts[0].date} → {pts[pts.length - 1].date} (min {min}, max {max})
      </p>
    </div>
  );
};

/* ---------- Main Component ---------- */
const App: React.FC = () => {
  const [company, setCompany] = useState("");
  const [loading, setLoading] = useState(false);

  /* Data state */
  const [intel, setIntel] = useState<string | null>(null);
  const [scorecard, setScorecard] = useState<any | null>(null);
  const [financials, setFinancials] = useState<any | null>(null);
  const [jobs, setJobs] = useState<any | null>(null);
  const [news, setNews] = useState<any[] | null>(null);
  const [events, setEvents] = useState<any[] | null>(null);

  /* Errors */
  const [errors, setErrors] = useState<Record<string, string>>({});

  const intelRef = useRef<HTMLDivElement>(null);

  const resetState = () => {
    setIntel(null);
    setScorecard(null);
    setFinancials(null);
    setJobs(null);
    setNews(null);
    setEvents(null);
    setErrors({});
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
      const [intelRes, scoreRes, finRes, jobsRes, newsRes, eventsRes] =
        await Promise.allSettled([
          fetch(`${API_BASE}/companies/intel`, { method: "POST", headers, body }),
          fetch(`${API_BASE}/companies/scorecard-real`, { method: "POST", headers, body }),
          fetch(`${API_BASE}/companies/financials`, { method: "POST", headers, body }),
          fetch(`${API_BASE}/companies/jobs`, { method: "POST", headers, body }),
          fetch(`${API_BASE}/companies/news`, { method: "POST", headers, body }),
          fetch(`${API_BASE}/companies/events`, { method: "POST", headers, body }),
        ]);

      const process = async (
        label: string,
        result: PromiseSettledResult<Response>,
        setter: (v: any) => void,
        pick?: (data: any) => any
      ) => {
        if (result.status === "fulfilled") {
          if (!result.value.ok) {
            setErrors((e) => ({ ...e, [label]: `${result.value.status}` }));
            return;
          }
          const data = await safeJson(result.value);
          if (data == null) {
            setErrors((e) => ({ ...e, [label]: "bad_json" }));
            return;
          }
          setter(pick ? pick(data) : data);
        } else {
          setErrors((e) => ({ ...e, [label]: "fetch_fail" }));
        }
      };

      await process("intel", intelRes, (d) => setIntel(d?.what_they_cookin || null));
      await process("scorecard", scoreRes, (d) => setScorecard(d));
      await process("financials", finRes, (d) => setFinancials(d));
      await process("jobs", jobsRes, (d) => setJobs(d));
      await process("news", newsRes, (d) => setNews(d?.news || []));
      await process("events", eventsRes, (d) => setEvents(d?.events || []));

      setTimeout(
        () => intelRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }),
        100
      );
    } catch (err: any) {
      setErrors((e) => ({ ...e, global: err.message || "unknown" }));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white text-black flex flex-col">
      {/* Header / Search */}
      <header className="border-b px-4 py-3 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-xl font-bold">
            WhatchuCookin<span>🔥</span>
          </h1>
          <p className="text-xs text-neutral-500">Company intel + signals</p>
        </div>
        <div className="flex gap-2 w-full md:w-auto">
          <Input
            placeholder="Enter company (e.g. NVDA)"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            className="text-sm"
          />
          <Button onClick={handleFetch} disabled={loading}>
            {loading ? "Loading…" : "Cook"}
          </Button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* LEFT: Intel + News + Events */}
        <aside className="w-full md:w-80 border-r overflow-y-auto p-4 space-y-4">
          {/* Intel */}
          <div ref={intelRef}>
            <SectionTitle title="Intel" emoji="📊" />
            <Card className="border">
              <CardContent className="p-3">
                {!intel && !loading && <p className="text-xs text-neutral-400">No data</p>}
                {loading && !intel && <p className="text-xs animate-pulse">Loading…</p>}
                {intel && <p className="text-sm leading-snug whitespace-pre-line">{intel}</p>}
              </CardContent>
            </Card>
          </div>

          {/* News */}
          <div>
            <SectionTitle title="News" emoji="📰" />
            <Card className="border">
              <CardContent className="p-3 space-y-2">
                {loading && !news && <p className="text-xs animate-pulse">Loading…</p>}
                {!loading && (!news || news.length === 0) && (
                  <p className="text-xs text-neutral-400">No recent headlines.</p>
                )}
                {news &&
                  news.slice(0, 6).map((n, i) => (
                    <div key={i} className="text-xs">
                      <p className="font-medium line-clamp-2">{n.title}</p>
                      <p className="text-[10px] text-neutral-500">
                        {n.source || "Source"} • {n.published_at || ""}
                      </p>
                    </div>
                  ))}
              </CardContent>
            </Card>
          </div>

          {/* Events */}
          <div>
            <SectionTitle title="Upcoming Events" emoji="📅" />
            <Card className="border">
              <CardContent className="p-3 space-y-2">
                {loading && !events && <p className="text-xs animate-pulse">Loading…</p>}
                {!loading && (!events || events.length === 0) && (
                  <p className="text-xs text-neutral-400">No upcoming events.</p>
                )}
                {events &&
                  events.slice(0, 5).map((ev, i) => (
                    <div key={i} className="text-xs">
                      <p className="font-medium">{ev.name}</p>
                      <p className="text-[10px] text-neutral-500">
                        {ev.date} {ev.location ? "• " + ev.location : ""}
                      </p>
                    </div>
                  ))}
              </CardContent>
            </Card>
          </div>
        </aside>

        {/* RIGHT: Scorecard / Financials / Jobs / Analytics */}
        <main className="flex-1 overflow-y-auto p-4 space-y-6">
          {/* Scorecard */}
          <section>
            <SectionTitle title="Scorecard" emoji="🧠" />
            <Card className="border">
              <CardContent className="p-4">
                {!scorecard && !loading && <p className="text-xs text-neutral-400">No score</p>}
                {loading && !scorecard && <p className="text-xs animate-pulse">Loading…</p>}
                {scorecard && (
                  <div className="space-y-3">
                    <div className="flex flex-wrap gap-2 mb-2">
                      <StatBadge
                        label="Composite"
                        value={scorecard.composite as number}
                      />
                      {(Object.entries(scorecard.scores || {}) as [string, number][]).map(
                        ([k, v]) => (
                          <StatBadge
                            key={k}
                            label={k.replace(/_/g, " ")}
                            value={v as number}
                          />
                        )
                      )}
                    </div>
                    <p className="text-xs text-neutral-700">{scorecard.explanation}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </section>

          {/* Financials */}
          <section>
            <SectionTitle title="Financials" emoji="💹" />
            <Card className="border">
              <CardContent className="p-4 flex flex-wrap gap-3">
                {!financials && !loading && <p className="text-xs text-neutral-400">No data</p>}
                {loading && !financials && <p className="text-xs animate-pulse">Loading…</p>}
                {financials && (
                  <>
                    <StatBadge label="Price" value={financials.price as number} />
                    <StatBadge
                      label="Δ %"
                      value={financials.change_percent as number}
                    />
                    <StatBadge label="Mkt Cap" value={financials.market_cap} />
                    <StatBadge label="P/E" value={financials.pe as number} />
                    <StatBadge label="P/S" value={financials.ps as number} />
                    <StatBadge label="P/B" value={financials.pb as number} />
                    <StatBadge
                      label="Op Margin %"
                      value={financials.op_margin_pct as number}
                    />
                    <StatBadge
                      label="Net Margin %"
                      value={financials.net_margin_pct as number}
                    />
                    <StatBadge
                      label="Rev YoY %"
                      value={financials.rev_growth_yoy as number}
                    />
                    <StatBadge label="Rev TTM" value={financials.rev_ttm} />
                  </>
                )}
              </CardContent>
            </Card>
          </section>

          {/* Jobs */}
          <section>
            <SectionTitle title="Jobs" emoji="🧪" />
            <Card className="border">
              <CardContent className="p-4 space-y-4">
                {!jobs && !loading && <p className="text-xs text-neutral-400">No jobs</p>}
                {loading && !jobs && <p className="text-xs animate-pulse">Loading jobs…</p>}
                {jobs && <JobsPanel jobs={jobs} />}
              </CardContent>
            </Card>
          </section>

          {/* Data Analytics with Time Series */}
          <section>
            <SectionTitle title="Data Analytics" emoji="📈" />
            <Card className="border">
              <CardContent className="p-4 space-y-4">
                <p className="text-xs text-neutral-600">
                  Early preview: dynamic analytics from stored history & sentiment scoring.
                </p>
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="border rounded p-3">
                    <p className="text-xs font-semibold mb-1">Hiring Trend</p>
                    {jobs?.history ? (
                      <HiringTrendSparkline
                        data={jobs.history as SparklinePoint[]}
                      />
                    ) : (
                      <p className="text-[10px] text-neutral-500">
                        Provide <code>jobs.history</code> array from backend to see a trend.
                      </p>
                    )}
                  </div>
                  <div className="border rounded p-3">
                    <p className="text-xs font-semibold mb-1">Sentiment Timeline</p>
                    <p className="text-[10px] text-neutral-500">
                      Placeholder mini-chart of average headline sentiment over time.
                    </p>
                  </div>
                  <div className="border rounded p-3">
                    <p className="text-xs font-semibold mb-1">Peer Comparison</p>
                    <p className="text-[10px] text-neutral-500">
                      Radar / bars comparing scorecard metrics vs peers (soon).
                    </p>
                  </div>
                  <div className="border rounded p-3">
                    <p className="text-xs font-semibold mb-1">Composite Breakdown</p>
                    <p className="text-[10px] text-neutral-500">
                      Stacked contributions to composite score (soon).
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </section>
        </main>
      </div>

      {/* Global Error */}
      {errors.global && (
        <div className="fixed bottom-4 left-1/2 -translate-x-1/2 bg-red-600 text-white text-xs px-3 py-2 rounded">
          {errors.global}
        </div>
      )}
    </div>
  );
};

export default App;
