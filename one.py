    from flask import Flask, request, jsonify
    from flask_cors import CORS
    from pymongo import MongoClient
    from bson.objectid import ObjectId
    import datetime

    # --- SETUP ---
    app = Flask(__name__)
    CORS(app)

    # --- DATABASE CONNECTION (LOCAL) ---
    MONGO_URI = "mongodb://localhost:27017/" 
    client = MongoClient(MONGO_URI)
    db = client["jalcycle"] 

    users_collection = db["users"]
    greywater_entries_collection = db["greywater_entries"]
    delivery_updates_collection = db["delivery_updates"]

    print("✅ Connected to local MongoDB!")

    # --- API ROUTES ---
    @app.route('/login', methods=['POST'])
    def login():
        data = request.json
        phone = data.get('phone')
        password = data.get('password')
        user = users_collection.find_one({"phone_no": int(phone)})
        if not user:
            return jsonify({"error": "Phone number not registered."}), 404
        if user.get("password") == password:
            return jsonify({
                "message": "Login successful!",
                "role": user.get("role", "default"),
                "user_id": str(user["_id"])
            }), 200
        else:
            return jsonify({"error": "Invalid password."}), 401

    @app.route('/submit_water', methods=['POST'])
    def submit_water():
        data = request.json
        new_entry = {
            "household_id": ObjectId(data.get("user_id")),
            "litres": data.get("water_have"),
            "address": data.get("address"),
            "status": "available",
            "posted_at": datetime.datetime.utcnow()
        }
        result = greywater_entries_collection.insert_one(new_entry)
        return jsonify({"message": "Entry submitted successfully", "id": str(result.inserted_id)}), 201

    @app.route('/get_requests', methods=['GET'])
    def get_requests():
        entries = list(greywater_entries_collection.find({"status": "available"}))
        for entry in entries:
            entry["_id"] = str(entry["_id"])
        return jsonify(entries)

    @app.route('/get_delivery_tasks', methods=['GET'])
    def get_delivery_tasks():
        tasks = list(greywater_entries_collection.find({"status": "requested"}))
        for task in tasks:
            task["_id"] = str(task["_id"])
        return jsonify(tasks)

    # --- RUN THE APP ---
    if __name__ == '__main__':
        app.run(debug=True,host='0.0.0.0', port=5000)