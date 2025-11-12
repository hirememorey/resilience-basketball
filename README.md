# NBA Playoff Resilience Analytics

A comprehensive data science project analyzing NBA player performance under playoff pressure. This project builds a predictive model to identify factors that make players "playoff resilient" - maintaining or exceeding regular-season production in postseason games.

## 🎯 Project Vision

**Core Question:** What measurable factors in a player's regular-season performance predict their ability to maintain production in the postseason?

**Ultimate Goal:** Create a "Playoff Resilience Score" that helps basketball decision-makers make championship-focused investments by better predicting how regular-season production translates to playoff success.

## 📊 Current Status: Data Pipeline Infrastructure Complete, Analysis Framework Blocked ❌

**Phase 1 & 2 Complete:** Full NBA data collection infrastructure operational
- ✅ Database schema with 11 tables
- ✅ NBA Stats API integration with rate limiting and caching
- ✅ 569 players with complete 2024-25 season statistics
- ✅ 1,168+ metrics covering traditional and advanced analytics
- ✅ Data validation and quality assurance systems

**Phase 3 Blocked:** Statistical resilience analytics framework cannot be implemented
- ❌ **Critical Issue:** NBA play-by-play APIs return empty data (`{}` responses)
- ❌ **Possession-level analysis impossible** with current API access
- ❌ **Statistical resilience metrics built prematurely** without data validation
- ❌ **405 players have calculated metrics** but framework is invalid without possession data

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
- `player_season_stats`: Traditional box score statistics + resilience metrics (PTS, REB, AST, diversification scores, etc.)
- `player_advanced_stats`: Advanced metrics (TS%, USG%, ORTG/DRTG, etc.)
- `player_tracking_stats`: Play-type and tracking data (drives, touches, etc.)
- `possessions`: Possession metadata (duration, teams, points scored) - schema ready for future play-by-play data
- `possession_events`: Individual player actions within possessions - schema ready for future implementation
- `possession_lineups`: Players on court during each possession - schema ready for future implementation
- `possession_matchups`: Defensive matchups between players - schema ready for future implementation

## 📈 Data Coverage

### Current Season: 2024-25
- **569 Active NBA Players** with complete statistical profiles
- **405+ Players** with calculated resilience scores and diversification metrics
- **29 Statistical Categories** including:
  - Traditional: Points, Rebounds, Assists, Steals, Blocks
  - Advanced: True Shooting %, Usage %, Offensive/Defensive Rating
  - Tracking: Drives, Touches, Catch-and-Shoot efficiency
  - **Resilience**: Production diversification, shot selection balance, efficiency stability, composite scores

### Sample Statistics
- Average Points per Game: 8.9
- Average Field Goal %: 44.6%
- Max Points in a Game: 32.7
- Players with Premature Metrics: 405 (invalid without possession data)
- Data Quality Score: 100% ✅ (infrastructure only)

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
│       │   ├── possession_fetcher.py  # Play-by-play framework (API unavailable)
│       │   └── __init__.py
│       ├── db/               # Database schema and models
│       │   └── schema.py     # ENHANCED: 11 tables + resilience metrics
│       └── scripts/          # Data population scripts
│           ├── populate_player_data.py
│           ├── populate_player_metadata.py  # NEW: Player names/info population
│           ├── populate_possession_data.py  # Possession framework (API unavailable)
│           └── calculate_resilience_scores.py  # NEW: Resilience metrics calculation
├── data/                     # SQLite databases and cache
├── logs/                     # Application logs
├── foundational_principles.md # Project vision and methodology
├── prompts.md               # Development command templates
├── validate_data.py         # Data quality validation
├── validate_possessions.py  # Possession validation framework
├── test_api.py             # API connectivity tests
├── test_possessions.py     # Possession analytics framework
└── README.md
```

## 🔬 Research Framework

### Core Hypotheses (Cannot Test Yet)
1. **Skill Diversification**: Players with varied offensive skills are harder to defend in playoffs
2. **Over-Specialization Fragility**: One-dimensional players are more vulnerable to playoff schemes
3. **Adaptability Measurement**: Year-over-year changes indicate playoff readiness

**Blocked by empty play-by-play API responses**

### Guiding Principles (Still Valid)
- **Dynamic over Static**: Focus on career trajectories vs. single-season snapshots
- **Leading Indicators**: Predict playoff success from regular-season patterns
- **Beyond Box Scores**: Include advanced metrics and play-type distributions
- **Context Matters**: Account for age, team changes, and opponent quality
- **Validate Data First**: Never build analytics on untested data sources

### Success Criteria
- **Predictive Accuracy**: Model correctly identifies playoff performance patterns
- **Actionable Insights**: Clear recommendations for team decision-makers
- **Research Publication**: Suitable for MIT Sloan Sports Analytics Conference

## 🛠️ Development

### Adding New Resilience Metrics
1. Update `src/nba_data/scripts/calculate_resilience_scores.py` with new metric calculations
2. Add corresponding database columns to `schema.py`
3. Update validation logic in resilience calculation scripts

### Building Predictive Models
1. Use resilience scores from database for feature engineering
2. Implement ML models in new analysis scripts
3. Add model validation and performance tracking

### Multi-Season Analysis
1. Modify calculation scripts to handle historical seasons
2. Update database schema for longitudinal tracking
3. Implement year-over-year resilience trend analysis

### Quality Assurance
- All data passes statistical validation
- API rate limiting prevents service disruption
- Comprehensive error handling and logging
- Resilience metrics validated against performance indicators

## 📚 Key Insights Developed

### Data Pipeline Architecture
- **Evidence-Driven Development**: Direct API inspection over assumptions
- **Validation-First Approach**: Test data quality before scaling
- **Modular Design**: Components can be independently updated

### NBA Analytics Challenges (Critical Lesson)
- **API Reliability Myth**: Even "working" APIs can return empty data - validate content, not just HTTP status
- **Data Availability Reality**: NBA Stats API play-by-play endpoints return empty responses
- **Premature Implementation Risk**: Building analytics frameworks on unvalidated data sources wastes significant effort
- **Statistical Proxies Are Dangerous**: Box score approximations cannot replace possession-level data for resilience analysis

### Performance Optimizations
- **Intelligent Caching**: 1-day cache expiration balances freshness vs. performance
- **Batch Processing**: Efficient handling of 500+ player datasets
- **Memory Management**: Streaming data processing for large datasets
- **Resilience Metrics**: Lightweight calculation enables real-time analysis

### Research Methodology (Lessons Learned)
- **Hypothesis-Driven Development**: Start with research questions, adapt data strategy accordingly
- **Data Validation Critical**: Never build frameworks on untested data sources
- **Premature Implementation Risk**: Statistical approximations without data validation waste effort
- **Framework Viability**: Core hypotheses require possession data, not box score proxies

## 🔄 Next Steps (Phase 3: Data Source Resolution Required)

### Critical Path Forward
- ❌ **Framework Blocked**: Cannot proceed with resilience analysis without possession data
- 🔄 **Immediate Priority**: Find alternative sources for play-by-play or possession data
- 🔄 **Validate APIs**: Test all NBA Stats API endpoints for actual data availability
- 🔄 **Explore Alternatives**: Investigate third-party data providers or scraping approaches

### Once Data Sources Resolved
### Statistical Resilience Analysis
- 🔄 **Restart Framework**: Rebuild resilience metrics with proper possession data
- 🔄 **Validate Hypotheses**: Test core hypotheses with actual possession-level data
- 🔄 **Correlation Analysis**: Analyze diversification vs. playoff performance

### Machine Learning Pipeline
- 🔄 **Foundation**: Wait for valid possession data before feature engineering
- 🔄 **Models**: Build predictive models only after data validation
- 🔄 **Validation**: Ensure models are based on real data, not empty responses

### Research Publication
- ❌ **Data Invalid**: Current metrics are built on unvalidated assumptions
- 🔄 **Reset Timeline**: Publication goals depend on finding viable data sources
- 🔄 **Reassess Scope**: May need to pivot research questions based on available data

### Future Enhancements
- **Playoff Data Integration**: Source postseason performance data for validation
- **Real-Time Resilience**: Adapt framework for in-season player evaluation
- **Advanced Possession Analysis**: Revisit play-by-play data with improved API access

## 🤝 Contributing

### For New Developers
1. Read `foundational_principles.md` for research vision and statistical resilience methodology
2. Review `README.md` for current implementation status
3. Run validation suite: `python validate_data.py`
4. Check `prompts.md` for development workflow templates
5. Examine `src/nba_data/scripts/calculate_resilience_scores.py` for resilience calculation logic

### Development Workflow
- Use provided prompt templates for consistent development
- Always run validation after changes
- Statistical resilience framework prioritizes analytical utility over data completeness
- Document insights in relevant markdown files
- Test API connectivity before major changes
- Focus on hypothesis testing rather than exhaustive data collection

## 📄 Documentation

- **[Foundational Principles](foundational_principles.md)**: Research vision and statistical resilience methodology
- **[Development Prompts](prompts.md)**: Standardized development workflows
- **[API Documentation](src/nba_data/api/)**: Inline code documentation and resilience framework
- **[Data Validation](validate_data.py)**: Player data quality assurance
- **[Resilience Analysis](src/nba_data/scripts/calculate_resilience_scores.py)**: Statistical resilience calculation methodology
- **[Database Schema](src/nba_data/db/schema.py)**: Data structure and resilience metrics documentation

## ⚖️ License

This project is developed for research and educational purposes. Data sourced from NBA Stats API with appropriate usage patterns.

## 🙏 Acknowledgments

Built upon the foundation of the NBA Lineup Optimizer research project, adapted for focused playoff resilience analysis.
