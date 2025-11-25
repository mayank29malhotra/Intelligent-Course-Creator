---
title: Intelligent-Course-Creator
app_file: app.py
sdk: python
sdk_version: 6.0.0
---
# Intelligent Course Creator

A professional, production-ready multi-agent orchestration system for automatically generating comprehensive, high-quality educational courses using **Google Gemini** with a **Gradio web interface**.

## 🎯 Overview

The Intelligent Course Creator uses **5 specialized agents** with feedback loops and quality assurance to create complete course structures including:
- ✅ Curriculum design with modules and lessons
- ✅ Detailed instruction materials
- ✅ Practice exercises and assessments
- ✅ Quality validation with automatic refinement
- ✅ Interactive web interface for easy course creation
- ✅ Powered by Google Gemini 2.0 Flash lite model

## 🏗️ Architecture

```
Input (Course Topic)
    ↓
[Curriculum Designer Agent] → Designs modules, lessons, learning objectives
    ↓
[Instruction Designer Agent] → Creates detailed instruction materials
    ↓
[Practice Designer Agent] → Generates practice exercises & assessments
    ↓
[QA Agent] → Evaluates quality (completeness, accuracy, alignment)
    ↓
[Decision Loop] → If quality < threshold, restart from failed component
    ↓
[Coordinator Agent] → Compiles final course plan
    ↓
Output (Complete Course Structure)
```

## 🌐 User Interface

- **Gradio Web Interface**: Modern, responsive web UI for course creation
- **Real-time Progress Tracking**: Monitor course generation in real-time
- **Interactive Controls**: Adjust duration, quality threshold via sliders
- **JSON Output Display**: View and copy complete course structure
- **Mobile Friendly**: Works on desktop and mobile devices

## 📁 Project Structure

```
intelligent_course_creator/
├── agents/                          # Specialized agents
│   ├── curriculum_designer_agent.py # Designs course structure
│   ├── instruction_designer_agent.py # Creates teaching materials
│   ├── practice_designer_agent.py    # Generates exercises
│   ├── qa_agent.py                  # Quality assurance
│   └── __init__.py
├── models/                          # Pydantic data models
│   ├── course_models.py             # All course structure models
│   └── __init__.py
├── tools/                           # Function tools for agents
│   ├── course_tools.py              # Tool implementations
│   └── __init__.py
├── config/                          # Configuration modules
│   ├── gemini_config.py             # Gemini API setup & GeminiAgent
│   └── __init__.py
├── coordinator_agent.py             # Main orchestrator
├── gradio_interface.py              # Web interface (NEW)
├── runner.py                        # Execution entry point (updated)
├── requirements.txt                 # Dependencies (updated)
├── .env.example                     # Environment template (updated)
└── README.md                        # This file
```

## 🚀 Quick Start

### 1. Setup

```bash
# Clone or navigate to project
cd intelligent_course_creator

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY from https://ai.google.dev/
```

### 2. Run the Course Creator

#### Option A: Web Interface (Recommended)
```bash
python runner.py --web
# Open browser to http://localhost:7860
```

#### Option B: Command Line
```bash
python runner.py --topic "Python Programming for Beginners" --audience "High school students" --hours 40
```

### 3. Output

The system generates a `CourseCompletion` object containing:
- **Curriculum**: Complete structure with modules and lessons
- **Instructions**: Detailed teaching materials for all lessons
- **Practice**: Exercises and assessments for all lessons
- **Quality Report**: QA findings and recommendations

## 🔑 Key Features

### Google Gemini Integration
- **Model**: Gemini 2.0 Flash lite (free tier available)
- **Custom Wrapper**: `GeminiAgent` class for consistent interface
- **JSON Responses**: Structured output parsing with Pydantic
- **Cost-Effective**: Free tier supports course generation

### Agent-to-Agent Handoffs
Each agent receives output from the previous agent, ensuring coherence and quality:
```
Curriculum → Instruction → Practice → QA
```

### Conditional Refinement Loops
If QA quality score < threshold:
1. Identifies specific issues
2. Routes feedback to responsible agent
3. Reruns that component with improvements
4. Repeats until quality threshold met (≥75%)

### Structured Outputs
All agents return **Pydantic models** with full type validation:
- `Curriculum`: Course structure
- `Instruction`: Teaching materials
- `Practice`: Exercises and assessments
- `QualityAssurance`: Validation report

### Parallel Execution
When applicable, operations run in parallel:
- All lesson instructions created simultaneously
- All practice sets created simultaneously
- Results collected and validated

## 📊 Agents & Responsibilities

### Curriculum Designer Agent
- Analyzes course topics
- Defines learning outcomes
- Creates module and lesson structure
- Plans assessment strategy
- **Output**: `Curriculum` with SMART objectives
- **Powered by**: Gemini 2.0 Flash lite

### Instruction Designer Agent
- Creates detailed lesson content
- Provides teaching tips
- Designs engagement strategies
- Addresses misconceptions
- **Output**: `Instruction` with comprehensive materials
- **Powered by**: Gemini 2.0 Flash lite

### Practice Designer Agent
- Creates varied exercise types
- Designs assessments and quizzes
- Provides feedback rubrics
- Plans remediation options
- **Output**: `Practice` with diverse activities
- **Powered by**: Gemini 2.0 Flash lite

### QA Agent
- Validates curriculum alignment
- Checks completeness
- Verifies accuracy and clarity
- Identifies gaps and issues
- Provides improvement recommendations
- **Output**: `QualityAssurance` with score and recommendations
- **Powered by**: Gemini 2.0 Flash lite

### Coordinator Agent
- Orchestrates the entire pipeline
- Manages feedback loops
- Handles iteration and refinement
- Compiles final course
- **Output**: `CourseCompletion` with all materials

## 🛠️ Usage Examples

### Web Interface (Easiest)

```bash
python runner.py --web
# Fill in the form:
# - Course Topic: "Machine Learning Fundamentals"
# - Target Audience: "Software engineers"
# - Duration: 60 hours
# - Quality Threshold: 75%
# Click "Create Course"
```

### Python API

```python
from coordinator_agent import CourseCreationCoordinator

coordinator = CourseCreationCoordinator(
    quality_threshold=75.0,
    max_iterations=3
)

course = await coordinator.create_course(
    course_topic="Machine Learning Fundamentals",
    target_audience="Software engineers",
    duration_hours=60,
    verbose=True
)

print(f"Course created with {len(course.curriculum.modules)} modules")
print(f"Quality score: {course.quality_report.overall_quality_score}%")
```

### Command Line

```bash
# Basic
python runner.py --topic "Data Science" --audience "Analysts" --hours 40

# Advanced
python runner.py \
    --topic "Advanced Python Patterns" \
    --audience "Professional developers" \
    --hours 60 \
    --quality 85.0 \
    --max-iterations 5
```

## 🧪 Testing

Run tests to validate agent outputs:

```bash
# Run all tests
pytest tests/

# Test specific component
pytest tests/test_curriculum_designer.py

# With coverage
pytest tests/ --cov=intelligent_course_creator
```

## 📈 Observability

### Logging
Monitor execution with detailed logs showing:
- Curriculum design progress
- Instruction creation progress
- Practice material generation progress
- QA iteration status

### Performance Metrics
- Total execution time
- Per-agent latency
- QA pass rate
- Average iterations to quality threshold

### Debug Mode
Set verbose=True in coordinator to see detailed progress

## 🔐 Security & Best Practices

### API Key Management
- Never commit `.env` with real API keys
- Use environment variables for credentials
- Get free Gemini API key: https://ai.google.dev/
- Rotate API keys regularly

### PII Handling
- Avoid storing personal information in course examples
- Sanitize user-provided sample content
- Review outputs for sensitive data

### Content Quality
- All outputs validated against Pydantic schemas
- Quality thresholds enforced
- Manual review recommended for production courses

## 📝 Customization

### Modify Agent Instructions
Edit instructions in each agent file:
```python
# agents/curriculum_designer_agent.py
INSTRUCTIONS = "Your custom instructions here..."
```

### Adjust Quality Thresholds
```python
# In runner.py CLI mode
python runner.py ... --quality 85.0
```

### Modify Gemini Model Settings
Edit `config/gemini_config.py`:
```python
GEMINI_MODEL = "gemini-2.0-flash-lite"  # Change model version
```

### Customize Web Interface
Edit `gradio_interface.py` to modify:
- UI layout and components
- Progress tracking display
- Output formatting

## 🚦 Troubleshooting

### Invalid API Key
- Get free key from https://ai.google.dev/
- Ensure `.env` has `GEMINI_API_KEY=...`
- Verify key is in `intelligent_course_creator/` directory

### Gradio Port Already in Use
- Edit `.env`: `GRADIO_SERVER_PORT=8080`
- Or kill existing process on port 7860

### QA Loop Not Converging
- Lower `--quality` threshold (default 75%)
- Increase `--max-iterations` (default 3)
- Review QA recommendations in output

### Token Limits
- Reduce `--hours` to simplify course
- Limit number of modules in curriculum
- Summarize instruction content

### Gemini API Rate Limits
- Free tier has usage limits
- Reduce concurrent requests
- Add delays between API calls

## 🌐 Deployment

### Local Development
```bash
python runner.py --web
```

### Production Deployment
```bash
# Configure in .env
GRADIO_SHARE=True              # Share public link
GRADIO_SERVER_NAME=0.0.0.0     # Expose on all interfaces
GRADIO_SERVER_PORT=8000        # Custom port
```

### Docker Deployment (Optional)
Create Dockerfile based on project structure and deploy to cloud

## 📚 Related Projects

- **Agent Manager Refactor**: Research pipeline with similar patterns
- **Code Learning Assistant**: Specialist agents for code education
- **Customer Care Telegram**: Multi-agent orchestration with state management

## 🤝 Contributing

To improve this system:
1. Test changes with sample courses
2. Validate Pydantic model outputs
3. Run full test suite before committing
4. Document any new agent capabilities

## 📄 License

This project is part of the OpenAI SDK Agents portfolio, now powered by Google Gemini.

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review agent instructions for clarity
3. Examine QA reports for specific recommendations
4. Check Gemini API documentation: https://ai.google.dev/

---

**Version**: 2.0.0 (Gemini + Gradio Edition)  
**Last Updated**: January 2025  
**Status**: Production Ready  
**LLM Provider**: Google Gemini 2.0 Flash lite 
**UI Framework**: Gradio
