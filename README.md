# Publius

Publius is a super simple digital reader for _The Federalist Papers_ that helps students better understand Classical references in the text. Read the full writeup [here](https://github.com/flxcn/publius/blob/main/publius_paper.pdf).

## Highlights
- Includes full text of all 85 papers, from Project Gutenburg
- Exact keyword match search functionality, author and publishing venue information
- Passage highlight feature for Classical reference, powered by Anthropic's Claude 3 Opus
- Written in Python + Flask for easy local deployment

## Usage
After cloning this repo, go ahead and duplicate `.env.example` and rename the file to `.env`. Then, go ahead and insert your own `ANTHROPIC_API_KEY=""`.

To run locally, in your command line:
1. Install Flask if you have not already, `$ pip install flask`
2. Then run the Flask app `$ python -m flask`

## Feedback
If you see any bugs or improvements feel free to open an Issue! Code is freely available under MIT license.
