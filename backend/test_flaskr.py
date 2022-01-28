import json
import unittest
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from backend.flaskr.models import setup_db, Question


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    # test_get_categories and test_get_categories failure scenario
    # GET categories endpoint test
    def get_categories_test(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data["categories"]))

    def get_categories_test_failure(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["categories"]))
        self.assertEqual(data['total_categories'] > 0, True)

        self.assertEqual(data['success'], True)

    # test_create_question and test_create_question failure scenario
    # POST questions endpoint test
    def post_question_test(self):
        question_json = {
            'question': 'question sample',
            'answer': 'answer sample',
            'difficulty': 1,
            'category': 1
        }

        res = self.client().post('/questions', json=question_json)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_post_question_failure(self):
        question_json = {
            'question': 'question sample',
            'answer': 'answer sample',
            'difficulty': 1,
            'category': 1
        }
        res = self.client().post('/questions', json=question_json)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(json.loads(res.data)["success"], False)

    # test_get_questions_by_category and test_get_questions_by_category failure scenario

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['success'], True)

    def test_get_questions_by_category_failure(self):
        res = self.client().get('/categories/a/questions')
        self.assertEqual(res.status_code, 404)

    # test_search_questions and test_search_questions failure scenario

    def test_search_questions(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'a'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])
        self.assertEqual(data['success'], True)

    def test_search_questions_failure(self):
        res = self.client().post('/questions/search', json={
            'search_result': '', })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["message"], "not found")
        self.assertEqual(data["success"], False)

    # test_delete_question and test_delete_question failure scenario
    def test_delete_question(self):
        question = Question(question='question_json', answer='answer',
                            difficulty=1, category=1)
        question = Question.query.filter(Question.id == question.id)
        question.insert()
        question_id = question.id

        res = self.client().delete(f'/questions/{question_id}')

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['deleted'], str(question_id))
        self.assertEqual(question, None)
        self.assertEqual(data['success'], True)

    def test_deleting_question_failure(self):
        res = self.client().delete('/questions/a')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)

        self.assertEqual(data['message'], 'unprocessable')
        self.assertEqual(data['success'], False)

    # test_play_quiz and test_play_quiz failure scenario
    def test_play_quiz(self):
        res = self.client().post('/quiz', json={'previous_q': [],
                                                'category_quiz': {'type': 'Entertainment', 'id': 5}})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_play_quiz_failure(self):
        res = self.client().post('/quiz', json={'previous_q': []})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["message"], "unprocessable")
        self.assertEqual(data["success"], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
