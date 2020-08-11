from flask import Blueprint

main_blueprint = Blueprint('main', __name__)


from . import views, errors
from ..models import Permission


@main_blueprint.app_context_processor
def inject_permission():
    return dict(Permission=Permission)
