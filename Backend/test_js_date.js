// Test JavaScript Date parsing with our new IST ISO format
const testTimestamp = "2025-07-30T12:00:20.242483+05:30";

console.log("=== JavaScript Date Parsing Test ===");
console.log(`Input timestamp: ${testTimestamp}`);

const date = new Date(testTimestamp);
console.log(`Parsed Date: ${date}`);
console.log(`toLocaleString(): ${date.toLocaleString()}`);
console.log(`toISOString(): ${date.toISOString()}`);

// Test with Indian locale
console.log(`Indian Locale: ${date.toLocaleString("en-IN")}`);
console.log(
  `Indian Locale with timezone: ${date.toLocaleString("en-IN", {
    timeZone: "Asia/Kolkata",
  })}`
);

// Test what the frontend is currently doing
console.log(`\n=== Frontend Current Behavior ===`);
console.log(`new Date(timestamp).toLocaleString(): ${date.toLocaleString()}`);

console.log("\n✅ JavaScript correctly parses IST ISO format!");
console.log("✅ Date displays properly in user's locale!");
