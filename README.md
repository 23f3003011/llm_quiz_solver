# LLM Quiz Solver

An intelligent quiz-solving system powered by Large Language Models (LLMs) that automatically solves data analysis quizzes, processes files, and handles API-based questions.

## Features

- **JavaScript-Heavy Page Rendering**: Uses Playwright to render and interact with JavaScript-heavy quiz pages
- **Multi-Format File Processing**: Handles PDF, CSV, and Excel file downloads and processing
- **API Integration**: Automatically detects and calls relevant APIs from questions
- **Data Analysis**: Performs data analysis tasks including sum, average, count, and statistical operations
- **Visualization Support**: Handles questions related to charts and graphs
- **LLM Integration**: Supports both OpenAI and Anthropic APIs for intelligent problem-solving
- **Session Management**: Tracks active quiz sessions with timeout handling
- **RESTful API**: Flask-based API for easy integration

## Project Structure

```
llm_quiz_solver/
├── main.py              # Flask API server
├── quiz_solver.py        # Core quiz solving logic
├── llm_handler.py        # LLM API integration
├── requirements.txt      # Project dependencies
├── .env                 # Environment variables (not included)
├─┠ README.md            # This file
└── LICENSE              # MIT License
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/llm_quiz_solver.git
cd llm_quiz_solver
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file with:
```
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
LLM_MODEL=gpt-4-turbo
SECRET_STRING=your_secret_key
EMAIL=your_email@example.com
```

## Usage

### Start the Server

```bash
python main.py
```

The server will run on `http://0.0.0.0:5000`

### API Endpoints

#### Solve Quiz
```bash
POST /quiz
Content-Type: application/json

{
  "email": "your-email@example.com",
  "url": "https://quiz-url.com",
  "secret": "your_secret_key"
}
```

Response:
```json
{
  "answer": "calculated_answer",
  "status": "success"
}
```

#### Health Check
```bash
GET /health
```

## Dependencies

- **Flask**: Web framework for API
- **Playwright**: Browser automation for JavaScript rendering
- **Requests**: HTTP client for API calls
- **Pandas**: Data analysis and processing
- **NumPy**: Numerical computations
- **OpenAI**: OpenAI API integration
- **Anthropic**: Anthropic Claude API integration
- **PyPDF2**: PDF file processing
- **Pillow**: Image processing

See `requirements.txt` for complete list and versions.

## Architecture

### Components

1. **main.py**: Flask API server
   - Handles HTTP requests
   - Session management
   - Request validation

2. **quiz_solver.py**: Quiz solving orchestrator
   - Page rendering with Playwright
   - Question extraction
   - Strategy selection based on question type
   - File processing coordination

3. **llm_handler.py**: LLM integration
   - OpenAI and Anthropic API handling
   - Solution planning
   - Generic problem solving
   - Data analysis prompting

### Question Types Supported

- **File Download**: Automatic download and processing of PDF, CSV, Excel files
- **API Calls**: Detection and execution of API endpoints
- **Data Analysis**: Sum, average, count, statistical analysis
- **Visualization**: Chart and graph interpretation
- **Generic**: General knowledge questions solved by LLM

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: OpenAI API key for GPT models
- `ANTHROPIC_API_KEY`: Anthropic API key for Claude models
- `LLM_MODEL`: Default LLM model to use (default: gpt-4-turbo)
- `SECRET_STRING`: Secret key for API authentication
- `EMAIL`: Default email for submissions

### Timeout Settings

- Quiz timeout: 180 seconds (3 minutes)
- Page render timeout: 30 seconds
- API call timeout: 10 seconds

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This tool is for educational purposes only. Ensure you have the appropriate permissions to use it on quiz platforms and comply with their terms of service.
