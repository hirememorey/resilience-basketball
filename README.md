# NBA Playoff Resilience Analytics

A comprehensive data science project analyzing NBA player performance under playoff pressure. This project builds a predictive model to identify factors that make players "playoff resilient" - maintaining or exceeding regular-season production in postseason games.

## 🎯 Project Vision

**Core Question:** What measurable factors in a player's regular-season performance predict their ability to maintain production in the postseason?

**Ultimate Goal:** Create a "Playoff Resilience Score" that helps basketball decision-makers make championship-focused investments by better predicting how regular-season production translates to playoff success.

## 📊 Current Status: Possession-Level Analytics Ready ✅

**Phase 1 & 2 Complete:** Full NBA data collection infrastructure operational
- ✅ Database schema with 11 tables (including possession-level tracking)
- ✅ NBA Stats API integration with rate limiting and caching (play-by-play support added)
- ✅ 569 players with complete 2024-25 season statistics
- ✅ 1,168 metrics covering traditional and advanced analytics
- ✅ Data validation and quality assurance systems

**Phase 3 Infrastructure Complete:** Possession-level resilience analytics framework
- ✅ Possession parsing engine for granular player behavior analysis
- ✅ Possession-level database schema (4 new tables: possessions, possession_events, possession_lineups, possession_matchups)
- ✅ Play-by-play data fetcher with intelligent caching
- ✅ Possession data validation and quality assurance
- ✅ Ready for resilience feature engineering and predictive modeling

## 🏗️ Architecture

### Data Pipeline
```
NBA Stats API → Data Fetcher → SQLite Database → Analysis Models
```

### Core Components
- **API Layer**: NBA Stats API client with intelligent caching and rate limiting
- **Data Layer**: SQLite database with normalized schema for player analytics
- **Validation Layer**: Comprehensive data quality checks and statistical validation
- **Analytics Ready**: Structured data for machine learning and statistical analysis

### Database Schema
- `teams`: Team information and metadata
- `games`: Game records with scores and seasons
- `players`: Player profiles and physical attributes
- `player_season_stats`: Traditional box score statistics (PTS, REB, AST, etc.)
- `player_advanced_stats`: Advanced metrics (TS%, USG%, ORTG/DRTG, etc.)
- `player_tracking_stats`: Play-type and tracking data (drives, touches, etc.)
- `possessions`: Possession metadata (duration, teams, points scored)
- `possession_events`: Individual player actions within possessions
- `possession_lineups`: Players on court during each possession
- `possession_matchups`: Defensive matchups between players

## 📈 Data Coverage

### Current Season: 2024-25
- **569 Active NBA Players** with complete statistical profiles
- **22 Statistical Categories** including:
  - Traditional: Points, Rebounds, Assists, Steals, Blocks
  - Advanced: True Shooting %, Usage %, Offensive/Defensive Rating
  - Tracking: Drives, Touches, Catch-and-Shoot efficiency

### Sample Statistics
- Average Points per Game: 8.9
- Average Field Goal %: 44.6%
- Max Points in a Game: 32.7
- Data Quality Score: 100% ✅

## 🚀 Quick Start

### Prerequisites
```bash
pip install pandas requests tqdm tenacity pydantic
```

### Initialize Database
```bash
python src/nba_data/db/schema.py
```

### Populate Data (2024-25 Season)
```bash
python src/nba_data/scripts/populate_player_data.py
```

### Validate Data Quality
```bash
python validate_data.py
python validate_possessions.py  # Possession-level data validation
```

### Run Tests
```bash
python test_api.py
python test_possessions.py  # Possession analytics tests
```

## 📁 Project Structure

```
resilience-basketball/
├── src/
│   └── nba_data/
│       ├── api/              # NBA Stats API clients
│       │   ├── nba_stats_client.py
│       │   ├── data_fetcher.py
│       │   ├── possession_fetcher.py  # NEW: Play-by-play data fetching
│       │   └── __init__.py
│       ├── db/               # Database schema and models
│       │   └── schema.py     # ENHANCED: 11 tables including possession tracking
│       └── scripts/          # Data population scripts
│           ├── populate_player_data.py
│           └── populate_possession_data.py  # NEW: Possession data population
├── data/                     # SQLite databases and cache
├── logs/                     # Application logs
├── foundational_principles.md # Project vision and methodology
├── prompts.md               # Development command templates
├── validate_data.py         # Data quality validation
├── validate_possessions.py  # NEW: Possession data validation
├── test_api.py             # API connectivity tests
├── test_possessions.py     # NEW: Possession analytics tests
└── README.md
```

## 🔬 Research Framework

### Core Hypotheses
1. **Skill Diversification**: Players with varied offensive skills are harder to defend in playoffs
2. **Over-Specialization Fragility**: One-dimensional players are more vulnerable to playoff schemes
3. **Adaptability Measurement**: Year-over-year changes indicate playoff readiness

### Guiding Principles
- **Dynamic over Static**: Focus on career trajectories vs. single-season snapshots
- **Leading Indicators**: Predict playoff success from regular-season patterns
- **Beyond Box Scores**: Include advanced metrics and play-type distributions
- **Context Matters**: Account for age, team changes, and opponent quality

### Success Criteria
- **Predictive Accuracy**: Model correctly identifies playoff performance patterns
- **Actionable Insights**: Clear recommendations for team decision-makers
- **Research Publication**: Suitable for MIT Sloan Sports Analytics Conference

## 🛠️ Development

### Adding New Metrics
1. Update `src/nba_data/api/data_fetcher.py` with new metric mappings
2. Add corresponding database columns to `schema.py`
3. Update population scripts to handle new data

### Adding Possession-Level Features
1. Update `src/nba_data/api/possession_fetcher.py` for new event types or parsing logic
2. Add columns to possession tables in `schema.py`
3. Update `populate_possession_data.py` to handle new data structures

### Multi-Season Expansion
1. Modify API calls to accept season parameters
2. Update database schema for season-specific tables
3. Implement longitudinal analysis features

### Quality Assurance
- All data passes statistical validation
- API rate limiting prevents service disruption
- Comprehensive error handling and logging
- Possession data integrity validation

## 📚 Key Insights Developed

### Data Pipeline Architecture
- **Evidence-Driven Development**: Direct API inspection over assumptions
- **Validation-First Approach**: Test data quality before scaling
- **Modular Design**: Components can be independently updated
- **Possession-Level Granularity**: Transformative for resilience analysis

### NBA Analytics Challenges
- **API Reliability**: Rate limiting and caching critical for production use
- **Data Consistency**: Multiple API endpoints require unified data models
- **Statistical Validity**: Comprehensive validation prevents analysis errors
- **Possession Parsing**: Complex event sequencing requires sophisticated logic

### Performance Optimizations
- **Intelligent Caching**: 1-day cache expiration balances freshness vs. performance
- **Batch Processing**: Efficient handling of 500+ player datasets
- **Memory Management**: Streaming data processing for large datasets
- **Hierarchical Validation**: Multi-level quality checks for possession data

## 🔄 Next Steps (Phase 3)

### Possession Data Population
- ✅ **Infrastructure Complete**: Possession-level tracking ready for data population
- 🔄 **Next**: Populate possession data for games in database
- 🔄 **Future**: Implement possession data for playoff seasons

### Resilience Feature Engineering
- ✅ **Foundation**: Possession-level player behavior tracking implemented
- 🔄 **Next**: Build resilience metrics (decision quality, adaptation speed, matchup performance)
- 🔄 **Future**: Machine learning models for resilience prediction

### Advanced Analytics
- Longitudinal player career analysis using possession trajectories
- Team fit optimization using possession-level chemistry metrics
- Predictive modeling of playoff performance patterns

### Research Publication
- Statistical analysis of possession-level resilience factors
- Case studies of resilient vs. fragile players using granular data
- Predictive model validation for MIT Sloan submission

## 🤝 Contributing

### For New Developers
1. Read `foundational_principles.md` for project vision
2. Review `README.md` for technical architecture
3. Run validation suite: `python validate_data.py`
4. Check `prompts.md` for development workflow templates

### Development Workflow
- Use provided prompt templates for consistent development
- Always run validation after changes
- Document insights in relevant markdown files
- Test API connectivity before major changes

## 📄 Documentation

- **[Foundational Principles](foundational_principles.md)**: Research vision and methodology
- **[Development Prompts](prompts.md)**: Standardized development workflows
- **[API Documentation](src/nba_data/api/)**: Inline code documentation (including possession_fetcher.py)
- **[Data Validation](validate_data.py)**: Player data quality assurance
- **[Possession Validation](validate_possessions.py)**: Possession-level data validation
- **[Possession Tests](test_possessions.py)**: Possession analytics testing

## ⚖️ License

This project is developed for research and educational purposes. Data sourced from NBA Stats API with appropriate usage patterns.

## 🙏 Acknowledgments

Built upon the foundation of the NBA Lineup Optimizer research project, adapted for focused playoff resilience analysis.
