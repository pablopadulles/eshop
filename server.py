from flask import Flask, render_template, Response, jsonify, request, url_for, redirect, session
# ~ from camera import VideoCamera
from flask_tryton import Tryton
import os
import configparser
import urllib
from urllib.parse import urljoin
from flask_sitemap import Sitemap
from datetime import datetime

app = Flask(__name__)
configfile = os.environ.get('FLASK_CONFIG')
app.secret_key = b'p\xa6]\xda\xbe\xfd\xc4{b\xffk$\xfd\x13\xe8(\x1e\x14\x03p\x03P\x08B@\xec\xe0\xde\xa3S\x03k'

if configfile:
    config = configparser.ConfigParser()
    config.read(configfile)
    app.config['TRYTON_DATABASE'] = config.get('tryton', 'db')
    app.config['TRYTON_CONFIG'] = config.get('tryton', 'trytond-conf')
else:
    app.config['TRYTON_DATABASE'] = 'vidriosfrancisco'
    app.config['TRYTON_CONFIG'] = '/etc/tryton/trytond.conf'

tryton = Tryton(app)
ext = Sitemap(app=app)
User = tryton.pool.get('res.user')
ProductTemplate = tryton.pool.get('product.template')
Product = tryton.pool.get('product.product')
ProductCategory = tryton.pool.get('product.category')

video_camera = None
global_frame = None

@tryton.default_context
def default_context():
    return User.get_preferences(context_only=True)

@app.route('/home')
@app.route('/home.html')
@app.route('/index.html')
@app.route('/', methods=["GET", "POST"])
@tryton.transaction()
def index():
    if request.method == "GET":
        carrito = dict(session)
        total = 0
        for c in carrito:
            total += int(carrito[c]['cantidad']) * int(carrito[c]['precio'])

        pt = Product.search_random([], limit=4)
        return render_template('home.html', product_template=pt, carrito=carrito, len=len(carrito), total=total)


@ext.register_generator
def index():
    # Not needed if you set SITEMAP_INCLUDE_RULES_WITHOUT_PARAMS=True
    app.config['SITEMAP_URL_SCHEME']='https'
    now = datetime.now().isoformat()
    yield 'index', {}, now
    yield 'shop', {}, now
    yield 'checkout', {}, now
    yield 'nosotros', {}, now
    yield 'comocomprar', {}, now
    # yield 'product_details', {'name':1}, now



@app.route('/productos/<categoria>', methods=["GET", "POST"])
@app.route('/productos', methods=["GET", "POST"])
@tryton.transaction()
def shop(categoria=None):
    if request.method == "GET":
        categorias = ProductCategory.search([])
        carrito = dict(session)
        total = 0
        for c in carrito:
            total += int(carrito[c]['cantidad']) * int(carrito[c]['precio'])
        if categoria:
            pro_cat, = ProductCategory.search([[('name', '=', categoria)]])
            pt = Product.search([('categories', '=', pro_cat)])
        else:
            pt = Product.search_random([], limit=9)
        return render_template('shop.html', product_template=pt, categorias=categorias, carrito=carrito, len=len(carrito), total=total)

@app.route('/<name>', methods=["GET", "POST"])
@tryton.transaction()
def product_details(name=None):
    if request.method == "GET":
        if name:
            carrito = dict(session)
            total = 0
            for c in carrito:
                total += int(carrito[c]['cantidad']) * int(carrito[c]['precio'])

            p_random = Product.search_random([], limit=4)
            pro = Product.search([('url', '=', name)])
            if not pro:
                pro = Product.search([('name', '=', name)])

        return render_template('product-details.html', p_random=p_random, product=pro[0], carrito=carrito, len=len(carrito), total=total)

@app.route('/checkout', methods=["GET", "POST"])
@app.route('/checkout.html', methods=["GET", "POST"])
@tryton.transaction()
def checkout():
    if request.method == "GET":
        carrito = dict(session)
        total = 0
        for c in carrito:
            total += int(carrito[c]['cantidad']) * int(carrito[c]['precio'])
        return render_template('checkout.html', carrito=carrito, len=len(carrito), total=total)
    if request.method == "POST":
        preferences = User.get_preferences(context_only=True)
        Company = tryton.pool.get('company.company')
        company = Company(preferences.get('company', 1))
        telefono = company.party.get_random_telefono()
        msg = "Hola Vidrios Francisco! Soy *%s, %s* y quiero hacer el siguiente pedido:\n\n" % (request.form.get('name'),
                                                                                            request.form.get('lastname'))
        total = 0
        for carrito in dict(session):
            msg += "- x%s %s\n" % (session[carrito]['cantidad'], carrito)
            total += int(session[carrito]['cantidad']) * int(session[carrito]['precio'])

        msg += "*Total $ %s*\n\n Dirección de entrega: %s, %s, %s\nQuiero abonar con *%s*\nMuchas Gracias" % (str(total),
                                                                                                                request.form.get('direccion'),
                                                                                                                request.form.get('ciudad'),
                                                                                                                request.form.get('provincia'),
                                                                                                                request.form.get('f_pago'),)
        url = "https://wa.me/+549" + str(telefono) + "/?text="
        msg2 = urllib.parse.quote(msg)
        session.clear()

        return redirect(url + msg2)

@app.route('/nosotros', methods=["GET", "POST"])
@app.route('/nosotros.html', methods=["GET", "POST"])
@tryton.transaction()
def nosotros():
    if request.method == "GET":
        carrito = dict(session)
        total = 0
        for c in carrito:
            total += int(carrito[c]['cantidad']) * int(carrito[c]['precio'])
        return render_template('nosotros.html', carrito=carrito, len=len(carrito), total=total)

@app.route('/comocomprar', methods=["GET", "POST"])
@app.route('/comocomprar.html', methods=["GET", "POST"])
@tryton.transaction()
def comocomprar():
    if request.method == "GET":
        carrito = dict(session)
        total = 0
        for c in carrito:
            total += int(carrito[c]['cantidad']) * int(carrito[c]['precio'])
        return render_template('comocomprar.html', carrito=carrito, len=len(carrito), total=total)

@app.route('/addCarrito', methods=['GET'])
@tryton.transaction()
def addCarrito():
    if request.args.get('nombre', None):
        if int(request.args.get('cantidad')) == 0:
            return jsonify(
            resultado=False
            )
        if session.get(request.args.get('nombre', None), False):
            actualiza = session.pop(request.args.get('nombre'))
            actualiza['cantidad'] += int(request.args.get('cantidad', None))
            session.update({request.args.get('nombre'):actualiza})
        else:
            product, = Product.search([('id', '=', request.args.get('producto_id', None))])
            session[request.args.get('nombre')] = {'cantidad': int(request.args.get('cantidad', None)),
                                                   'precio': str(product.template.list_price), #request.args.get('precio', None).replace('$', ''),
                                                   'producto_id': request.args.get('producto_id', None),
                                                   'img': product.get_image()
                                                   }
    #res = dict(session)
    #res.update({'len': len(session)})

    return jsonify(
        resultado=True,
    #    carrito=res
    )

@app.route('/delCarrito', methods=['GET'])
@tryton.transaction()
def delCarrito():
    if request.args.get('nombre', None):
            session.pop(request.args.get('nombre'))

    return jsonify(
        resultado=True,
    #    carrito=res
    )


#AJAC cada ves q agrega un articulo a su carrito, tienen q agregarlo a "session"
if __name__ == '__main__':

    app.run(host='0.0.0.0', threaded=True)
