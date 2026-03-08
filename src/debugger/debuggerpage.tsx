"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { GlassCard } from "@/components/ui/glass-card";
import { GradientText } from "@/components/ui/gradient-text";
import { Bug, Loader2, AlertCircle, CheckCircle } from "lucide-react";

interface DebugError {
    line: number;
    message: string;
}

interface DebugResult {
    errors: DebugError[];
    corrected_code: string;
    explanation: string;
}

const SUPPORTED_LANGUAGES = [
    { value: "python", label: "Python" },
    { value: "javascript", label: "JavaScript" },
    { value: "typescript", label: "TypeScript" },
    { value: "java", label: "Java" },
    { value: "cpp", label: "C++" },
    { value: "go", label: "Go" },
    { value: "rust", label: "Rust" }
];

export default function DebuggerPage() {
    const [language, setLanguage] = useState("python");
    const [code, setCode] = useState("");
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<DebugResult | null>(null);
    const [error, setError] = useState("");

    const handleDebug = async () => {
        if (!code.trim()) {
            setError("Please enter some code to debug");
            return;
        }

        if (code.length > 10000) {
            setError("Code is too long (maximum 10,000 characters)");
            return;
        }

        setLoading(true);
        setError("");
        setResult(null);

        try {
            const token = localStorage.getItem("access_token");
            if (!token) {
                window.location.href = "/login";
                return;
            }

            const response = await fetch("http://localhost:5000/ai/debug", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({ language, code })
            });

            if (response.status === 401) {
                localStorage.removeItem("access_token");
                window.location.href = "/login";
                return;
            }

            if (!response.ok) {
                throw new Error("Failed to analyze code");
            }

            const data = await response.json();
            setResult(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : "An error occurred");
        } finally {
            setLoading(false);
        }
    };

    const handleClear = () => {
        setCode("");
        setResult(null);
        setError("");
    };

    return (
        <div className="container mx-auto p-6 max-w-7xl">
            <div className="mb-8 text-center">
                <h1 className="text-4xl font-bold mb-2">
                    <GradientText>AI Code Debugger</GradientText>
                </h1>
                <p className="text-muted-foreground">
                    Find and fix bugs in your code with AI assistance
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Input Section */}
                <div className="space-y-4">
                    <GlassCard className="p-6">
                        <div className="space-y-4">
                            <div>
                                <Label htmlFor="language" className="text-lg">
                                    Programming Language
                                </Label>
                                <select
                                    id="language"
                                    value={language}
                                    onChange={(e) => setLanguage(e.target.value)}
                                    disabled={loading}
                                    className="w-full mt-2 p-2 bg-black/40 border border-white/10 rounded-lg text-white"
                                >
                                    {SUPPORTED_LANGUAGES.map((lang) => (
                                        <option key={lang.value} value={lang.value}>
                                            {lang.label}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <Label htmlFor="code" className="text-lg">
                                    Your Code
                                </Label>
                                <textarea
                                    id="code"
                                    value={code}
                                    onChange={(e) => setCode(e.target.value)}
                                    disabled={loading}
                                    placeholder="Paste your code here..."
                                    className="w-full mt-2 p-4 bg-black/40 border border-white/10 rounded-lg text-white font-mono text-sm min-h-[400px] resize-y"
                                />
                                <div className="flex justify-between items-center mt-2 text-xs text-muted-foreground">
                                    <span>{code.length} / 10,000 characters</span>
                                    {code.length > 10000 && (
                                        <span className="text-red-400">Code too long!</span>
                                    )}
                                </div>
                            </div>

                            {error && (
                                <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400">
                                    {error}
                                </div>
                            )}

                            <div className="flex gap-2">
                                <Button
                                    onClick={handleDebug}
                                    disabled={loading || !code.trim() || code.length > 10000}
                                    className="flex-1 bg-primary hover:bg-primary/90"
                                >
                                    {loading ? (
                                        <>
                                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                            Analyzing...
                                        </>
                                    ) : (
                                        <>
                                            <Bug className="mr-2 h-4 w-4" />
                                            Debug Code
                                        </>
                                    )}
                                </Button>
                                <Button
                                    onClick={handleClear}
                                    disabled={loading}
                                    variant="outline"
                                    className="bg-white/5"
                                >
                                    Clear
                                </Button>
                            </div>
                        </div>
                    </GlassCard>
                </div>

                {/* Results Section */}
                <div className="space-y-4">
                    {result && (
                        <>
                            {/* Errors Section */}
                            <GlassCard className="p-6">
                                <div className="flex items-center gap-2 mb-4">
                                    {result.errors.length > 0 ? (
                                        <>
                                            <AlertCircle className="h-5 w-5 text-red-400" />
                                            <h2 className="text-xl font-bold">
                                                Issues Found ({result.errors.length})
                                            </h2>
                                        </>
                                    ) : (
                                        <>
                                            <CheckCircle className="h-5 w-5 text-green-400" />
                                            <h2 className="text-xl font-bold">No Issues Found</h2>
                                        </>
                                    )}
                                </div>
                                {result.errors.length > 0 ? (
                                    <div className="space-y-3">
                                        {result.errors.map((err, index) => (
                                            <div
                                                key={index}
                                                className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg"
                                            >
                                                <div className="flex items-start gap-2">
                                                    <span className="text-red-400 font-mono text-sm">
                                                        Line {err.line}:
                                                    </span>
                                                    <span className="text-sm text-muted-foreground">
                                                        {err.message}
                                                    </span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <p className="text-muted-foreground">
                                        Your code looks good! No syntax errors or common issues detected.
                                    </p>
                                )}
                            </GlassCard>

                            {/* Corrected Code Section */}
                            {result.corrected_code && (
                                <GlassCard className="p-6">
                                    <h2 className="text-xl font-bold mb-4">Corrected Code</h2>
                                    <div className="relative">
                                        <pre className="bg-black/40 p-4 rounded-lg overflow-x-auto max-h-[400px]">
                                            <code className="text-sm text-gray-300 font-mono">
                                                {result.corrected_code}
                                            </code>
                                        </pre>
                                        <Button
                                            onClick={() => {
                                                navigator.clipboard.writeText(result.corrected_code);
                                            }}
                                            variant="outline"
                                            size="sm"
                                            className="absolute top-2 right-2 bg-white/5"
                                        >
                                            Copy
                                        </Button>
                                    </div>
                                </GlassCard>
                            )}

                            {/* Explanation Section */}
                            {result.explanation && (
                                <GlassCard className="p-6">
                                    <h2 className="text-xl font-bold mb-4">Explanation</h2>
                                    <p className="text-muted-foreground whitespace-pre-wrap">
                                        {result.explanation}
                                    </p>
                                </GlassCard>
                            )}
                        </>
                    )}

                    {!result && !loading && (
                        <GlassCard className="p-6">
                            <div className="text-center py-12">
                                <Bug className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                                <p className="text-muted-foreground">
                                    Enter your code and click "Debug Code" to get started
                                </p>
                            </div>
                        </GlassCard>
                    )}
                </div>
            </div>
        </div>
    );
}
