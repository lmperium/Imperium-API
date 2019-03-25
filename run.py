from app import create_app, db
from app.models import Worker
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from flask_migrate import Migrate
from sqlalchemy import update


app = create_app('development')


def check_status():

    with app.app_context():
        workers = Worker.query.filter_by(status='active').all()

        if workers is not None:
            for worker in workers:
                last_seen = worker.last_seen
                t_diff = datetime.now() - last_seen

                if t_diff.total_seconds() / 60 > 10:
                    stmt = update(Worker)\
                           .where(Worker.worker_id == worker.worker_id)\
                           .values(status='offline')
                    db.session.execute(stmt)
                    db.session.commit()


migrate = Migrate(app, db)

scheduler = BackgroundScheduler()
scheduler.add_job(check_status, trigger='interval', minutes=10)
scheduler.start()


if __name__ == '__main__':
    app.run(use_reloader=False)
