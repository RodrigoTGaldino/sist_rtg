from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, text, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
auth = HTTPBasicAuth(app)

Base = declarative_base()


class Produto(Base):
    __tablename__ = "produto"
    id = Column(Integer, primary_key=True)
    produto = Column(String(255))
    quantidade = Column(Integer)
    valor = Column(Float)


user = {
    "rodrigo": generate_password_hash("1234"),
    "arthur": generate_password_hash("56789"),
}


def connect_db():
    try:
        db_uri = "mysql+mysqlconnector://root:arthur@localhost:3306/produtos"
        engine = create_engine(db_uri)
        return engine
    except Exception as e:
        print("Database connection error:", str(e))
        raise


@auth.verify_password
def verify_password(username, password):
    if username in user and check_password_hash(user.get(username), password):
        return username


def create_table():
    engine = connect_db()
    Base.metadata.create_all(engine)


@app.route("/produtos", methods=["GET"])
@auth.login_required
def listar_produtos():
    try:
        engine = connect_db()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM produto"))

            products = []
            for row in result:
                product = {"produto": row[0], "quantidade": row[1], "valor": row[2]}
                products.append(product)
            return jsonify({"products": products}), 200

    except Exception as e:
        print("Database error:", str(e))
        return jsonify({"error": "Database error"}), 500


@app.route("/produtos", methods=["POST"])
@auth.login_required
def adicionar_produto():
    try:
        data = request.json
        if not data or not all(
            key in data for key in ("produto", "quantidade", "valor")
        ):
            return jsonify({"error": "Dados do produto incompletos"}), 400

        produto = Produto(
            produto=data["produto"],
            quantidade=data["quantidade"],
            valor=data["valor"],
        )

        engine = connect_db()
        session_01 = sessionmaker(bind=engine)
        session = session_01()

        session.add(produto)
        session.commit()

        return jsonify({"message": "Produto adicionado com sucesso"}), 201

    except Exception as e:
        print("Database error:", str(e))
        return jsonify({"error": "Erro ao adicionar o produto"}), 500


if __name__ == "__main__":
    create_table()
    app.run(debug=True)
