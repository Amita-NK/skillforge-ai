"use client";

import { useState, useEffect } from "react";
import { GlassCard } from "@/components/ui/glass-card";
import { GradientText } from "@/components/ui/gradient-text";
import { TrendingUp, Target, Clock, Award, Lightbulb, Loader2 } from "lucide-react";

interface ProgressRecord {
    id: number;
    user_id: number;
    topic: string;
    accuracy: number;
    attempts: number;
    time_spent: number;
    last_updated: string;
}

interface Recommendation {
    topic: string;
    type: "EASIER" | "PRACTICE" | "ADVANCE" | "START";
    reason: string;
}

export default function ProgressPage() {
    const [progress, setProgress] = useState<ProgressRecord[]>([]);
    const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        fetchProgress();
        fetchRecommendations();
    }, []);

    const fetchProgress = async () => {
        try {
            const token = localStorage.getItem("access_token");
            if (!token) {
                window.location.href = "/login";
                return;
            }

            const response = await fetch("http://localhost:5000/api/progress", {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });

            if (response.status === 401) {
                localStorage.removeItem("access_token");
                window.location.href = "/login";
                return;
            }

            if (!response.ok) {
                throw new Error("Failed to fetch progress");
            }

            const data = await response.json();
            setProgress(data.progress || []);
        } catch (err) {
            setError(err instanceof Error ? err.message : "An error occurred");
        } finally {
            setLoading(false);
        }
    };

    const fetchRecommendations = async () => {
        try {
            const token = localStorage.getItem("access_token");
            if (!token) return;

            const response = await fetch("http://localhost:5000/ai/recommendations", {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                setRecommendations(data.recommendations || []);
            }
        } catch (err) {
            console.error("Failed to fetch recommendations:", err);
        }
    };

    const getRecommendationIcon = (type: string) => {
        switch (type) {
            case "EASIER":
                return <Lightbulb className="h-5 w-5 text-yellow-400" />;
            case "PRACTICE":
                return <Target className="h-5 w-5 text-blue-400" />;
            case "ADVANCE":
                return <Award className="h-5 w-5 text-green-400" />;
            default:
                return <TrendingUp className="h-5 w-5 text-purple-400" />;
        }
    };

    const getRecommendationColor = (type: string) => {
        switch (type) {
            case "EASIER":
                return "border-yellow-500/20 bg-yellow-500/10";
            case "PRACTICE":
                return "border-blue-500/20 bg-blue-500/10";
            case "ADVANCE":
                return "border-green-500/20 bg-green-500/10";
            default:
                return "border-purple-500/20 bg-purple-500/10";
        }
    };

    const formatTime = (seconds: number) => {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        if (hours > 0) {
            return `${hours}h ${minutes}m`;
        }
        return `${minutes}m`;
    };

    const calculateOverallStats = () => {
        if (progress.length === 0) {
            return {
                avgAccuracy: 0,
                totalAttempts: 0,
                totalTime: 0,
                topicsStudied: 0
            };
        }

        const totalAccuracy = progress.reduce((sum, p) => sum + p.accuracy, 0);
        const totalAttempts = progress.reduce((sum, p) => sum + p.attempts, 0);
        const totalTime = progress.reduce((sum, p) => sum + p.time_spent, 0);

        return {
            avgAccuracy: totalAccuracy / progress.length,
            totalAttempts,
            totalTime,
            topicsStudied: progress.length
        };
    };

    if (loading) {
        return (
            <div className="container mx-auto p-6 max-w-6xl">
                <div className="flex items-center justify-center min-h-[400px]">
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                </div>
            </div>
        );
    }

    const stats = calculateOverallStats();

    return (
        <div className="container mx-auto p-6 max-w-6xl">
            <div className="mb-8 text-center">
                <h1 className="text-4xl font-bold mb-2">
                    <GradientText>Your Progress</GradientText>
                </h1>
                <p className="text-muted-foreground">
                    Track your learning journey and get personalized recommendations
                </p>
            </div>

            {error && (
                <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400">
                    {error}
                </div>
            )}

            {/* Overall Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                <GlassCard className="p-6">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-primary/20 rounded-lg">
                            <TrendingUp className="h-6 w-6 text-primary" />
                        </div>
                        <div>
                            <p className="text-sm text-muted-foreground">Avg Accuracy</p>
                            <p className="text-2xl font-bold">{stats.avgAccuracy.toFixed(1)}%</p>
                        </div>
                    </div>
                </GlassCard>

                <GlassCard className="p-6">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-blue-500/20 rounded-lg">
                            <Target className="h-6 w-6 text-blue-400" />
                        </div>
                        <div>
                            <p className="text-sm text-muted-foreground">Topics Studied</p>
                            <p className="text-2xl font-bold">{stats.topicsStudied}</p>
                        </div>
                    </div>
                </GlassCard>

                <GlassCard className="p-6">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-green-500/20 rounded-lg">
                            <Award className="h-6 w-6 text-green-400" />
                        </div>
                        <div>
                            <p className="text-sm text-muted-foreground">Total Attempts</p>
                            <p className="text-2xl font-bold">{stats.totalAttempts}</p>
                        </div>
                    </div>
                </GlassCard>

                <GlassCard className="p-6">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-purple-500/20 rounded-lg">
                            <Clock className="h-6 w-6 text-purple-400" />
                        </div>
                        <div>
                            <p className="text-sm text-muted-foreground">Time Spent</p>
                            <p className="text-2xl font-bold">{formatTime(stats.totalTime)}</p>
                        </div>
                    </div>
                </GlassCard>
            </div>

            {/* Recommendations */}
            {recommendations.length > 0 && (
                <div className="mb-8">
                    <h2 className="text-2xl font-bold mb-4">Personalized Recommendations</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {recommendations.map((rec, index) => (
                            <GlassCard
                                key={index}
                                className={`p-6 border ${getRecommendationColor(rec.type)}`}
                            >
                                <div className="flex items-start gap-3">
                                    {getRecommendationIcon(rec.type)}
                                    <div className="flex-1">
                                        <h3 className="font-semibold mb-1">{rec.topic}</h3>
                                        <p className="text-sm text-muted-foreground">{rec.reason}</p>
                                        <span className="inline-block mt-2 px-2 py-1 text-xs rounded-full bg-white/10">
                                            {rec.type}
                                        </span>
                                    </div>
                                </div>
                            </GlassCard>
                        ))}
                    </div>
                </div>
            )}

            {/* Detailed Progress */}
            <div>
                <h2 className="text-2xl font-bold mb-4">Topic Progress</h2>
                {progress.length === 0 ? (
                    <GlassCard className="p-12 text-center">
                        <TrendingUp className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                        <p className="text-muted-foreground">
                            No progress data yet. Start taking quizzes to track your progress!
                        </p>
                    </GlassCard>
                ) : (
                    <div className="space-y-4">
                        {progress.map((record) => (
                            <GlassCard key={record.id} className="p-6">
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className="text-xl font-semibold">{record.topic}</h3>
                                    <span className={`text-2xl font-bold ${
                                        record.accuracy >= 80 ? "text-green-400" :
                                        record.accuracy >= 50 ? "text-yellow-400" :
                                        "text-red-400"
                                    }`}>
                                        {record.accuracy.toFixed(1)}%
                                    </span>
                                </div>

                                <div className="w-full bg-white/10 rounded-full h-2 mb-4">
                                    <div
                                        className={`h-2 rounded-full transition-all ${
                                            record.accuracy >= 80 ? "bg-green-400" :
                                            record.accuracy >= 50 ? "bg-yellow-400" :
                                            "bg-red-400"
                                        }`}
                                        style={{ width: `${record.accuracy}%` }}
                                    />
                                </div>

                                <div className="grid grid-cols-3 gap-4 text-sm">
                                    <div>
                                        <p className="text-muted-foreground">Attempts</p>
                                        <p className="font-semibold">{record.attempts}</p>
                                    </div>
                                    <div>
                                        <p className="text-muted-foreground">Time Spent</p>
                                        <p className="font-semibold">{formatTime(record.time_spent)}</p>
                                    </div>
                                    <div>
                                        <p className="text-muted-foreground">Last Updated</p>
                                        <p className="font-semibold">
                                            {new Date(record.last_updated).toLocaleDateString()}
                                        </p>
                                    </div>
                                </div>
                            </GlassCard>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
