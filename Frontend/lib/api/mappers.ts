import { User, Position, Stock, TransactionType } from "@/types";

// Types that match our backend API models

export interface ApiUser {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
}

export interface ApiStock {
  id: number;
  symbol: string;
  name: string;
  current_price: number;
  previous_close?: number;
  exchange: string;
  sector?: string;
  is_active: boolean;
  last_updated: string;
  price_change?: number;
  price_change_percent?: number;
}

export interface ApiPosition {
  id: number;
  stock: ApiStock;
  shares: number;
  average_price: number;
  current_value: number;
  total_return: number;
  total_return_percent: number;
}

export interface ApiPortfolio {
  id: number;
  user_id: number;
  cash_balance: number;
  positions: ApiPosition[];
  total_value: number;
  invested_value: number;
  total_return: number;
  total_return_percent: number;
  created_at: string;
  updated_at: string;
}

export interface ApiTransaction {
  id: number;
  stock: ApiStock;
  transaction_type: string;
  shares: number;
  price: number;
  total_amount: number;
  timestamp: string;
  status: string;
  notes?: string;
}

// Functions to convert API types to our frontend types

export function apiUserToUser(apiUser: ApiUser): User {
  return {
    id: apiUser.id.toString(),
    name: apiUser.full_name || apiUser.username,
    email: apiUser.email,
    avatarUrl: "/placeholder-user.jpg", // Default avatar until we have real ones
    balance: 0, // This will come from portfolio
  };
}

export function apiPositionToStockPosition(apiPosition: ApiPosition): Position {
  return {
    symbol: apiPosition.stock.symbol,
    shares: apiPosition.shares,
    averageCost: apiPosition.average_price,
    currentPrice: apiPosition.stock.current_price,
    currentValue: apiPosition.current_value,
    totalReturn: apiPosition.total_return,
    totalReturnPercent: apiPosition.total_return_percent,
  };
}

export function apiStockToStock(apiStock: ApiStock): Stock {
  return {
    id: apiStock.id,
    symbol: apiStock.symbol,
    name: apiStock.name,
    currentPrice: apiStock.current_price,
    change: apiStock.price_change || 0,
    changePercent: apiStock.price_change_percent || 0,
  };
}

export function apiTransactionToTransaction(apiTransaction: ApiTransaction) {
  return {
    id: apiTransaction.id.toString(),
    symbol: apiTransaction.stock.symbol,
    shares: apiTransaction.shares,
    price: apiTransaction.price,
    type:
      apiTransaction.transaction_type === "BUY"
        ? TransactionType.BUY
        : TransactionType.SELL,
    timestamp: apiTransaction.timestamp,
    total: apiTransaction.total_amount,
  };
}

export function apiPortfolioToPortfolio(apiPortfolio: ApiPortfolio) {
  return {
    positions: apiPortfolio.positions.map(apiPositionToStockPosition),
    totalValue: apiPortfolio.total_value,
    investedValue: apiPortfolio.invested_value,
    totalReturn: apiPortfolio.total_return,
    totalReturnPercent: apiPortfolio.total_return_percent,
    cash: apiPortfolio.cash_balance,
  };
}
