// MongoDB Initialization Script
// Creates TimeSeries collections and indexes

db = db.getSiblingDB('market_analysis');

// Create TimeSeries collections
db.createCollection('stock_prices', {
    timeseries: {
        timeField: 'timestamp',
        metaField: 'metadata',
        granularity: 'minutes'
    }
});

db.createCollection('technical_indicators', {
    timeseries: {
        timeField: 'timestamp',
        metaField: 'metadata',
        granularity: 'hours'
    }
});

db.createCollection('sentiment_data', {
    timeseries: {
        timeField: 'timestamp',
        metaField: 'metadata',
        granularity: 'hours'
    }
});

db.createCollection('news_articles', {
    timeseries: {
        timeField: 'published_at',
        metaField: 'metadata',
        granularity: 'hours'
    }
});

db.createCollection('ml_predictions', {
    timeseries: {
        timeField: 'prediction_time',
        metaField: 'metadata',
        granularity: 'hours'
    }
});

db.createCollection('quant_signals', {
    timeseries: {
        timeField: 'timestamp',
        metaField: 'metadata',
        granularity: 'hours'
    }
});

// Create regular collections
db.createCollection('watchlists');
db.createCollection('analysis_results');
db.createCollection('user_portfolios');

// Create indexes
db.watchlists.createIndex({ userId: 1, symbol: 1, exchange: 1 }, { unique: true });
db.watchlists.createIndex({ userId: 1 });

db.analysis_results.createIndex({ symbol: 1, exchange: 1, timestamp: -1 });
db.analysis_results.createIndex({ userId: 1, timestamp: -1 });
db.analysis_results.createIndex({ analysisId: 1 }, { unique: true });

db.user_portfolios.createIndex({ userId: 1 }, { unique: true });

// Create metadata indexes for TimeSeries collections
db.stock_prices.createIndex({ 'metadata.symbol': 1, 'metadata.exchange': 1, timestamp: -1 });
db.technical_indicators.createIndex({ 'metadata.symbol': 1, timestamp: -1 });
db.sentiment_data.createIndex({ 'metadata.symbol': 1, timestamp: -1 });
db.news_articles.createIndex({ 'metadata.symbol': 1, published_at: -1 });
db.ml_predictions.createIndex({ 'metadata.symbol': 1, prediction_time: -1 });
db.quant_signals.createIndex({ 'metadata.symbol': 1, timestamp: -1 });

print('Market Analysis database initialized successfully');
print('Created 6 TimeSeries collections and 3 regular collections');
print('Created indexes for efficient querying');
