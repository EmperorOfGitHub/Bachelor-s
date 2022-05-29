from VGTUcoin.models import User
from VGTUcoin.forms import *
from flask import Flask, jsonify, request, render_template, url_for, flash, redirect
from VGTUcoin import app, db, bcrypt
from VGTUcoin import blockchainObj
from flask_login import login_user, current_user, logout_user, login_required
from Crypto.PublicKey import RSA
import requests


@app.route("/")
@app.route("/home")
def home():
    blockchainObj.resolveConflicts()
    return render_template('blockchain.html', title="Blockchain", blockchain=blockchainObj)

@app.route("/purchase", methods=['GET', 'POST'])
def purchase():
    form = BuyForm()
    formNL = BuyFormNotLoggedIn()
    if form.validate_on_submit():
        print("Sveiki")
        feedback = blockchainObj.buy(form.buyer.data, form.amount.data)
        if feedback:
            flash(f'Ačiū už apsipirkimą! Valiuta atsiras jūsų paskyroje per keletą minučių', 'success')
        return render_template('purchase.html', title="Purchase", blockchain=blockchainObj, form=form, formNL=formNL)

    if formNL.validate_on_submit():
        return redirect(url_for('login'))

    return render_template('purchase.html', title="Purchase", blockchain=blockchainObj, form=form, formNL=formNL)

@app.route("/blockchain")
def blockchain():
    blockchainObj.resolveConflicts()
    return render_template('blockchain.html', title="Blockchain", blockchain=blockchainObj)


@app.route("/transaction", methods=['GET', 'POST'])
def transaction():
    form = TransactionForm()
    formNL = TransactionFormNotLoggedIn()
    if form.validate_on_submit():
        print("Sveiki")
        feedback = blockchainObj.addTransaction(
            form.sender.data, form.reciever.data, form.amount.data, form.key.data, form.key.data)
        if feedback:
            flash(f'Pervedimas atliktas', 'success')
        return render_template('transaction.html', title="Transaction", blockchain=blockchainObj, form=form, formNL=formNL)

    if formNL.validate_on_submit():
        return redirect(url_for('login'))

    return render_template('transaction.html', title="Transaction", blockchain=blockchainObj, form=form, formNL=formNL)


@app.route("/minerPage")
def minerPage():
    return render_template('minerPage.html', title="Mine", blockchain=blockchainObj)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # password hashing
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        keyGen = blockchainObj.generateKeys()
        user = User(name=form.name.data, username=form.username.data,
                    email=form.email.data, password=hashed_password, key=keyGen)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        nextPage = request.args.get('next')
        flash(
            f'Paskyra sukurta @{form.username.data}! Esate prisijungę', 'success')
        return redirect(nextPage) if nextPage else redirect(url_for('home'))
    return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            nextPage = request.args.get('next')
            flash(f'Sveiki, dabar esate prisijungę', 'success')
            return redirect(nextPage) if nextPage else redirect(url_for('home'))
        else:
            flash('Nepavyko prisijungti, patikrinkite el. paštą ir slaptažodį', 'danger')
    return render_template('login.html', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account', blockchain=blockchainObj)


# BLOCKCHAIN BACKEND REQUESTS
@app.route('/mine', methods=['GET'])
def mine():
    print("Pavyko")
    miner = request.args.get('miner', None)
    lastBlock = blockchainObj.getLastBlock()

    if len(blockchainObj.pendingTransactions) <= 1:
        flash(f'Per mažai operacijų (Turi būti > 1)', 'danger')
    else:
        feedback = blockchainObj.minePendingTransactions(miner)
        if feedback:
            flash(
                f'Kasyba atlikta, kasybos atlygis pridėtas prie laukiančių operacijų', 'success')
        else:
            flash(f'Klaida', 'danger')
    return render_template('minerPage.html', title="Mine", blockchain=blockchainObj)


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'reciever', 'amt']
    if not all(k in values for k in required):
        return 'Truksta duomenų', 400

    index = blockchainObj.addTransaction(
        values['sender'], values['reciever'], values['amt'])

    response = {'message': f'Operacija bus įtraukta į bloką {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchainObj.chainJSONencode(),
        'length': len(blockchainObj.chain),
    }
    return jsonify(response), 200