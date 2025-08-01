// Test API URL - temporary debug file
console.log("API URL:", process.env.NEXT_PUBLIC_API_URL);
console.log("All env vars:", {
  API_URL: process.env.NEXT_PUBLIC_API_URL,
  SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL?.slice(0, 30) + "...",
});
