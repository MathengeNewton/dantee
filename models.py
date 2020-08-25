from app import db,bcrypt


class Officers(db.Model):
    __tablename__="officers"
    id = db.Column(db.Integer, nullable=False,
                   primary_key=True, autoincrement=True)
    officer_rank = db.Column(db.String(), nullable=False)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)   
    phone_number = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    work_id = db.Column(db.String, nullable=False,unique = True)
    time_created = db.Column(db.TIMESTAMP, server_default=db.func.now())
    time_updated = db.Column(
        db.TIMESTAMP, onupdate=db.func.now(), server_default=db.func.now())

    # insert new user class

    def insert_record(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def all(cls):
        return cls.query.all()

    # check if email is in use
    @classmethod
    def check_email_exist(cls, email):
        customer = cls.query.filter_by(email=email).first()
        if customer:
            return True
        else:
            return False

    # validate password
    @classmethod
    def validate_password(cls, email, password):
        customer = cls.query.filter_by(email=email).first()

        if customer and bcrypt.check_password_hash(customer.password, password):
            return True
        else:
            return False
    @classmethod
    def get_name_by_workid(cls, wid):
        strwid = str(wid)
        officer =  cls.query.filter_by(work_id = strwid).first()
        if officer:
            return officer.name
        else:
            return False

    @classmethod
    def get_officers_id_by_email(cls, email):
        officer =  cls.query.filter_by(email=email).first()
        if officer:
            return officer.id
        else:
            return False
    # get user id
    @classmethod
    def get_user_id(cls, email):
        return cls.query.filter_by(email=email).first().id

    @classmethod
    def get_id_by_work_id(cls, wid):
        workid = cls.query.filter_by(work_id=wid).first()
        if workid:
            return workid.id
        else:
            return False
        

    @classmethod
    def rank(cls, uid):
        officer = cls.query.filter_by(id=uid).first()
        if officer:
            return officer.rank
        else:
            return False

    @classmethod
    def check_ocpd(cls, uid):
        officer = cls.query.filter_by(id=uid).first()
        if officer:
            rank = officer.officer_rank
            if rank == 'OCPD':
                return True
            else:
                return False
        else:
            return False




class Inmates(db.Model):
    __tablename__="inmates"
    id = db.Column(db.Integer, nullable=False,
                   primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    id_number = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String())
    time_created = db.Column(db.TIMESTAMP, server_default=db.func.now())
    time_updated = db.Column(
        db.TIMESTAMP, onupdate=db.func.now(), server_default=db.func.now())

    # insert new inmate class

    def insert_record(self):
        db.session.add(self)
        db.session.commit()

    # check if inmate exists
    @classmethod
    def check_inmate_exist(cls, id):
        inmate = cls.query.filter_by(id_number=id).first()
        if inmate:
            return True
        else:
            return False

    # get inmate id
    @classmethod
    def get_inmate_id_by_nid(cls, nid):
        inmate =  cls.query.filter_by(id_number=nid).first()
        if inmate:
            return inmate.id
        else:
            return False

    @classmethod
    def get_name_by_id(cls, id):
        inmate =  cls.query.filter_by(id=id).first()
        if inmate:
            return inmate.name
        else:
            return False


class Offences(db.Model):
    __tablename__="inmate_offence"
    id = db.Column(db.Integer, nullable=False,
                   primary_key=True, autoincrement=True)
    description = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False,default = "not cleared")
    arresting_officer = db.Column(db.Integer,db.ForeignKey('officers.id'),nullable=False)
    booking_officer = db.Column(db.Integer,db.ForeignKey('officers.id'),nullable=False)
    inmate = db.Column(db.Integer,db.ForeignKey('inmates.id'),nullable=False)
    time = db.Column(db.TIMESTAMP, server_default=db.func.now())
    time_updated = db.Column(db.TIMESTAMP, onupdate=db.func.now(), server_default=db.func.now())
    
    def insert_record(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def all_offences(cls):
        offenses = cls.query.all()
        return offenses

    @classmethod
    def pending_processing(cls):
        cases = cls.query.filter_by(status = "not cleared").all()
        return cases

    @classmethod
    def pending_court(cls):
        cases = cls.query.filter(cls.status.like("not cleared"),cls.category.like("felony"),cls.category.like("infraction")).all()
        return cases

    @classmethod
    def pending_release(cls):
        cases = cls.query.filter(cls.status.like("not cleared"),cls.category.like("misdemeanor")).all()
        return cases

    @classmethod
    def get_offence_by_inmate(cls, nid):
        offence =  cls.query.filter_by(inmate=nid).first()
        if offence:
            return offence
        else:
            return False

    @classmethod
    def update_offence_by_id(cls, nid):
        offence =  cls.query.filter_by(id=nid).first()
        if offence:
            offence.status = "cleared"
            db.session.commit()
            return True
        else:
            return False



class Courtcase(db.Model):
    __tablename__="inmate_courtcase"
    id = db.Column(db.Integer, nullable=False,
                   primary_key=True, autoincrement=True)
    case = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.String())
    status = db.Column(db.String(),default = 'fowarded')
    time_created = db.Column(db.TIMESTAMP, server_default=db.func.now())
    time_updated = db.Column(db.TIMESTAMP, onupdate=db.func.now(), server_default=db.func.now())

    # insert case class
    def insert_record(self):
        db.session.add(self)

class Cashbails(db.Model):
    __tablename__="inmate_cashbails"
    id = db.Column(db.Integer, nullable=False,
                   primary_key=True, autoincrement=True)
    case = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.String())
    time_created = db.Column(db.TIMESTAMP, server_default=db.func.now())
    time_updated = db.Column(
        db.TIMESTAMP, onupdate=db.func.now(), server_default=db.func.now())

    # insert bail class
    def insert_record(self):
        db.session.add(self)