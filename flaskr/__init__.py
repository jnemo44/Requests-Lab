import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy #, or_
from flask_cors import CORS
import random

from models import setup_db, Book

BOOKS_PER_SHELF = 8

def paginate_books(reguest, selection):
    page = reguest.args.get('page',1,type=int)
    start = (page-1)*BOOKS_PER_SHELF
    end = start+BOOKS_PER_SHELF

    books = [book.format() for book in selection]
    current_books = books[start:end]

    return current_books



# @TODO: General Instructions
#   - As you're creating endpoints, define them and then search for 'TODO' within the frontend to update the endpoints there. 
#     If you do not update the endpoints, the lab will not work - of no fault of your API code! 
#   - Make sure for each route that you're thinking through when to abort and with which kind of error 
#   - If you change any of the response body keys, make sure you update the frontend to correspond. 

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  # CORS Headers 
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  # @TODO: Write a route that retrivies all books, paginated. 
  #         You can use the constant above to paginate by eight books.
  #         If you decide to change the number of books per page,
  #         update the frontend to handle additional books in the styling and pagination
  #         Response body keys: 'success', 'books' and 'total_books'
  # TEST: When completed, the webpage will display books including title, author, and rating shown as stars
  @app.route('/books', methods=['GET'])
  def get_books():
    selection = Book.query.order_by(Book.id).all()
    current_books = paginate_books(request, selection)

    if len(current_books) == 0:
        abort(404)
    
    return jsonify({
        'success':True,
        'books': current_books,
        'total_books':len(Book.query.all())
    })

  # @TODO: Write a route that will update a single book's rating. 
  #         It should only be able to update the rating, not the entire representation
  #         and should follow API design principles regarding method and route.  
  #         Response body keys: 'success'
  # TEST: When completed, you will be able to click on stars to update a book's rating and it will persist after refresh
  @app.route('/books/<int:book_id>', methods=['PATCH'])
  def edit_rating(book_id):
      
    body = request.get_json()
      
    try:
        selected_book = Book.query.filter(Book.id==book_id).one_or_none()

        #Check to see if the book exsists
        if selected_book is None:
            #Book not found
            abort(404)
        #Find a specified rating in the request body
        if 'rating' in body:
            selected_book.rating = int(body.get('rating'))
        
        #Update the record in the db
        selected_book.update()

        return jsonify({
            'success':True,
            'book_updated':book_id
        })
    except:
        abort(400)
        


  # @TODO: Write a route that will delete a single book. 
  #        Response body keys: 'success', 'deleted'(id of deleted book), 'books' and 'total_books'
  #        Response body keys: 'success', 'books' and 'total_books'

  # TEST: When completed, you will be able to delete a single book by clicking on the trashcan.
  @app.route('/books/<int:book_id>', methods=['DELETE'])
  def delete_book(book_id):
    try:
        selected_book = Book.query.filter(Book.id==book_id).one_or_none()

        if selected_book is None:
            #Book not found
            abort(404)
        else:
            #Delete the book
            selected_book.delete()
            #Query the db to GET updated info
            selection = Book.query.order_by(Book.id).all()
            current_books = paginate_books(request, selection)

        return jsonify({
            "success":True,
            "deleted_book_id":book_id,
            "books": current_books,
            "total_books": len(Book.query.all())
        })

    except:
        abort(422)

  # @TODO: Write a route that create a new book. 
  #        Response body keys: 'success', 'created'(id of created book), 'books' and 'total_books'
  # TEST: When completed, you will be able to a new book using the form. Try doing so from the last page of books. 
  #       Your new book should show up immediately after you submit it at the end of the page.
  @app.route('/books', methods=['POST'])
  def create_book():
    body = request.get_json()
    
    #Proceed to book creation and set default to None
    new_title = body.get('title', None)
    new_author = body.get('author', None)
    new_rating = body.get('rating', None)
    search_term = body.get('search',None)

    
    try:
        if search_term:
            selection = Book.query.filter(Book.title.ilike('%'+search_term+'%'))
            current_books = paginate_books(request, selection)

            return jsonify({
                'success':True,
                'total_books':len(selection.all()),
                'books':current_books
            })

        else:
            book = Book(title=new_title,author=new_author,rating=new_rating)
            book.insert()

            #Query the db to GET updated info
            selection = Book.query.order_by(Book.id).all()
            current_books = paginate_books(request, selection)

            return jsonify({
                'success': True,
                'created': book.id,
                'current_books':current_books,
                'total_books':len(Book.query.all())
            })
    except:
        abort(422)

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          'success':False,
          'error':400,
          'message':'Bad Request'
      }),400
  
  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          'success':False,
          'error':404,
          'message':'Resource not found!'
      }),404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          'success':False,
          'error':422,
          'message':'Unprocessable'
      }),422
                
  
  return app