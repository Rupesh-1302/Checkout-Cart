from chalice import Chalice, Response
from DatabaseTasks.main import Product, Cart, Session, User, engine
from hashlib import sha256

app = Chalice(app_name='checkout_cart')

local_session = Session(bind=engine)


@app.route('/')
def index():
    return {'hello': 'world'}


#  Making a POST request to register a new user
@app.route('/register', methods=['POST'])
def register():
    """ Register a new user """
    try:
        # Taking the data from the request
        data = app.current_request.json_body
        user_name = data['user_name']
        full_name = data['full_name']
        password = data['password']

        #  Checking if password is strong enough
        if(len(password) < 8):
            return Response(
                body={
                    "Type": "Error",
                    "Message": "Password must be atleast 8 characters long"
                },
                status_code=400,
            )

        # Checking if user name is already taken
        users = local_session.query(User).all()
        for user in users:
            if(user.user_name == user_name):
                return Response(
                    body={
                        "Type": "Error",
                        "Message": "User already exists"
                    },
                    status_code=400,
                )

        #  Converting the password to hash
        h = sha256()
        h.update(password.encode())
        hash = h.hexdigest()

        # Creating the user
        user_data = User(user_name=user_name,
                         full_name=full_name, password=hash)
        local_session.add(user_data)

        #  Committing the changes
        local_session.commit()

        # Returning the response
        return Response(
            body={
                "Type": "Success",
                "Message": "User registered successfully",
            },
            status_code=201,
        )

    #  Handling the error
    except Exception as e:
        return Response(
            body={
                "Type": "Error",
                "Message": "Something went wrong, please try again.",
                "Error": str(e),
            },
            status_code=400,
        )


# Making a POST request to login a user
@app.route('/login', methods=['POST'])
def login():
    """ Login a user """
    try:
        # Taking the data from the request
        data = app.current_request.json_body
        user_name = data['user_name']
        password = data['password']
        isUser = False

        # Checking if user name is registered
        users = local_session.query(User).all()
        for user in users:
            if(user.user_name == user_name):
                old_password = user.password
                isUser = True

        # If user name is not registered return error
        if not isUser:
            return Response(
                body={
                    "Type": "Error",
                    "Message": "User not registered",
                },
                status_code=400,
            )

        #  Converting the password to hash
        h = sha256()
        h.update(password.encode())
        hash = h.hexdigest()

        # Checking if password is correct
        if(old_password != hash):
            return Response(
                body={
                    "Type": "Error",
                    "Message": "Password is incorrect",
                },
                status_code=400,
            )

        return Response(
            body={
                "Type": "Success",
                "Message": "User logged in successfully",
            },
            status_code=200,
        )

    # Handling the error
    except Exception as e:
        return Response(
            body={
                "Type": "Error",
                "Message": "Something went wrong, please try again.",
                "Error": str(e),
            },
            status_code=400,
        )


# route for handling Cart Addition and Deletion


@app.route('/api/cart', methods=['POST', 'DELETE'], cors=True)
def handle_cart():
    request = app.current_request
    data = request.json_body
    user_id = data["userId"] if "userId" in data else None
    product_id = data["productId"] if "productId" in data else None
    quantity = 1
    local_session = Session(bind=engine)
    if 'quantity' in data:
        quantity = data["quantity"]
    if not user_id or not product_id:
        return Response(status_code=403, body={"message": "Invalid Request"})

    if request.method == 'POST':
        # Handling adding to cart
        try:
            newCartItem = Cart(
                userId=user_id, productId=product_id, quantity=quantity)
            local_session.add(newCartItem)
            local_session.commit()
            return Response(status_code=200, body={"message": "Item added to cart successfully"})
        except Exception as e:
            print(e)
            return Response(status_code=400, body={"message": "Something went Wrong"})
    else:
        # Handling Deletion from cart
        try:
            cartItem = local_session.query(Cart).filter(
                Cart.userId == user_id).filter(Cart.productId == product_id).first()
            local_session.delete(cartItem)
            local_session.commit()
            return Response(status_code=200, body={"message": "Item deleted from cart successfully"})
        except Exception as e:
            print(e)
            return Response(status_code=400, body={"message": "Something went Wrong"})


#  Driver code
if "__name__" == "__main__":
    app.run(debug=True)
