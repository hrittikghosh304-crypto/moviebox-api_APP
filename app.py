import asyncio
from flask import Flask, request, jsonify
from moviebox_api.v2.core import Search, MovieDetails, TVSeriesDetails

app = Flask(__name__)

# moviebox-api is primarily async, so we'll run it in a loop
def run_async(coroutine):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(coroutine)
    loop.close()
    return result

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Moviebox API is running."})

@app.route('/api/search', methods=['GET'])
def search_api():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    
    try:
        search_client = Search()
        # Ensure we properly await the async get_content_model
        results_model = run_async(search_client.get_content_model(query))
        
        # We can dump the result model to a dict to serialize it
        # pydantic models have `.model_dump()` or `.dict()` depending on version. 
        # For pydantic>=2.x it's model_dump()
        try:
            data = results_model.model_dump()
        except AttributeError:
            data = results_model.dict()
            
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/movie', methods=['GET'])
def movie_details():
    movie_id = request.args.get('id')
    if not movie_id:
        return jsonify({"error": "Query parameter 'id' is required"}), 400

    try:
        # Usually from search, detailPath looks like `/movie/1234`
        movie_client = MovieDetails(session=None)
        movie_model = run_async(movie_client.get_content_model(movie_id))
        
        try:
            data = movie_model.model_dump()
        except AttributeError:
            data = movie_model.dict()
            
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # You can specify host to 0.0.0.0 for external access
    app.run(host='0.0.0.0', port=5000, debug=True)
