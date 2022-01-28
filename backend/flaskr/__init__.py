# /////////////

import os
from flask import Flask, request, abort, jsonify, app
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

# Done  Set up CORS. Allow '*' for origins. Delete the sample route
#  setup CORS on a resource and origin
    CORS(app, resources={r"*": {"origins": "*"}})

    # Done Use the after_request decorator to set Access-Control-Allow

    @app.after_request
    def after_request(response):
        # create a function which run after each request
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,POST,PUT,DELETE,OPTIONS')
        # then get the response after request
        return response

# Done Create an endpoint to handle GET requests for all available categories.

    @app.route('/categories')
    def get_categories():

        # apply query on categories to get all categories
        categories = Category.query.all()
        # add the categories in category_set
        category_set = {category.id:
                        category.type
                        for category in categories}
        # if there is no categories , abort a 404 error
        if not category_set:
            print("category_set is empty")
            abort(404)
        else:
            return jsonify({
                'success': True,
                'categories': category_set
            })

# DONE  Create an endpoint to handle GET requests for questions

    @app.route('/questions')
    def get_questions():
        # get the first and last pages
        page = request.args.get('page', 1, type=int)
        first = (page - 1) * QUESTIONS_PER_PAGE
        last = first + QUESTIONS_PER_PAGE

        # get all questions query
        questions = Question.query.all()
        all_questions = len(questions)
        categories = Category.query.all()

        category_set = {category.id:
                        category.type
                        for category in categories}
        # if there is no questions , abort a 404 error
        if not all_questions:
            print("there is no question")
            abort(404)

        questions = [question.format() for question in questions]
        # get existing page
        exist_questions = questions[first:last]

        return jsonify({
            'success': True,
            'questions': exist_questions,
            'total_questions': all_questions,
            'categories': category_set
        })

# Done  Create an endpoint to DELETE question using a question ID.

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            #  question id query
            delete_question_id = Question.query.\
                filter(Question.id == question_id)

            # if there is  no question , 404 error
            if delete_question_id is None:
                abort(404)
            else:
                # delete the question
                delete_question_id.delete()

        except:
            # if there is issue in deleting question
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()
            # success response
        return jsonify({
            'success': True,
        })

# Done Create an endpoint to POST a new question,

    @app.route('/questions', methods=['POST'])
    def post_question():

        # get request
        req_data = request.get_json()

        # get the question parts
        question_req = req_data.get('question')
        answer = req_data.get('answer')
        difficulty = req_data.get('difficulty')
        category = req_data.get('category')

        add_question = Question(
            question=question_req,
            answer=answer,
            difficulty=difficulty,
            category=category
        )
        # insert question into database
        add_question.insert()
        # abort method if there is no question_req
        if question_req is None:
            abort(422)
        else:
            return jsonify({
                "success": True,
            })

# Done  Create a POST endpoint to get questions based on a search term.

    @app.route("/search", methods=["POST"])
    def get_questions_based_on_search():
        # get search term
        search_term = request.get_json().get('search')
        # get search result
        search_result = (Question.query
                         .filter(Question.question
                                 .ilike("%{}%".format(search_term))).all())
        resulted_question = [question.format() for question in search_result]
        # get the number of search results
        result_num = len(resulted_question)

        if search_term is not None:
            # if search result has questions

            return jsonify({
                "success": True,
                "questions": resulted_question,
                "total_questions": result_num,
            })
        else:
            # get all question ,if search is null
            all_questions = Question.query.all()
            # return the result
            return jsonify({
                "success": True,
                "questions": all_questions,
                "total_questions": len(all_questions),

            })

# Done Create a GET endpoint to get questions based on category.

    @app.route('/categories/<int:category_id>/questions')
    def get_questions_based_on_category(category_id):
        # get the first and last pages
        page = request.args.get('page', 1, type=int)
        first = (page - 1) * QUESTIONS_PER_PAGE
        last = first + QUESTIONS_PER_PAGE

        # category id query
        category_filter = Category.query\
            .filter(Category.id == category_id)
        # filter question by category id
        question_filter = Question.query\
            .filter_by(category_filter=category_filter.id)\
            .all()

        questions = [question.format() for question in question_filter]
        # get existing page
        exist_questions = questions[first:last]
        # get all questions
        all_questions = Question.query.all()

        # the json result
        return jsonify({
            'success': True,
            'questions': exist_questions,
            'total_questions': len(all_questions)})

# Done  Create a POST endpoint to get questions to play the quiz.

    @app.route("/quiz", methods=["POST"])
    def get_quiz_question():
        # get request
        req_data = request.get_json()

        # get the quiz parts
        previous_q = req_data.get('previous_q')
        category_quiz = req_data.get('quiz_category')
        # filter questions by category
        questions_filter = Question.query\
            .filter_by(category=category_quiz['id']).all()
#Return sucssess if the number of previous question is equal to number of categories
        if (len(previous_q) == len(questions_filter)):
            return jsonify({
                'success': True
            })

        # get random question
        question =\
            questions_filter[random.randrange(0, len(questions_filter), 1)]
        return jsonify({
            'success': True,
            'question': question.format()
        })

# Done Create error handlers for all expected errors including 404 and 422.

# handle the case if server is unable to process the contained instructions
    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            "success": False,
            "message": "Unprocessable Entity",
            "error": 422,
        }), 422

    # handle of errors 404 if resource not found
    @app.errorhandler(404)
    def resource_not_found(error):
        return jsonify({
            "success": False,
            "message": "resource not found",
            "error": 404,

        }), 404

    return app
