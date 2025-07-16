// src/App.tsx
import React, { useState, useRef } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

const App: React.FC = () => {
  const [company, setCompany] = useState("");
  const [roast, setRoast] = useState<string | null>(null);
  const [gossip, setGossip] = useState<string | null>(null);
  const [intel, setIntel] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const roastRef = useRef<HTMLDivElement>(null);

  const handleFetch = async () => {
    console.log("Fetching data for:", company);
    if (!company.trim()) return;
    setLoading(true);
    setRoast(null);
    setGossip(null);
    setIntel(null);
    try {
      const [roastRes, gossipRes, intelRes] = await Promise.all([
        fetch("http://localhost:8000/roast", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ company }),
        }),

        fetch("http://localhost:8000/gossip/gossip", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ company }),
        }),
        fetch("http://localhost:8000/companies/intel", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ company }),
        }),
      ]);

      const roastData = await roastRes.json();
      const gossipData = await gossipRes.json();
      const intelData = await intelRes.json();

      setRoast(roastData.roast?.roast?.slice(0, 280));
      setGossip(gossipData.gossip
              ?.split("\n")[0]     // take just the first paragraph
              .slice(0, 300) || "No gossip available.");
      setIntel(intelData.what_they_cookin
               ?.replace(/^"|"$/g, "") // remove surrounding quotes
                .slice(0, 400) || "No intel available.");
      
      console.log("roastData", roastData);
      console.log("gossipData", gossipData);
      console.log("intelData", intelData);


      

      // Scroll to roast section after content loads
      roastRef.current?.scrollIntoView({ behavior: "smooth" });
    } catch (err) {
      setRoast("Couldn't fetch the roast. Try again later.");
      setGossip("Couldn't fetch the gossip. Try again later.");
      setIntel("Couldn't fetch the intel. Try again later.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white flex flex-col items-center justify-center gap-6 p-4">
      <h1 className="text-4xl font-bold text-center">WhatchuCookin 🔥</h1>
      <p className="text-sm text-gray-400">Type a company name and get the full meal: Roast 🍗, Gossip 🗣️, Intel 📊</p>

      <div className="flex gap-2 w-full max-w-md">
        <Input
          placeholder="e.g. Meta, Amazon, Tesla..."
          value={company}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setCompany(e.target.value)}
          className="flex-grow bg-white text-black"
        />
        <Button onClick={handleFetch} disabled={loading}>
          {loading ? "Cookin'..." : "Serve It"}
        </Button>
      </div>

      {roast && (
        <div ref={roastRef}>
          <Card className="bg-white text-black max-w-xl w-full mt-4">
            <CardContent className="p-4 text-center">
              <h2 className="font-bold text-xl mb-2">Roast 🍗</h2>
              <p className="italic">{roast}</p>
            </CardContent>
          </Card>
        </div>
      )}

      {intel && (
        <Card className="bg-white text-black max-w-xl w-full mt-4">
          <CardContent className="p-4 text-center">
            <h2 className="font-bold text-xl mb-2">Intel 📊</h2>
            <p className="italic whitespace-pre-line">{intel}</p>
          </CardContent>
        </Card>
      )}

      {gossip && (
        <Card className="bg-white text-black max-w-xl w-full mt-4">
          <CardContent className="p-4 text-center">
            <h2 className="font-bold text-xl mb-2">Gossip 🗣️</h2>
            <p className="italic">{gossip}</p>
          </CardContent>
        </Card>
      )}

    </div>
  );
};

export default App;
