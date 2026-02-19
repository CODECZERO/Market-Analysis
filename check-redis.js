// Simple script to check Redis keys
const Redis = require("ioredis");

const redis = new Redis(process.env.REDIS_URL || "rediss://default:AeAJAAIncDExYmEzMmNhZjYxMTI0OThlYTFhMWUzNjM4N2QwYjk4NnAxNTczNTM@knowing-dassie-57353.upstash.io:6379");

async function checkRedis() {
    try {
        console.log("Connecting to Redis...");

        // Check summary keys
        const summaryKeys = await redis.keys("summary:brand:*");
        console.log("\n=== summary:brand:* keys ===");
        console.log(summaryKeys.length > 0 ? summaryKeys : "(none)");

        // Check state keys
        const stateKeys = await redis.keys("state:brand:*");
        console.log("\n=== state:brand:* keys ===");
        console.log(stateKeys.length > 0 ? stateKeys : "(none)");

        // Check data keys (timeline, optimized_mentions)
        const dataKeys = await redis.keys("data:brand:*");
        console.log("\n=== data:brand:* keys ===");
        console.log(dataKeys.length > 0 ? dataKeys.slice(0, 20) : "(none)");
        if (dataKeys.length > 20) console.log(`... and ${dataKeys.length - 20} more`);

        // Check leads keys
        const leadsKeys = await redis.keys("leads:brand:*");
        console.log("\n=== leads:brand:* keys ===");
        console.log(leadsKeys.length > 0 ? leadsKeys : "(none)");

        // If we have a summary key, check its content
        if (summaryKeys.length > 0) {
            const sampleSummary = await redis.get(summaryKeys[0]);
            console.log("\n=== Sample summary content ===");
            if (sampleSummary) {
                const parsed = JSON.parse(sampleSummary);
                console.log("Key:", summaryKeys[0]);
                console.log("totalMentions:", parsed.totalMentions);
                console.log("sentiment:", parsed.sentiment);
                console.log("\n=== ADVANCED INTELLIGENCE DATA ===");
                console.log("entities:", JSON.stringify(parsed.entities, null, 2));
                console.log("feature_requests:", parsed.feature_requests);
                console.log("pain_points:", parsed.pain_points);
                console.log("churn_risks:", parsed.churn_risks);
                console.log("recommended_actions:", parsed.recommended_actions);
                console.log("avgLeadScore:", parsed.avgLeadScore);
            } else {
                console.log("(empty)");
            }
        }

        // Check timeline ZSET
        const timelineKeys = dataKeys.filter(k => k.includes(":timeline"));
        if (timelineKeys.length > 0) {
            const count = await redis.zcard(timelineKeys[0]);
            console.log(`\n=== Timeline ${timelineKeys[0]} ===`);
            console.log(`Contains ${count} items`);
        }

    } catch (error) {
        console.error("Error:", error.message);
    } finally {
        await redis.quit();
    }
}

checkRedis();
