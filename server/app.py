from flask import Flask, request,jsonify
from sqlalchemy import Column, Integer, Text, Float, DateTime, create_engine, ForeignKey, func, and_
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import func
from flask_restful import Resource, Api
from dataclasses import dataclass
#import json
import simplejson as j
import pandas as pd
from flask_cors import CORS, cross_origin
from sqlalchemy.sql import text
from sqlalchemy import and_



Base = declarative_base()  # Basisklasse aller in SQLAlchemy verwendeten Klassen
metadata = Base.metadata

engine = create_engine('sqlite:///olympics.db', echo=True)

db_session = scoped_session(sessionmaker(autoflush=True, bind=engine))
Base.query = db_session.query_property() #Dadurch hat jedes Base - Objekt (also auch ein GeoInfo) ein Attribut query für Abfragen
app = Flask(__name__) #Die Flask-Anwendung
CORS(app, resources={r"/*": {"origins": "*"}})

# darf man von Webseiten aus nicht zugrfeifen
api = Api(app) #Die Flask API


@dataclass
class NocRegions(Base):
    noc : str
    region : str
    notes : str

    __tablename__ = 'noc_regions'
    noc = Column('NOC', Text, primary_key=True)
    region = Column('region', Text)
    notes = Column('notes', Text)


@dataclass #Diese ermoeglicht das Schreiben als JSON mit jsonify
class AthleteEvents(Base):
    __tablename__ = 'athlete_events'

    id: int
    name: str
    sex: str
    age: int
    height: int
    weight: int
    noc: NocRegions

    id = Column('ID', Integer, primary_key=True)
    name = Column('Name', Text)
    sex = Column('Sex', Text)
    age = Column('Age', Integer)
    height = Column('Height', Integer)
    weight = Column('Weight', Integer)
    team = Column('Team', Text)
    noc = Column('NOC', Text, ForeignKey(NocRegions.noc))
    games = Column('Games', Text)
    year = Column('Year', Integer)
    season = Column('Season', Text)
    city = Column('City', Text)
    sport = Column('Sport', Text)
    event = Column('Event', Text)
    medal = Column('Medal', Text)



@app.route('/event_by_noc/<string:noc>')
def event_by_noc(noc):
    infos = AthleteEvents.query.filter(AthleteEvents.noc == noc).all()
    return jsonify(infos)

@app.route('/regions')
def regions():
    infos = NocRegions.query.all()
    return  jsonify(infos)

@app.route('/events')
def events():
    infos = db_session.query(AthleteEvents.event).distinct(AthleteEvents.event).order_by(AthleteEvents.event).all()
    return  j.dumps(infos)

def medals_by_noc(noc):
    m = db_session.query(AthleteEvents.medal, func.count(AthleteEvents.medal)).filter(and_(AthleteEvents.medal != 'NA',AthleteEvents.noc == noc)).group_by(AthleteEvents.medal).all()
    m = pd.DataFrame.from_records(m, columns=['medal', 'cnt'])
    print(m)
    m['medal'] = pd.Categorical(m['medal'], ["Gold", "Silver", "Bronze"])
    m =  m.sort_values("medal")
    return m.values.tolist()

@app.route('/medals/<string:noc>')
def medals(noc):
    m = medals_by_noc(noc)
    return jsonify(m)

@app.route('/medals2/<string:noc>')
def medals2(noc):
    m = medals_by_noc(noc)
    key = []
    val = []
    for i in m:
        print(i[0] , i[1])
        key.append(i[0])
        val.append(i[1])
    res = [{'x' : key, 'y' : val , 'type':'bar'}]
    return j.dumps(res)


@app.route('/count_by_sex')
def events_group_by_sex():
    with engine.connect() as conn:
        query = text("SELECT sex, medal, count(*) FROM athlete_events WHERE medal != 'NA' GROUP BY sex, medal")
        res = conn.execute(query)
    res = [(row[0], row[1], row[2]) for row in res]
    print(res)
    return j.dumps(res)

@app.route('/count_by_sex2')
def events_group_by_sex2():
    res = engine.execute("SELECT sex, medal, count(*) FROM athlete_events WHERE medal != 'NA' GROUP BY sex, medal")
    keyM = []
    valM = []
    keyF = []
    valF = []
    for r in res:
        if r[0] == 'M':
            keyM.append(r[1])
            valM.append(r[2])
        else:
            keyF.append(r[1])
            valF.append(r[2])
    res = [(row[0], row[1], row[2]) for row in res]
    res = [{'x': keyM, 'y': valM, 'type': 'bar'},{'x': keyF, 'y': valF, 'type': 'bar'}]
    return j.dumps(res)

#@app.route('/count_by_sex2/<noc>')
#def count_by_sex2(noc):
    with engine.connect() as conn:
        query = text("SELECT sex, medal, count(*) FROM athlete_events WHERE medal != 'NA' AND NOC = :noc GROUP BY sex, medal")
        res = conn.execute(query, {'noc': noc})  # Pass parameters as a dictionary

    keyM = []
    valM = []
    keyF = []
    valF = []
    for r in res:
        if r[0] == 'M':
            keyM.append(r[1])
            valM.append(r[2])
        else:
            keyF.append(r[1])
            valF.append(r[2])
    res = [(row[0], row[1], row[2]) for row in res]
    res = [{'x': keyM, 'y': valM, 'type': 'bar'},{'x': keyF, 'y': valF, 'type': 'bar'}]
    return j.dumps(res)

@app.route('/event_by_region_noc/<string:noc>')
def event_by_region_noc(noc):
    infos = AthleteEvents.query.join(NocRegions, AthleteEvents.noc == NocRegions.noc).filter(NocRegions.region == noc).all()
    return jsonify(infos)

@app.route('/event_by_region/<string:region>')
def event_by_region(region):
    infos = AthleteEvents.query.join(NocRegions, AthleteEvents.noc == NocRegions.noc).filter(NocRegions.region == region).all()
    return jsonify(infos)

#@app.route('/MF_by_noc/<string:noc>')
#def MF_by_noc(noc):
    counts = (
        db_session.query(AthleteEvents.sex, func.count(AthleteEvents.sex))
        .filter(AthleteEvents.noc == noc)
        .group_by(AthleteEvents.sex)
        .all()
    )
    return jsonify(counts)


@app.teardown_appcontext
def shutdown_session(exception=None):
    print("Shutdown Session")
    db_session.remove()

@app.route('/count_by_sex2/<string:noc>')
def count_by_sex2(noc):
    res = db_session.query(AthleteEvents.sex, AthleteEvents.medal, func.count(AthleteEvents.medal)).filter(and_(AthleteEvents.medal != 'NA', AthleteEvents.noc == noc)).group_by(AthleteEvents.sex, AthleteEvents.medal).all()
    keyM = []
    valM = []
    keyF = []
    valF = []
    for r in res:
        if r[0] == 'M':
            keyM.append(r[1])
            valM.append(r[2])
        else:
            keyF.append(r[1])
            valF.append(r[2])
    res = [{'x': keyM, 'y': valM, 'type': 'bar'},{'x': keyF, 'y': valF, 'type': 'bar'}]
    return j.dumps(res)

@app.route('/MF_by_noc/<string:noc>')
def MF_by_noc(noc):
    res = db_session.query(AthleteEvents.sex, func.count(AthleteEvents.sex)).filter(and_(AthleteEvents.noc == noc)).group_by(AthleteEvents.sex).all()
    key = []
    val = []
    for r in res:
        key.append(r[0])
        val.append(r[1])
    res = [{'x': key, 'y': val, 'type': 'bar'}]
    return j.dumps(res)

@app.route('/age_by_height/<string:noc>')
def age_by_height(noc):
    res = db_session.query(AthleteEvents.age, AthleteEvents.height).filter(and_(AthleteEvents.noc == noc)).all()
    res = [{'x': [row[0] for row in res], 'y': [row[1] for row in res], 'mode': 'markers', 'type': 'scatter'}]
    return j.dumps(res)

@app.route('/medals/<region>/<event>', methods=['GET'])
def get_medals_by_event(region, event):
    medals = db_session.query(AthleteEvents.medal, func.count(AthleteEvents.medal)) \
        .join(NocRegions, AthleteEvents.noc == NocRegions.noc) \
        .filter(and_(AthleteEvents.medal != 'NA', NocRegions.region == region, AthleteEvents.event == event)) \
        .group_by(AthleteEvents.medal).all()
    
    medals_df = pd.DataFrame.from_records(medals, columns=['medal', 'cnt'])
    medals_df['medal'] = pd.Categorical(medals_df['medal'], ["Gold", "Silver", "Bronze"])
    medals_df = medals_df.sort_values("medal")
    return jsonify(medals_df.values.tolist())

@app.route('/medals2/<region>/<event>', methods=['GET'])
def get_medals2_by_event(region, event):
    medals = db_session.query(AthleteEvents.medal, func.count(AthleteEvents.medal)) \
        .join(NocRegions, AthleteEvents.noc == NocRegions.noc) \
        .filter(and_(AthleteEvents.medal != 'NA', NocRegions.region == region, AthleteEvents.event == event)) \
        .group_by(AthleteEvents.medal).all()
    
    medals_df = pd.DataFrame.from_records(medals, columns=['medal', 'cnt'])
    medals_df['medal'] = pd.Categorical(medals_df['medal'], ["Gold", "Silver", "Bronze"])
    medals_df = medals_df.sort_values("medal")

    key = []
    val = []
    for row in medals_df.itertuples():
        key.append(row.medal)
        val.append(row.cnt)

    response = [{'x': key, 'y': val, 'type': 'bar'}]
    return j.dumps(response)


if __name__ == '__main__':
    app.run(debug=True)