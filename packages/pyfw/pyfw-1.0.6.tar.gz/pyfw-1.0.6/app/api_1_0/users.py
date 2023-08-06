from flask import jsonify, request, current_app, url_for
from . import api
from ..models import User



@api.route('/users/<int:id>', methods=['GET', 'POST'])
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())



@api.route('/users/tree')
def get_user_tree():

    return """
[{
	"id":1,
	"text":"My Documents",
	"children":[{
		"id":11,
		"text":"Photos",
		"state":"closed",
		"children":[{
			"id":111,
			"text":"Friend"
		},{
			"id":112,
			"text":"Wife"
		},{
			"id":113,
			"text":"Company"
		}]
	},{
		"id":12,
		"text":"Program Files",
		"children":[{
			"id":121,
			"text":"Intel"
		},{
			"id":122,
			"text":"Java",
			"attributes":{
				"p1":"Custom Attribute1",
				"p2":"Custom Attribute2"
			}
		},{
			"id":123,
			"text":"Microsoft Office"
		},{
			"id":124,
			"text":"Games",
			"checked":true
		}]
	},{
		"id":13,
		"text":"index.html"
	},{
		"id":14,
		"text":"about.html"
	},{
		"id":15,
		"text":"welcome.html"
	}]
}]
"""





@api.route('/userslist/<int:id>', methods=['GET', 'POST'])
def get_user_list(id):
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.id.desc()).paginate(
        page,
        error_out=False)
    userlist = pagination.items

    # print(userlist)
    return jsonify({
        'rows': [user.to_json() for user in userlist],

        'total': pagination.total
    })





# @api.route('/users/<int:id>/posts/')
# def get_user_posts(id):
#     user = User.query.get_or_404(id)
#     page = request.args.get('page', 1, type=int)
#     pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
#         page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
#         error_out=False)
#     posts = pagination.items
#     prev = None
#     if pagination.has_prev:
#         prev = url_for('api.get_user_posts', id=id, page=page-1,
#                        _external=True)
#     next = None
#     if pagination.has_next:
#         next = url_for('api.get_user_posts', id=id, page=page+1,
#                        _external=True)
#     return jsonify({
#         'posts': [post.to_json() for post in posts],
#         'prev': prev,
#         'next': next,
#         'count': pagination.total
#     })


# @api.route('/users/<int:id>/timeline/')
# def get_user_followed_posts(id):
#     user = User.query.get_or_404(id)
#     page = request.args.get('page', 1, type=int)
#     pagination = user.followed_posts.order_by(Post.timestamp.desc()).paginate(
#         page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
#         error_out=False)
#     posts = pagination.items
#     prev = None
#     if pagination.has_prev:
#         prev = url_for('api.get_user_followed_posts', id=id, page=page-1,
#                        _external=True)
#     next = None
#     if pagination.has_next:
#         next = url_for('api.get_user_followed_posts', id=id, page=page+1,
#                        _external=True)
#     return jsonify({
#         'posts': [post.to_json() for post in posts],
#         'prev': prev,
#         'next': next,
#         'count': pagination.total
#     })
