import flask
from flask import *
import logging
import psycopg2
from datetime import *

app = flask.Flask(__name__)

StatusCodes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500
}

global listaToken
numeroIndice = 0


def db_connection():
    db = psycopg2.connect(
        user='postgres',
        password='postgres',
        host='localhost',
        port='5432',
        database='postgres'
    )

    return db


@app.route('/')
def landingpage():
    return


@app.route('/dbproj/user/', methods=['POST'])
def registarUtilizador():
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'POST /dbproj/user - payload: {payload}')

    if 'Nome' not in payload or 'Password' not in payload or 'Permissoes' not in payload or 'ID' not in payload or 'Email' not in payload or 'Morada' not in payload or 'NIF' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'Payload incorreto'}
        return flask.jsonify(response)
    else:
        statement = 'INSERT INTO utilizador (Nome, Permissoes, ID, Password, Email) VALUES (%s, %s, %s, %s, %s);'
        values = (payload['Nome'], payload['Permissoes'], payload['ID'], payload['Password'], payload['Email'])
        cur.execute(statement, values)

    if payload['Permissoes'] == 'Administrador':
        if 'Nome' in payload:
            statement1 = 'INSERT INTO administrador (Nome, utilizador_id) VALUES (%s, %s);'
            cur.execute(statement1, (payload['Nome'], int(payload['ID'])))
        else:
            response = {'status': StatusCodes['api_error'], 'results': 'Payload incorreto'}
            return flask.jsonify(response)

    elif payload['Permissoes'] == 'Comprador':
        if 'Nome' in payload and 'Morada' in payload and 'NIF':
            statement1 = 'INSERT INTO comprador (Nome,Morada, NIF, utilizador_id) VALUES (%s, %s,  %s, %s);'
            values1 = (payload['Nome'], payload['Morada'], int(payload['NIF']), int(payload['ID']))
            cur.execute(statement1, values1)
        else:
            response = {'status': StatusCodes['api_error'], 'results': 'Payload incorreto'}
            return flask.jsonify(response)

    elif payload['Permissoes'] == 'Vendedor':
        if 'Nome' in payload and 'NIF' in payload and 'Morada' in payload:
            statement1 = 'INSERT INTO vendedor (Nome, NIF, Morada, utilizador_id) VALUES (%s,  %s, %s, %s);'
            values1 = (payload['Nome'], int(payload['NIF']), payload['Morada'], int(payload['ID']))
            cur.execute(statement1, values1)
        else:
            response = {'status': StatusCodes['api_error'], 'results': 'Payload incorreto'}
            return flask.jsonify(response)
    else:
        response = {'status': StatusCodes['api_error'], 'results': 'Payload incorreto'}
        return flask.jsonify(response)

    try:
        conn.commit()
        response = {'status': StatusCodes['success'], 'results': f'UTILIZADOR INSERIDO {payload["Nome"]}'}
        global numeroIndice
        numeroIndice += 1

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /dbproj/user - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()
    return flask.jsonify(response)


@app.route('/dbproj/user/', methods=['PUT'])
def loginUtilizador():
    global listaToken
    logger.info('PUT /dbproj/user')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'PUT /dbproj/user - payload: {payload}')

    if 'Username' not in payload or 'Password' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'Payload incorreto'}
        return flask.jsonify(response)
    else:
        try:
            username = payload['Username']
            password = payload['Password']
            querie = 'SELECT ID FROM Utilizador WHERE Nome = %s and Password = %s;'
            values = (username, password)
            cur.execute(querie, values)
            rows = cur.fetchall()
            if len(rows) == 0:
                print("UTILIZADOR NÃO EXISTE")
                response = {'status': StatusCodes['api_error'], 'results': 'utilizador não existe ou password errada'}
                return flask.jsonify(response)
            else:
                listaToken = rows[0][0]

                response = {'status': StatusCodes['success'], 'results': (rows[0][0], listaToken)}
            conn.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f'PUT /dbproj/user - error: {error}')
            response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
            # an error occurred, rollback
            conn.rollback()

        finally:
            if conn is not None:
                conn.close()

    return flask.jsonify(response)


@app.route('/dbproj/product/', methods=['POST'])
def criarProduto():
    global listaToken
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'POST /dbproj/product - payload: {payload}')
    cur.execute('SELECT Permissoes FROM Utilizador WHERE ID = %s;', (listaToken,))
    rows = cur.fetchall()
    print(rows)
    if rows[0][0] != 'Vendedor':
        response = {'status': StatusCodes['api_error'], 'results': 'Sem premissoes'}
        return flask.jsonify(response)
    else:
        if 'IDProduto' not in payload or 'Stock' not in payload or 'Empresa' not in payload or 'Nome' not in payload or 'Preco' not in payload or 'tipo' not in payload:
            response = {'status': StatusCodes['api_error'], 'results': 'Payload incorreto INICIAL'}
            return flask.jsonify(response)

        if payload['tipo'] == 'Computador':
            if 'Processador' not in payload or 'RAM' not in payload or 'Disco' not in payload or 'Refrigeracao' not in payload or 'tipo' not in payload:
                print("ERRO INICIAL NO PAYLOAD")
                response = {'status': StatusCodes['api_error'], 'results': 'Payload incorreto INICIAL'}
                return flask.jsonify(response)
            else:
                statement1 = 'INSERT INTO Computador (Processador,RAM,Disco,Refrigeracao,produtos_idproduto) VALUES (%s, %s, %s, %s, %s);'
                values1 = (
                    payload['Processador'], payload['RAM'], payload['Disco'], payload['Refrigeracao'],
                    payload['IDProduto'])
        elif payload['tipo'] == 'Televisao':
            if 'Modelo' in payload and 'Marca' in payload and 'Ecra' in payload:
                statement1 = 'INSERT INTO Televisao (Modelo, Marca, Ecra,produtos_idproduto) VALUES (%s, %s, %s,%s);'
                values1 = (
                    payload['Modelo'], payload['Marca'], payload['Ecra'], payload['IDProduto'])
            else:
                response = {'status': StatusCodes['api_error'], 'results': 'Payload incorreto TV'}
                return flask.jsonify(response)

        elif payload['tipo'] == 'Smartphone':
            if 'Modelo' in payload and 'Marca' in payload and 'Ecra' in payload and 'Processador' in payload:
                statement1 = 'INSERT INTO Smartphone (Modelo, Marca, Ecra,Processador,produtos_idproduto) VALUES (%s, %s, %s, %s,%s);'
                values1 = (
                    payload['Modelo'], payload['Marca'], payload['Ecra'],
                    payload['Processador'], payload['IDProduto'])
            else:
                response = {'status': StatusCodes['api_error'], 'results': 'Payload incorreto SP'}
                return flask.jsonify(response)
        else:
            response = {'status': StatusCodes['api_error'], 'results': 'Payload incorreto'}
            return flask.jsonify(response)
        statement = 'INSERT INTO Produtos (IDProduto,Stock,Empresa,Nome,Preco,tipo) VALUES (%s, %s, %s, %s, %s, %s);'
        values = (
            payload['IDProduto'], payload['Stock'], payload['Empresa'], payload['Nome'], payload['Preco'],
            payload['tipo'])

    try:
        cur.execute('BEGIN TRANSACTION;')
        cur.execute(statement, values)
        cur.execute(statement1, values1)

        # commit the transaction
        conn.commit()
        response = {'status': StatusCodes['success'], 'results': f'PRODUTO CRIADO {payload["IDProduto"]}'}
        global numeroIndice

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /dbproj/products - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


@app.route('/dbproj/product/update/{product_id}', methods=['PUT'])
def atualizaProdutos():
    logger.info('PUT /dbproj/product/update/{product_id}')

    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    product_id = request.args.get('{product_id}')
    logger.debug(f'PUT /dbproj/products/update/{product_id} - payload: {payload}')
    cur.execute('SELECT Permissoes FROM Utilizador WHERE ID = %s;', (listaToken,))
    row2 = cur.fetchall()
    cur.execute('SELECT Empresa FROM Produtos WHERE idproduto = %s;', (product_id,))
    row3 = cur.fetchall()
    cur.execute('SELECT utilizador_id FROM Vendedor WHERE nome = %s;', (row3[0],))
    row4 = cur.fetchall()
    if row2[0][0] != 'Vendedor' or row4[0][0] != listaToken:
        response = {'status': StatusCodes['api_error'], 'results': 'Sem premissoes'}
        return flask.jsonify(response)
    else:
        if 'Stock' in payload:
            Stock = payload['Stock']
            cur.execute('SELECT idproduto,preco,stock,nome FROM Produtos WHERE idproduto = %s', (product_id,))
            aux = cur.fetchall()
            print(aux)
            cur.execute('INSERT INTO historicoproduto (idproduto, preco,stock,nome) VALUES(%s,%s,%s,%s)', aux[0])
            statement1 = 'UPDATE Produtos SET Stock = %s WHERE idproduto = %s;'
            values = (Stock, (product_id,))
            cur.execute(statement1, values)
        elif 'Nome' in payload:
            Nome = payload['Nome']
            statement1 = 'UPDATE Produtos SET Nome = %s WHERE idproduto = %s;'
            values = (Nome, product_id)
            cur.execute(statement1, values)
        elif 'Preco' in payload:
            Preco = payload['Preco']
            statement1 = 'UPDATE Produtos SET Preco = %s WHERE idproduto = %s;'
            values = (Preco, product_id)
            cur.execute(statement1, values)
        elif 'Cupao' in payload:
            Cupao = payload['Cupao']
            statement1 = 'UPDATE Produtos SET Cupao = %s WHERE idproduto = %s;'
            values = (Cupao, product_id)
            cur.execute(statement1, values)
        elif 'Descricao' in payload:
            Descricao = payload['Descricao']
            statement1 = 'UPDATE Produtos SET Descricao = %s WHERE idproduto = %s;'
            values = (Descricao, product_id)
            cur.execute(statement1, values)

        else:
            response = {'status': StatusCodes['api_error'], 'results': 'Payload incorreto'}
            return flask.jsonify(response)

    try:
        # commit the transaction
        conn.commit()
        response = {'status': StatusCodes['success'], 'results': f'Produto atualizado {payload["Stock"]}'}


    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'PUT /dbproj/products - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


@app.route('/dbproj/order/', methods=['POST'])
def Compra():
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'POST /dbproj/order - payload: {payload}')

    token = request.args.get('token')
    cur.execute('SELECT Nome FROM utilizador WHERE ID = %s;', [token])
    cur.execute('SELECT Permissoes FROM utilizador WHERE ID = %s;', (listaToken,))
    row3 = cur.fetchall()
    if row3[0][0] != 'Comprador':
        response = {'status': StatusCodes['api_error'], 'results': 'Sem premissoes'}
        return flask.jsonify(response)
    else:
        if 'cart' not in payload or 'Cupao' not in payload:
            print("ERRO INICIAL NO PAYLOAD")
            response = {'status': StatusCodes['api_error'], 'results': 'Payload incorreto INICIAL'}
            return flask.jsonify(response)
        else:
            preco = 0
            statement1 = 0
            for i in payload['cart']:
                id = i[0]
                quantidade = i[1]
                cur.execute('SELECT Stock FROM Produtos WHERE IDProduto = %s;', (id,))
                aux = cur.fetchall()
                print(aux)
                if aux[0][0] > quantidade:
                    statement1 = 'UPDATE Produtos SET Stock = %s WHERE IDProduto = %s;'
                    cur.execute('SELECT Stock FROM Produtos WHERE IDProduto = %s;', (id,))
                    aux = cur.fetchall()
                    values = (aux[0][0] - quantidade, id)
                    cur.execute(statement1, values)
                    cur.execute('SELECT Preco FROM Produtos WHERE IDProduto = %s;', (id,))
                    aux = cur.fetchall()
                    preco += aux[0][0] * quantidade
                    cur.execute('SELECT IDCupao FROM Cupoes WHERE IDUtilizador = %s;', (listaToken,))
                    aux = cur.fetchall()
                    if aux != None and aux == payload['Cupao']:
                        cur.execute('SELECT ValorDesconto FROM Campanha WHERE ID = %s;', aux)
                        aux = cur.fetchall()
                        preco = preco * aux[0][0]
                else:
                    response = {'status': StatusCodes['internal_error'], 'results': 'Stock not suficient'}
                    return flask.jsonify(response)
        statement = 'INSERT INTO Compras (ID,IDComprador,IDCupao,Data, valortotal) VALUES (%s, %s, %s, %s, %s);'
        get_id_statement = 'SELECT max(ID) FROM Compras;'
        cur.execute(get_id_statement)
        last_id = cur.fetchone()
        if last_id[0] is None:
            last_id = (1,)
        now = datetime.now()
        values = (((last_id[0] + 1),), (listaToken,), payload['Cupao'], now.strftime("%Y-%m-%d %H:%M:%S"), preco)
        cur.execute(statement, values)
        for i in payload['cart']:
            id = i[0]
            statement2 = 'INSERT INTO HistoricoCompras (IDCompra, IDProduto) VALUES (%s, %s);'
            values2 = (last_id[0] + 1, id)
            cur.execute(statement2, values2)

    try:
        # commit the transaction
        conn.commit()
        response = {'status': StatusCodes['success'], 'results': f' COMPRA EFETUADA {last_id[0] + 1}'}


    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /dbproj/order - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


@app.route('/dbproj/rating/{product_id}', methods=['POST'])
def raiting_feedback():
    product_id = request.args.get('{product_id}')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'POST /dbproj/rating/{product_id} - payload: {payload}')

    cur.execute('SELECT Permissoes FROM Utilizador WHERE ID = %s;', (listaToken,))
    row3 = cur.fetchall()
    if row3[0][0] != 'Comprador':
        response = {'status': StatusCodes['api_error'], 'results': 'Sem premissoes'}
        return flask.jsonify(response)
    else:
        if 'raiting' not in payload or 'feedback' not in payload:
            print("ERRO INICIAL NO PAYLOAD")
            response = {'status': StatusCodes['api_error'], 'results': 'Payload incorreto INICIAL'}
            return flask.jsonify(response)
        else:
            if payload['raiting'] > 5 or payload['raiting'] < 0:
                response = {'status': StatusCodes['api_error'], 'results': 'Rating invalido'}
                return flask.jsonify(response)
            else:
                statement = 'UPDATE Produtos SET Classificacao = %s WHERE IDProduto = %s;'
                cur.execute('SELECT Classificacao FROM Produtos WHERE idproduto = %s;', (product_id,))
                aux = cur.fetchall()
                if aux[0][0] == None:
                    aux = 2.5
                else:
                    aux = aux[0][0]
                aux1 = aux + payload['raiting']
                aux1 = aux1 / 2
                values = ((aux,), (product_id,))
                cur.execute(statement, values)
                statement1 = 'INSERT INTO Comentario (idcomentario,idanterior,mensagem) VALUES (%s,%s, %s);'
                get_id_statement = 'SELECT max(idcomentario) FROM Comentario;'
                cur.execute(get_id_statement)
                last_id = cur.fetchone()
                if last_id[0] is None:
                    last_id = (0,)
                values1 = ((last_id[0] + 1,), last_id, payload['feedback'])
                cur.execute(statement1, values1)
    try:
        # commit the transaction
        conn.commit()
        response = {'status': StatusCodes['success'], 'results': f'FEEDBACK INSSERIDO {product_id}'}


    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /dbproj/rating - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


@app.route('/dbproj/product/{product_id}', methods=['GET'])
def consulta_produtos():
    product_id = request.args.get('{product_id}')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'GET /dbproj/product{product_id} - payload: {payload}')
    try:
        cur.execute('SELECT * from Produtos WHERE idproduto=%s;', (product_id,))
        print(product_id)
        rows = cur.fetchall()
        print(rows)
        if len(rows) < 1:
            conn.commit()
            response = {'status': StatusCodes['api_error'], 'results': 'Produto não encontrado'}
        else:
            response = {'status': StatusCodes['success'], 'results': rows}


    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /dbproj/product - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


@app.route('/dbproj/campaign/{admin_id}', methods=['POST'])
def criar_capanha():
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'POST /dbproj/campaign - payload: {payload}')

    admin_id = request.args.get('admin_id')
    cur.execute('SELECT Permissoes FROM Utilizador WHERE id = %s;', (admin_id,))
    aux = cur.fetchall()
    if aux[0][0] != "Administrador":
        response = {'status': StatusCodes['api_error'], 'results': 'Utilizador não tem permissões'}
        return flask.jsonify(response)
    if 'data_inicio' not in payload or 'data_fim' not in payload or 'valordesconto' not in payload or 'numcupoes' not in payload or 'descricao' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'Error in payload'}
    else:
        try:
            max_data = cur.execute('SELECT max(data_fim) FROM campanha;')
            now = datetime.now()
            if max_data == None:
                max_data = now
            if max_data > now:
                response = {'status': StatusCodes['api_error'], 'results': 'Já existe uma campanha ativa'}
                return flask.jsonify(response)

            else:
                get_id_statement = 'SELECT max(ID) FROM Campanha;'
                cur.execute(get_id_statement)
                last_id = cur.fetchone()
                if last_id[0] is None:
                    last_id = 0
                    statement = 'INSERT INTO campanha (id ,idadministrador,data_inicio, data_fim, valordesconto,numcupoes,descricao ) VALUES (%s, %s, %s, %s, %s,%s,%s);'
                    values = ((last_id + 1,), (admin_id,), payload['data_inicio'],
                              payload['data_fim'], payload['valordesconto'], payload['numcupoes'], payload['descricao'])
                else:
                    statement = 'INSERT INTO campanha (id ,idadministrador,data_inicio, data_fim, valordesconto,numcupoes,descricao ) VALUES (%s, %s, %s, %s, %s,%s,%s);'
                    values = (last_id[0] + 1, (admin_id,), payload['data_inicio'],
                              payload['data_fim'], payload['valordesconto'], payload['numcupoes'], payload['descricao'])
                cur.execute(statement, values)
                conn.commit()
                response = {'status': StatusCodes['success'], 'results': 'Campanha Criada'}

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f'POST /dbproj/campaign - error: {error}')
            response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
            # an error occurred, rollback
            conn.rollback()


        finally:
            if conn is not None:
                conn.close()

    return flask.jsonify(response)


@app.route('/dbproj/filtros/', methods=['GET'])
def filtros():
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'GET /dbproj/product/filters - payload: {payload}')
    cur.execute('SELECT Permissoes FROM utilizador WHERE ID = %s;', (listaToken,))
    row3 = cur.fetchall()
    if row3[0][0] != "Comprador":
        response = {'status': StatusCodes['api_error'], 'results': 'Sem premissoes'}
        return flask.jsonify(response)
    else:
        try:
            if 'Tipo' in payload:
                Tipo = payload['Tipo']
                if Tipo == "Computador":
                    statement = 'SELECT * from Produtos, Computador WHERE Tipo = %s;'
                elif Tipo == "Televisao":
                    statement = 'SELECT * from Produtos, Televisao WHERE Tipo = %s ;'
                elif Tipo == "SmartPhone":
                    statement = 'SELECT * from Produtos, SmartPhone WHERE Tipo = %s;'
                else:
                    response = {'status': StatusCodes['api_error'], 'results': 'Tipo invalido'}
                    return flask.jsonify(response)
                values = Tipo
                cur.execute(statement, (values,))
                rows = cur.fetchall()
                conn.commit()
                response = {'status': StatusCodes['success'], 'results': rows}
            else:
                response = {'status': StatusCodes['api_error'], 'results': 'Payload errado'}
                return flask.jsonify(response)

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f'GET /dbproj/product/filters - error: {error}')
            response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
            # an error occurred, rollback
            conn.rollback()

        finally:
            if conn is not None:
                conn.close()

    return flask.jsonify(response)


@app.route('/proj/report/year/', methods=['GET'])
def stats():
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()
    logger.debug(f'GET /dbproj/product - payload: {payload}')
    cur.execute("SELECT * FROM Compras WHERE Data >= Data-365;")
    rows = cur.fetchall()
    if len(rows) < 1:
        response = {'status': StatusCodes['api_error'], 'results': 'Erro a obter dados'}
        return flask.jsonify(response)
    else:
        try:
            for i in rows:
                response = {'status': StatusCodes['success'],
                            'results': {"valor total de compras": i[4],
                                        "total de compras feitas": len(rows)}}
                conn.commit()
                flask.jsonify(response)

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f'GET /dbproj/product - error: {error}')
            response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
            conn.rollback()

        finally:
            if conn is not None:
                conn.close()

        return flask.jsonify(response)


@app.route('/dbproj/report/campaign/', methods=['GET'])
def estatisticas_campanha():
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'GET /dbproj/report/campaign - payload: {payload}')
    cur.execute('SELECT Permissoes FROM Utilizador WHERE ID = %s;', (listaToken,))
    row3 = cur.fetchall()
    if row3[0][0] != 'Administrador':
        response = {'status': StatusCodes['api_error'], 'results': 'Sem premissoes'}
        return flask.jsonify(response)
    else:
        try:
            statement = 'SELECT id, descricao, numcupoes, cupoes_usados FROM campanha;'
            cur.execute(statement)
            rows = cur.fetchall()
            response = {'status': StatusCodes['success'], 'results': rows}
            conn.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f'GET /dbproj/report/campaigns/ - error: {error}')
            response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
            # an error occurred, rollback
            conn.rollback()

        finally:
            if conn is not None:
                conn.close()

    return flask.jsonify(response)


@app.route('/dbproj/product/compare', methods=['GET'])
def comparar_produtos():
    payload = flask.request.get_json()

    global listaToken

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'GET /dbproj/product/compare - payload: {payload}')

    prod1 = payload['prod1']
    prod2 = payload['prod2']

    cur.execute('SELECT Permissoes FROM Utilizador WHERE id = %s;', (listaToken,))
    row3 = cur.fetchall()
    try:
        if row3[0][0] != 'Comprador':
            response = {'status': StatusCodes['api_error'], 'results': 'Sem premissoes'}
            return flask.jsonify(response)
        else:
            if 'prod1' not in payload or 'prod2' not in payload:
                response = {'status': StatusCodes['api_error'], 'results': 'ERROR in payload'}
                return flask.jsonify(response)
            else:
                cur.execute('SELECT * FROM Produtos WHERE idproduto = %s;', (prod1,))
                rows1 = cur.fetchall()
                if rows1[0][7] == 'Computador':
                    cur.execute('SELECT * FROM Computador WHERE produtos_idproduto = %s;', (prod1,))
                    rows = cur.fetchall()
                elif rows1[0][7] == 'Televisao':
                    cur.execute('SELECT * FROM Produtos,Televisao WHERE produtos_idproduto = %s;', (prod1,))
                    rows = cur.fetchall()
                elif rows1[0][7] == 'Smartphone':
                    cur.execute('SELECT * FROM Produtos,Smartphone WHERE produtos_idproduto = %s;', (prod1,))
                    rows = cur.fetchall()
                else:
                    response = {'status': StatusCodes['api_error'], 'results': 'Produto não encontrado'}

                cur.execute('SELECT * FROM Produtos WHERE idproduto = %s;', (prod2,))
                rows = cur.fetchall()
                if rows[0][7] == 'Computador':
                    cur.execute('SELECT * FROM Computador WHERE produtos_idproduto = %s;', (prod2,))
                    rows = cur.fetchall()
                elif rows[0][7] == 'Televisao':
                    cur.execute('SELECT * FROM Produtos,Televisao WHERE produtos_idproduto = %s;', (prod2,))
                    rows = cur.fetchall()
                elif rows[0][7] == 'Smartphone':
                    cur.execute('SELECT * FROM Produtos,Smartphone WHERE produtos_idproduto = %s;', (prod2,))
                    rows = cur.fetchall()
                else:
                    response = {'status': StatusCodes['api_error'], 'results': 'Produto não encontrado'}
                response = {'status': ['success'], 'results': [rows, rows1]}
                conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /dbproj/product/compare - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()
    finally:
        if conn is not None:
            conn.close()
    return flask.jsonify(response)


if __name__ == '__main__':
    # set up logging
    logging.basicConfig(filename='log_file.log')
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s', '%H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    host = '127.0.0.1'
    port = 8080
    app.run(host=host, debug=True, threaded=True, port=port)
    logger.info(f'API v1.1 online: http://{host}:{port}')
