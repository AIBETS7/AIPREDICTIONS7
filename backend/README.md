# AI Football Predictions Backend

This backend system collects data from multiple football websites and uses AI to generate predictions for La Liga matches.

## Features

- **Multi-source data collection**: FlashScore, SofaScore, BetsAPI
- **AI-powered predictions**: Machine learning models for various betting types
- **Real-time data updates**: Automated data collection
- **RESTful API**: Easy integration with frontend
- **Comprehensive logging**: Detailed error tracking and monitoring

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file in the backend directory:

```env
BETSAPI_KEY=your_betsapi_key_here
FLASHSCORE_API_KEY=your_flashscore_key_here
SOFASCORE_API_KEY=your_sofascore_key_here
```

### 3. Run Data Collection

```bash
python run_collector.py
```

### 4. Start the API Server

```bash
python main.py
```

## API Endpoints

### Health Check
- `GET /api/health` - Check system status

### Data Collection
- `POST /api/collect-data` - Trigger data collection
- `GET /api/status` - Get system status and data source health

### Predictions
- `GET /api/predictions` - Get AI predictions for upcoming matches
- `POST /api/train-models` - Train AI models with historical data

### Data Access
- `GET /api/matches` - Get matches data
- `GET /api/teams` - Get teams data

## Data Sources

### FlashScore
- **URL**: https://www.flashscore.com
- **Data**: Matches, team stats, H2H records, odds
- **Method**: Web scraping

### SofaScore
- **URL**: https://www.sofascore.com
- **Data**: Matches, team stats, H2H records, odds
- **Method**: Web scraping

### BetsAPI
- **URL**: https://betsapi.com
- **Data**: Matches, odds, live data
- **Method**: Official API

## AI Models

The system uses ensemble machine learning models for different prediction types:

- **Match Winner**: Home win, Draw, Away win
- **Over/Under**: Over 2.5 goals, Under 2.5 goals
- **Both Teams Score**: Yes, No
- **Correct Score**: Various score combinations
- **First Goalscorer**: Player predictions
- **Half Time Result**: HT/FT combinations
- **Double Chance**: Multiple outcome combinations

## Configuration

Edit `config/settings.py` to customize:

- Data source priorities
- Update frequencies
- AI model parameters
- Rate limiting
- Logging settings

## Data Flow

1. **Data Collection**: Scrapers collect data from multiple sources
2. **Data Processing**: Raw data is cleaned and structured
3. **Feature Engineering**: AI features are extracted from data
4. **Model Prediction**: AI models generate predictions
5. **API Delivery**: Predictions are served via REST API

## Monitoring

- Check logs in `logs/football_predictions.log`
- Monitor data source success rates
- Track prediction accuracy
- Monitor API response times

## Legal Considerations

- Respect robots.txt files
- Implement rate limiting
- Check terms of service for each data source
- Consider using official APIs where available
- Implement proper error handling

## Troubleshooting

### Common Issues

1. **Rate Limiting**: Increase delays between requests
2. **Website Changes**: Update scraper selectors
3. **API Key Issues**: Verify API keys are valid
4. **Memory Issues**: Reduce data collection scope

### Debug Mode

Enable debug logging in `config/settings.py`:

```python
LOGGING_CONFIG = {
    'level': 'DEBUG',
    # ... other settings
}
```

## Performance Optimization

- Use connection pooling for HTTP requests
- Implement caching for frequently accessed data
- Optimize database queries
- Use async/await for I/O operations
- Implement data compression

## Security

- Validate all input data
- Sanitize API responses
- Use HTTPS for all external requests
- Implement proper authentication
- Monitor for suspicious activity
