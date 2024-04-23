from flask import Flask, render_template, jsonify, request, flash, redirect, sessions
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from funciones import *
from sqlalchemy.sql import text
import uuid
import requests

app = Flask(__name__)


# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#api url
#api_url='http://127.0.0.1:5000/api'
api_url='http://localhost:3030/api/v1/'


@app.route("/", methods=["GET"])
@login_required
def index():
    if session["rol"] == 'cliente':
        lista_propiedades = []
        data = requests.get(api_url+'propiedadesRoutes/')

        if data.status_code == 200:
                dataJSON=data.json()
                propiedades = dataJSON["data"]

                for prop in propiedades:
                            ubicacionData = requests.get(api_url+'ubicacionRoutes/'+prop["ubicacion_id"])
                            ubicacion=ubicacionData.json()
                            ubicacion=ubicacion["data"]
                          
                            lista_propiedades.append([
                                prop["_id"],
                                prop["ubicacion_id"],
                                prop["propietarios"][0],
                                prop["descripcion"],
                                prop["capacidad"],
                                prop["precio_por_noche"],
                                prop["cantidad_banos"],
                                prop["img"],
                                ubicacion["pais"],
                                ubicacion["provincia_estado"],
                                ubicacion["direccion"],
                                ubicacion["detalle"]
                            ])
        return render_template("index.html", username=session["username"],propiedades=lista_propiedades )
    else:
        return redirect("/reservaciones")
    

@app.route("/reservaciones", methods=["GET"])
@login_required
def reservaciones():
    lista_res = []
    data = requests.get(api_url+'reservacionRoutes/')
    
    if data.status_code == 200:
            dataJSON=data.json()
            reservaciones = dataJSON["data"]
            for res in reservaciones:
                prop = requests.get(api_url+'propiedadesRoutes/'+res["propiedades"]["id"])
                if prop.status_code == 200:
                    dataprop=prop.json()
                    propiedad=dataprop["data"]
                    
                    lista_res.append([res["_id"],res["cliente"]["id"],
                                                propiedad["descripcion"],res["fecha_ingreso"],
                                                res["fecha_salida"],limpiarString(str(res["numero_huspedes"])),
                                                res["estado_reserva"]])

    return render_template("Reservaciones.html", reservaciones=lista_res)

@app.route("/misReservaciones", methods=["GET","POST"])
@login_required
def misReservaciones():
    lista_reservas = []

    data = requests.get(api_url+'reservacionRoutes/cliente/'+session["id_cliente"])

    if data.status_code == 200:
            dataJSON=data.json()
            reservas = dataJSON["data"]

            for res in reservas:
                lista_reservas.append([res["_id"],res["fecha_ingreso"],
                                                res["fecha_salida"],limpiarString(str(res["numero_huspedes"])),
                                                res["estado_reserva"]])
                    
    return render_template("misReservaciones.html",reservas=lista_reservas)

@app.route("/clientes", methods=["GET","POST"])
@login_required
def clientes():
    if request.method == "POST":
        data = {"nombres" : request.form.get("nombres"),
        "apellidos" : request.form.get("apellidos"),
        "usuario" : request.form.get("usuario"),
        "clave" : request.form.get("clave"),
        "estado" : 1,
        "rol" : request.form.get("rol")}
        
        #consulta api
        data = requests.post(api_url+'clientesRoutes/',json=data)

        
        if data.status_code != 200:
            flash("error")
            return redirect("/clientes")
        else:
            flash('¡Cuenta creada exitosamente!')
            # Redirect user to login page
            return redirect("/clientes")
    else:
        lista_cli = []
        data = requests.get(api_url+'clientesRoutes/')

        if data.status_code == 200:
                dataJSON=data.json()
                clientes = dataJSON["data"]

                for res in clientes:
                    lista_cli.append([res["_id"],res["nombres"],
                                                res["apellidos"],res["usuario"],
                                                res["clave"],res["estado"],
                                                res["rol"]])
                    
        return render_template("clientes.html", clientes=lista_cli)
    
@app.route("/propiedades", methods=["GET","POST"])
@login_required
def propiedades():

    if request.method == "POST":
        #ubicacion
        UbicacionData = {
            "pais" : request.form.get("pais"),
            "provincia_estado" : request.form.get("provincia"),
            "direccion" : request.form.get("direccion"),
            "detalle" : request.form.get("detalle"),
        }

        Ubicacion = requests.post(api_url+'ubicacionRoutes/',json=UbicacionData)
        Ubicacion=Ubicacion.json()
        Ubicacion=Ubicacion["data"]

        #amenidad
        amenidadObj = {
            "piscina": request.form.get("piscina"),
            "jacuzzi": request.form.get("jacuzzi"),
            "wifi": request.form.get("wifi"),
            "estacionamiento_garaje": request.form.get("estacionamiento_garaje"),
            "aire_acondicionado": request.form.get("aire_acondicionado"),
            "calefaccion": request.form.get("calefaccion"),
            "agua": request.form.get("agua"),
            "tv_por_cable": request.form.get("tv_por_cable"),
            "lavanderia": request.form.get("lavanderia"),
            "gimnasio": request.form.get("gimnasio"),
            "sauna": request.form.get("sauna"),
            "cocina_totalmente_equipada": request.form.get("cocina_totalmente_equipada"),
            "vista_panoramica": request.form.get("vista_panoramica"),
            "acceso_privado_playa": request.form.get("acceso_privado_playa"),
            "servicio_limpieza": request.form.get("servicio_limpieza"),
            "consejeria_24_horas": request.form.get("consejeria_24_horas"),
            "restaurante_bar_establecimiento": request.form.get("restaurante_bar_establecimiento"),
            "servicio_habitacion": request.form.get("servicio_habitacion"),
            "canchas": request.form.get("canchas"),
            "campos_deportivos": request.form.get("campos_deportivos"),
            "salon_de_juegos": request.form.get("salon_de_juegos")
            
        }

        amenidadData = requests.post(api_url+'amenidadesRoutes/',json=amenidadObj)
        amenidades=amenidadData.json()
        amenidades=amenidades["data"]


        #propiedad
        data = {
            "ubicacion_id" : Ubicacion,
            "propietarios" : request.form.get("propietario"),
            "descripcion" : request.form.get("descripcion"),
            "capacidad" : request.form.get("capacidad"),
            "precio_por_noche" : request.form.get("precio"),
            "cantidad_banos" : request.form.get("banos"),
            "img" : request.form.get("img"),
            "amenidad_id": amenidades
        }
        
        #consulta api
        data = requests.post(api_url+'propiedadesRoutes/',json=data)

        return redirect("/propiedades")
    else:     
        lista_propiedades = []
        lista_ubicaciones = []

        data = requests.get(api_url+'propiedadesRoutes/')

        if data.status_code == 200:
                dataJSON=data.json()
                propiedades = dataJSON["data"]
                #ubicaciones
                ubicacionData = requests.get(api_url+'ubicacionRoutes/')
                ubicaciones=ubicacionData.json()
                ubicaciones=ubicaciones["data"]

                for u in ubicaciones:
                            lista_ubicaciones.append([
                                u["_id"],
                                u["pais"],
                                u["provincia_estado"],
                                u["direccion"],
                                u["detalle"]
                            ])

                for prop in propiedades:
                            lista_propiedades.append([
                                prop["_id"],
                                prop["ubicacion_id"],
                                prop["propietarios"][0],
                                prop["descripcion"],
                                prop["capacidad"],
                                prop["precio_por_noche"],
                                prop["cantidad_banos"],
                                prop["img"]
                            ])
                    
        return render_template("propiedades.html", propiedades=lista_propiedades,ubicaciones=lista_ubicaciones)

@app.route("/propiedadesDetalle/<id>", methods=["GET","POST"])
@login_required
def propiedadesDetalle(id):
    data = requests.get(api_url+'propiedadesRoutes/'+id)
    if data.status_code == 200:
            dataJSON=data.json()
            propiedades = dataJSON["data"]
            #Ubicaciones
            ubicacionData = requests.get(api_url+'ubicacionRoutes/'+propiedades["ubicacion_id"])
            ubicacion=ubicacionData.json()
            ubicacion=ubicacion["data"]
            #amenidades
            amenidadData = requests.get(api_url+'amenidadesRoutes/'+propiedades["amenidad_id"])
            amenidad=amenidadData.json()
            amenidad=amenidad["data"]
            #objeto respuesta
            objetoPropiedad = [
                            propiedades["_id"],
                            ubicacion["pais"],
                            ubicacion["provincia_estado"],
                            ubicacion["direccion"],
                            ubicacion["detalle"],
                            propiedades["propietarios"][0],
                            propiedades["descripcion"],
                            propiedades["capacidad"],
                            propiedades["precio_por_noche"],
                            propiedades["cantidad_banos"],
                            propiedades["img"]
            ]

            amenidad = [
                    amenidad["piscina"],
                    amenidad["jacuzzi"],
                    amenidad["wifi"],
                    amenidad["estacionamiento_garaje"],
                    amenidad["aire_acondicionado"],
                    amenidad["calefaccion"],
                    amenidad["agua"],
                    amenidad["tv_por_cable"],
                    amenidad["lavanderia"],
                    amenidad["gimnasio"],
                    amenidad["sauna"],
                    amenidad["cocina_totalmente_equipada"],
                    amenidad["vista_panoramica"],
                    amenidad["acceso_privado_playa"],
                    amenidad["servicio_limpieza"],
                    amenidad["consejeria_24_horas"],
                    amenidad["restaurante_bar_establecimiento"],
                    amenidad["servicio_habitacion"],
                    amenidad["actividades_recreacionales"]["canchas"],
                    amenidad["actividades_recreacionales"]["campos_deportivos"],
                    amenidad["actividades_recreacionales"]["salon_de_juegos"]
                ]
                
            return render_template("propiedadDetalle.html", propiedad=objetoPropiedad,amenidad=amenidad)
    else:
        return redirect("/")
    
@app.route("/reservar/<id>", methods=["POST","GET"])
@login_required
def reservar(id):
        dataprop = requests.get(api_url+'propiedadesRoutes/'+id)
        dataJSON=dataprop.json()
        propiedad = dataJSON["data"]

        data = {
        "cliente" :session["id_cliente"],
        "propiedades" : id,
        "fecha_ingreso" : request.form.get("fecha_entrada"),
        "fecha_salida" : request.form.get("fecha_salida"),
        "adultos" : request.form.get("adultos"),
        "ninos" : request.form.get("ninos"),
        "bebes" : request.form.get("bebes"),
        "mascotas" : request.form.get("mascotas"),
        "estado_reserva" : "confirmada",
        "monto_pago":propiedad["precio_por_noche"],
        "numero_tarjeta":request.form.get("card-number")
        }
        
        #consulta api
        data = requests.post(api_url+'reservacionRoutes/',json=data)
        return redirect("/misReservaciones")

@app.route("/ReservaDetalle/<id>", methods=["GET","POST"])
@login_required
def resDetalle(id):
    reservacionData = requests.get(api_url+'reservacionRoutes/'+id)
    reservacion = reservacionData.json()
    reservacion = reservacion["data"]

    #cliente
    clienteData = requests.get(api_url+'clientesRoutes/cliente/'+reservacion["cliente"]["id"])
    cliente = clienteData.json()
    cliente = cliente["data"]

    reserva = [
         reservacion["_id"],
         cliente["nombres"]+" "+cliente["apellidos"],
         reservacion["fecha_ingreso"],
         reservacion["fecha_salida"],
         limpiarString(str(reservacion["numero_huspedes"]))

    ]
    
    data = requests.get(api_url+'propiedadesRoutes/'+reservacion["propiedades"]["id"])
    if data.status_code == 200:
            dataJSON=data.json()
            propiedades = dataJSON["data"]
            ubicacionData = requests.get(api_url+'ubicacionRoutes/'+propiedades["ubicacion_id"])
            ubicacion=ubicacionData.json()
            ubicacion=ubicacion["data"]
            objetoPropiedad = [
                            propiedades["_id"],
                            ubicacion["pais"],
                            ubicacion["provincia_estado"],
                            ubicacion["direccion"],
                            ubicacion["detalle"],
                            propiedades["propietarios"],
                            propiedades["descripcion"],
                            propiedades["capacidad"],
                            propiedades["precio_por_noche"],
                            propiedades["cantidad_banos"],
                            propiedades["img"]
            ]

            #pagos
            pagoData = requests.get(api_url+'pagosRoutes/'+id)
            pago = pagoData.json()
            pago = pago["data"]
            numeroTrj = pago["numero_tarjeta"]

            pagoObj = [
                pago["_id"],
                pago["metodo_pago"],
                pago["monto_pagado"],
                pago["estado_pago"],
                pago["fecha_pago"],
                numeroTrj[-4:]
            ]
                
            return render_template("detalleReservaAdmin.html", propiedad=objetoPropiedad,reserva=reserva, pago=pagoObj)
    else:
        return redirect("/")

@app.route("/reservaDetalle/<id>", methods=["GET","POST"])
@login_required
def reservaDetalle(id):
    reservacionData = requests.get(api_url+'reservacionRoutes/'+id)
    reservacion = reservacionData.json()
    reservacion = reservacion["data"]

    reserva = [
         reservacion["_id"],
         reservacion["cliente"]["id"],
         reservacion["fecha_ingreso"],
         reservacion["fecha_salida"],
         limpiarString(str(reservacion["numero_huspedes"]))

    ]
    
    data = requests.get(api_url+'propiedadesRoutes/'+reservacion["propiedades"]["id"])
    if data.status_code == 200:
            dataJSON=data.json()
            propiedades = dataJSON["data"]
            ubicacionData = requests.get(api_url+'ubicacionRoutes/'+propiedades["ubicacion_id"])
            ubicacion=ubicacionData.json()
            ubicacion=ubicacion["data"]
            objetoPropiedad = [
                            propiedades["_id"],
                            ubicacion["pais"],
                            ubicacion["provincia_estado"],
                            ubicacion["direccion"],
                            ubicacion["detalle"],
                            propiedades["propietarios"],
                            propiedades["descripcion"],
                            propiedades["capacidad"],
                            propiedades["precio_por_noche"],
                            propiedades["cantidad_banos"],
                            propiedades["img"]
            ]

            #pagos
            pagoData = requests.get(api_url+'pagosRoutes/'+id)
            pago = pagoData.json()
            pago = pago["data"]
            numeroTrj = pago["numero_tarjeta"]

            pagoObj = [
                pago["_id"],
                pago["metodo_pago"],
                pago["monto_pagado"],
                pago["estado_pago"],
                pago["fecha_pago"],
                numeroTrj[-4:]
            ]
                
            return render_template("detalleReserva.html", propiedad=objetoPropiedad,reserva=reserva, pago=pagoObj)
    else:
        return redirect("/")
    
@app.route("/deleteReserva/<id>", methods=["DELETE","GET"])
@login_required
def deleteReserva(id):
     data = {"id":id}
     res = requests.put(api_url+'reservacionRoutes/'+id, json=data)    
     return redirect("/")

@app.route("/deleteCliente/<id>", methods=["DELETE","GET"])
@login_required
def deleteCliente(id):
     data = {"id":id}
     res = requests.put(api_url+'clientesRoutes/'+id, json=data)   
     return redirect("/clientes")

@app.route("/deletePropiedad/<id>", methods=["DELETE","GET"])
@login_required
def deletePropiedad(id):
     data = {"id":id}
     res = requests.delete(api_url+'propiedadesRoutes/'+id)   
     return redirect("/propiedades")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not request.form.get("username"):
            flash('Ingrese un nombre de usuario')
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash('Ingrese una contraseña')
            return redirect("/login")
        
        #consulta api
        data = requests.get(api_url+'clientesRoutes/'+username)

        if data.status_code == 200:
            #jsonserializable
            user=data.json()
            user=user["data"]

            # Ensure username exists and password is correct
            if len(user) != 1 and (user['clave'] == password) and (user['estado'] == 1):
                session["username"] = username
                session["rol"] = user['rol']
                session["id_cliente"] = user['_id']

                return redirect('/')
            else:
                flash('usuario o contraseña incorrectos')
                return redirect('/login')
    else:
        return render_template("login.html")
    
@app.route("/registrarme", methods=["POST", "GET"])
def registrarme():
    if request.method == "POST":
        data = {"nombres" : request.form.get("nombres"),
        "apellidos" : request.form.get("apellidos"),
        "usuario" : request.form.get("usuario"),
        "clave" : request.form.get("clave"),
        "estado" : 1,
        "rol" : "cliente"}
        
        #consulta api
        data = requests.post(api_url+'clientesRoutes/',json=data)

        
        if data.status_code != 200:
            flash("error")
            return redirect("/login")
        else:
            flash('¡Cuenta creada exitosamente!')
    return render_template("registroUsuario.html")

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
