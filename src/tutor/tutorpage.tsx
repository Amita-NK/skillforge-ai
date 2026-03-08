"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { GlassCard } from "@/components/ui/glass-card";
import { GradientText } from "@/components/ui/gradient-text";
import { BookOpen, Loader2, Lightbulb, Code } from "lucide-react";

export default function TutorPage() {
    const [topic, setTopic] = useState("");
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<{
        explanation: string;
        examples: string[];
        analogy: string;
    } | null>(null);
    const [error, setError] = useState("");

    const handleExplain = async () => {
        if (!topic.trim()) {
            setError("Please enter a topic");
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

            const response = await fetch("http://localhost:5000/ai/explain", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({ topic })
            });

            if (response.status === 401) {
                localStorage.removeItem("access_token");
                window.location.href = "/login";
                return;
            }

            if (!response.ok) {
                throw new Error("Failed to generate explanation");
            }

            const data = await response.json();
            setResult(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : "An error occurred");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container mx-auto p-6 max-w-4xl">
            <div className="mb-8 text-center">
                <h1 className="text-4xl font-bold mb-2">
                    <GradientText>AI Tutor</GradientText>
                </h1>
                <p className="text-muted-foreground">
                    Get detailed explanations for any programming concept
                </p>
            </div>

            <GlassCard className="p-6 mb-6">
                <div className="space-y-4">
                    <div>
                        <Label htmlFor="topic" className="text-lg">
                            What would you like to learn?
                        </Label>
                        <div className="flex gap-2 mt-2">
                            <Input
                                id="topic"
                                placeholder="e.g., binary search algorithm, recursion, async/await..."
                                value={topic}
                                onChange={(e) => setTopic(e.target.value)}
                                onKeyPress={(e) => e.key === "Enter" && handleExplain()}
                                className="bg-transparent flex-1"
                                disabled={loading}
                            />
                            <Button
                                onClick={handleExplain}
                                disabled={loading || !topic.trim()}
                                className="bg-primary hover:bg-primary/90"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                        Thinking...
                                    </>
                                ) : (
                                    <>
                                        <BookOpen className="mr-2 h-4 w-4" />
                                        Explain
                                    </>
                                )}
                            </Button>
                        </div>
                    </div>

                    {error && (
                        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400">
                            {error}
                        </div>
                    )}
                </div>
            </GlassCard>

            {result && (
                <div className="space-y-6">
                    {/* Explanation Section */}
                    <GlassCard className="p-6">
                        <div className="flex items-center gap-2 mb-4">
                            <BookOpen className="h-5 w-5 text-primary" />
                            <h2 className="text-2xl font-bold">Explanation</h2>
                        </div>
                        <div className="prose prose-invert max-w-none">
                            <p className="text-muted-foreground whitespace-pre-wrap">
                                {result.explanation}
                            </p>
                        </div>
                    </GlassCard>

                    {/* Analogy Section */}
                    {result.analogy && (
                        <GlassCard className="p-6">
                            <div className="flex items-center gap-2 mb-4">
                                <Lightbulb className="h-5 w-5 text-yellow-400" />
                                <h2 className="text-2xl font-bold">Real-World Analogy</h2>
                            </div>
                            <div className="prose prose-invert max-w-none">
                                <p className="text-muted-foreground whitespace-pre-wrap">
                                    {result.analogy}
                                </p>
                            </div>
                        </GlassCard>
                    )}

                    {/* Examples Section */}
                    {result.examples && result.examples.length > 0 && (
                        <GlassCard className="p-6">
                            <div className="flex items-center gap-2 mb-4">
                                <Code className="h-5 w-5 text-green-400" />
                                <h2 className="text-2xl font-bold">Code Examples</h2>
                            </div>
                            <div className="space-y-4">
                                {result.examples.map((example, index) => (
                                    <div key={index} className="relative">
                                        <pre className="bg-black/40 p-4 rounded-lg overflow-x-auto">
                                            <code className="text-sm text-gray-300">
                                                {example}
                                            </code>
                                        </pre>
                                    </div>
                                ))}
                            </div>
                        </GlassCard>
                    )}
                </div>
            )}
        </div>
    );
}
