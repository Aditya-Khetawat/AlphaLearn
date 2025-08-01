"use client";

import { useState } from "react";
import { GraduationCap, Clock, Star, BarChart3 } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { MainLayout } from "@/components/layout/main-layout";

// Learning content data
const learningContent = [
  {
    title: "Stock Market Basics",
    description:
      "Learn the fundamentals of how the stock market works, including key terms and concepts.",
    difficulty: "Beginner",
    duration: "15 min",
    rating: 4.8,
  },
  {
    title: "Understanding Financial Statements",
    description:
      "Dive into balance sheets, income statements, and cash flow statements to evaluate companies.",
    difficulty: "Intermediate",
    duration: "25 min",
    rating: 4.6,
  },
  {
    title: "Technical Analysis Fundamentals",
    description:
      "Master chart patterns, indicators, and technical analysis tools for better trading decisions.",
    difficulty: "Intermediate",
    duration: "30 min",
    rating: 4.7,
  },
  {
    title: "Risk Management Strategies",
    description:
      "Learn how to protect your investments and manage risk in your trading portfolio.",
    difficulty: "Beginner",
    duration: "20 min",
    rating: 4.9,
  },
  {
    title: "Options Trading Basics",
    description:
      "Introduction to options contracts, calls, puts, and basic options strategies.",
    difficulty: "Advanced",
    duration: "40 min",
    rating: 4.5,
  },
  {
    title: "Dividend Investing",
    description:
      "Understand dividend stocks, yield calculations, and building a dividend portfolio.",
    difficulty: "Beginner",
    duration: "18 min",
    rating: 4.7,
  },
  {
    title: "Market Psychology",
    description:
      "Explore behavioral finance and how emotions affect trading and investment decisions.",
    difficulty: "Intermediate",
    duration: "22 min",
    rating: 4.6,
  },
  {
    title: "Advanced Portfolio Theory",
    description:
      "Deep dive into modern portfolio theory, asset allocation, and diversification strategies.",
    difficulty: "Advanced",
    duration: "35 min",
    rating: 4.4,
  },
  {
    title: "Cryptocurrency Fundamentals",
    description:
      "Learn about digital currencies, blockchain technology, and crypto trading basics.",
    difficulty: "Beginner",
    duration: "28 min",
    rating: 4.3,
  },
];

function getDifficultyBadge(difficulty: string) {
  switch (difficulty) {
    case "Beginner":
      return (
        <Badge className="bg-green-600 hover:bg-green-700">Beginner</Badge>
      );
    case "Intermediate":
      return (
        <Badge className="bg-yellow-600 hover:bg-yellow-700">
          Intermediate
        </Badge>
      );
    case "Advanced":
      return <Badge className="bg-red-600 hover:bg-red-700">Advanced</Badge>;
    default:
      return <Badge variant="outline">Unknown</Badge>;
  }
}

export default function LearnPage() {
  return (
    <MainLayout>
      {/* Page Header */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold mb-2 flex items-center gap-3">
          <GraduationCap className="h-8 w-8 text-blue-500" />
          Learn About Trading
        </h2>
        <p className="text-muted-foreground">
          Master the fundamentals of trading and investing with our
          comprehensive learning resources.
        </p>
      </div>

      {/* Learning Content Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {learningContent.map((content, index) => (
          <Card
            key={index}
            className="hover:bg-accent/50 transition-colors cursor-pointer group"
          >
            <CardHeader>
              <div className="flex items-start justify-between mb-2">
                <CardTitle className="text-lg group-hover:text-blue-400 transition-colors">
                  {content.title}
                </CardTitle>
                <div className="flex items-center gap-1 text-yellow-500">
                  <Star className="h-4 w-4 fill-current" />
                  <span className="text-sm text-muted-foreground">
                    {content.rating}
                  </span>
                </div>
              </div>
              <CardDescription className="text-sm leading-relaxed">
                {content.description}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  {getDifficultyBadge(content.difficulty)}
                  <div className="flex items-center gap-1 text-muted-foreground">
                    <Clock className="h-4 w-4" />
                    <span className="text-sm">{content.duration}</span>
                  </div>
                </div>
              </div>
              <Button
                className="w-full mt-4 bg-blue-600 hover:bg-blue-700 text-white"
                onClick={() => console.log(`Starting: ${content.title}`)}
              >
                Start Learning
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Progress Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Your Learning Progress
          </CardTitle>
          <CardDescription>
            Track your progress across different learning modules
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold mb-1">-</div>
              <p className="text-sm text-muted-foreground">Courses Completed</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold mb-1">-</div>
              <p className="text-sm text-muted-foreground">Minutes Learned</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold mb-1">
                {learningContent.length}
              </div>
              <p className="text-sm text-muted-foreground">
                Total Courses Available
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </MainLayout>
  );
}
