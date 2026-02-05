import { GlassCard } from "@/components/ui/glass-card";
import { Badge } from "@/components/ui/badge";
import { Trophy, Medal, Flame, Target, Shield, Zap } from "lucide-react";
import { Progress } from "@/components/ui/progress";

export default function GamificationPage() {
    return (
        <div className="space-y-8">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Your Achievements</h1>
                    <p className="text-muted-foreground">Level 12 • 2,450 XP</p>
                </div>
                <div className="flex items-center gap-2 rounded-full border border-orange-500/20 bg-orange-500/10 px-4 py-2 text-orange-400">
                    <Flame className="h-5 w-5 fill-current" />
                    <span className="font-bold">12 Day Streak!</span>
                </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-3">
                {/* Main Column: Badges & Challenges */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Daily Challenges */}
                    <section>
                        <h2 className="mb-4 text-xl font-semibold">Daily Quests</h2>
                        <div className="grid gap-4 sm:grid-cols-2">
                            {[
                                { title: "Fix 3 Bugs", progress: 2, total: 3, xp: 50 },
                                { title: "Complete 1 Lesson", progress: 0, total: 1, xp: 100 },
                            ].map((quest, i) => (
                                <GlassCard key={i} className="p-4" gradient={false}>
                                    <div className="mb-2 flex justify-between">
                                        <span className="font-medium">{quest.title}</span>
                                        <Badge variant="secondary" className="bg-yellow-500/10 text-yellow-500">+{quest.xp} XP</Badge>
                                    </div>
                                    <Progress value={(quest.progress / quest.total) * 100} className="h-2" />
                                    <div className="mt-2 text-xs text-muted-foreground">{quest.progress} / {quest.total} completed</div>
                                </GlassCard>
                            ))}
                        </div>
                    </section>

                    {/* Badges */}
                    <section>
                        <h2 className="mb-4 text-xl font-semibold">Earned Badges</h2>
                        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                            {[
                                { name: "Bug Hunter", icon: Bug, color: "text-red-400" },
                                { name: "Fast Learner", icon: Zap, color: "text-yellow-400" },
                                { name: "Consistent", icon: Flame, color: "text-orange-400" },
                                { name: "Pro", icon: Shield, color: "text-blue-400" },
                            ].map((badge, i) => (
                                <div key={i} className="flex flex-col items-center justify-center gap-2 rounded-xl border border-white/5 bg-white/5 p-6 text-center transition-all hover:bg-white/10 hover:scale-105">
                                    <div className={`rounded-full bg-white/5 p-3 ${badge.color}`}>
                                        <badge.icon className="h-8 w-8" />
                                    </div>
                                    <span className="font-medium">{badge.name}</span>
                                </div>
                            ))}
                        </div>
                    </section>
                </div>

                {/* Sidebar: Leaderboard */}
                <div className="space-y-6">
                    <h2 className="text-xl font-semibold">Global Leaderboard</h2>
                    <GlassCard className="p-0">
                        {/* Header */}
                        <div className="flex items-center justify-between border-b border-white/5 bg-white/5 p-4 text-xs font-medium text-muted-foreground">
                            <span>User</span>
                            <span>XP</span>
                        </div>
                        {/* Rows */}
                        <div className="divide-y divide-white/5">
                            {[
                                { name: "Sarah K.", xp: 3200, country: "🇺🇸" },
                                { name: "Mike Chen", xp: 2950, country: "🇨🇦" },
                                { name: "Alex Dev", xp: 2450, country: "🇬🇧" },
                                { name: "Jessica R.", xp: 2100, country: "🇩🇪" },
                                { name: "David L.", xp: 1800, country: "🇫🇷" },
                            ].map((user, i) => (
                                <div key={i} className={`flex items-center justify-between p-4 ${user.name === "Alex Dev" ? "bg-primary/10" : "hover:bg-white/5"}`}>
                                    <div className="flex items-center gap-3">
                                        <div className="flex w-6 justify-center font-bold text-muted-foreground">{i + 1}</div>
                                        <div className="flex items-center gap-2">
                                            {i === 0 && <Trophy className="h-4 w-4 text-yellow-500" />}
                                            <span className="font-medium">{user.name}</span>
                                            <span className="opacity-50">{user.country}</span>
                                        </div>
                                    </div>
                                    <span className="font-mono text-sm">{user.xp}</span>
                                </div>
                            ))}
                        </div>
                    </GlassCard>
                </div>
            </div>
        </div>
    );
}

// Icon helper
function Bug({ className }: { className?: string }) {
    return (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={className}
        >
            <path d="m8 2 1.88 1.88" />
            <path d="M14.12 3.88 16 2" />
            <path d="M9 7.13v-1a3.003 3.003 0 1 1 6 0v1" />
            <path d="M12 20c-3.3 0-6-2.7-6-6v-3a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v3c0 3.3-2.7 6-6 6" />
            <path d="M12 20v-9" />
            <path d="M6.53 9C4.6 8.8 3 7.1 3 5" />
            <path d="M6 13H2" />
            <path d="M3 21c0-2.1 1.7-3.9 3.8-4" />
            <path d="M20.97 5c0 2.1-1.6 3.8-3.5 4" />
            <path d="M22 13h-4" />
            <path d="M17.2 17c2.1.1 3.8 1.9 3.8 4" />
        </svg>
    )
}
