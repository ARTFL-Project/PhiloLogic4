"""Rebuild web app after PhiloLogic database copied to new server / VM / docker env"""
import sys
import os


if __name__ == "__main__":
    philo_db = sys.argv[1]
    app_path = f"{philo_db}/app"
    os.system(f"rm -rf {app_path}")
    os.system(f"cp -R /var/lib/philologic4/web_app/app {philo_db}/")
    os.system(f"chown -R $(whoami) ${app_path}")  # Make sure we have the correct permissions for npm to run
    os.system(f"cd {app_path}; npm run build;")
    print(f"{philo_db} done")
