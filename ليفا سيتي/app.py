from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'liva-city-super-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ====================== MODELS ======================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150))
    phone = db.Column(db.String(30))
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='employee')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def role_label(self):
        return {'admin': 'مدير النظام', 'manager': 'مدير', 'employee': 'موظف'}.get(self.role, self.role)


class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    area = db.Column(db.Float, default=0)
    location = db.Column(db.String(200))
    status = db.Column(db.String(30), default='متاح')
    balance = db.Column(db.Float, default=0)
    shops = db.Column(db.Integer, default=0)
    shops_description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Buyer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(30))
    national_id = db.Column(db.String(30))
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'))
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    property = db.relationship('Property', backref='buyers')


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyer.id'))
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'))
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50))
    is_encrypted = db.Column(db.Boolean, default=True)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    buyer = db.relationship('Buyer', backref='payments')
    property = db.relationship('Property', backref='payments')


# ====================== DECORATORS ======================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            flash('ليس لديك صلاحية للوصول لهذه الصفحة ❌', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated


# ====================== AUTH ======================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.is_active and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['full_name'] = user.full_name
            session['role'] = user.role
            flash(f'مرحباً {user.full_name} 👋', 'success')
            return redirect(url_for('dashboard'))

        flash('بيانات الدخول غير صحيحة أو الحساب معطّل ❌', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج', 'info')
    return redirect(url_for('login'))


# ====================== DASHBOARD ======================
@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    total_properties = Property.query.count()
    total_buyers = Buyer.query.count()
    total_payments = db.session.query(db.func.sum(Payment.amount)).scalar() or 0
    available = Property.query.filter_by(status='متاح').count()
    sold = Property.query.filter_by(status='مباع').count()
    total_users = User.query.count()

    total_balance = db.session.query(db.func.sum(Property.balance)).scalar() or 0
    total_shops = db.session.query(db.func.sum(Property.shops)).scalar() or 0

    recent_payments = Payment.query.order_by(Payment.payment_date.desc()).limit(5).all()
    recent_buyers = Buyer.query.order_by(Buyer.purchase_date.desc()).limit(5).all()

    return render_template('dashboard.html',
        total_properties=total_properties,
        total_buyers=total_buyers,
        total_payments=total_payments,
        available=available,
        sold=sold,
        total_users=total_users,
        total_balance=total_balance,
        total_shops=total_shops,
        recent_payments=recent_payments,
        recent_buyers=recent_buyers
    )


# ====================== PROPERTIES ======================
@app.route('/properties')
@login_required
def properties():
    all_props = Property.query.order_by(Property.created_at.desc()).all()
    return render_template('properties.html', properties=all_props)


@app.route('/properties/add', methods=['POST'])
@login_required
def add_property():
    p = Property(
        name=request.form['name'],
        type=request.form['type'],
        price=float(request.form['price']),
        area=float(request.form.get('area', 0)),
        location=request.form.get('location', ''),
        status=request.form.get('status', 'متاح'),
        balance=float(request.form.get('balance') or 0),
        shops=int(request.form.get('shops') or 0),
        shops_description=request.form.get('shops_description', '')
    )
    db.session.add(p)
    db.session.commit()

    flash('تم إضافة العقار بنجاح ✅', 'success')
    return redirect(url_for('properties'))


@app.route('/properties/edit/<int:id>', methods=['POST'])
@login_required
def edit_property(id):
    p = Property.query.get_or_404(id)
    p.name = request.form['name']
    p.type = request.form['type']
    p.price = float(request.form['price'])
    p.area = float(request.form.get('area') or 0)
    p.location = request.form.get('location', '')
    p.status = request.form.get('status', 'متاح')
    p.balance = float(request.form.get('balance') or 0)
    p.shops = int(request.form.get('shops') or 0)
    p.shops_description = request.form.get('shops_description', '')
    db.session.commit()

    flash('تم تعديل العقار بنجاح ✅', 'success')
    return redirect(url_for('properties'))


@app.route('/properties/delete/<int:id>')
@login_required
def delete_property(id):
    p = Property.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()

    flash('تم حذف العقار', 'info')
    return redirect(url_for('properties'))


# ====================== BUYERS ======================
@app.route('/buyers')
@login_required
def buyers():
    all_buyers = Buyer.query.order_by(Buyer.purchase_date.desc()).all()
    props = Property.query.all()
    return render_template('buyers.html', buyers=all_buyers, properties=props)


@app.route('/buyers/add', methods=['POST'])
@login_required
def add_buyer():
    b = Buyer(
        name=request.form['name'],
        phone=request.form.get('phone', ''),
        national_id=request.form.get('national_id', ''),
        property_id=request.form.get('property_id') or None
    )
    db.session.add(b)
    if b.property_id:
        prop = Property.query.get(b.property_id)
        if prop:
            prop.status = 'مباع'
    db.session.commit()

    flash('تم إضافة المشتري بنجاح ✅', 'success')
    return redirect(url_for('buyers'))


@app.route('/buyers/delete/<int:id>')
@login_required
def delete_buyer(id):
    b = Buyer.query.get_or_404(id)
    db.session.delete(b)
    db.session.commit()

    flash('تم حذف المشتري', 'info')
    return redirect(url_for('buyers'))


# ====================== PAYMENTS ======================
@app.route('/payments')
@login_required
def payments():
    all_payments = Payment.query.order_by(Payment.payment_date.desc()).all()
    buyers_list = Buyer.query.all()
    props = Property.query.all()
    return render_template('payments.html',
        payments=all_payments,
        buyers=buyers_list,
        properties=props
    )


@app.route('/payments/add', methods=['POST'])
@login_required
def add_payment():
    p = Payment(
        buyer_id=request.form['buyer_id'],
        property_id=request.form.get('property_id') or None,
        amount=float(request.form['amount']),
        payment_method=request.form.get('payment_method', 'كاش'),
        is_encrypted=request.form.get('is_encrypted') == 'on',
        notes=request.form.get('notes', '')
    )
    db.session.add(p)

    if p.property_id:
        prop = Property.query.get(p.property_id)
        if prop:
            prop.balance = max(0, (prop.balance or 0) - p.amount)

    db.session.commit()

    flash('تم تسجيل الدفعة بنجاح ✅', 'success')
    return redirect(url_for('payments'))


@app.route('/payments/delete/<int:id>')
@login_required
def delete_payment(id):
    p = Payment.query.get_or_404(id)
    property_id = p.property_id
    amount = p.amount
    db.session.delete(p)

    if property_id:
        prop = Property.query.get(property_id)
        if prop:
            prop.balance = (prop.balance or 0) + amount

    db.session.commit()

    flash('تم حذف الدفعة', 'info')
    return redirect(url_for('payments'))


# ====================== USERS ======================
@app.route('/users')
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('users.html', users=all_users)


@app.route('/users/add', methods=['POST'])
@admin_required
def add_user():
    username = request.form['username'].strip()
    password = request.form['password']

    if User.query.filter_by(username=username).first():
        flash(f'اسم المستخدم "{username}" مستخدم بالفعل ❌', 'danger')
        return redirect(url_for('users'))

    if len(password) < 6:
        flash('كلمة المرور يجب أن تكون 6 أحرف على الأقل ❌', 'danger')
        return redirect(url_for('users'))

    new_user = User(
        username=username,
        full_name=request.form['full_name'].strip(),
        email=request.form.get('email', '').strip(),
        phone=request.form.get('phone', '').strip(),
        password=generate_password_hash(password),
        role=request.form.get('role', 'employee'),
        is_active=True
    )
    db.session.add(new_user)
    db.session.commit()

    flash(f'تم إنشاء حساب "{new_user.full_name}" بنجاح ✅', 'success')
    return redirect(url_for('users'))


@app.route('/users/edit/<int:id>', methods=['POST'])
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    user.full_name = request.form['full_name'].strip()
    user.email = request.form.get('email', '').strip()
    user.phone = request.form.get('phone', '').strip()

    new_role = request.form.get('role', user.role)
    if user.role == 'admin' and new_role != 'admin':
        admins_count = User.query.filter_by(role='admin', is_active=True).count()
        if admins_count <= 1:
            flash('لا يمكن تغيير دور آخر مدير نظام ❌', 'danger')
            return redirect(url_for('users'))

    user.role = new_role
    db.session.commit()

    flash(f'تم تعديل بيانات "{user.full_name}" ✅', 'success')
    return redirect(url_for('users'))


@app.route('/users/toggle/<int:id>')
@admin_required
def toggle_user(id):
    user = User.query.get_or_404(id)
    if user.id == session['user_id']:
        flash('لا يمكنك تعطيل حسابك الخاص ❌', 'danger')
        return redirect(url_for('users'))

    if user.role == 'admin' and user.is_active:
        admins_count = User.query.filter_by(role='admin', is_active=True).count()
        if admins_count <= 1:
            flash('لا يمكن تعطيل آخر مدير نظام ❌', 'danger')
            return redirect(url_for('users'))

    user.is_active = not user.is_active
    db.session.commit()
    status = 'تفعيل' if user.is_active else 'تعطيل'
    flash(f'تم {status} حساب "{user.full_name}" ✅', 'success')
    return redirect(url_for('users'))


@app.route('/users/delete/<int:id>')
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    if user.id == session['user_id']:
        flash('لا يمكنك حذف حسابك الخاص ❌', 'danger')
        return redirect(url_for('users'))
    if user.role == 'admin':
        admins_count = User.query.filter_by(role='admin').count()
        if admins_count <= 1:
            flash('لا يمكن حذف آخر مدير نظام ❌', 'danger')
            return redirect(url_for('users'))
    name = user.full_name
    db.session.delete(user)
    db.session.commit()

    flash(f'تم حذف حساب "{name}"', 'info')
    return redirect(url_for('users'))


@app.route('/users/reset-password/<int:id>', methods=['POST'])
@admin_required
def reset_password(id):
    user = User.query.get_or_404(id)
    new_pw = request.form['new_password']
    if len(new_pw) < 6:
        flash('كلمة المرور يجب أن تكون 6 أحرف على الأقل ❌', 'danger')
        return redirect(url_for('users'))
    user.password = generate_password_hash(new_pw)
    db.session.commit()
    flash(f'تم تغيير كلمة مرور "{user.full_name}" ✅', 'success')
    return redirect(url_for('users'))


# ====================== PROFILE ======================
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        old_pw = request.form['old_password']
        new_pw = request.form['new_password']
        if not check_password_hash(user.password, old_pw):
            flash('كلمة المرور الحالية غير صحيحة ❌', 'danger')
        elif len(new_pw) < 6:
            flash('كلمة المرور الجديدة قصيرة جداً ❌', 'danger')
        else:
            user.password = generate_password_hash(new_pw)
            db.session.commit()
            flash('تم تغيير كلمة المرور بنجاح ✅', 'success')
            return redirect(url_for('profile'))
    return render_template('profile.html', user=user)


# ====================== INIT DB ======================
def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                full_name='مدير النظام',
                email='admin@liva.com',
                phone='0500000000',
                password=generate_password_hash('admin123'),
                role='admin',
                is_active=True
            )
            db.session.add(admin)
            db.session.commit()
            print('✅ تم إنشاء حساب المدير: admin / admin123')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)