import { createClient } from "@supabase/supabase-js";

// These environment variables need to be set in .env.local
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

if (!supabaseUrl || !supabaseKey) {
  throw new Error("Supabase URL and anon key must be provided");
}

export const supabase = createClient(supabaseUrl, supabaseKey);
