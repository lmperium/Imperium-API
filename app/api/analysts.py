from app.api import bp


@bp.route('/analysts', method=['GET'])
def get_analysts():
    pass


@bp.route('/analysts', method=['POST'])
def register_analyst():
    pass


@bp.route('/analysts/<int:id>', method=['GET'])
def get_analyst(id: int):
    pass
