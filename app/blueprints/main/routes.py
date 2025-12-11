import os
from flask import render_template, redirect, url_for, current_app, flash, request, abort
from werkzeug.utils import secure_filename
from app.models import AvatarProject
from app.services.anam import anam_service
from . import main_bp
from .forms import ProjectForm

# In-memory storage
PROJECTS = []
NEXT_ID = 1

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    global NEXT_ID
    form = ProjectForm()
    if form.validate_on_submit():
        title = form.title.data
        comic = form.comic_file.data
        protagonist = form.protagonist_image.data
        
        # Secure filenames
        comic_filename = secure_filename(comic.filename)
        protagonist_filename = secure_filename(protagonist.filename)
        
        # Save paths
        upload_folder = current_app.config['UPLOAD_FOLDER']
        comic_path = os.path.join(upload_folder, comic_filename)
        protagonist_path = os.path.join(upload_folder, protagonist_filename)
        
        comic.save(comic_path)
        protagonist.save(protagonist_path)
        
        # Call Anam API (Mock)
        try:
            # Pass gender to service for voice selection
            avatar_id = anam_service.create_avatar_from_image(
                protagonist_path,
                name=title,
                gender=form.gender.data
            )
            
            project = AvatarProject(
                id=NEXT_ID,
                title=title,
                comic_file_path=comic_filename,
                protagonist_image_path=protagonist_filename,
                anam_avatar_id=avatar_id
            )
            PROJECTS.append(project)
            NEXT_ID += 1
            
            flash('Avatar created successfully!', 'success')
            return redirect(url_for('main.view_project', project_id=project.id))
            
        except Exception as e:
            current_app.logger.error(f"Error creating avatar: {e}")
            flash('Error communicating with Anam API', 'danger')

    # Sort projects by creation time (newest first)
    sorted_projects = sorted(PROJECTS, key=lambda p: p.created_at, reverse=True)
    return render_template('index.html', form=form, projects=sorted_projects)

@main_bp.route('/project/<int:project_id>')
def view_project(project_id):
    project = next((p for p in PROJECTS if p.id == project_id), None)
    if not project:
        abort(404)
        
    # Get config for embedding
    config = anam_service.get_avatar_config(project.anam_avatar_id)
    return render_template('view_project.html', project=project, anam_config=config)