"use client";

import { useState } from "react";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Play, Bug, Clock, Cpu, Zap, AlertTriangle, CheckCircle } from "lucide-react";

export default function DebuggerPage() {
    const [code, setCode] = useState(`function fibonacci(n) {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}`);
    const [analyzing, setAnalyzing] = useState(false);
    const [result, setResult] = useState<any>(null);

    const handleAnalyze = () => {
        setAnalyzing(true);
        // Simulate AI Analysis
        setTimeout(() => {
            setResult({
                complexity: "O(2^n) - Exponential",
                memory: "High (Stack overflow risk)",
                bugs: [
                    { line: 3, type: "Performance", message: "Recursive calls without memoization cause exponential growth." }
                ],
                suggestion: `function fibonacci(n, memo = {}) {
  if (n in memo) return memo[n];
  if (n <= 1) return n;
  memo[n] = fibonacci(n - 1, memo) + fibonacci(n - 2, memo);
  return memo[n];
} // Time: O(n)`
            });
            setAnalyzing(false);
        }, 1500);
    };

    return (
        <div className="flex h-[calc(100vh-6rem)] flex-col gap-4">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold">Smart Code Debugger</h1>
                <Button onClick={handleAnalyze} disabled={analyzing} className="bg-primary hover:bg-primary/90 text-white">
                    {analyzing ? (
                        <>
                            <Clock className="mr-2 h-4 w-4 animate-spin" />
                            Analyzing...
                        </>
                    ) : (
                        <>
                            <Bug className="mr-2 h-4 w-4" />
                            Analyze Code
                        </>
                    )}
                </Button>
            </div>

            <div className="grid h-full flex-1 gap-4 lg:grid-cols-2">
                {/* Editor Area */}
                <GlassCard className="flex flex-col overflow-hidden p-0" gradient={false}>
                    <div className="border-b border-white/5 bg-white/5 px-4 py-2 text-xs text-muted-foreground">
                        main.js
                    </div>
                    <textarea
                        value={code}
                        onChange={(e) => setCode(e.target.value)}
                        className="flex-1 resize-none bg-transparent p-4 font-mono text-sm leading-relaxed text-blue-100 outline-none"
                        spellCheck={false}
                    />
                </GlassCard>

                {/* Analysis Panel */}
                <div className="flex flex-col gap-4">
                    {/* Complexity Stats */}
                    <div className="grid grid-cols-2 gap-4">
                        <GlassCard className="p-4" gradient={false}>
                            <div className="flex items-center gap-2 text-muted-foreground">
                                <Clock className="h-4 w-4" />
                                <span className="text-xs">Time Complexity</span>
                            </div>
                            <p className="mt-1 text-lg font-bold text-white">{result ? result.complexity : "--"}</p>
                        </GlassCard>
                        <GlassCard className="p-4" gradient={false}>
                            <div className="flex items-center gap-2 text-muted-foreground">
                                <Cpu className="h-4 w-4" />
                                <span className="text-xs">Memory Usage</span>
                            </div>
                            <p className="mt-1 text-lg font-bold text-white">{result ? result.memory : "--"}</p>
                        </GlassCard>
                    </div>

                    {/* Issues List */}
                    <GlassCard className="flex-1 overflow-auto p-4" gradient={false}>
                        <h3 className="mb-4 font-semibold">Analysis Report</h3>
                        {!result ? (
                            <div className="flex h-32 items-center justify-center text-muted-foreground">
                                <p>Click analyze to detect bugs & optimize.</p>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                {/* Bugs */}
                                <div className="space-y-2">
                                    {result.bugs.map((bug: any, i: number) => (
                                        <div key={i} className="rounded-lg border border-red-500/20 bg-red-500/10 p-3 text-sm">
                                            <div className="flex items-center gap-2 text-red-400">
                                                <AlertTriangle className="h-4 w-4" />
                                                <span className="font-semibold">{bug.type} Issue</span>
                                            </div>
                                            <p className="mt-1 text-muted-foreground">{bug.message}</p>
                                        </div>
                                    ))}
                                </div>

                                {/* Fix */}
                                <div className="space-y-2">
                                    <div className="flex items-center gap-2 text-green-400">
                                        <Zap className="h-4 w-4" />
                                        <span className="font-semibold">Suggested Fix</span>
                                    </div>
                                    <div className="rounded-lg bg-black/40 p-3 font-mono text-xs text-green-100">
                                        <pre>{result.suggestion}</pre>
                                    </div>
                                </div>
                            </div>
                        )}
                    </GlassCard>
                </div>
            </div>
        </div>
    );
}
