# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from datetime import datetime
import requests
from dotenv import load_dotenv
from flask import request, jsonify

load_dotenv()
app = Flask(__name__)

# Add Claude API configuration
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')

@app.route('/ask_claude', methods=['POST'])
def ask_claude():
    data = request.get_json()
    
    if not data or 'query' not in data or 'context' not in data:
        return jsonify({"error": "Invalid request data"}), 400
    
    user_query = data['query']
    text_context = data['context']
    paper_id = data.get('paper_id', 0)
    
    # Check if API key exists
    api_key = os.environ.get('CLAUDE_API_KEY')
    if not api_key:
        print("Warning: CLAUDE_API_KEY not set in environment variables")
        mock_response = "⚠️ Claude API key is not configured. This is a mock response.\n\n"
        mock_response += f"Your query: {user_query}\n\n"
        mock_response += "To get actual responses from Claude, please set the CLAUDE_API_KEY environment variable."
        return jsonify({"response": mock_response})
    
    # Format the prompt for Claude
    prompt = f"""You are an expert on the Classics and the Federalist Papers.  I am reading Federalist Paper #{paper_id} and I need help understanding this:

"{text_context}"

Please provide a clear, helpful explanation addressing these three components:

1. Action: What is the central event being discussed? How does it relate to some community or primary audience?

2. Evaluation: How does the author offer an evaluation of the significance of this action to the community. In particular, is the action held up as “good” or “bad?” 

3. Norm Setting: What norms are conveyed by this action's inclusion in the Federalist Papers?

Include relevant historical context if needed."""
    
    # Log information for debugging
    print(f"Sending request to Claude API for paper #{paper_id}")
    
    try:
        # Use the Messages API with the REQUIRED anthropic-version header
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"  # This header is required
            },
            json={
                "model": "claude-3-opus-20240229",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        
        print(f"API Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error response: {response.text}")
            return jsonify({"error": f"Claude API error: {response.text}"}), 500
        
        result = response.json()
        
        # Extract Claude's response from the API response
        if "content" in result and len(result["content"]) > 0:
            claude_response = result["content"][0]["text"]
        else:
            print("Unexpected response format:", result)
            claude_response = "Error: Received unexpected response format from Claude"
        
        return jsonify({"response": claude_response})
        
    except Exception as e:
        print(f"Exception when calling Claude API: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    
# Load the Federalist Papers data
def load_papers():
    try:
        # Get the absolute path to the current file (app.py)
        base_dir = os.path.abspath(os.path.dirname(__file__))
        # Construct the absolute path to the data file
        data_file = os.path.join(base_dir, 'data', 'federalist_papers.json')

        with open(data_file, 'r', encoding='utf-8') as f:
            papers = json.load(f)
            # Make sure papers are sorted by paper_id
            papers.sort(key=lambda x: x["paper_id"])
            return papers
    except Exception as e:
        print(f"Error loading papers: {e}")
        # Return placeholder data if file doesn't exist
        return [
            {
                "author": "HAMILTON",
                "text": "This is the content of Federalist Paper #1...",
                "date": None,
                "title": "General Introduction",
                "paper_id": 1,
                "venue": "For the Independent Journal"
            }
        ]

@app.route('/')
def index():
    papers = load_papers()
    return render_template('index.html', papers=papers)

@app.route('/paper/<int:paper_id>')
def view_paper(paper_id):
    papers = load_papers()
    paper = next((p for p in papers if p["paper_id"] == paper_id), None)
    if paper:
        return render_template('paper.html', paper=paper)
    return "Paper not found", 404

@app.route('/search')
def search():
    query = request.args.get('query', '').lower()
    if not query:
        return render_template('search.html', results=[], query="")
    
    papers = load_papers()
    # Search in title and text
    results = [p for p in papers if query in p["title"].lower() or query in p["text"].lower()]
    return render_template('search.html', results=results, query=query)

@app.route('/authors')
def authors():
    papers = load_papers()
    # Get unique authors
    author_set = set(paper["author"] for paper in papers if paper["author"])
    
    # Count papers per author
    author_counts = {}
    for author in author_set:
        author_counts[author] = len([p for p in papers if p["author"] == author])
    
    # Sort by count (descending)
    sorted_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)
    
    return render_template('authors.html', authors=sorted_authors)

@app.route('/author/<author_name>')
def author_papers(author_name):
    papers = load_papers()
    # Filter papers by author
    author_papers = [p for p in papers if p["author"] == author_name]
    return render_template('author_papers.html', papers=author_papers, author=author_name)

@app.route('/venues')
def venues():
    papers = load_papers()
    # Get papers organized by venue
    venues = {}
    for paper in papers:
        venue = paper.get("venue", "Unknown")
        if venue not in venues:
            venues[venue] = []
        venues[venue].append(paper)
    
    return render_template('venues.html', venues=venues)

@app.route('/api/papers')
def api_papers():
    papers = load_papers()
    return jsonify(papers)

@app.route('/api/paper/<int:paper_id>')
def api_paper(paper_id):
    papers = load_papers()
    paper = next((p for p in papers if p["paper_id"] == paper_id), None)
    if paper:
        return jsonify(paper)
    return jsonify({"error": "Paper not found"}), 404


if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    app.run(debug=True)