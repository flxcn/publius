# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)

# Load the Federalist Papers data
def load_papers():
    try:
        with open('data/federalist_papers.json', 'r', encoding='utf-8') as f:
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