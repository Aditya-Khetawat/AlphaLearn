// User types
export interface User {
  id: string;
  name: string;
  email: string;
  avatarUrl?: string;
  balance: number;
}

// Stock types
export interface Stock {
  id: number;
  symbol: string;
  name: string;
  currentPrice: number;
  change: number;
  changePercent: number;
  previousClose?: number;
  open?: number;
  high?: number;
  low?: number;
  volume?: number;
}

// Portfolio types
export interface Position {
  symbol: string;
  shares: number;
  averageCost: number;
  currentPrice: number;
  currentValue: number;
  totalReturn: number;
  totalReturnPercent: number;
}

export interface Portfolio {
  positions: Position[];
  totalValue: number;
  totalCost?: number;
  investedValue?: number;
  totalReturn: number;
  totalReturnPercent: number;
  cash: number;
}

// Transaction types
export enum TransactionType {
  BUY = "BUY",
  SELL = "SELL",
}

export interface Transaction {
  id: string;
  symbol: string;
  shares: number;
  price: number;
  type: TransactionType;
  timestamp: string;
  total: number;
}

// Leaderboard types
export interface LeaderboardEntry {
  userId: string;
  userName: string;
  userAvatar?: string;
  portfolioValue: number;
  totalReturn: number;
  totalReturnPercent: number;
  rank: number;
}

// Learning content types
export interface LearningResource {
  id: string;
  title: string;
  description: string;
  category: string;
  difficulty: string;
  duration: string;
  imageUrl?: string;
  url: string;
}
