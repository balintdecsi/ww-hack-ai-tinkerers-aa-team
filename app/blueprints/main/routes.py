import os
from flask import render_template, redirect, url_for, current_app, flash, request, abort
from werkzeug.utils import secure_filename
from app.models import AvatarProject, MangaProject
from app.services.anam import anam_service
from app.services.manga_generator import manga_service
from . import main_bp
from .forms import ProjectForm, MangaForm

# In-memory storage
PROJECTS = []
NEXT_ID = 1

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    global NEXT_ID
    project_form = ProjectForm()
    manga_form = MangaForm()
    
    # Handle ProjectForm (Avatar)
    if 'submit' in request.form and project_form.validate_on_submit():
        title = project_form.title.data
        comic = project_form.comic_file.data
        protagonist = project_form.protagonist_image.data
        
        comic_filename = secure_filename(comic.filename)
        protagonist_filename = secure_filename(protagonist.filename)
        
        upload_folder = current_app.config['UPLOAD_FOLDER']
        comic.save(os.path.join(upload_folder, comic_filename))
        protagonist.save(os.path.join(upload_folder, protagonist_filename))
        
        try:
            avatar_id = anam_service.create_avatar_from_image(
                os.path.join(upload_folder, protagonist_filename),
                name=title,
                gender=project_form.gender.data
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
            flash(f'Error creating avatar: {e}', 'danger')

    # Handle MangaForm
    if 'submit' in request.form and manga_form.validate_on_submit():
        title = manga_form.title.data
        plot = manga_form.plot.data
        files = request.files.getlist(manga_form.reference_images.name)
        
        saved_ref_paths = []
        upload_folder = current_app.config['UPLOAD_FOLDER']
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                path = os.path.join(upload_folder, filename)
                file.save(path)
                saved_ref_paths.append(path)
        
        try:
            result = manga_service.generate_manga(title, plot, saved_ref_paths)
            
            project = MangaProject(
                id=NEXT_ID,
                title=title,
                script=result['script'],
                audio_path=result['audio_file'],
                pages=result['pages']
            )
            PROJECTS.append(project)
            NEXT_ID += 1
            
            flash('Manga generated successfully!', 'success')
            return redirect(url_for('main.view_manga', project_id=project.id))
            
        except Exception as e:
            current_app.logger.error(f"Error generating manga: {e}")
            flash(f'Error generating manga: {e}', 'danger')

    # Sort projects by creation time (newest first)
    sorted_projects = sorted(PROJECTS, key=lambda p: p.created_at, reverse=True)
    return render_template('index.html', project_form=project_form, manga_form=manga_form, projects=sorted_projects)

@main_bp.route('/project/<int:project_id>')
def view_project(project_id):
    project = next((p for p in PROJECTS if p.id == project_id), None)
    if not project or project.type != 'avatar':
        abort(404)
        
    config = anam_service.get_avatar_config(project.anam_avatar_id)
    return render_template('view_project.html', project=project, anam_config=config)

@main_bp.route('/manga/<int:project_id>')
def view_manga(project_id):
    project = next((p for p in PROJECTS if p.id == project_id), None)
    if not project or project.type != 'manga':
        abort(404)
        
    return render_template('view_manga.html', project=project)
