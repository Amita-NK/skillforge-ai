"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { GlassCard } from "@/components/ui/glass-card";
import { GradientText } from "@/components/ui/gradient-text";
import { Brain, Loader2, CheckCircle2, XCircle, ArrowRight, RotateCcw } from "lucide-react";

interface Question {
    question: string;
    options: string[];
    correct: number;
    explanation: string;
}

type QuizState = "setup" | "taking" | "results";

export default function QuizPage() {
    // Setup state
    const [topic, setTopic] = useState("");
    const [difficulty, setDifficulty] = useState<"easy" | "medium" | "hard">("medium");
    const [count, setCount] = useState(5);
    
    // Quiz state
    const [quizState, setQuizState] = useState<QuizState>("setup");
    const [questions, setQuestions] = useState<Question[]>([]);
    const [currentQuestion, setCurrentQuestion] = useState(0);
    const [selectedAnswers, setSelectedAnswers] = useState<number[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleGenerateQuiz = async () => {
        if (!topic.trim()) {
            setError("Please enter a topic");
            return;
        }

        setLoading(true);
        setError("");

        try {
            const token = localStorage.getItem("access_token");
            if (!token) {
                window.location.href = "/login";
                return;
            }

            const response = await fetch("http://localhost:5000/ai/quiz", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({ topic, difficulty, count })
            });

            if (response.status === 401) {
                localStorage.removeItem("access_token");
                window.location.href = "/login";
                return;
            }

            if (!response.ok) {
                throw new Error("Failed to generate quiz");
            }

            const data = await response.json();
            setQuestions(data.questions);
            setSelectedAnswers(new Array(data.questions.length).fill(-1));
            setQuizState("taking");
            setCurrentQuestion(0);
        } catch (err) {
            setError(err instanceof Error ? err.message : "An error occurred");
        } finally {
            setLoading(false);
        }
    };

    const handleSelectAnswer = (optionIndex: number) => {
        const newAnswers = [...selectedAnswers];
        newAnswers[currentQuestion] = optionIndex;
        setSelectedAnswers(newAnswers);
    };

    const handleNext = () => {
        if (currentQuestion < questions.length - 1) {
            setCurrentQuestion(currentQuestion + 1);
        }
    };

    const handlePrevious = () => {
        if (currentQuestion > 0) {
            setCurrentQuestion(currentQuestion - 1);
        }
    };

    const handleFinish = async () => {
        const score = selectedAnswers.reduce((acc, answer, index) => {
            return acc + (answer === questions[index].correct ? 1 : 0);
        }, 0);

        // Submit results to backend
        try {
            const token = localStorage.getItem("access_token");
            if (token) {
                await fetch("http://localhost:5000/api/quiz/complete", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        topic,
                        difficulty,
                        score,
                        total_questions: questions.length,
                        time_spent: 0 // TODO: Track actual time
                    })
                });
            }
        } catch (err) {
            console.error("Failed to submit quiz results:", err);
        }

        setQuizState("results");
    };

    const handleRestart = () => {
        setQuizState("setup");
        setQuestions([]);
        setSelectedAnswers([]);
        setCurrentQuestion(0);
        setTopic("");
        setError("");
    };

    const calculateScore = () => {
        return selectedAnswers.reduce((acc, answer, index) => {
            return acc + (answer === questions[index].correct ? 1 : 0);
        }, 0);
    };

    if (quizState === "setup") {
        return (
            <div className="container mx-auto p-6 max-w-2xl">
                <div className="mb-8 text-center">
                    <h1 className="text-4xl font-bold mb-2">
                        <GradientText>AI Quiz Generator</GradientText>
                    </h1>
                    <p className="text-muted-foreground">
                        Test your knowledge with AI-generated quizzes
                    </p>
                </div>

                <GlassCard className="p-6">
                    <div className="space-y-6">
                        <div>
                            <Label htmlFor="topic" className="text-lg">Topic</Label>
                            <Input
                                id="topic"
                                placeholder="e.g., Python basics, Data structures..."
                                value={topic}
                                onChange={(e) => setTopic(e.target.value)}
                                className="bg-transparent mt-2"
                                disabled={loading}
                            />
                        </div>

                        <div>
                            <Label className="text-lg">Difficulty</Label>
                            <div className="grid grid-cols-3 gap-2 mt-2">
                                {(["easy", "medium", "hard"] as const).map((level) => (
                                    <Button
                                        key={level}
                                        variant={difficulty === level ? "default" : "outline"}
                                        onClick={() => setDifficulty(level)}
                                        disabled={loading}
                                        className={difficulty === level ? "bg-primary" : "bg-white/5"}
                                    >
                                        {level.charAt(0).toUpperCase() + level.slice(1)}
                                    </Button>
                                ))}
                            </div>
                        </div>

                        <div>
                            <Label htmlFor="count" className="text-lg">
                                Number of Questions ({count})
                            </Label>
                            <input
                                id="count"
                                type="range"
                                min="1"
                                max="20"
                                value={count}
                                onChange={(e) => setCount(parseInt(e.target.value))}
                                disabled={loading}
                                className="w-full mt-2"
                            />
                            <div className="flex justify-between text-xs text-muted-foreground mt-1">
                                <span>1</span>
                                <span>20</span>
                            </div>
                        </div>

                        {error && (
                            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400">
                                {error}
                            </div>
                        )}

                        <Button
                            onClick={handleGenerateQuiz}
                            disabled={loading || !topic.trim()}
                            className="w-full bg-primary hover:bg-primary/90"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Generating Quiz...
                                </>
                            ) : (
                                <>
                                    <Brain className="mr-2 h-4 w-4" />
                                    Generate Quiz
                                </>
                            )}
                        </Button>
                    </div>
                </GlassCard>
            </div>
        );
    }

    if (quizState === "taking") {
        const question = questions[currentQuestion];
        const progress = ((currentQuestion + 1) / questions.length) * 100;

        return (
            <div className="container mx-auto p-6 max-w-3xl">
                <div className="mb-6">
                    <div className="flex justify-between items-center mb-2">
                        <h2 className="text-xl font-bold">
                            Question {currentQuestion + 1} of {questions.length}
                        </h2>
                        <span className="text-sm text-muted-foreground">
                            {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)} • {topic}
                        </span>
                    </div>
                    <div className="w-full bg-white/10 rounded-full h-2">
                        <div
                            className="bg-primary h-2 rounded-full transition-all"
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                </div>

                <GlassCard className="p-6 mb-6">
                    <h3 className="text-xl font-semibold mb-6">{question.question}</h3>
                    <div className="space-y-3">
                        {question.options.map((option, index) => (
                            <button
                                key={index}
                                onClick={() => handleSelectAnswer(index)}
                                className={`w-full p-4 text-left rounded-lg border-2 transition-all ${
                                    selectedAnswers[currentQuestion] === index
                                        ? "border-primary bg-primary/20"
                                        : "border-white/10 bg-white/5 hover:bg-white/10"
                                }`}
                            >
                                <div className="flex items-center gap-3">
                                    <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                                        selectedAnswers[currentQuestion] === index
                                            ? "border-primary bg-primary"
                                            : "border-white/30"
                                    }`}>
                                        {selectedAnswers[currentQuestion] === index && (
                                            <div className="w-2 h-2 bg-white rounded-full" />
                                        )}
                                    </div>
                                    <span>{option}</span>
                                </div>
                            </button>
                        ))}
                    </div>
                </GlassCard>

                <div className="flex justify-between gap-4">
                    <Button
                        onClick={handlePrevious}
                        disabled={currentQuestion === 0}
                        variant="outline"
                        className="bg-white/5"
                    >
                        Previous
                    </Button>
                    {currentQuestion === questions.length - 1 ? (
                        <Button
                            onClick={handleFinish}
                            disabled={selectedAnswers[currentQuestion] === -1}
                            className="bg-primary hover:bg-primary/90"
                        >
                            Finish Quiz
                        </Button>
                    ) : (
                        <Button
                            onClick={handleNext}
                            disabled={selectedAnswers[currentQuestion] === -1}
                            className="bg-primary hover:bg-primary/90"
                        >
                            Next <ArrowRight className="ml-2 h-4 w-4" />
                        </Button>
                    )}
                </div>
            </div>
        );
    }

    // Results state
    const score = calculateScore();
    const percentage = (score / questions.length) * 100;

    return (
        <div className="container mx-auto p-6 max-w-3xl">
            <div className="mb-8 text-center">
                <h1 className="text-4xl font-bold mb-2">
                    <GradientText>Quiz Complete!</GradientText>
                </h1>
                <p className="text-2xl font-semibold mt-4">
                    Score: {score} / {questions.length} ({percentage.toFixed(0)}%)
                </p>
            </div>

            <div className="space-y-4 mb-6">
                {questions.map((question, index) => {
                    const isCorrect = selectedAnswers[index] === question.correct;
                    return (
                        <GlassCard key={index} className="p-6">
                            <div className="flex items-start gap-3 mb-3">
                                {isCorrect ? (
                                    <CheckCircle2 className="h-6 w-6 text-green-400 flex-shrink-0 mt-1" />
                                ) : (
                                    <XCircle className="h-6 w-6 text-red-400 flex-shrink-0 mt-1" />
                                )}
                                <div className="flex-1">
                                    <h3 className="font-semibold mb-2">
                                        Question {index + 1}: {question.question}
                                    </h3>
                                    <div className="space-y-2">
                                        <p className="text-sm">
                                            <span className="text-muted-foreground">Your answer: </span>
                                            <span className={isCorrect ? "text-green-400" : "text-red-400"}>
                                                {question.options[selectedAnswers[index]]}
                                            </span>
                                        </p>
                                        {!isCorrect && (
                                            <p className="text-sm">
                                                <span className="text-muted-foreground">Correct answer: </span>
                                                <span className="text-green-400">
                                                    {question.options[question.correct]}
                                                </span>
                                            </p>
                                        )}
                                        {question.explanation && (
                                            <p className="text-sm text-muted-foreground mt-2">
                                                {question.explanation}
                                            </p>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </GlassCard>
                    );
                })}
            </div>

            <Button
                onClick={handleRestart}
                className="w-full bg-primary hover:bg-primary/90"
            >
                <RotateCcw className="mr-2 h-4 w-4" />
                Take Another Quiz
            </Button>
        </div>
    );
}
