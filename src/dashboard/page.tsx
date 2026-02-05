import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import { GradientText } from "@/components/ui/gradient-text";
import { ArrowRight, BookOpen, Bug, Target, TrendingUp } from "lucide-react";

export default function DashboardPage() {
    return (
        <div className="space-y-8">
            {/* Welcome Section */}
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">
                        Welcome back, <GradientText>Alex</GradientText>
                    </h1>
                    <p className="text-muted-foreground">
                        You're on a 12-day streak! Keep up the momentum.
                    </p>
                </div>
                <div className="flex gap-3">
                    <Button className="bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg shadow-primary/20">
                        Resume Learning
                        <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                {[
                    { label: "Hours Learned", value: "42.5h", icon: TrendingUp, color: "text-green-400", bg: "bg-green-500/10" },
                    { label: "Skills Mastered", value: "8", icon: Target, color: "text-blue-400", bg: "bg-blue-500/10" },
                    { label: "Bugs Fixed", value: "124", icon: Bug, color: "text-pink-400", bg: "bg-pink-500/10" },
                    { label: "Lessons Completed", value: "36", icon: BookOpen, color: "text-purple-400", bg: "bg-purple-500/10" },
                ].map((stat, i) => (
                    <GlassCard key={i} className="flex items-center gap-4 p-4" gradient={false}>
                        <div className={`flex h-12 w-12 items-center justify-center rounded-lg ${stat.bg} ${stat.color}`}>
                            <stat.icon className="h-6 w-6" />
                        </div>
                        <div>
                            <p className="text-sm font-medium text-muted-foreground">{stat.label}</p>
                            <h3 className="text-2xl font-bold">{stat.value}</h3>
                        </div>
                    </GlassCard>
                ))}
            </div>

            {/* Main Content Area: Recommendations & Activity */}
            <div className="grid gap-6 lg:grid-cols-3">
                {/* Recommended Path */}
                <div className="space-y-6 lg:col-span-2">
                    <div>
                        <h2 className="text-xl font-semibold tracking-tight">Recommended for You</h2>
                        <p className="text-sm text-muted-foreground">Based on your recent debugging patterns.</p>
                    </div>

                    <div className="grid gap-4">
                        {[1, 2, 3].map((i) => (
                            <GlassCard key={i} className="group relative flex items-center justify-between p-6 transition-all hover:border-primary/50">
                                <div className="flex items-center gap-4">
                                    <div className="flex h-12 w-12 items-center justify-center rounded-full bg-white/5 font-bold text-muted-foreground group-hover:bg-primary/20 group-hover:text-primary">
                                        {i}
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-medium group-hover:text-primary transition-colors">Advanced React Performance Optimization</h3>
                                        <p className="text-sm text-muted-foreground">Estimated time: 15 min • Difficulty: Hard</p>
                                    </div>
                                </div>
                                <Button variant="ghost" size="icon" className="group-hover:translate-x-1 transition-transform">
                                    <ArrowRight className="h-5 w-5" />
                                </Button>
                            </GlassCard>
                        ))}
                    </div>
                </div>

                {/* Side Panel: Leaderboard / Activity */}
                <div className="space-y-6">
                    <h2 className="text-xl font-semibold tracking-tight">Top Learners</h2>
                    <GlassCard className="p-0">
                        <div className="divide-y divide-white/5">
                            {[
                                { name: "Sarah K.", xp: "3,200 XP", rank: 1 },
                                { name: "Mike Chen", xp: "2,950 XP", rank: 2 },
                                { name: "Alex Dev", xp: "2,450 XP", rank: 3 }, // Current User
                                { name: "Jessica R.", xp: "2,100 XP", rank: 4 },
                            ].map((user, i) => (
                                <div key={i} className={`flex items-center justify-between p-4 ${user.name === "Alex Dev" ? "bg-primary/10" : "hover:bg-white/5"}`}>
                                    <div className="flex items-center gap-3">
                                        <span className={`flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold ${i < 3 ? "bg-yellow-500/20 text-yellow-500" : "bg-white/5 text-muted-foreground"}`}>
                                            {user.rank}
                                        </span>
                                        <span className="text-sm font-medium">{user.name}</span>
                                    </div>
                                    <span className="text-xs font-bold text-muted-foreground">{user.xp}</span>
                                </div>
                            ))}
                        </div>
                    </GlassCard>
                </div>
            </div>
        </div>
    );
}
