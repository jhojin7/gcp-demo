import os
import logging
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, send_file, abort
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import tempfile
import io

from config import get_config, Config
from gcp_storage import GCPStorageService
from services.file_service import FileService
from services.version_service import VersionService
from models.user import User
from models.operation import Operation


def create_app(config_name=None):
    """
    Application factory for Flask app.

    Args:
        config_name: Configuration environment name

    Returns:
        Configured Flask application
    """
    app = Flask(__name__)

    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)

    # Setup logging
    config.setup_logging()
    logger = logging.getLogger(__name__)

    # Validate required configuration
    missing_config = config.validate_required_settings()
    if missing_config:
        logger.error(f"Missing required configuration: {missing_config}")
        raise ValueError(f"Missing required configuration: {missing_config}")

    # Print configuration summary in debug mode
    if config.DEBUG:
        config.print_configuration_summary()

    # Create upload directory
    config.create_upload_directory()

    # Initialize services
    try:
        gcp_service = GCPStorageService(**config.get_gcp_config())
        file_service = FileService(gcp_service)
        version_service = VersionService(gcp_service)

        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise

    # Store services in app context
    app.gcp_service = gcp_service
    app.file_service = file_service
    app.version_service = version_service

    def get_current_user():
        """Get current user context (simplified for single-user implementation)."""
        return User(
            user_id=config.DEFAULT_USER_ID,
            display_name=config.DEFAULT_USER_NAME
        )

    def log_operation(operation: Operation):
        """Log operation for audit trail."""
        if config.ENABLE_AUDIT_LOGGING:
            logger.info(f"AUDIT: {operation.to_audit_log_entry()}")

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('error.html',
                             error_code=404,
                             error_message="File or page not found"), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return render_template('error.html',
                             error_code=500,
                             error_message="Internal server error"), 500

    @app.errorhandler(RequestEntityTooLarge)
    def file_too_large(error):
        max_size = app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024)
        return render_template('error.html',
                             error_code=413,
                             error_message=f"File too large. Maximum size: {max_size}MB"), 413

    @app.errorhandler(PermissionError)
    def permission_denied(error):
        return render_template('error.html',
                             error_code=403,
                             error_message="Access denied"), 403

    # Main routes
    @app.route('/')
    @app.route('/folder/<path:folder_path>')
    def file_browser(folder_path=''):
        """
        File browser endpoint - displays files and folders.
        GET / or GET /folder/<path>
        """
        try:
            user = get_current_user()

            # Normalize folder path
            if folder_path and not folder_path.endswith('/'):
                folder_path += '/'
            if not folder_path.startswith('/'):
                folder_path = '/' + folder_path

            # Get files in current folder
            files = file_service.list_files(folder_path, user, include_deleted=False)

            # Get subfolders
            folders = file_service.get_folders_in_path(folder_path, user)

            # Create breadcrumb trail
            breadcrumbs = []
            if folder_path != '/':
                from models.folder import Folder
                current_folder = Folder(virtual_path=folder_path, owner_id=user.user_id)
                breadcrumbs = current_folder.get_breadcrumb_trail()
            else:
                breadcrumbs = [{'name': 'Root', 'path': '/', 'is_current': True}]

            # Log view operation
            operation = Operation.create_view_operation(
                user_id=user.user_id,
                ip_address=request.remote_addr
            )
            log_operation(operation)

            return render_template('index.html',
                                 files=files,
                                 folders=folders,
                                 current_path=folder_path,
                                 breadcrumbs=breadcrumbs,
                                 upload_config=config.get_upload_config())

        except Exception as e:
            logger.error(f"File browser error: {e}")
            flash(f"Error loading folder: {e}", 'error')
            return redirect(url_for('file_browser'))

    @app.route('/upload', methods=['POST'])
    def upload_file():
        """
        File upload endpoint.
        POST /upload
        """
        try:
            user = get_current_user()

            # Check if file was uploaded
            if 'file' not in request.files:
                flash('No file selected', 'error')
                return redirect(request.referrer or url_for('file_browser'))

            file = request.files['file']
            if file.filename == '':
                flash('No file selected', 'error')
                return redirect(request.referrer or url_for('file_browser'))

            # Get target folder
            target_folder = request.form.get('folder', '/')
            if not target_folder.endswith('/'):
                target_folder += '/'

            # Validate file
            if not config.is_file_allowed(file.filename):
                flash(f'File type not allowed. Allowed types: {", ".join(config.UPLOAD_ALLOWED_EXTENSIONS)}', 'error')
                return redirect(request.referrer or url_for('file_browser'))

            # Secure filename
            filename = secure_filename(file.filename)
            if not filename:
                flash('Invalid filename', 'error')
                return redirect(request.referrer or url_for('file_browser'))

            # Read file content
            file_content = file.read()
            if len(file_content) == 0:
                flash('Empty file cannot be uploaded', 'error')
                return redirect(request.referrer or url_for('file_browser'))

            # Upload file
            file_obj, file_version, operation = file_service.upload_file(
                file_content=file_content,
                filename=filename,
                virtual_path=target_folder,
                user=user,
                content_type=file.content_type
            )

            # Log operation
            log_operation(operation)

            flash(f'File "{filename}" uploaded successfully', 'success')
            return redirect(url_for('file_browser', folder_path=target_folder.strip('/')))

        except Exception as e:
            logger.error(f"Upload error: {e}")
            flash(f"Upload failed: {e}", 'error')
            return redirect(request.referrer or url_for('file_browser'))

    @app.route('/download/<path:file_id>')
    def download_file(file_id):
        """
        Download current version of file.
        GET /download/<file_id>
        """
        try:
            user = get_current_user()

            # Download file
            content, filename, operation = file_service.download_file(
                file_id=file_id,
                user=user
            )

            # Log operation
            log_operation(operation)

            # Create file-like object for sending
            file_obj = io.BytesIO(content)
            file_obj.seek(0)

            return send_file(
                file_obj,
                as_attachment=True,
                download_name=filename,
                mimetype='application/octet-stream'
            )

        except FileNotFoundError:
            abort(404)
        except PermissionError:
            abort(403)
        except Exception as e:
            logger.error(f"Download error: {e}")
            flash(f"Download failed: {e}", 'error')
            return redirect(url_for('file_browser'))

    @app.route('/download/<path:file_id>/<version_id>')
    def download_file_version(file_id, version_id):
        """
        Download specific version of file.
        GET /download/<file_id>/<version_id>
        """
        try:
            user = get_current_user()

            # Download specific version
            content, filename, operation = file_service.download_file(
                file_id=file_id,
                user=user,
                version_id=version_id
            )

            # Log operation
            log_operation(operation)

            # Create file-like object for sending
            file_obj = io.BytesIO(content)
            file_obj.seek(0)

            return send_file(
                file_obj,
                as_attachment=True,
                download_name=filename,
                mimetype='application/octet-stream'
            )

        except FileNotFoundError:
            abort(404)
        except PermissionError:
            abort(403)
        except Exception as e:
            logger.error(f"Version download error: {e}")
            flash(f"Download failed: {e}", 'error')
            return redirect(url_for('file_browser'))

    @app.route('/delete/<path:file_id>', methods=['POST'])
    def delete_file(file_id):
        """
        Delete file (soft delete).
        POST /delete/<file_id>
        """
        try:
            user = get_current_user()

            # Delete file
            operation = file_service.delete_file(file_id, user)

            # Log operation
            log_operation(operation)

            flash(f'File deleted successfully', 'success')
            return redirect(request.referrer or url_for('file_browser'))

        except FileNotFoundError:
            flash('File not found', 'error')
        except PermissionError:
            flash('Access denied', 'error')
        except Exception as e:
            logger.error(f"Delete error: {e}")
            flash(f"Delete failed: {e}", 'error')

        return redirect(request.referrer or url_for('file_browser'))

    @app.route('/versions/<path:file_id>')
    def version_history(file_id):
        """
        View version history for a file.
        GET /versions/<file_id>
        """
        try:
            user = get_current_user()

            # Get version history
            versions = version_service.get_version_history(file_id, user)

            # Get file info
            file_info = file_service.get_file_info(file_id, user)
            if not file_info:
                abort(404)

            return render_template('versions.html',
                                 file_info=file_info,
                                 versions=versions,
                                 file_id=file_id)

        except FileNotFoundError:
            abort(404)
        except PermissionError:
            abort(403)
        except Exception as e:
            logger.error(f"Version history error: {e}")
            flash(f"Error loading version history: {e}", 'error')
            return redirect(url_for('file_browser'))

    @app.route('/restore/<path:file_id>/<version_id>', methods=['POST'])
    def restore_version(file_id, version_id):
        """
        Restore file to specific version.
        POST /restore/<file_id>/<version_id>
        """
        try:
            user = get_current_user()

            # Restore version
            file_obj, new_version, operation = file_service.restore_file_version(
                file_id=file_id,
                version_id=version_id,
                user=user
            )

            # Log operation
            log_operation(operation)

            flash(f'File restored to version {version_id}', 'success')
            return redirect(url_for('version_history', file_id=file_id))

        except FileNotFoundError:
            flash('File or version not found', 'error')
        except PermissionError:
            flash('Access denied', 'error')
        except Exception as e:
            logger.error(f"Restore error: {e}")
            flash(f"Restore failed: {e}", 'error')

        return redirect(url_for('version_history', file_id=file_id))

    # API endpoints
    @app.route('/api/files')
    def api_files():
        """
        API endpoint for listing files.
        GET /api/files?folder=<path>
        """
        try:
            user = get_current_user()
            folder_path = request.args.get('folder', '/')

            files = file_service.list_files(folder_path, user, include_deleted=False)
            folders = file_service.get_folders_in_path(folder_path, user)

            return jsonify({
                'success': True,
                'folder_path': folder_path,
                'files': [f.to_dict() for f in files],
                'folders': [f.to_dict() for f in folders]
            })

        except Exception as e:
            logger.error(f"API files error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/versions/<path:file_id>')
    def api_versions(file_id):
        """
        API endpoint for file version history.
        GET /api/versions/<file_id>
        """
        try:
            user = get_current_user()

            versions = version_service.get_version_history(file_id, user)

            return jsonify({
                'success': True,
                'file_id': file_id,
                'versions': [v.to_dict() for v in versions]
            })

        except FileNotFoundError:
            return jsonify({'success': False, 'error': 'File not found'}), 404
        except PermissionError:
            return jsonify({'success': False, 'error': 'Access denied'}), 403
        except Exception as e:
            logger.error(f"API versions error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/file/<path:file_id>/info')
    def api_file_info(file_id):
        """
        API endpoint for file information.
        GET /api/file/<file_id>/info
        """
        try:
            user = get_current_user()

            file_info = file_service.get_file_info(file_id, user)
            if not file_info:
                return jsonify({'success': False, 'error': 'File not found'}), 404

            return jsonify({
                'success': True,
                'file_info': file_info
            })

        except PermissionError:
            return jsonify({'success': False, 'error': 'Access denied'}), 403
        except Exception as e:
            logger.error(f"API file info error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    return app


# Application entry point
if __name__ == '__main__':
    app = create_app()
    config = get_config()

    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )