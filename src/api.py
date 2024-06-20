from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Commune, User, Asset, Project
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
api = Api(app)

# Setup database connection
engine = create_engine('sqlite:///prometheus.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to Project Prometheus API"})

class HealthCheck(Resource):
    def get(self):
        return jsonify({"status": "healthy"})

class CommuneResource(Resource):
    def get(self, commune_id=None):
        session = Session()
        if commune_id:
            commune = session.query(Commune).filter_by(id=commune_id).first()
            if commune:
                return jsonify({
                    "id": commune.id,
                    "name": commune.name,
                    "description": commune.description,
                    "created_at": commune.created_at.isoformat()
                })
            return {"message": "Commune not found"}, 404
        else:
            communes = session.query(Commune).all()
            return jsonify([{
                "id": c.id,
                "name": c.name,
                "description": c.description,
                "created_at": c.created_at.isoformat()
            } for c in communes])

    def post(self):
        data = request.get_json()
        if not data or 'name' not in data:
            return {"message": "Name is required"}, 400
        
        session = Session()
        new_commune = Commune(name=data['name'], description=data.get('description', ''))
        session.add(new_commune)
        try:
            session.commit()
            return {
                "id": new_commune.id,
                "name": new_commune.name,
                "description": new_commune.description,
                "created_at": new_commune.created_at.isoformat()
            }, 201
        except IntegrityError:
            session.rollback()
            return {"message": "A commune with this name already exists"}, 400
        finally:
            session.close()
        
    def put(self, commune_id):
        data = request.get_json()
        if not data:
            return {"message": "No input data provided"}, 400
        
        session = Session()
        commune = session.query(Commune).filter_by(id=commune_id).first()
        if not commune:
            return {"message": "Commune not found"}, 404
        
        commune.name = data.get('name', commune.name)
        commune.description = data.get('description', commune.description)
        session.commit()
        
        return jsonify({
            "id": commune.id,
            "name": commune.name,
            "description": commune.description,
            "created_at": commune.created_at.isoformat()
        })

    def delete(self, commune_id):
        session = Session()
        commune = session.query(Commune).filter_by(id=commune_id).first()
        if not commune:
            return {"message": "Commune not found"}, 404
        
        session.delete(commune)
        session.commit()
        return {"message": "Commune deleted successfully"}, 200

class AssetResource(Resource):
    def get(self, asset_id):
        # TODO: Implement fetching asset details
        return jsonify({"message": f"Details for asset {asset_id}"})

    def post(self):
        # TODO: Implement registering a new asset
        data = request.get_json()
        return jsonify({"message": "New asset registered", "data": data})

class ProjectResource(Resource):
    def get(self, project_id):
        # TODO: Implement fetching project details
        return jsonify({"message": f"Details for project {project_id}"})

    def post(self):
        # TODO: Implement creating a new project
        data = request.get_json()
        return jsonify({"message": "New project created", "data": data})

api.add_resource(HealthCheck, '/health')
api.add_resource(CommuneResource, '/commune', '/commune/<int:commune_id>')
api.add_resource(AssetResource, '/asset/<int:asset_id>', '/asset')
api.add_resource(ProjectResource, '/project/<int:project_id>', '/project')

if __name__ == '__main__':
    app.run(debug=True)