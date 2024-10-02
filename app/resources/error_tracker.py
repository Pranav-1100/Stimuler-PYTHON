from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app, request
from app.utils.error_tracker import SortedArrayTracker
from collections import defaultdict
import json
import random


class ErrorUpdate(Resource):
    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('error_category', type=str, required=True)
        parser.add_argument('error_subcategory', type=str, required=True)
        data = parser.parse_args()

        user_email = get_jwt_identity()
        user = current_app.db.users.find_one({'email': user_email})

        if not user:
            return {'message': 'User not found'}, 404

        user_id = str(user['_id'])
        
        # Try to get tracker data from Redis cache
        # cached_tracker = current_app.redis.get(f"error_tracker:{user_id}")  # Commented out Redis cache

        # Simulating cache retrieval
        # if cached_tracker:
        #     tracker_data = json.loads(cached_tracker)
        #     tracker = SortedArrayTracker()
        #     tracker.error_map = defaultdict(int, tracker_data['error_map'])
        #     tracker.sorted_errors = tracker_data['sorted_errors']
        # else:
        user_tracker = current_app.db.error_trackers.find_one({'user_id': user_id})
        if not user_tracker:
            tracker = SortedArrayTracker()
        else:
            tracker = SortedArrayTracker()
            tracker.error_map = defaultdict(int, user_tracker.get('error_map', {}))
            tracker.sorted_errors = user_tracker.get('sorted_errors', [])

        tracker.update_error(data['error_category'], data['error_subcategory'])

        # Update Redis cache
        # current_app.redis.set(  # Commented out Redis cache update
        #     f"error_tracker:{user_id}",
        #     json.dumps({
        #         'error_map': dict(tracker.error_map),
        #         'sorted_errors': tracker.sorted_errors
        #     }),
        #     ex=3600  # Cache for 1 hour
        # )

        current_app.db.error_trackers.update_one(
            {'user_id': user_id},
            {
                '$set': {
                    'user_id': user_id,
                    'error_map': dict(tracker.error_map),
                    'sorted_errors': tracker.sorted_errors
                }
            },
            upsert=True
        )

        return {'message': 'Error updated successfully'}, 200

class TopErrors(Resource):
    @jwt_required()
    def get(self):
        n = request.args.get('n', default=10, type=int)
        
        user_email = get_jwt_identity()
        user = current_app.db.users.find_one({'email': user_email})

        if not user:
            return {'message': 'User not found'}, 404

        user_id = str(user['_id'])

        # Try to get tracker data from Redis cache
        # cached_tracker = current_app.redis.get(f"error_tracker:{user_id}")  # Commented out Redis cache

        # Simulating cache retrieval
        # if cached_tracker:
        #     tracker_data = json.loads(cached_tracker)
        #     tracker = SortedArrayTracker()
        #     tracker.error_map = defaultdict(int, tracker_data['error_map'])
        #     tracker.sorted_errors = tracker_data['sorted_errors']
        # else:
        user_tracker = current_app.db.error_trackers.find_one({'user_id': user_id})
        if not user_tracker:
            return {'errors': []}, 200
        tracker = SortedArrayTracker()
        tracker.error_map = defaultdict(int, user_tracker.get('error_map', {}))
        tracker.sorted_errors = user_tracker.get('sorted_errors', [])

        # Update Redis cache
        # current_app.redis.set(  # Commented out Redis cache update
        #     f"error_tracker:{user_id}",
        #     json.dumps({
        #         'error_map': dict(tracker.error_map),
        #         'sorted_errors': tracker.sorted_errors
        #     }),
        #     ex=3600  # Cache for 1 hour
        # )

        top_errors = tracker.get_top_n_errors(n)

        return {
            'errors': [
                {
                    'error_category': key.split(':')[0],
                    'error_subcategory': key.split(':')[1],
                    'count': count
                } for count, key in top_errors
            ]
        }, 200

class GenerateDummyData(Resource):
    @jwt_required()
    def post(self):
        user_email = get_jwt_identity()
        user = current_app.db.users.find_one({'email': user_email})

        if not user:
            return {'message': 'User not found'}, 404

        user_id = str(user['_id'])
        
        error_categories = ['Grammar', 'Vocabulary', 'Pronunciation', 'Fluency']
        error_subcategories = {
            'Grammar': ['Verb Tense', 'Subject-Verb Agreement', 'Article Usage', 'Prepositions', 'Word Order'],
            'Vocabulary': ['Wrong Word Choice', 'Collocation', 'Idiomatic Expression', 'Word Formation', 'Register'],
            'Pronunciation': ['Vowel Sounds', 'Consonant Sounds', 'Stress', 'Intonation', 'Linking'],
            'Fluency': ['Hesitation', 'Repetition', 'Self-Correction', 'Filler Words', 'Pausing']
        }

        tracker = SortedArrayTracker()
        for _ in range(1000):
            category = random.choice(error_categories)
            subcategory = random.choice(error_subcategories[category])
            tracker.update_error(category, subcategory)

        # Update Redis cache
        # current_app.redis.set(  # Commented out Redis cache update
        #     f"error_tracker:{user_id}",
        #     json.dumps({
        #         'error_map': dict(tracker.error_map),
        #         'sorted_errors': tracker.sorted_errors
        #     }),
        #     ex=3600  # Cache for 1 hour
        # )

        # Update MongoDB
        current_app.db.error_trackers.update_one(
            {'user_id': user_id},
            {
                '$set': {
                    'user_id': user_id,
                    'error_map': dict(tracker.error_map),
                    'sorted_errors': tracker.sorted_errors
                }
            },
            upsert=True
        )

        return {'message': 'Dummy data generated successfully'}, 200
