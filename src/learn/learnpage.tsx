import Link from "next/link";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import { GradientText } from "@/components/ui/gradient-text";
import { ArrowRight, BookOpen, Clock, Code2, Database, LayoutTemplate, Star } from "lucide-react";
import { Progress } from "@/components/ui/progress";

const modules = [
    {
        category: "Frontend Development",
        icon: LayoutTemplate,
        color: "text-blue-400 bg-blue-500/10",
        topics: [
            { id: "react-hooks", title: "Mastering React Hooks", progress: 65, time: "45m", level: "Intermediate" },
            { id: "css-grid", title: "CSS Grid & Flexbox", progress: 100, time: "30m", level: "Beginner" },
            { id: "nextjs-routing", title: "Next.js App Router", progress: 0, time: "60m", level: "Advanced" },
        ]
    },
    {
        category: "Data Structures & Algos",
        icon: Code2,
        color: "text-purple-400 bg-purple-500/10",
        topics: [
            { id: "binary-trees", title: "Visualizing Binary Trees", progress: 20, time: "90m", level: "Hard" },
            { id: "sorting", title: "Sorting Algorithms", progress: 0, time: "45m", level: "Beginner" },
        ]
    },
    {
        category: "System Design",
        icon: Database,
        color: "text-green-400 bg-green-500/10",
        topics: [
            { id: "caching", title: "Caching Strategies", progress: 0, time: "40m", level: "Intermediate" },
        ]
    }
];

export default function LearningCatalog() {
    return (
        <div className="space-y-8">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Learning Studio</h1>
                <p className="text-muted-foreground">Select a module to start your adaptive learning session.</p>
            </div>

            <div className="grid gap-8">
                {modules.map((module, i) => (
                    <div key={i} className="space-y-4">
                        <div className="flex items-center gap-3">
                            <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${module.color}`}>
                                <module.icon className="h-6 w-6" />
                            </div>
                            <h2 className="text-xl font-semibold">{module.category}</h2>
                        </div>

                        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                            {module.topics.map((topic) => (
                                <GlassCard key={topic.id} className="flex flex-col justify-between p-6 transition-all hover:scale-[1.02]">
                                    <div className="space-y-4">
                                        <div className="flex items-start justify-between">
                                            <span className={`rounded-full px-2 py-1 text-xs font-medium ${topic.level === "Beginner" ? "bg-green-500/10 text-green-400" :
                                                    topic.level === "Intermediate" ? "bg-yellow-500/10 text-yellow-400" :
                                                        "bg-red-500/10 text-red-400"
                                                }`}>
                                                {topic.level}
                                            </span>
                                            {topic.progress === 100 && <Star className="h-4 w-4 fill-yellow-500 text-yellow-500" />}
                                        </div>

                                        <div>
                                            <h3 className="text-lg font-bold leading-tight mb-1">{topic.title}</h3>
                                            <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                                <Clock className="h-3 w-3" />
                                                <span>{topic.time}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="mt-6 space-y-3">
                                        <div className="space-y-1">
                                            <div className="flex justify-between text-xs">
                                                <span>Progress</span>
                                                <span>{topic.progress}%</span>
                                            </div>
                                            <Progress value={topic.progress} className="h-1.5" />
                                        </div>

                                        <Link href={`/learn/${topic.id}`} className="block">
                                            <Button className="w-full bg-primary/10 text-primary hover:bg-primary hover:text-primary-foreground">
                                                {topic.progress === 0 ? "Start Lesson" : topic.progress === 100 ? "Review" : "Continue"}
                                                <ArrowRight className="ml-2 h-4 w-4" />
                                            </Button>
                                        </Link>
                                    </div>
                                </GlassCard>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
