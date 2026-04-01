from flask import Flask, request, jsonify
from moviebox_api.v2.core import Search, MovieDetails, TVSeriesDetails
from moviebox_api.v2.requests import Session
import asyncio

app = Flask(__name__)

# Helper to run async code in a synchronous Flask route
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "message": "Moviebox API is running.",
        "status": "online",
        "endpoints": {
            "search": "/api/search?q=movie_title",
            "movie": "/api/movie?id=movie_path"
        }
    })

@app.route('/api/search', methods=['GET'])
def search_api():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    
    try:
        session = Session()
        search_client = Search(session=session)
        # In v2, Search.get_content_model takes query as argument if not set in init
        # or uses the one from init. v1 init takes query. 
        # Let's check v2 core again to be sure.
        results_model = run_async(search_client.get_content_model(query))
        
        try:
            data = results_model.model_dump()
        except AttributeError:
            data = results_model.dict()
            
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/movie', methods=['GET'])
def movie_details():
    movie_path = request.args.get('id') # Usually the detailPath from search
    if not movie_path:
        return jsonify({"error": "Query parameter 'id' is required"}), 400

    try:
        session = Session()
        movie_client = MovieDetails(session=session)
        movie_model = run_async(movie_client.get_content_model(movie_path))
        
        try:
            data = movie_model.model_dump()
        except AttributeError:
            data = movie_model.dict()
            
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
