from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Commune, User, Asset, Project
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from flask import request, jsonify
from flask_restful import Resource
from models import Asset
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
        try:
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
        finally:
            session.close()

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
        try:
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
        finally:
            session.close()

    def delete(self, commune_id):
        session = Session()
        try:
            commune = session.query(Commune).filter_by(id=commune_id).first()
            if not commune:
                return {"message": "Commune not found"}, 404
            
            session.delete(commune)
            session.commit()
            return {"message": "Commune deleted successfully"}, 200
        finally:
            session.close()

class UserResource(Resource):
    def get(self, user_id=None):
        session = Session()
        try:
            if user_id:
                user = session.query(User).filter_by(id=user_id).first()
                if user:
                    return jsonify({
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "commune_id": user.commune_id
                    })
                return {"message": "User not found"}, 404
            else:
                users = session.query(User).all()
                return jsonify([{
                    "id": u.id,
                    "username": u.username,
                    "email": u.email,
                    "commune_id": u.commune_id
                } for u in users])
        finally:
            session.close()

    def post(self):
        data = request.get_json()
        if not data or 'username' not in data or 'email' not in data:
            return {"message": "Username and email are required"}, 400
        
        session = Session()
        new_user = User(
            username=data['username'],
            email=data['email'],
            password_hash=data.get('password'),  # In a real app, you'd hash this
            commune_id=data.get('commune_id')
        )
        session.add(new_user)
        try:
            session.commit()
            return {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email,
                "commune_id": new_user.commune_id
            }, 201
        except IntegrityError:
            session.rollback()
            return {"message": "A user with this username or email already exists"}, 400
        finally:
            session.close()

    def put(self, user_id):
        data = request.get_json()
        if not data:
            return {"message": "No input data provided"}, 400
        
        session = Session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return {"message": "User not found"}, 404
            
            user.username = data.get('username', user.username)
            user.email = data.get('email', user.email)
            user.commune_id = data.get('commune_id', user.commune_id)
            if 'password' in data:
                user.password_hash = data['password']  # Remember to hash in a real app
            
            session.commit()
            return jsonify({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "commune_id": user.commune_id
            })
        except IntegrityError:
            session.rollback()
            return {"message": "A user with this username or email already exists"}, 400
        finally:
            session.close()

    def delete(self, user_id):
        session = Session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return {"message": "User not found"}, 404
            
            session.delete(user)
            session.commit()
            return {"message": "User deleted successfully"}, 200
        finally:
            session.close()

class AssetResource(Resource):
    def get(self, asset_id=None):
        session = Session()
        try:
            if asset_id:
                asset = session.query(Asset).filter_by(id=asset_id).first()
                if asset:
                    return jsonify({
                        "id": asset.id,
                        "name": asset.name,
                        "description": asset.description,
                        "type": asset.type,
                        "value": asset.value
                    })
                return {"message": "Asset not found"}, 404
            else:
                assets = session.query(Asset).all()
                return jsonify([{
                    "id": a.id,
                    "name": a.name,
                    "description": a.description,
                    "type": a.type,
                    "value": a.value
                } for a in assets])
        finally:
            session.close()

    def post(self):
        data = request.get_json()
        if not data or 'name' not in data:
            return {"message": "Name is required"}, 400
        
        session = Session()
        new_asset = Asset(
            name=data['name'],
            description=data.get('description', ''),
            type=data.get('type'),
            value=data.get('value')
        )
        session.add(new_asset)
        try:
            session.commit()
            return {
                "id": new_asset.id,
                "name": new_asset.name,
                "description": new_asset.description,
                "type": new_asset.type,
                "value": new_asset.value
            }, 201
        except IntegrityError:
            session.rollback()
            return {"message": "An asset with this name already exists"}, 400
        finally:
            session.close()

    def put(self, asset_id):
        data = request.get_json()
        if not data:
            return {"message": "No input data provided"}, 400
        
        session = Session()
        try:
            asset = session.query(Asset).filter_by(id=asset_id).first()
            if not asset:
                return {"message": "Asset not found"}, 404
            
            asset.name = data.get('name', asset.name)
            asset.description = data.get('description', asset.description)
            asset.type = data.get('type', asset.type)
            asset.value = data.get('value', asset.value)
            
            session.commit()
            return jsonify({
                "id": asset.id,
                "name": asset.name,
                "description": asset.description,
                "type": asset.type,
                "value": asset.value
            })
        except IntegrityError:
            session.rollback()
            return {"message": "An asset with this name already exists"}, 400
        finally:
            session.close()

    def delete(self, asset_id):
        session = Session()
        try:
            asset = session.query(Asset).filter_by(id=asset_id).first()
            if not asset:
                return {"message": "Asset not found"}, 404
            
            session.delete(asset)
            session.commit()
            return {"message": "Asset deleted successfully"}, 200
        finally:
            session.close()

class ProjectResource(Resource):
    def get(self, project_id=None):
        session = Session()
        try:
            if project_id:
                project = session.query(Project).filter_by(id=project_id).first()
                if project:
                    return jsonify({
                        "id": project.id,
                        "name": project.name,
                        "description": project.description,
                        "start_date": project.start_date.isoformat() if project.start_date else None,
                        "end_date": project.end_date.isoformat() if project.end_date else None,
                        "status": project.status,
                        "commune_id": project.commune_id
                    })
                return {"message": "Project not found"}, 404
            else:
                projects = session.query(Project).all()
                return jsonify([{
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "start_date": p.start_date.isoformat() if p.start_date else None,
                    "end_date": p.end_date.isoformat() if p.end_date else None,
                    "status": p.status,
                    "commune_id": p.commune_id
                } for p in projects])
        finally:
            session.close()

    def post(self):
        data = request.get_json()
        if not data or 'name' not in data:
            return {"message": "Name is required"}, 400
        
        session = Session()
        new_project = Project(
            name=data['name'],
            description=data.get('description', ''),
            start_date=datetime.fromisoformat(data['start_date']) if data.get('start_date') else None,
            end_date=datetime.fromisoformat(data['end_date']) if data.get('end_date') else None,
            status=data.get('status'),
            commune_id=data.get('commune_id')
        )
        session.add(new_project)
        try:
            session.commit()
            return {
                "id": new_project.id,
                "name": new_project.name,
                "description": new_project.description,
                "start_date": new_project.start_date.isoformat() if new_project.start_date else None,
                "end_date": new_project.end_date.isoformat() if new_project.end_date else None,
                "status": new_project.status,
                "commune_id": new_project.commune_id
            }, 201
        except IntegrityError:
            session.rollback()
            return {"message": "A project with this name already exists"}, 400
        finally:
            session.close()

    def put(self, project_id):
        data = request.get_json()
        if not data:
            return {"message": "No input data provided"}, 400
        
        session = Session()
        try:
            project = session.query(Project).filter_by(id=project_id).first()
            if not project:
                return {"message": "Project not found"}, 404
            
            project.name = data.get('name', project.name)
            project.description = data.get('description', project.description)
            project.start_date = datetime.fromisoformat(data['start_date']) if data.get('start_date') else project.start_date
            project.end_date = datetime.fromisoformat(data['end_date']) if data.get('end_date') else project.end_date
            project.status = data.get('status', project.status)
            project.commune_id = data.get('commune_id', project.commune_id)
            
            session.commit()
            return jsonify({
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "start_date": project.start_date.isoformat() if project.start_date else None,
                "end_date": project.end_date.isoformat() if project.end_date else None,
                "status": project.status,
                "commune_id": project.commune_id
            })
        except IntegrityError:
            session.rollback()
            return {"message": "A project with this name already exists"}, 400
        finally:
            session.close()

    def delete(self, project_id):
        session = Session()
        try:
            project = session.query(Project).filter_by(id=project_id).first()
            if not project:
                return {"message": "Project not found"}, 404
            
            session.delete(project)
            session.commit()
            return {"message": "Project deleted successfully"}, 200
        finally:
            session.close()

api.add_resource(HealthCheck, '/health')
api.add_resource(CommuneResource, '/commune', '/commune/<int:commune_id>')
api.add_resource(UserResource, '/user', '/user/<int:user_id>')
api.add_resource(AssetResource, '/asset', '/asset/<int:asset_id>')
api.add_resource(ProjectResource, '/project', '/project/<int:project_id>')

if __name__ == '__main__':
    app.run(debug=True)