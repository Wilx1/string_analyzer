from collections import OrderedDict
# from crypt import methods
from datetime import datetime, timezone
from flask import Flask, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text as txt
import json
import hashlib
from werkzeug.exceptions import BadRequest
import os

app = Flask(__name__)

PORT = int(os.environ.get("PORT", 5000))


#db configuration
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///data.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

current_time = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

class StringRecord(db.Model):
    id = db.Column(db.String(64), primary_key=True)  # sha256 hash as ID
    value = db.Column(db.String(255), unique=True, nullable=False)
    length = db.Column(db.Integer)
    is_palindrome = db.Column(db.Boolean)
    unique_characters = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    sha256_hash = db.Column(db.String(64))
    character_frequency_map = db.Column(db.JSON)
    created_at = db.Column(db.String(50), default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """Convert DB record to a serializable dictionary"""
        return {
            "id": self.id,
            "value": self.value,
            "properties": {
                "length": self.length,
                "is_palindrome": self.is_palindrome,
                "unique_characters": self.unique_characters,
                "word_count": self.word_count,
                "sha256_hash": self.sha256_hash,
                "character_frequency_map": self.character_frequency_map or {}
            },
            # Convert datetime to ISO format (e.g. 2025-10-22T12:00:00Z)
            "created_at": self.created_at if isinstance(self.created_at, str)
            else self.created_at.isoformat().replace("+00:00", "Z")
        }

with app.app_context():
    db.create_all()

### Function definitions ============================================================

def is_json_object(input_string):
    """
    Checks if the input_string is a valid JSON object.
    Returns True if it's a valid JSON object (Python dictionary), False otherwise.
    """
    try:
        parsed_data = json.loads(input_string)
        # A JSON object maps to a Python dictionary
        return isinstance(parsed_data, dict)
    except json.JSONDecodeError:
        # If json.loads() raises an error, it's not valid JSON
        return False

## is_palindrome
def is_palindrome(param_text):
    """
    Checks if a given string is a palindrome, ignoring case.

    Args:
        param_text: The input string to check.

    Returns:
        True if the string is a palindrome, False otherwise.
    """
    cleaned_text = "".join(char for char in param_text if char.isalnum()).lower()
    return cleaned_text == cleaned_text[::-1]

## wordcount
def wordcount(param_text):
    """
        Counts the number of words in a sentence.

        Args:
            param_text: The input string to check.

        Returns:
            Number of words.
        """
    split_text = param_text.split()
    return len(split_text)
## count unique xters
def unique_xters(param_text):
    """Counts the frequency of each character using a dictionary."""
    param_text = set(param_text.lower().replace(" ", ""))
    num_of_chars = len(param_text)
    return num_of_chars

## mapping of xter to occurence
def xter_occurence(param_text):
    """Maps each character to the number of
     occurrence using a dictionary."""
    counts = {}
    for char in param_text.lower().replace(" ", ""):
        if char in counts:
            counts[char] += 1
        else:
            counts[char] = 1
    return counts

## sha256_hash of string
def sha256_hash(input_string):
    """
    Generates the SHA-256 hash of a string.

    Args:
        input_string (str): The string to be hashed.

    Returns:
        str: The hexadecimal representation of the hash.
    """
    # Encode the string to a byte-like object (using utf-8 is standard).
    encoded_string = input_string.encode('utf-8')

    # Create a new SHA-256 hash object.
    hash_object = hashlib.sha256(encoded_string)

    # Return the hash as a hexadecimal string.
    return hash_object.hexdigest()


# routes============================================================

@app.route('/')
def home():
    return {
        'message': 'nothing here.'
    }



@app.route('/strings', methods=["GET", "POST"])
def strings():
    # check method used
    if request.method == 'GET':
        text_is_palindrome = request.args.get('is_palindrome')
        min_length = request.args.get('min_length', type=int)
        max_length = request.args.get('max_length', type=int)
        word_count = request.args.get('word_count', type=int)
        contains_character = request.args.get('contains_character', type=str)

        # Convert is_palindrome to bool if provided
        if text_is_palindrome is not None:
            text_is_palindrome = text_is_palindrome.lower() == 'true'

        query = StringRecord.query

        if text_is_palindrome is not None:
            query = query.filter(StringRecord.is_palindrome == text_is_palindrome)

        if min_length is not None:
            query = query.filter(StringRecord.length >= min_length)

        if max_length is not None:
            query = query.filter(StringRecord.length <= max_length)

        if word_count is not None:
            query = query.filter(StringRecord.word_count == word_count)

        if contains_character:
            query = query.filter(
                txt(f"json_extract(character_frequency_map, '$.{contains_character}') IS NOT NULL")
            )

        results = query.all()
        data = [item.to_dict() for item in results]

        filters_applied = {
            "is_palindrome": text_is_palindrome,
            "min_length": min_length,
            "max_length": max_length,
            "word_count": word_count,
            "contains_character": contains_character
        }

        response = {
            "data": data,
            "count": len(data),
            "filters_applied": {k: v for k, v in filters_applied.items() if v is not None}
        }

        return jsonify(response), 200

    elif request.method == "POST":
        ## Check if input is a json
        value = None
        if not request.content_type or request.content_type != 'application/json':
            return jsonify({
                "error": "Invalid Content-Type. Expected 'application/json'."
            }), 415
        try:
            data = request.get_json(silent=True)
            if not data or "value" not in data:
                return jsonify({
                    "error": 'Invalid request body or missing "value" field'
                }), 502  # Bad Request

            value = data["value"]

            # check if value already exists in db
            check_db = StringRecord.query.filter_by(value=value).first()
            if check_db:
                return jsonify({"message":"String already exists in the system"}), 409

            # 3. Validate data type
            if not isinstance(value, str):
                return jsonify({
                    "error": 'Invalid data type for "value" (must be string)'
                }), 502  # Unprocessable Entity


            input_data = json.dumps(data)
            text = is_json_object(input_data)

            if not text:
                return {
                    'message': 'Only json objects are accepted here'
                }
            else:
                # it's a json
                # process and store in db
                hashed_text = sha256_hash(value)

                new_string = StringRecord(
                    id = hashed_text,
                    value = value,
                    length = len(value),
                    is_palindrome = is_palindrome(value),
                    unique_characters = unique_xters(value),
                    word_count = wordcount(value),
                    sha256_hash = hashed_text,
                    character_frequency_map = xter_occurence(value),
                    created_at = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                )

                # Save to DB
                db.session.add(new_string)
                db.session.commit()

                # force order
                data = OrderedDict()
                data['id'] =new_string.id
                data['value'] = new_string.value
                data['properties'] = {
                    "length": new_string.length,
                    "is_palindrome": new_string.is_palindrome,
                    "unique_characters": new_string.unique_characters,
                    "word_count": new_string.word_count,
                    "sha256_hash": new_string.sha256_hash,
                    "character_frequency_map": new_string.character_frequency_map
                }
                data['created_at'] = new_string.created_at
                json_data = json.dumps(data, indent=2, ensure_ascii=False)
                return Response(json_data, mimetype="application/json", status=201)


        except BadRequest as e:
            return jsonify({"error": "Invalid JSON format", "details": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "Something went wrong", "details": str(e)}), 500


@app.route('/strings/<string_value>')
def get_string(string_value):
    retrieved_record = StringRecord.query.filter_by(value=string_value).first()

    if not retrieved_record:
        return jsonify({"error": "String not found"}), 404

    # Build the JSON response
    data = {
        "id": retrieved_record.id,
        "value": retrieved_record.value,
        "properties": {
            "length": len(retrieved_record.value),
            "is_palindrome": retrieved_record.value.lower() == retrieved_record.value[::-1].lower(),
            "unique_characters": len(set(retrieved_record.value)),
            "word_count": len(retrieved_record.value.split()),
            "sha256_hash": retrieved_record.id,
            "character_frequency_map": {ch: retrieved_record.value.count(ch) for ch in set(retrieved_record.value)}
        },
        "created_at": retrieved_record.created_at
    }

    # force order
    data = OrderedDict()
    data['id'] = retrieved_record.id
    data['value'] = retrieved_record.value
    data['properties'] = {
        "length": retrieved_record.length,
        "is_palindrome": retrieved_record.is_palindrome,
        "unique_characters": retrieved_record.unique_characters,
        "word_count": retrieved_record.word_count,
        "sha256_hash": retrieved_record.sha256_hash,
        "character_frequency_map": retrieved_record.character_frequency_map
    }
    data['created_at'] = retrieved_record.created_at
    json_data = json.dumps(data, indent=2, ensure_ascii=False)
    return Response(json_data, mimetype="application/json", status=200)


@app.route('/strings/filter-by-natural-language', methods=['GET'])
def filter_by_natural_language():
    query = request.args.get('query', '').strip().lower()

    if not query:
        return jsonify({"error": "Missing query parameter"}), 400

    parsed_filters = {}

    # --- interpret natural language ---
    if "single word" in query:
        parsed_filters["word_count"] = 1
    if "palindromic" in query or "palindrome" in query:
        parsed_filters["is_palindrome"] = True
    match = re.search(r'longer than (\d+)', query)
    if match:
        parsed_filters["min_length"] = int(match.group(1)) + 1
    match = re.search(r'shorter than (\d+)', query)
    if match:
        parsed_filters["max_length"] = int(match.group(1)) - 1
    match = re.search(r'contain(?:s|ing)?(?: the letter)? ([a-zA-Z])', query)
    if match:
        parsed_filters["contains_character"] = match.group(1).lower()

    if not parsed_filters:
        return jsonify({"error": "Unable to parse natural language query"}), 400

    # --- reuse logic by calling your main filtering function ---
    query_obj = StringRecord.query

    if "is_palindrome" in parsed_filters:
        query_obj = query_obj.filter(StringRecord.is_palindrome == parsed_filters["is_palindrome"])
    if "min_length" in parsed_filters:
        query_obj = query_obj.filter(StringRecord.length >= parsed_filters["min_length"])
    if "max_length" in parsed_filters:
        query_obj = query_obj.filter(StringRecord.length <= parsed_filters["max_length"])
    if "word_count" in parsed_filters:
        query_obj = query_obj.filter(StringRecord.word_count == parsed_filters["word_count"])
    if "contains_character" in parsed_filters:
        char = parsed_filters["contains_character"]
        query_obj = query_obj.filter(
            text(f"json_extract(character_frequency_map, '$.{char}') IS NOT NULL")
        )

    results = query_obj.all()
    data = [record.to_dict() for record in results]

    return jsonify({
        "data": data,
        "count": len(data),
        "interpreted_query": {
            "original": query,
            "parsed_filters": parsed_filters
        }
    }), 200


@app.route('/strings/<string_value>', methods=['DELETE'])
def delete_string(string_value):
    # Try to find the string record in the database
    record = StringRecord.query.filter_by(value=string_value).first()

    # If not found, return 404 Not Found
    if not record:
        return jsonify({
            "error": "String not found",
            "message": f"The string '{string_value}' does not exist in the system."
        }), 404

    # If found, delete it
    db.session.delete(record)
    db.session.commit()

    # Return 204 No Content (no response body)
    return '', 204


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=PORT)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
